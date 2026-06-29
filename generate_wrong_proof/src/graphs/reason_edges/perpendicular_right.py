from src.graphs.reason_edge import ReasonEdge, connect_from_one, listed_edges


def build_perpendicular_right_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += listed_edges([("def_perp", "perp_con_ang"), ("def_perp", "rhombus_diag_perp"), ("def_perp", "kite_diag_perp")], "perpendicular_family")
    edges += listed_edges([("def_perp", "def_con_right"), ("def_con_right", "perp_con_ang")], "right_angle_family")
    edges.append(ReasonEdge("def_perp", "rhl", "perpendicular_triangle_congruence_dependency", 1))
    edges.append(ReasonEdge("def_con_right", "rhl", "right_triangle_congruence_dependency", 1))
    edges += connect_from_one("perp_con_ang", ["asa", "aas"], "perpendicular_triangle_congruence_dependency")

    return edges
