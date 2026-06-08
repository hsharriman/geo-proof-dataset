import numpy as np


def distance_between_points(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def get_line_angle(x1, y1, x2, y2):
    # Returns angle in degrees between 0 and 180
    return np.degrees(np.arctan2(y2 - y1, x2 - x1)) % 180


def combine_lines(lines, angle_tolerance_deg=5.0, distance_tolerance_px=20.0):
    """
    Combines redundant, fragmented, or overlapping lines into single definitive lines.

    1. Makes almost-parallel lines perfectly parallel by averaging their angles.
    2. Groups lines by angle and checks the perpendicular distance between them.
    3. Merges lines if their perpendicular distance is within the threshold.
    4. Finds the outermost (leftmost/rightmost) coordinates of the merged group.
    """
    if len(lines) == 0:
        return np.empty((0, 4))

    # Ensure shape is (N, 4)
    lines_array = np.array(lines, dtype=float).reshape(-1, 4)
    processed_lines = []
    for line in lines_array:
        x1, y1, x2, y2 = line
        # Calculate angle in degrees (-90 to 90) to handle orientation invariants
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1)) % 180
        if angle > 90:
            angle -= 180

        # Calculate line length
        length = np.hypot(x2 - x1, y2 - y1)
        processed_lines.append(
            {
                "coords": (x1, y1, x2, y2),
                "angle": angle,
                "length": length,
                "merged": False,
            }
        )
    final_combined_lines = []

    # Iterate through every line to find merge candidates
    for i in range(len(processed_lines)):
        if processed_lines[i]["merged"]:
            continue

        # Current base line group starts with just this line
        current_group = [processed_lines[i]]
        processed_lines[i]["merged"] = True

        x1_a, y1_a, x2_a, y2_a = processed_lines[i]["coords"]
        angle_a = processed_lines[i]["angle"]

        for j in range(i + 1, len(processed_lines)):
            if processed_lines[j]["merged"]:
                continue

            angle_b = processed_lines[j]["angle"]

            # --- STEP 1: Check if lines are almost parallel ---
            angle_diff = abs(angle_a - angle_b)
            # Handle wrap-around near 90/-90 degrees
            if angle_diff > 90:
                angle_diff = 180 - angle_diff

            if angle_diff <= angle_tolerance_deg:
                # --- STEP 2 & 3: Calculate perpendicular distance ---
                x1_b, y1_b, x2_b, y2_b = processed_lines[j]["coords"]

                # Perpendicular distance from midpoint of line B to line A
                mid_x_b = (x1_b + x2_b) / 2.0
                mid_y_b = (y1_b + y2_b) / 2.0

                # Line equation A*x + B*y + C = 0 for line A
                A = y2_a - y1_a
                B = x1_a - x2_a
                C = x2_a * y1_a - x1_a * y2_a

                denom = np.hypot(A, B)
                if denom > 1e-6:
                    perp_dist = abs(A * mid_x_b + B * mid_y_b + C) / denom
                else:
                    perp_dist = 0

                # If they are parallel and close enough, group them
                if perp_dist <= distance_tolerance_px:
                    current_group.append(processed_lines[j])
                    processed_lines[j]["merged"] = True

        # --- STEP 1 (Cont.): Make them perfectly parallel ---
        # Average the angles of all lines in the group weighted by length
        total_len = sum(l["length"] for l in current_group)
        avg_angle = sum(l["angle"] * l["length"] for l in current_group) / total_len

        # --- STEP 4 & 5: Project points onto the parallel axis to get extreme ends ---
        # Convert angle back to a directional unit vector
        rad = np.radians(avg_angle)
        dx, dy = np.cos(rad), np.sin(rad)

        # Collect all raw endpoints in this merged group
        all_pts = []
        for item in current_group:
            x1, y1, x2, y2 = item["coords"]
            all_pts.append((x1, y1))
            all_pts.append((x2, y2))

        all_pts = np.array(all_pts)

        # Project endpoints onto the line direction vector to sort them linearly
        projections = all_pts[:, 0] * dx + all_pts[:, 1] * dy

        # Find the indexes of the absolute extreme points
        min_idx = np.argmin(projections)
        max_idx = np.argmax(projections)

        # Extract the true leftmost and rightmost coordinates
        start_pt = all_pts[min_idx]
        end_pt = all_pts[max_idx]

        final_combined_lines.append(
            [int(start_pt[0]), int(start_pt[1]), int(end_pt[0]), int(end_pt[1])]
        )

    return np.array(final_combined_lines)


def get_distinct_points(points_array, threshold=10):
    # threshold is the minimum distance between points to be considered distinct
    if len(points_array) == 0:
        return []
    distinct_points = []
    for pt in points_array:
        if all(
            distance_between_points(pt, existing) >= threshold
            for existing in distinct_points
        ):
            distinct_points.append(pt)
    formatted_points = [(int(x), int(y)) for x, y in distinct_points]
    return formatted_points


def rescale_points(points_list):
    points = np.array(points_list, dtype=float)
    x = points[:, 0]
    y = points[:, 1]

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    W = x_max - x_min
    H = y_max - y_min

    if H >= W:
        # Portrait or Square
        max_w, max_h = 10.0, 10.0
    else:
        # Landscape
        max_w, max_h = 15.0, 10.0

    scale = min(max_w / W, max_h / H)
    rescaled_points = points * scale

    return [(p[0], p[1]) for p in rescaled_points], scale


def align_points(points, tolerance=1):  # TODO: fix align points logic
    if not points:
        return []

    # Extract coordinates into numpy arrays
    x_coords = np.array([p[0] for p in points])
    y_coords = np.array([p[1] for p in points])

    # Calculate the mean target values for both axes
    mean_x = np.mean(x_coords)
    mean_y = np.mean(y_coords)

    aligned_points = []
    for x, y in zip(x_coords, y_coords):
        # Independently check and snap the X coordinate
        new_x = mean_x if abs(x - mean_x) <= tolerance else int(x)

        # Independently check and snap the Y coordinate
        new_y = mean_y if abs(y - mean_y) <= tolerance else int(y)

        aligned_points.append((new_x, new_y))

    return aligned_points


def force_align_points(points, tolerance=1.5):
    if not points or len(points) == 0:
        return []

    points = np.array(points, dtype=float)
    aligned_points = points.copy()

    for axis_idx in [0, 1]:  # 0 for X, 1 for Y
        coords = points[:, axis_idx]

        # Sort coordinates to find natural local gaps
        sorted_indices = np.argsort(coords)
        sorted_coords = coords[sorted_indices]

        # Find where consecutive coordinates are further apart than the tolerance
        gaps = np.diff(sorted_coords) > tolerance
        # Split into distinct local cluster groups
        split_indices = np.where(gaps)[0] + 1
        clusters = np.split(sorted_indices, split_indices)

        # Calculate the mean for each local group and snap them
        for cluster in clusters:
            if len(cluster) > 0:
                local_mean = np.mean(coords[cluster])
                # You can use int(round(local_mean)) here if you need integer grids,
                # but leaving it as float preserves precise rescaled positions.
                aligned_points[cluster, axis_idx] = local_mean

        # change into integers after alignment
        aligned_points[:, axis_idx] = np.round(aligned_points[:, axis_idx])

    return aligned_points.tolist()


def _get_intersection_point(line1, line2, tolerance=15):
    """
    Finds the intersection point of two line segments if it falls
    within the bounds of both segments (plus a small pixel tolerance).
    """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # Determinant formulas for line-line intersection
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    # If denominator is 0, lines are parallel
    if abs(denom) < 1e-6:
        return None

    # Calculate exact intersection point (px, py)
    t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
    t = t_num / denom

    px = x1 + t * (x2 - x1)
    py = y1 + t * (y2 - y1)

    # Segment boundary check: Ensure the intersection is on BOTH segments
    # We include a small tolerance margin because lines might not perfectly touch
    on_segment1 = (
        min(x1, x2) - tolerance <= px <= max(x1, x2) + tolerance
        and min(y1, y2) - tolerance <= py <= max(y1, y2) + tolerance
    )

    on_segment2 = (
        min(x3, x4) - tolerance <= px <= max(x3, x4) + tolerance
        and min(y3, y4) - tolerance <= py <= max(y3, y4) + tolerance
    )

    if on_segment1 and on_segment2:
        return [int(px), int(py)]

    return None


def get_all_intersection_points(all_lines, distance_threshold=15.0):
    intersection_points = []

    # Double loop to check every line combination exactly once
    for idx, line1 in enumerate(all_lines):
        for line2 in all_lines[idx + 1 :]:
            point = _get_intersection_point(line1, line2)
            if point is not None:
                intersection_points.append(point)

    # Convert to a clean NumPy array and remove any exact duplicate points
    intersection_points = np.array(intersection_points)

    # Merge points that are below your distance threshold
    if len(intersection_points) > 0:
        filtered_points = []

        for point in intersection_points:
            # Check if this point is close to any point we've already saved
            is_duplicate = False
            for saved_point in filtered_points:
                if distance_between_points(point, saved_point) < distance_threshold:
                    is_duplicate = True
                    break  # Stop checking, we found a close neighbor

            # If it's not close to any existing saved point, keep it
            if not is_duplicate:
                filtered_points.append(point)

        intersection_points = np.array(filtered_points)

    print(f"Found {len(intersection_points)} valid segment intersection points:")
    return intersection_points
