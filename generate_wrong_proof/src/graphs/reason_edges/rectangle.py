from src.graphs.reason_edge import ReasonEdge, listed_edges


def build_rectangle_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += listed_edges([("rectangle", "rectangle_pgram"), ("rectangle", "rect_diag_con"), ("rectangle_pgram", "rect_diag_con")], "rectangle_family")
    edges.append(ReasonEdge("rect_diag_con", "rect_diag_con_conv", "converse_confusion", 1))
    edges.append(ReasonEdge("rect_diag_con_conv", "rect_pgram_ang", "rectangle_converse_family", 1))
    edges.append(ReasonEdge("rectangle", "def_con_right", "rectangle_right_angle_dependency", 1))
    edges += listed_edges([
        ("rectangle", "def_parallelogram"),
        ("rectangle_pgram", "def_parallelogram"),
        ("rectangle_pgram", "pgram_opp_sides"),
        ("rectangle_pgram", "pgram_opp_angs"),
    ], "rectangle_parallelogram_dependency")
    edges += listed_edges([("rect_diag_con", "sss"), ("rect_diag_con", "sas")], "rectangle_triangle_congruence_dependency")
    edges.append(ReasonEdge("rect_diag_con", "def_midpt", "rectangle_segment_dependency", 1))

    return edges
