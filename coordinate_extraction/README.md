### Expected Extracted Format

pt: A(X_A, Y_A, relative_label_position), B(X_B, Y_B, relative_label_position),
...

possible relative_label_positions: t, tr, r, br, b, bl, l, tl

#### Current Format

[[X_A, Y_A], [X_B, Y_B], ...]

---

**TODOs**

High priority

- [x] align extracted coordinates with labels
- [ ] fix rescale_points so that if figure is taller than it is wide (i.e.
      portrait or square aspect ratio), then the visible (x,y) coordinates
      should be (0->10, 0->10). if figure is wider than it is tall (landscape
      aspect ratio), then max coordinates should be (0->15, 0->10).

Medium priority

- [ ] fix circle intersection threshold logic
- [ ] fix `_get_tangency_point` (currently picking up a point at the line end or
      might have been combined to the line end when calculating
      `distinct_points` - needs to check and either fix the logic or prioritize
      for `distinct_points`)
- [ ] (minor) prioritize circle center, tangent point, ... for getting
      `distinct_points`
- [ ] refactor `combine_geometry.py` file

Low Priority

- [ ] implement other diagram logic extraction
  - [x] `on_line`
  - [ ] `intersect_seg`
  - [ ] `traversal` (needs logic building)
  - [ ] `on_circle`
  - [ ] `chord` (currently using secant)
  - [ ] `secant`
  - [ ] `tangent`
- [ ] fix `align_points` or `force_align_points` function (currently unused) <--
      needs `on_line` logic
