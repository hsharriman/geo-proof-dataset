from __future__ import annotations

from generate_wrong_proof.src.geometry.geometry_objects import object_key, object_type
from generate_wrong_proof.src.graphs.dependencies_tree import STATEMENT_SIGNATURES


def statement_signature(predicate: str) -> list[str] | None:
    return STATEMENT_SIGNATURES.get(predicate)


def arguments_match_signature(predicate: str, arguments: list[str]) -> bool:
    signature = statement_signature(predicate)
    if signature is None:
        return False
    if len(signature) != len(arguments):
        return False
    for argument, expected_type in zip(arguments, signature):
        if object_type(argument) != expected_type:
            return False
    return True


def preserve_statement_signature_when_predicate_unchanged(
    old_predicate: str,
    new_predicate: str,
    new_arguments: list[str],
) -> bool:
    if old_predicate != new_predicate:
        return True
    return arguments_match_signature(old_predicate, new_arguments)


def preserve_argument_type(
    old_arguments: list[str],
    new_arguments: list[str],
) -> bool:
    if len(old_arguments) != len(new_arguments):
        return False
    for old_argument, new_argument in zip(old_arguments, new_arguments):
        if object_type(old_argument) != object_type(new_argument):
            return False
    return True


def equality_pattern(arguments: list[str]) -> set[tuple[int, int]]:
    pattern: set[tuple[int, int]] = set()

    for first_index in range(len(arguments)):
        for second_index in range(first_index + 1, len(arguments)):
            if object_key(arguments[first_index]) == object_key(arguments[second_index]):
                pattern.add((first_index, second_index))

    return pattern


def preserve_equality_pattern(old_arguments: list[str], new_arguments: list[str]) -> bool:
    return equality_pattern(old_arguments) == equality_pattern(new_arguments)


def equality_class_indices(arguments: list[str], index: int) -> list[int]:
    target_key = object_key(arguments[index])

    return [
        current_index
        for current_index, argument in enumerate(arguments)
        if object_key(argument) == target_key
    ]


def changed_argument_indices(
    old_arguments: list[str],
    new_arguments: list[str],
) -> list[int]:
    return [
        index
        for index, (old_argument, new_argument) in enumerate(
            zip(old_arguments, new_arguments)
        )
        if old_argument != new_argument
    ]


def edit_small_subtree_only(old_arguments: list[str], new_arguments: list[str]) -> bool:
    changed_indices = changed_argument_indices(old_arguments, new_arguments)

    if not changed_indices:
        return False

    equality_indices = equality_class_indices(old_arguments, changed_indices[0])
    return changed_indices == equality_indices


def object_edit_satisfies_constraints(
    predicate: str,
    old_arguments: list[str],
    new_arguments: list[str],
) -> bool:
    if not preserve_statement_signature_when_predicate_unchanged(old_predicate=predicate, new_predicate=predicate, new_arguments=new_arguments):
        return False
    if not preserve_argument_type(old_arguments, new_arguments):
        return False
    if not preserve_equality_pattern(old_arguments, new_arguments):
        return False
    if not edit_small_subtree_only(old_arguments, new_arguments):
        return False
    return True


def predicate_edit_satisfies_constraints(
    old_predicate: str,
    new_predicate: str,
    new_arguments: list[str],
) -> bool:
    if old_predicate == new_predicate:
        return False
    return arguments_match_signature(new_predicate, new_arguments)
