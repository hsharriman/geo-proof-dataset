from __future__ import annotations

from itertools import permutations as iter_permutations

from generate_wrong_proof.src.geometry.geometry_objects import (
    TreeNode,
    argument_tree,
    object_key,
    object_type,
    statement_tree,
    tree_arguments,
)
from generate_wrong_proof.src.graphs.dependencies_tree import STATEMENT_SIGNATURES
from generate_wrong_proof.src.graphs.predicate_graph import predicate_neighbors
from generate_wrong_proof.src.mutation.constraints import (
    equality_class_indices,
    object_edit_satisfies_constraints,
    predicate_edit_satisfies_constraints,
)
from generate_wrong_proof.src.mutation.mutation_context import MutationContext
from generate_wrong_proof.src.mutation.mutation_types import build_mutation
from generate_wrong_proof.src.parsing.proof_parser import (
    Step,
    parse_statement,
    render_statement,
)


def point_values(node: TreeNode) -> list[str]:
    return [child.value for child in node.children]


def non_identity_permutations(values: list[str]) -> list[list[str]]:
    return [list(order) for order in iter_permutations(values) if list(order) != values]


def edit_angle_tree(node: TreeNode) -> list[TreeNode]:
    points = point_values(node)
    if len(points) != 3:
        return []
    reversed_points = list(reversed(points))
    return [
        argument_tree("a_" + "".join(new_points))
        for new_points in non_identity_permutations(points)
        if new_points != reversed_points
    ]


def edit_triangle_tree(node: TreeNode) -> list[TreeNode]:
    points = point_values(node)
    if len(points) != 3:
        return []
    return [
        argument_tree("t_" + "".join(new_points))
        for new_points in non_identity_permutations(points)
    ]


def edit_segment_tree(
    node: TreeNode,
    points: list[str],
    segments: list[str],
) -> list[TreeNode]:
    old_points = point_values(node)
    if len(old_points) != 2:
        return []
    old_key = object_key(node.value)
    seen_keys: set[str] = set()
    mutations: list[TreeNode] = []
    def add_segment(segment: str) -> None:
        if object_type(segment) != "segment":
            return
        key = object_key(segment)
        if key == old_key or key in seen_keys:
            return
        if len(set(old_points).intersection(set(segment))) != 1:
            return
        seen_keys.add(key)
        mutations.append(argument_tree(segment))
    for segment in segments:
        add_segment(segment)
    for index in range(2):
        for point in points:
            if point in old_points:
                continue
            new_points = old_points[:]
            new_points[index] = point
            add_segment("".join(new_points))
    return mutations


def edit_circle_tree(node: TreeNode, points: list[str]) -> list[TreeNode]:
    old_points = point_values(node)
    if len(old_points) < 2:
        return []
    center = old_points[0]
    old_value = node.value
    mutations: list[TreeNode] = []
    for point in points:
        if point in old_points:
            continue
        new_circle = "c_" + center + point
        if new_circle == old_value:
            continue
        mutations.append(argument_tree(new_circle))
    return mutations


def edit_object_tree(
    node: TreeNode,
    points: list[str],
    segments: list[str],
) -> list[TreeNode]:
    if node.kind == "angle":
        return edit_angle_tree(node)
    if node.kind == "triangle":
        return edit_triangle_tree(node)
    if node.kind == "segment":
        return edit_segment_tree(node, points, segments)
    if node.kind == "circle":
        return edit_circle_tree(node, points)
    return []


def reuse_arguments_for_signature(
    arguments: list[str],
    signature: list[str],
) -> list[str] | None:
    used_indices: set[int] = set()
    new_arguments: list[str] = []
    for expected_type in signature:
        chosen_index = None
        for index, argument in enumerate(arguments):
            if index in used_indices:
                continue
            if object_type(argument) != expected_type:
                continue
            chosen_index = index
            break
        if chosen_index is None:
            return None
        used_indices.add(chosen_index)
        new_arguments.append(arguments[chosen_index])
    return new_arguments


def edit_predicate(tree: TreeNode) -> list[TreeNode]:
    old_predicate = tree.value
    old_arguments = tree_arguments(tree)
    mutations: list[TreeNode] = []
    for new_predicate in predicate_neighbors(old_predicate):
        signature = STATEMENT_SIGNATURES.get(new_predicate)
        if signature is None:
            continue
        new_arguments = reuse_arguments_for_signature(old_arguments, signature)
        if new_arguments is None:
            continue
        if not predicate_edit_satisfies_constraints(old_predicate=old_predicate, new_predicate=new_predicate, new_arguments=new_arguments,):
            continue
        mutations.append(statement_tree(new_predicate, new_arguments))
    return mutations


def edit_statement_objects(
    tree: TreeNode,
    points: list[str],
    segments: list[str],
) -> list[TreeNode]:
    old_arguments = tree_arguments(tree)
    mutations: list[TreeNode] = []

    for index, child in enumerate(tree.children):
        indices = equality_class_indices(old_arguments, index)
        if index != indices[0]:
            continue
        for new_child in edit_object_tree(child, points, segments):
            new_arguments = old_arguments[:]
            for replacement_index in indices:
                new_arguments[replacement_index] = new_child.value
            if new_arguments == old_arguments:
                continue
            if not object_edit_satisfies_constraints(predicate=tree.value, old_arguments=old_arguments, new_arguments=new_arguments,):
                continue
            mutations.append(statement_tree(tree.value, new_arguments))
    return mutations


def tree_mutations(
    predicate: str,
    arguments: list[str],
    points: list[str] | None = None,
    segments: list[str] | None = None,
) -> list[dict]:
    old_tree = statement_tree(predicate, arguments)
    mutations: list[dict] = []

    for new_tree in edit_predicate(old_tree):
        mutations.append(
            {
                "new_predicate": new_tree.value,
                "new_arguments": tree_arguments(new_tree),
                "corruption_type": "wrong_statement_tree_predicate",
            }
        )
    for new_tree in edit_statement_objects(old_tree, points or [], segments or []):
        mutations.append(
            {
                "new_predicate": new_tree.value,
                "new_arguments": tree_arguments(new_tree),
                "corruption_type": "wrong_statement_tree_object",
            }
        )
    return mutations


def tree_permutation_mutations(
    step: Step,
    context: MutationContext,
) -> list[dict]:
    parsed_statement = parse_statement(step.statement)

    if parsed_statement is None:
        return []
    predicate, arguments = parsed_statement
    mutations: list[dict] = []
    for tree_mutation in tree_mutations(
        predicate,
        arguments,
        context.points,
        context.segments,
    ):
        after = render_statement(
            tree_mutation["new_predicate"],
            tree_mutation["new_arguments"],
        )
        mutation = build_mutation(
            step=step,
            before=step.statement,
            after=after,
            corruption_type=tree_mutation["corruption_type"],
            mutation_type="permutation_tree",
        )
        if mutation is not None:
            mutations.append(mutation)
    return mutations
