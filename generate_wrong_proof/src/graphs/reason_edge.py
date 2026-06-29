from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class ReasonEdge:
    source: str
    target: str
    kind: str
    weight: int


def pairwise_edges(reasons: list[str], kind: str, weight: int = 1) -> list[ReasonEdge]:
    return [ReasonEdge(source, target, kind, weight) for source, target in combinations(reasons, 2)]


def connect_from_one(source: str, targets: list[str], kind: str, weight: int = 1) -> list[ReasonEdge]:
    return [ReasonEdge(source, target, kind, weight) for target in targets]


def connect_to_one(sources: list[str], target: str, kind: str, weight: int = 1) -> list[ReasonEdge]:
    return [ReasonEdge(source, target, kind, weight) for source in sources]


def listed_edges(pairs: list[tuple[str, str]], kind: str, weight: int = 1) -> list[ReasonEdge]:
    return [ReasonEdge(source, target, kind, weight) for source, target in pairs]


def remove_duplicate_edges(edges: list[ReasonEdge]) -> tuple[ReasonEdge, ...]:
    seen: set[tuple[str, str, str]] = set()
    result: list[ReasonEdge] = []

    for edge in edges:
        key = (edge.source, edge.target, edge.kind)
        if key in seen:
            continue
        seen.add(key)
        result.append(edge)

    return tuple(result)