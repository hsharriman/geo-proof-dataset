from src.graphs.reason_edge import ReasonEdge, remove_duplicate_edges
from generate_wrong_proof.src.graphs.reason_edges import build_angle_congruence_edges
from generate_wrong_proof.src.graphs.reason_edges import build_linear_pair_edges
from generate_wrong_proof.src.graphs.reason_edges import build_other_quadrilateral_edges
from generate_wrong_proof.src.graphs.reason_edges import build_parallel_line_edges
from generate_wrong_proof.src.graphs.reason_edges import build_parallelogram_edges
from generate_wrong_proof.src.graphs.reason_edges import build_perpendicular_right_edges
from generate_wrong_proof.src.graphs.reason_edges import build_rectangle_edges
from generate_wrong_proof.src.graphs.reason_edges import build_rhombus_edges
from generate_wrong_proof.src.graphs.reason_edges import build_segment_congruence_edges
from generate_wrong_proof.src.graphs.reason_edges import build_special_triangle_edges
from generate_wrong_proof.src.graphs.reason_edges import build_triangle_center_edges
from generate_wrong_proof.src.graphs.reason_edges import build_triangle_congruence_edges
from generate_wrong_proof.src.graphs.reason_edges import build_triangle_similarity_edges


def build_reason_graph_edges() -> tuple[ReasonEdge, ...]:
    edges: list[ReasonEdge] = []

    edges += build_triangle_congruence_edges()
    edges += build_triangle_similarity_edges()
    edges += build_special_triangle_edges()
    edges += build_angle_congruence_edges()
    edges += build_segment_congruence_edges()
    edges += build_parallel_line_edges()
    edges += build_perpendicular_right_edges()
    edges += build_linear_pair_edges()
    edges += build_parallelogram_edges()
    edges += build_rectangle_edges()
    edges += build_rhombus_edges()
    edges += build_other_quadrilateral_edges()
    edges += build_triangle_center_edges()

    return remove_duplicate_edges(edges)


REASON_GRAPH_EDGES: tuple[ReasonEdge, ...] = build_reason_graph_edges()