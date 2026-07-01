from __future__ import annotations

from generate_wrong_proof.src.geometry.geometry_objects import (
    argument_tree,
    object_key,
    object_type,
)
from generate_wrong_proof.src.mutation.methods.tree_permutation import (
    edit_angle_tree,
    edit_triangle_tree,
    edit_circle_tree,
)
from generate_wrong_proof.src.mutation.mutation_context import MutationContext
from generate_wrong_proof.src.mutation.mutation_types import build_mutation
from generate_wrong_proof.src.parsing.proof_parser import (
    Step,
    parse_statement,
    render_statement,
)


def segment_replacements(
    segment: str,
    points: list[str],
    segments: list[str],
) -> list[str]:
    if object_type(segment) != "segment":
        return []
    start_point, end_point = segment
    old_key = object_key(segment)
    seen_keys: set[str] = set()
    mutations: list[str] = []
    def add_segment(candidate: str) -> None:
        if object_type(candidate) != "segment":
            return
        key = object_key(candidate)
        if key == old_key or key in seen_keys:
            return
        seen_keys.add(key)
        mutations.append(candidate)
    for declared_segment in segments:
        add_segment(declared_segment)
    for point in points:
        if point not in {start_point, end_point}:
            add_segment(start_point + point)
    return mutations


def argument_mutations(
    argument: str,
    points: list[str],
    segments: list[str],
) -> list[str]:
    kind = object_type(argument)
    if kind == "angle":
        return [node.value for node in edit_angle_tree(argument_tree(argument))]
    if kind == "triangle":
        return [node.value for node in edit_triangle_tree(argument_tree(argument))]
    if kind == "segment":
        return segment_replacements(argument, points, segments)
    if kind == "circle":
        return [node.value for node in edit_circle_tree(argument_tree(argument), points)]
    return []


def non_control_permutation_mutations(
    step: Step,
    context: MutationContext,
) -> list[dict]:
    parsed_statement = parse_statement(step.statement)
    if parsed_statement is None:
        return []
    predicate, arguments = parsed_statement
    mutations: list[dict] = []
    for index, argument in enumerate(arguments):
        for new_argument in argument_mutations(
            argument,
            context.points,
            context.segments,
        ):
            new_arguments = arguments[:]
            new_arguments[index] = new_argument
            after = render_statement(predicate, new_arguments)
            mutation = build_mutation(
                step=step,
                before=step.statement,
                after=after,
                corruption_type="wrong_statement_argument_permutation",
                mutation_type="permutation_non_tree",
            )
            if mutation is not None:
                mutations.append(mutation)
    return mutations
