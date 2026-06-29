from src.graphs.reason_edge import ReasonEdge, connect_from_one, connect_to_one, pairwise_edges
from src.graphs.reason_families import TRIANGLE_CONGRUENCE


def build_triangle_congruence_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += pairwise_edges(TRIANGLE_CONGRUENCE, "same_triangle_congruence_family")
    edges += connect_to_one(TRIANGLE_CONGRUENCE, "cpctc", "triangle_congruence_to_parts")
    edges.append(ReasonEdge("cpctc", "def_con_tri", "congruent_triangle_parts", 1))

    edges += connect_from_one("asa", ["vert_ang", "third_angle", "def_ang_bisect", "perp_con_ang", "base_angle"], "triangle_congruence_angle_dependency")
    edges += connect_from_one("aas", ["vert_ang", "third_angle", "def_ang_bisect", "perp_con_ang", "base_angle"], "triangle_congruence_angle_dependency")
    edges += connect_from_one("sas", ["vert_ang", "def_ang_bisect", "perp_con_ang"], "triangle_congruence_angle_dependency")

    edges += connect_from_one("sas", ["reflex_s", "def_midpt", "con_transitive", "perp_bisector", "pgram_opp_sides"], "triangle_congruence_segment_dependency")
    edges += connect_from_one("sss", ["reflex_s", "def_midpt", "con_transitive", "perp_bisector", "pgram_opp_sides", "rect_diag_con"], "triangle_congruence_segment_dependency")
    edges += connect_from_one("rhl", ["def_con_right", "def_perp", "perp_con_ang"], "triangle_congruence_right_angle_dependency")
    edges += connect_from_one("rhl", ["reflex_s", "def_midpt"], "triangle_congruence_segment_dependency")

    return edges
