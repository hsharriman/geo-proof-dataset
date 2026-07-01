from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TreeNode:
    kind: str
    value: str
    children: tuple["TreeNode", ...] = ()


def object_type(argument: str) -> str | None:
    if argument.startswith("a_"):
        return "angle"
    if argument.startswith("t_"):
        return "triangle"
    if argument.startswith("q_"):
        return "quadrilateral"
    if argument.isalpha() and argument.isupper() and len(argument) == 1:
        return "point"
    if argument.isalpha() and argument.isupper() and len(argument) == 2:
        return "segment"
    if argument.startswith("c_"):
        return "circle"
    return None


def object_key(argument: str) -> str:
    kind = object_type(argument)
    if kind == "segment":
        return "segment:" + "".join(sorted(argument))
    if kind == "angle" and len(argument) == 5:
        points = argument[2:]
        endpoints = "".join(sorted([points[0], points[2]]))
        vertex = points[1]
        return f"angle:{endpoints}:{vertex}"
    if kind == "triangle":
        return "triangle:" + "".join(sorted(argument[2:]))
    if kind == "quadrilateral":
        return "quadrilateral:" + "".join(sorted(argument[2:]))
    if kind == "circle":
        return "circle:" + argument
    return argument


def argument_tree(argument: str) -> TreeNode:
    kind = object_type(argument)

    if kind == "angle" and len(argument) == 5:
        points = argument[2:]
        return TreeNode(
            kind="angle",
            value=argument,
            children=(
                TreeNode(kind="point", value=points[0]),
                TreeNode(kind="vertex", value=points[1]),
                TreeNode(kind="point", value=points[2]),
            ),
        )

    if kind == "triangle" and len(argument) == 5:
        points = argument[2:]
        return TreeNode(
            kind="triangle",
            value=argument,
            children=tuple(
                TreeNode(kind="point", value=point)
                for point in points
            ),
        )

    if kind == "segment" and len(argument) == 2:
        return TreeNode(
            kind="segment",
            value=argument,
            children=(
                TreeNode(kind="point", value=argument[0]),
                TreeNode(kind="point", value=argument[1]),
            ),
        )

    if kind == "quadrilateral" and len(argument) >= 6:
        points = argument[2:]
        return TreeNode(
            kind="quadrilateral",
            value=argument,
            children=tuple(
                TreeNode(kind="point", value=point)
                for point in points
            ),
        )
    
    if kind == "circle" and argument.startswith("c_"):
        points = argument[2:]
        return TreeNode(
            kind="circle",
            value=argument,
            children=tuple(TreeNode(kind="point", value=point) for point in points),
        )

    return TreeNode(
        kind=kind or "unknown",
        value=argument,
        children=(),
    )


def statement_tree(
    predicate: str,
    arguments: list[str],
) -> TreeNode:
    return TreeNode(
        kind="statement",
        value=predicate,
        children=tuple(
            argument_tree(argument)
            for argument in arguments
        ),
    )


def tree_arguments(tree: TreeNode) -> list[str]:
    return [
        child.value
        for child in tree.children
    ]