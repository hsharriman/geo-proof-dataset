from src.graphs.reason_edge import ReasonEdge, connect_from_one, listed_edges


def build_special_triangle_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges += listed_edges([("def_isosceles", "base_angle"), ("def_isosceles", "base_angle_conv")], "isosceles_triangle_family")
    edges.append(ReasonEdge("base_angle", "base_angle_conv", "converse_confusion", 1))
    edges.append(ReasonEdge("equilat_equiang", "equiang_equilat", "converse_confusion", 1))
    edges += listed_edges([
        ("equilat_equiang", "def_equilateral"),
        ("equilat_equiang", "def_equiangular"),
        ("equiang_equilat", "def_equilateral"),
        ("equiang_equilat", "def_equiangular"),
    ], "equilateral_equiangular_family")

    edges += connect_from_one("base_angle", ["asa", "aas"], "special_triangle_to_triangle_congruence_dependency")
    edges.append(ReasonEdge("base_angle", "aa_sim", "special_triangle_to_triangle_similarity_dependency", 1))
    edges.append(ReasonEdge("base_angle_conv", "def_isosceles", "converse_confusion", 1))
    edges.append(ReasonEdge("def_equilateral", "def_isosceles", "special_triangle_definition_dependency", 1))
    edges.append(ReasonEdge("def_equilateral", "equilat_equiang", "special_triangle_angle_dependency", 1))
    edges.append(ReasonEdge("def_equiangular", "equiang_equilat", "special_triangle_side_dependency", 1))

    return edges
