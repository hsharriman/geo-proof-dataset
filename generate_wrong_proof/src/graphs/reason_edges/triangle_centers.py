from src.graphs.reason_edge import ReasonEdge


def build_triangle_center_edges() -> list[ReasonEdge]:
    edges: list[ReasonEdge] = []

    edges.append(ReasonEdge("circumcenter", "perp_bisector", "triangle_center_dependency", 1))
    edges.append(ReasonEdge("incenter", "def_ang_bisect", "triangle_center_dependency", 1))
    edges.append(ReasonEdge("circumcenter", "incenter", "triangle_center_family", 1))
    edges.append(ReasonEdge("circumcenter", "def_perp", "triangle_center_perpendicular_dependency", 1))
    edges.append(ReasonEdge("circumcenter", "def_midpt", "triangle_center_segment_dependency", 1))
    edges.append(ReasonEdge("incenter", "ang_bisect_conv", "triangle_center_angle_dependency", 1))
    edges.append(ReasonEdge("incenter", "base_angle", "triangle_center_angle_dependency", 1))

    return edges
