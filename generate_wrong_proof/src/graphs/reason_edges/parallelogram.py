from src.graphs.reason_edge import ReasonEdge, connect_from_one, listed_edges


def build_parallelogram_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += connect_from_one("def_parallelogram", ["pgram_opp_sides", "pgram_opp_angs", "pgram_consec_angs", "pgram_diag_bisect"], "parallelogram_family")
    edges += listed_edges([
        ("pgram_opp_sides", "pgram_opp_sides_conv"),
        ("pgram_opp_angs", "pgram_opp_angs_conv"),
        ("pgram_consec_angs", "pgram_consec_angs_conv"),
        ("pgram_diag_bisect", "pgram_diag_bisect_conv"),
    ], "converse_confusion")

    edges += listed_edges([
        ("pgram_opp_sides_conv", "pgram_opp_angs_conv"),
        ("pgram_opp_sides_conv", "pgram_opp_side_para"),
        ("pgram_opp_angs_conv", "pgram_consec_angs_conv"),
        ("pgram_diag_bisect_conv", "pgram_opp_side_para"),
    ], "parallelogram_converse_family")

    edges += listed_edges([("pgram_opp_sides", "def_midpt"), ("pgram_diag_bisect", "def_midpt")], "parallelogram_segment_dependency")
    edges += listed_edges([("pgram_opp_sides", "sss"), ("pgram_opp_sides", "sas"), ("pgram_opp_angs", "asa"), ("pgram_diag_bisect", "sas")], "parallelogram_triangle_congruence_dependency")
    edges.append(ReasonEdge("pgram_opp_angs", "vert_ang", "parallelogram_angle_dependency", 1))
    edges.append(ReasonEdge("pgram_consec_angs", "con_supplements", "parallelogram_supplement_dependency", 1))
    edges.append(ReasonEdge("pgram_opp_side_para", "def_parallelogram", "parallelogram_parallel_dependency", 1))

    return edges
