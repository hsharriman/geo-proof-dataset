from src.graphs.reason_edge import ReasonEdge, listed_edges


def build_segment_congruence_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += listed_edges([
        ("reflex_s", "def_midpt"),
        ("def_midpt", "perp_bisector"),
        ("def_midpt", "base_angle_conv"),
        ("def_midpt", "pgram_opp_sides"),
        ("def_midpt", "rect_diag_con"),
        ("reflex_s", "con_transitive"),
    ], "segment_congruence_family")

    edges.append(ReasonEdge("def_midpt", "midpt_conv", "converse_confusion", 1))
    edges += listed_edges([("def_midpt", "pgram_diag_bisect"), ("midpt_conv", "pgram_diag_bisect_conv")], "segment_quadrilateral_dependency")
    edges.append(ReasonEdge("perp_bisector", "circumcenter", "segment_triangle_center_dependency", 1))
    edges.append(ReasonEdge("perp_bisector", "def_perp", "segment_perpendicular_dependency", 1))

    return edges
