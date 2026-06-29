from src.graphs.reason_edge import ReasonEdge, connect_from_one, listed_edges, pairwise_edges
from src.graphs.reason_families import TRIANGLE_SIMILARITY


def build_triangle_similarity_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += pairwise_edges(TRIANGLE_SIMILARITY, "same_triangle_similarity_family")
    edges += listed_edges([("sas", "sas_sim"), ("sss", "sss_sim"), ("asa", "aa_sim"), ("aas", "aa_sim")], "triangle_congruence_similarity_confusion")
    edges += connect_from_one("aa_sim", ["vert_ang", "third_angle", "def_ang_bisect", "base_angle"], "triangle_similarity_angle_dependency")
    edges += connect_from_one("aa_sim", ["altint", "altext", "corresp_ang"], "triangle_similarity_parallel_angle_dependency")
    edges += connect_from_one("sas_sim", ["reflex_s", "def_midpt"], "triangle_similarity_segment_dependency")
    edges += connect_from_one("sss_sim", ["reflex_s", "def_midpt"], "triangle_similarity_segment_dependency")

    return edges
