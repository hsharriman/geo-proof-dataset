from __future__ import annotations
from collections import deque
from generate_wrong_proof.src.graphs.dependencies_tree import STATEMENT_TREE

def predicate_neighbors(predicate: str) -> list[str]:
    neighbors: list[str] = []

    for neighbor in STATEMENT_TREE.get(predicate, []):
        if neighbor not in neighbors:
            neighbors.append(neighbor)

    for parent, children in STATEMENT_TREE.items():
        if predicate in children and parent not in neighbors:
            neighbors.append(parent)

    return neighbors

def related_predicates(predicate: str) -> set[str]:
    related: set[str] = set()
    queue: deque[str] = deque(predicate_neighbors(predicate))

    while queue:
        current = queue.popleft()
        if current in related:
            continue
        related.add(current)
        for neighbor in predicate_neighbors(current):
            if neighbor not in related and neighbor != predicate:
                queue.append(neighbor)

    return related

def predicates_are_related(
    old_predicate: str,
    new_predicate: str,
) -> bool:
    if old_predicate == new_predicate:
        return False
    return new_predicate in related_predicates(old_predicate)