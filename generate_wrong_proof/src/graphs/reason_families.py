TRIANGLE_CONGRUENCE = ["sas", "sss", "asa", "aas", "rhl"]
TRIANGLE_SIMILARITY = ["aa_sim", "sss_sim", "sas_sim"]

SPECIAL_TRIANGLES = [
    "def_isosceles", "base_angle", "base_angle_conv",
    "equilat_equiang", "equiang_equilat", "def_equilateral", "def_equiangular",
]

ANGLE_CONGRUENCE = [
    "reflex_a", "vert_ang", "third_angle", "def_ang_bisect",
    "ang_bisect_conv", "perp_con_ang", "con_supplements",
    "con_supplements_same", "con_complements", "con_complements_same",
]

SEGMENT_CONGRUENCE = ["reflex_s", "def_midpt", "midpt_conv", "perp_bisector", "con_transitive"]
PARALLEL_ANGLE_THEOREMS = ["altint", "altext", "corresp_ang", "sameside_ang"]
PARALLEL_CONVERSE_THEOREMS = ["altint_conv", "altext_conv", "corresp_ang_conv", "sameside_ang_conv"]
PERPENDICULAR_RIGHT = ["def_perp", "def_con_right"]
LINEAR_PAIR = ["def_linear_pair", "linear_pair_conv"]

PARALLELOGRAM = [
    "def_parallelogram", "pgram_opp_sides", "pgram_opp_angs",
    "pgram_consec_angs", "pgram_diag_bisect", "pgram_opp_sides_conv",
    "pgram_opp_angs_conv", "pgram_consec_angs_conv",
    "pgram_diag_bisect_conv", "pgram_opp_side_para",
]

RECTANGLE = ["rectangle", "rectangle_pgram", "rect_diag_con", "rect_diag_con_conv", "rect_pgram_ang"]

RHOMBUS = [
    "rhombus_pgram", "rhombus_diag_perp", "rhombus_opp_bisect",
    "rhombus_diag_perp_conv", "rhombus_opp_bisect_conv", "rhombus_consec_sides",
]

OTHER_QUADRILATERALS = [
    "kite_diag_perp", "kite_opp_con_ang", "isos_trap_base_angs",
    "isos_trap_base_angs_conv", "isos_trap_con_diags",
]

TRIANGLE_CENTERS = ["circumcenter", "incenter"]

REASON_FAMILIES = {
    "triangle_congruence": TRIANGLE_CONGRUENCE,
    "triangle_similarity": TRIANGLE_SIMILARITY,
    "special_triangles": SPECIAL_TRIANGLES,
    "angle_congruence": ANGLE_CONGRUENCE,
    "segment_congruence": SEGMENT_CONGRUENCE,
    "parallel_lines": PARALLEL_ANGLE_THEOREMS + PARALLEL_CONVERSE_THEOREMS,
    "perpendicular_right": PERPENDICULAR_RIGHT,
    "linear_pair": LINEAR_PAIR,
    "parallelogram": PARALLELOGRAM,
    "rectangle": RECTANGLE,
    "rhombus": RHOMBUS,
    "other_quadrilaterals": OTHER_QUADRILATERALS,
    "triangle_centers": TRIANGLE_CENTERS,
}
