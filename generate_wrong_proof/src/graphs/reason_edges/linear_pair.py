from src.graphs.reason_edge import ReasonEdge, listed_edges


def build_linear_pair_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges.append(ReasonEdge("def_linear_pair", "linear_pair_conv", "converse_confusion", 1))
    edges += listed_edges([("def_linear_pair", "con_supplements"), ("linear_pair_conv", "con_supplements")], "supplement_family")
    edges.append(ReasonEdge("def_linear_pair", "sameside_ang", "linear_pair_parallel_dependency", 1))
    edges.append(ReasonEdge("linear_pair_conv", "sameside_ang_conv", "linear_pair_parallel_dependency", 1))

    return edges
