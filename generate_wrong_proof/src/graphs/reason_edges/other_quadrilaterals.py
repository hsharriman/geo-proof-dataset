from src.graphs.reason_edge import ReasonEdge, listed_edges


def build_other_quadrilateral_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges.append(ReasonEdge("kite_diag_perp", "kite_opp_con_ang", "kite_family", 1))
    edges.append(ReasonEdge("isos_trap_base_angs", "isos_trap_base_angs_conv", "converse_confusion", 1))
    edges += listed_edges([("isos_trap_base_angs", "isos_trap_con_diags"), ("isos_trap_base_angs_conv", "isos_trap_con_diags")], "isosceles_trapezoid_family")
    edges.append(ReasonEdge("kite_diag_perp", "def_perp", "kite_perpendicular_dependency", 1))
    edges.append(ReasonEdge("kite_diag_perp", "rhl", "kite_triangle_congruence_dependency", 1))
    edges.append(ReasonEdge("kite_opp_con_ang", "def_ang_bisect", "kite_angle_dependency", 1))
    edges.append(ReasonEdge("kite_opp_con_ang", "asa", "kite_triangle_congruence_dependency", 1))
    edges.append(ReasonEdge("isos_trap_base_angs", "base_angle", "trapezoid_angle_dependency", 1))
    edges.append(ReasonEdge("isos_trap_base_angs", "aas", "trapezoid_triangle_congruence_dependency", 1))
    edges.append(ReasonEdge("isos_trap_con_diags", "sss", "trapezoid_triangle_congruence_dependency", 1))
    edges.append(ReasonEdge("isos_trap_con_diags", "rect_diag_con", "trapezoid_diagonal_dependency", 1))

    return edges
