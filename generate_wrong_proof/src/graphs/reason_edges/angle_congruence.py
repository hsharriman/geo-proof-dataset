from src.graphs.reason_edge import ReasonEdge, connect_from_one, listed_edges


def build_angle_congruence_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += listed_edges([
        ("reflex_a", "vert_ang"),
        ("reflex_a", "third_angle"),
        ("vert_ang", "third_angle"),
        ("vert_ang", "def_ang_bisect"),
        ("third_angle", "def_ang_bisect"),
        ("def_ang_bisect", "perp_con_ang"),
        ("def_ang_bisect", "base_angle"),
    ], "angle_congruence_family")

    edges.append(ReasonEdge("def_ang_bisect", "ang_bisect_conv", "converse_confusion", 1))
    edges += listed_edges([("con_supplements", "con_supplements_same")], "supplement_family")
    edges += listed_edges([("con_complements", "con_complements_same")], "complement_family")
    edges += listed_edges([("con_supplements", "con_complements"), ("con_supplements_same", "con_complements_same")], "supplement_complement_confusion")

    edges += connect_from_one("vert_ang", ["altint", "altext", "corresp_ang"], "angle_parallel_dependency")
    edges += connect_from_one("third_angle", ["altint", "corresp_ang"], "angle_parallel_dependency")
    edges += connect_from_one("def_ang_bisect", ["altint", "corresp_ang"], "angle_parallel_dependency")
    edges += connect_from_one("con_supplements", ["sameside_ang"], "supplement_parallel_dependency")
    edges += connect_from_one("con_supplements_same", ["sameside_ang"], "supplement_parallel_dependency")
    edges += connect_from_one("con_supplements", ["def_linear_pair", "linear_pair_conv"], "supplement_linear_pair_dependency")

    return edges
