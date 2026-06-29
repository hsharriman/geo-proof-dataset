from src.graphs.reason_edge import ReasonEdge, connect_to_one, listed_edges, pairwise_edges
from src.graphs.reason_families import PARALLEL_ANGLE_THEOREMS, PARALLEL_CONVERSE_THEOREMS


def build_parallel_line_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += pairwise_edges(PARALLEL_ANGLE_THEOREMS, "parallel_angle_family")
    edges += listed_edges([
        ("altint", "altint_conv"),
        ("altext", "altext_conv"),
        ("corresp_ang", "corresp_ang_conv"),
        ("sameside_ang", "sameside_ang_conv"),
    ], "converse_confusion")

    edges += pairwise_edges(PARALLEL_CONVERSE_THEOREMS, "parallel_converse_family")
    edges += connect_to_one(["altint_conv", "corresp_ang_conv", "sameside_ang_conv"], "def_parallelogram", "parallel_parallelogram_dependency")
    edges += connect_to_one(["altint_conv", "corresp_ang_conv"], "pgram_opp_side_para", "parallel_parallelogram_dependency")
    edges += listed_edges([("altint", "asa"), ("corresp_ang", "asa"), ("altint", "aas"), ("corresp_ang", "aas")], "parallel_triangle_congruence_dependency")
    edges += connect_to_one(["altint", "corresp_ang", "altext"], "aa_sim", "parallel_triangle_similarity_dependency")

    return edges
