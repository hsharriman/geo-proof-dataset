from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import replace
from pathlib import Path

from generate_wrong_proof.src.mutation.mutation_collector import available_mutations, candidate_steps
from generate_wrong_proof.src.mutation.mutation_context import MutationContext
from generate_wrong_proof.src.mutation.mutation_types import (
    chain_has_required_types,
    chain_key,
    chain_metadata,
    forced_next_type,
    selected_mutation_types,
    validate_required_types,
)
from generate_wrong_proof.src.parsing.proof_parser import (
    Step,
    extract_points,
    extract_segments,
    parse_steps,
    read_lines,
    write_lines,
)


def changed_step(step: Step, statement: str) -> Step:
    return Step(step.line_index, step.raw, step.num, step.reason, step.refs, statement)


def changed_context(context: MutationContext, mutation: dict) -> MutationContext:
    step: Step = mutation["step"]
    steps = [
        changed_step(current_step, mutation["after"]) if current_step.num == step.num else current_step
        for current_step in context.steps
    ]
    return replace(context, steps=steps)


def wrong_base_name(input_path: Path) -> str:
    return re.sub(r"_c\d+$", "", input_path.stem)


def next_wrong_path(input_path: Path, output_dir: Path) -> tuple[Path, str]:
    base_name = wrong_base_name(input_path)
    pattern = re.compile(rf"^{re.escape(base_name)}_inc(\d+)\.txt$")
    indices = [int(match.group(1)) for path in output_dir.glob(f"{base_name}_inc*.txt") if (match := pattern.match(path.name))]
    wrong_id = f"inc{max(indices, default=0) + 1}"
    return output_dir / f"{base_name}_{wrong_id}.txt", wrong_id


def load_context(input_path: Path) -> tuple[list[str], MutationContext]:
    original_lines = read_lines(input_path)
    steps = parse_steps(original_lines)
    if not steps:
        raise ValueError(f"No proof steps found in {input_path}")
    return original_lines, MutationContext(steps, extract_points(original_lines), extract_segments(original_lines))


def mutation_target_count(
    context: MutationContext,
    step_num: int | None,
    num_corruptions: int | None,
    allowed_types: set[str],
    input_path: Path,
) -> int:
    mutations = available_mutations(candidate_steps(context.steps, step_num), context, allowed_types)
    if not mutations:
        raise ValueError(f"No possible wrong-statement mutations found in {input_path}")
    return num_corruptions or len(mutations)


def all_mutation_chains(
    context: MutationContext,
    step_num: int | None,
    mutations_per_proof: int | None,
    allowed_types: set[str],
    required_types: set[str],
) -> list[list[dict]]:
    chains: list[list[dict]] = []
    seen_chains: set[tuple[tuple[int, str, str], ...]] = set()

    max_mutations = len(candidate_steps(context.steps, step_num))

    if mutations_per_proof is None:
        target_lengths = range(1, max_mutations + 1)
    else:
        target_lengths = [mutations_per_proof]

    def collect(current_context: MutationContext, chain: list[dict], target_length: int) -> None:
        if len(chain) == target_length:
            if not chain_has_required_types(chain, required_types):
                return
            key = chain_key(chain)
            if key not in seen_chains:
                seen_chains.add(key)
                chains.append(chain)
            return

        required_type = forced_next_type(chain, required_types, target_length)
        mutations = available_mutations(candidate_steps(current_context.steps, step_num), current_context, allowed_types, required_type)
        used_step_nums = {mutation["step"].num for mutation in chain}
        for mutation in mutations:
            if mutation["step"].num in used_step_nums:
                continue
            collect(changed_context(current_context, mutation), chain + [mutation], target_length)

    for target_length in target_lengths:
        if target_length <= 0:
            continue
        if target_length > max_mutations:
            continue
        if len(required_types) > target_length:
            continue
        collect(context, [], target_length)

    return chains


def mutation_chains(
    context: MutationContext,
    step_num: int | None,
    target_count: int | None,
    mutations_per_proof: int | None,
    random_source: random.Random,
    allowed_types: set[str],
    required_types: set[str],
    all_possible: bool,
) -> list[list[dict]]:
    if all_possible:
        return all_mutation_chains(context, step_num, mutations_per_proof, allowed_types, required_types)
    if mutations_per_proof is None:
        mutations_per_proof = 1
    if target_count is None:
        target_count = 1
    chains = all_mutation_chains(context, step_num, mutations_per_proof, allowed_types, required_types)
    random_source.shuffle(chains)
    return chains[:target_count]


def apply_mutation_chain(
    original_lines: list[str],
    mutations: list[dict],
    input_path: Path,
    output_dir: Path,
) -> dict:
    corrupted_lines = original_lines[:]
    for mutation in mutations:
        step: Step = mutation["step"]
        corrupted_lines[step.line_index] = changed_step(step, mutation["after"]).render()
    output_path, wrong_id = next_wrong_path(input_path, output_dir)
    write_lines(output_path, corrupted_lines)
    return chain_metadata(str(input_path), str(output_path), wrong_id, mutations)


def corrupt_file(
    input_path: Path,
    output_dir: Path,
    step_num: int | None,
    num_corruptions: int | None,
    random_source: random.Random,
    allowed_types: set[str],
    required_types: set[str],
    mutations_per_proof: int | None,
    all_possible: bool,
) -> list[dict]:
    original_lines, context = load_context(input_path)
    if all_possible:
        target_count = None
    else:
        target_count = mutation_target_count(context, step_num, num_corruptions, allowed_types, input_path)
    chains = mutation_chains(context, step_num, target_count, mutations_per_proof, random_source, allowed_types, required_types, all_possible)
    return [apply_mutation_chain(original_lines, mutations, input_path, output_dir) for mutations in chains]

def collect_input_files(
    input_dir: Path,
    filenames: list[str] | None,
    glob_pattern: str,
    limit: int | None,
) -> list[Path]:
    input_files: list[Path] = []
    if filenames:
        for filename in filenames:
            input_file = input_dir / filename
            input_files.append(input_file)
    else:
        input_files = sorted(input_dir.glob(glob_pattern))
    if limit is not None:
        input_files = input_files[:limit]
    return input_files


def write_metadata(metadata_path: Path, metadata_rows: list[dict]) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("a", encoding="utf-8") as metadata_file:
        for row in metadata_rows:
            metadata_file.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("../geo-proof-dataset/proofs"))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--metadata-out", type=Path, default=None)
    parser.add_argument("--files", nargs="*")
    parser.add_argument("--glob", default="*.txt")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--step", type=int, default=None)
    parser.add_argument("--num-corruptions", type=int, default=None)
    parser.add_argument("--all-possible", action="store_true")
    parser.add_argument("--mutations-per-proof", type=int, default=None)
    parser.add_argument("--mutation-types", nargs="*", default=["all"])
    parser.add_argument("--require-mutation-types", nargs="*", default=[])
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    output_dir = args.output_dir or args.input_dir.parent / "wrong_proofs"
    metadata_out = args.metadata_out or output_dir / "wrong_statement_metadata.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed_types = selected_mutation_types(args.mutation_types, default_all=True)
    required_types = selected_mutation_types(args.require_mutation_types, default_all=False)
    validate_required_types(allowed_types, required_types, args.mutations_per_proof)
    random_source = random.Random(args.seed)
    metadata_rows: list[dict] = []
    for input_path in collect_input_files(args.input_dir, args.files, args.glob, args.limit):
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        metadata_rows.extend(
            corrupt_file(
                input_path,
                output_dir,
                args.step,
                args.num_corruptions,
                random_source,
                allowed_types,
                required_types,
                args.mutations_per_proof,
                args.all_possible,
            )
        )
    write_metadata(metadata_out, metadata_rows)
    print(f"Wrote {len(metadata_rows)} wrong proofs to {output_dir}")


if __name__ == "__main__":
    main()