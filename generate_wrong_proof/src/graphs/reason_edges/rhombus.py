from src.graphs.reason_edge import ReasonEdge, listed_edges


def build_rhombus_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += listed_edges([("rhombus_pgram", "rhombus_diag_perp"), ("rhombus_pgram", "rhombus_opp_bisect")], "rhombus_family")
    edges += listed_edges([("rhombus_diag_perp", "rhombus_diag_perp_conv"), ("rhombus_opp_bisect", "rhombus_opp_bisect_conv")], "converse_confusion")
    edges += listed_edges([("rhombus_diag_perp_conv", "rhombus_opp_bisect_conv"), ("rhombus_opp_bisect_conv", "rhombus_consec_sides")], "rhombus_converse_family")
    edges += listed_edges([("rhombus_pgram", "def_parallelogram"), ("rhombus_pgram", "pgram_opp_sides")], "rhombus_parallelogram_dependency")
    edges.append(ReasonEdge("rhombus_diag_perp", "def_perp", "rhombus_perpendicular_dependency", 1))
    edges += listed_edges([("rhombus_diag_perp", "rhl"), ("rhombus_opp_bisect", "asa"), ("rhombus_consec_sides", "sss")], "rhombus_triangle_congruence_dependency")
    edges.append(ReasonEdge("rhombus_opp_bisect", "def_ang_bisect", "rhombus_angle_dependency", 1))

    return edges
