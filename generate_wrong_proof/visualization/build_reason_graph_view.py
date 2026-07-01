from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent
VIEW_DIR = PROJECT_ROOT / "visualization" / "reason_graph_view"
DATA_OUTPUT_PATH = VIEW_DIR / "reason_graph_data.js"

for path in [REPOSITORY_ROOT, PROJECT_ROOT]:
    path_string = str(path)

    if path_string not in sys.path:
        sys.path.insert(0, path_string)


try:
    from generate_wrong_proof.src.graphs.reason_graph import REASON_GRAPH_EDGES
    from generate_wrong_proof.src.graphs.reason_families import REASON_FAMILIES
except ModuleNotFoundError:
    from src.graphs.reason_graph import REASON_GRAPH_EDGES
    from src.graphs.reason_families import REASON_FAMILIES


EDGE_COLORS = {
    "same family": "#4C78A8",
    "application/dependency": "#54A24B",
    "consequence": "#F58518",
    "converse/confusion": "#E45756",
    "confusion": "#B279A2",
    "related": "#777777",
}


FAMILY_COLORS = {
    "triangle_congruence": "#dbeafe",
    "triangle_similarity": "#ede9fe",
    "special_triangles": "#fef3c7",
    "angle_congruence": "#dcfce7",
    "segment_congruence": "#e0f2fe",
    "parallel_lines": "#fce7f3",
    "perpendicular_right": "#fee2e2",
    "linear_pair": "#f3f4f6",
    "parallelogram": "#ecfccb",
    "rectangle": "#ccfbf1",
    "rhombus": "#ffedd5",
    "other_quadrilaterals": "#f5f5f4",
    "triangle_centers": "#e9d5ff",
    "other": "#eeeeee",
}


def edge_semantic(edge_kind: str) -> str:
    if "converse" in edge_kind:
        return "converse/confusion"

    if "confusion" in edge_kind:
        return "confusion"

    if "to_parts" in edge_kind or "parts" in edge_kind:
        return "consequence"

    if "dependency" in edge_kind:
        return "application/dependency"

    if "same_" in edge_kind:
        return "same family"

    if "family" in edge_kind:
        return "same family"

    return "related"


def node_family(node: str) -> str:
    for family, nodes in REASON_FAMILIES.items():
        if node in nodes:
            return family

    return "other"


def compact_edge(edge) -> list[str]:
    return [
        edge.source,
        edge.target,
        edge_semantic(edge.kind),
        edge.kind,
    ]


def build_graph_data() -> dict:
    family_edges: dict[str, list[list[str]]] = defaultdict(list)
    pair_edges: dict[str, list[list[str]]] = defaultdict(list)

    for edge in REASON_GRAPH_EDGES:
        source_family = node_family(edge.source)
        target_family = node_family(edge.target)

        item = compact_edge(edge)

        if source_family == target_family:
            family_edges[source_family].append(item)
        else:
            pair_key = "|||".join(sorted([source_family, target_family]))
            pair_edges[pair_key].append(item)

    return {
        "families": REASON_FAMILIES,
        "family_edges": {
            family: family_edges[family]
            for family in REASON_FAMILIES
        },
        "pair_edges": dict(sorted(pair_edges.items())),
    }


def make_reason_graph_data_js() -> str:
    graph_data = build_graph_data()

    return (
        "window.GRAPH_DATA = "
        + json.dumps(graph_data, indent=2)
        + ";\n\n"
        + "window.EDGE_COLORS = "
        + json.dumps(EDGE_COLORS, indent=2)
        + ";\n\n"
        + "window.FAMILY_COLORS = "
        + json.dumps(FAMILY_COLORS, indent=2)
        + ";\n"
    )


def main() -> None:
    VIEW_DIR.mkdir(parents=True, exist_ok=True)

    DATA_OUTPUT_PATH.write_text(
        make_reason_graph_data_js(),
        encoding="utf-8",
    )

    print(f"Wrote {DATA_OUTPUT_PATH}")
    print(f"Total reason edges: {len(REASON_GRAPH_EDGES)}")


if __name__ == "__main__":
    main()