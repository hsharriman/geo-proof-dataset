from __future__ import annotations
from collections.abc import Callable
from generate_wrong_proof.src.mutation.methods.circular_reasoning import circular_reasoning_mutations
from generate_wrong_proof.src.mutation.methods.mixed_up_theorem import mixed_up_theorem_mutations
from generate_wrong_proof.src.mutation.methods.non_control_permutation import non_control_permutation_mutations
from generate_wrong_proof.src.mutation.methods.remove_step import remove_step_mutations
from generate_wrong_proof.src.mutation.methods.tree_permutation import tree_permutation_mutations
from generate_wrong_proof.src.mutation.mutation_context import MutationContext
from generate_wrong_proof.src.mutation.mutation_types import keep_mutation, mutation_key
from generate_wrong_proof.src.parsing.proof_parser import Step


MutationMethod = Callable[[Step, MutationContext], list[dict]]


MUTATION_METHODS: tuple[MutationMethod, ...] = (
    tree_permutation_mutations,
    non_control_permutation_mutations,
    mixed_up_theorem_mutations,
    remove_step_mutations,
    circular_reasoning_mutations,
)


def candidate_steps(steps: list[Step], step_num: int | None) -> list[Step]:
    if not steps:
        return []
    final_step = steps[-1]
    middle_steps = steps[:-1]
    if step_num is not None:
        if step_num == final_step.num:
            raise ValueError(f"Step [{step_num:02d}] is the final conclusion step")
        for step in middle_steps:
            if step.num == step_num:
                return [step]
        raise ValueError(f"Step [{step_num:02d}] not found before the final step")
    non_given_steps = [step for step in middle_steps if step.reason != "given"]
    return list(reversed(non_given_steps or middle_steps))


def unique_mutations(mutations: list[dict]) -> list[dict]:
    seen_keys: set[tuple[int, str, str]] = set()
    unique: list[dict] = []
    for mutation in mutations:
        key = mutation_key(mutation)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(mutation)
    return unique


def collect_step_mutations(step: Step, context: MutationContext) -> list[dict]:
    mutations: list[dict] = []
    for mutation_method in MUTATION_METHODS:
        mutations.extend(mutation_method(step, context))
    return unique_mutations(mutations)


def available_mutations(
    steps: list[Step],
    context: MutationContext,
    allowed_types: set[str],
    required_type: str | None = None,
) -> list[dict]:
    available: list[dict] = []
    for step in steps:
        step_mutations = collect_step_mutations(step, context)
        for mutation in step_mutations:
            if not keep_mutation(mutation, allowed_types):
                continue
            if required_type is not None and mutation["mutation_type"] != required_type:
                continue
            available.append(mutation)
    return available