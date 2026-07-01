from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal


ParamType = Literal[
    "segment",
    "angle",
    "triangle",
    "point",
    "quadrilateral",
    "circle",
]


STATEMENT_SIGNATURES: Dict[str, List[ParamType]] = {
    "on_line": ["segment", "point"],
    "transversal": [
        "point", "point", "point", "point",
        "point", "point", "point", "point",
    ],
    "intersect_seg": ["segment", "segment", "point"],

    "trapezoid_premise": ["quadrilateral", "segment", "segment"],
    "kite_premise": ["quadrilateral", "angle", "angle"],
    "isos_trapezoid_premise": ["quadrilateral", "segment", "segment"],

    "right": ["angle"],

    "con_seg": ["segment", "segment"],
    "con_ang": ["angle", "angle"],
    "con_tri": ["triangle", "triangle"],
    "con_right": ["angle", "angle"],

    "para": ["segment", "segment"],
    "perp": ["segment", "segment", "point"],

    "isosceles": ["triangle"],
    "midpt": ["segment", "point"],
    "ang_bisect": ["angle", "segment"],

    "rectangle": ["quadrilateral"],
    "parallelogram": ["quadrilateral"],
    "rhombus": ["quadrilateral"],
    "isos_trapezoid": ["quadrilateral"],

    "sim_seg": ["segment", "segment"],
    "sim_tri": ["triangle", "triangle"],

    "equilateral": ["triangle"],
    "equiangular": ["triangle"],

    "supplementary": ["angle", "angle"],
    "complementary": ["angle", "angle"],
    "linear_pair": ["angle", "angle"],

    "circumcenter": ["point", "triangle"],
    "incenter": ["point", "triangle"],
    "perp_bisector": ["segment", "segment", "point"],
    "seg_bisect": ["segment", "segment", "point"],

    "inscribed_angle": ["angle", "segment"],
    "tangent": ["circle", "segment", "point"],
    "chord": ["circle", "segment"],
    "arc": ["circle", "point", "point"],
    "radius": ["circle", "point"],
    "diameter": ["circle", "segment"],
    "inscribed_angle": ["angle", "segment"],
}


@dataclass(frozen=True)
class StatementSchema:
    """
    Static schema for one checker statement.

    Example:
        con_ang(a_ABD,a_ABC)

    Schema:
        predicate: con_ang
        arguments: angle, angle
    """

    predicate: str
    arguments: tuple[ParamType, ...]


def build_statement_schemas() -> Dict[str, StatementSchema]:
    return {
        predicate: StatementSchema(
            predicate=predicate,
            arguments=tuple(argument_types),
        )
        for predicate, argument_types in STATEMENT_SIGNATURES.items()
    }


STATEMENT_TREE_SCHEMAS: Dict[str, StatementSchema] = build_statement_schemas()


@dataclass(frozen=True)
class PredicateGroup:
    """
    Semantic neighborhood for predicate-level edits.

    Example:
        con_ang(...) may be edited near con_right(...).
        con_tri(...) may be edited near sim_tri(...).
    """

    name: str
    predicates: tuple[str, ...]


PREDICATE_GROUPS: tuple[PredicateGroup, ...] = (
    PredicateGroup(
        name="angle_relation",
        predicates=(
            "con_ang",
            "con_right",
            "supplementary",
            "complementary",
            "linear_pair",
        ),
    ),

    PredicateGroup(
        name="segment_relation",
        predicates=(
            "con_seg",
            "sim_seg",
        ),
    ),

    PredicateGroup(
        name="triangle_relation",
        predicates=(
            "con_tri",
            "sim_tri",
        ),
    ),

    PredicateGroup(
        name="line_relation",
        predicates=(
            "para",
            "perp",
        ),
    ),

    PredicateGroup(
        name="bisector_relation",
        predicates=(
            "midpt",
            "seg_bisect",
            "perp_bisector",
        ),
    ),

    PredicateGroup(
        name="quadrilateral_property",
        predicates=(
            "parallelogram",
            "rectangle",
            "rhombus",
            "isos_trapezoid",
        ),
    ),

    PredicateGroup(
        name="trapezoid_property",
        predicates=(
            "trapezoid_premise",
            "isos_trapezoid_premise",
            "isos_trapezoid",
        ),
    ),

    PredicateGroup(
        name="triangle_property",
        predicates=(
            "isosceles",
            "equilateral",
            "equiangular",
        ),
    ),

    PredicateGroup(
        name="center_property",
        predicates=(
            "circumcenter",
            "incenter",
        ),
    ),

    PredicateGroup(
        name="circle_relation",
        predicates=(
            "tangent",
            "chord",
            "arc",
            "radius",
            "diameter",
        ),
    ),
)


DIRECT_PREDICATE_EDGES: Dict[str, List[str]] = {
    "on_line": ["midpt"],
    "con_ang": ["con_right"],
    "parallelogram": ["rectangle", "rhombus"],
    "trapezoid_premise": ["isos_trapezoid_premise"],
    "isos_trapezoid_premise": ["isos_trapezoid"],
}


CONSTRAINT_NAMES: tuple[str, ...] = (
    "preserve_statement_signature_when_predicate_unchanged",
    "preserve_argument_type",
    "preserve_equality_pattern",
    "edit_small_subtree_only",
)


def add_edge(
    tree: Dict[str, List[str]],
    source: str,
    target: str,
) -> None:
    if source == target:
        return

    if source not in tree:
        tree[source] = []

    if target not in tree[source]:
        tree[source].append(target)


def build_predicate_tree() -> Dict[str, List[str]]:
    """
    Build the predicate-edit graph from direct edges and semantic groups.
    """
    tree: Dict[str, List[str]] = {
        source: targets[:]
        for source, targets in DIRECT_PREDICATE_EDGES.items()
    }

    for group in PREDICATE_GROUPS:
        for source in group.predicates:
            for target in group.predicates:
                add_edge(tree, source, target)

    return tree


PREDICATE_TREE: Dict[str, List[str]] = build_predicate_tree()


@dataclass(frozen=True)
class MutationTree:
    """
    Static data for the mutation system.

    Stores:
        1. statement schemas
        2. predicate edit graph
        3. constraint names
    """

    statement_schemas: Dict[str, StatementSchema]
    predicate_tree: Dict[str, List[str]]
    constraints: tuple[str, ...]


GEOMETRY_MUTATION_TREE = MutationTree(
    statement_schemas=STATEMENT_TREE_SCHEMAS,
    predicate_tree=PREDICATE_TREE,
    constraints=CONSTRAINT_NAMES,
)


STATEMENT_TREE: Dict[str, List[str]] = GEOMETRY_MUTATION_TREE.predicate_tree