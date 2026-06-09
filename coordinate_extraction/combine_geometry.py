# TODO: refactor code by defining functions for logics used multiple times
import numpy as np
import cv2


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

    return intersection_points


def mask_circles(binary_img, circles):
    perimeter_mask = np.zeros_like(binary_img)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center_x, center_y, radius = i[0], i[1], i[2]

            stroke_thickness = 12
            cv2.circle(
                perimeter_mask,
                (center_x, center_y),
                radius,
                255,
                thickness=stroke_thickness,
            )

    inverse_mask = cv2.bitwise_not(perimeter_mask)

    cleaned_binary = cv2.bitwise_and(binary_img, binary_img, mask=inverse_mask)

    return cleaned_binary


def _get_tangency_point(circle, line, threshold):
    cx, cy, r = circle
    x1, y1, x2, y2 = line

    dx = x2 - x1
    dy = y2 - y1

    line_length_squared = dx**2 + dy**2
    if line_length_squared < 1e-6:  # line length is zero
        return None
    # Project the circle's center onto the infinite line.
    # Find the scalar 't' that minimizes the distance to (cx, cy)
    t = ((cx - x1) * dx + (cy - y1) * dy) / line_length_squared

    # Calculate the exact coordinates of the closest point on the line
    tx = x1 + t * dx
    ty = y1 + t * dy

    # Verify it is actually a tangent line.
    # The distance from the center to this point should roughly equal the radius.
    dist_to_center = np.hypot(tx - cx, ty - cy)
    if abs(dist_to_center - r) <= threshold:
        return [int(round(tx)), int(round(ty))]

    return None


def get_all_tangency_points(lines, circles, threshold=20.0, point_touch_threshold=30.0):
    if lines is None or len(lines) == 0 or circles is None or len(circles) == 0:
        return np.empty((0, 2))
    clean_lines = np.array(lines).reshape(-1, 4)
    clean_circles = np.array(circles).reshape(-1, 3)

    all_tangent_points = []

    for circle in clean_circles:
        for line in clean_lines:

            # Use your pre-defined function to find the mathematical tangent point
            pt = _get_tangency_point(circle, line, threshold=threshold)
            if pt is not None:
                tx, ty = pt
                x1, y1, x2, y2 = line

                # Check if the point actually touches the circle
                within_segment = (
                    min(x1, x2) - point_touch_threshold
                    <= tx
                    <= max(x1, x2) + point_touch_threshold
                ) and (
                    min(y1, y2) - point_touch_threshold
                    <= ty
                    <= max(y1, y2) + point_touch_threshold
                )

                if within_segment:
                    all_tangent_points.append([tx, ty])

    return all_tangent_points


def get_line_circle_intersection_points(lines, circles, threshold=5.0):
    if lines is None or len(lines) == 0 or circles is None or len(circles) == 0:
        return np.empty((0, 2))

    clean_lines = np.array(lines).reshape(-1, 4)
    clean_circles = np.array(circles).reshape(-1, 3)

    intersection_points = []

    for circle in clean_circles:
        cx, cy, r = circle
        # Account for pixel noise by giving the radius a tiny buffer
        effective_radius = (
            r + threshold
        )  # TODO: change threshold logic so that it would return actual coordinate after checking threshold (circle8 example)

        for line in clean_lines:
            x1, y1, x2, y2 = line

            dx = x2 - x1
            dy = y2 - y1
            line_lensq = dx**2 + dy**2
            if line_lensq < 1e-6:
                continue

            # Project circle center onto the infinite line to find the closest point
            t = ((cx - x1) * dx + (cy - y1) * dy) / line_lensq

            # Clamp 't' between 0 and 1 to keep the point strictly ON the line segment
            t_clamped = max(0.0, min(1.0, t))
            closest_x = x1 + t_clamped * dx
            closest_y = y1 + t_clamped * dy

            # Perpendicular distance from circle center to the closest point on the segment
            dist_to_center = np.hypot(closest_x - cx, closest_y - cy)

            if dist_to_center > effective_radius:
                continue

            # Calculate the intersection points using the chord half-length
            # (Pythagorean theorem: half_chord^2 + dist_to_center^2 = radius^2)
            half_chord = np.sqrt(max(0.0, effective_radius**2 - dist_to_center**2))

            # Unit direction vectors of the line
            line_len = np.sqrt(line_lensq)
            ux = dx / line_len
            uy = dy / line_len

            # Compute the two intersection points along the trajectory
            # If the closest point was clamped to an endpoint, we base our offset there
            pt1 = [
                int(round(closest_x + ux * half_chord)),
                int(round(closest_y + uy * half_chord)),
            ]
            pt2 = [
                int(round(closest_x - ux * half_chord)),
                int(round(closest_y - uy * half_chord)),
            ]

            # Double check that the final calculated points are reasonably on the segment
            for pt in [pt1, pt2]:
                # Quick bounding box validation with a small margin
                margin = 5
                if (
                    min(x1, x2) - margin <= pt[0] <= max(x1, x2) + margin
                    and min(y1, y2) - margin <= pt[1] <= max(y1, y2) + margin
                ):
                    intersection_points.append(pt)

    # Convert to NumPy array and remove duplicate coordinates
    intersection_points = np.array(intersection_points)
    if len(intersection_points) > 0:
        intersection_points = np.unique(intersection_points, axis=0)

    return intersection_points


def _point_on_circle(point, circle, threshold):
    px, py = point
    cx, cy, r = circle

    dist_to_center = np.sqrt((px - cx) ** 2 + (py - cy) ** 2)

    if abs(dist_to_center - r) <= threshold:
        return True
    return False


def get_all_points_on_circles(points, circles, threshold=10.0):
    if points is None or len(points) == 0 or circles is None or len(circles) == 0:
        return np.empty((0, 2))

    clean_points = points.reshape(-1, 3)[:, :2]
    clean_circles = circles.reshape(-1, 3)

    points_on_circles = []

    for point in clean_points:
        for circle in clean_circles:
            if _point_on_circle(point, circle, threshold=threshold):
                points_on_circles.append(point)
                break  # Found a match for this point, move to the next point

    return points_on_circles


def _get_point_on_line(point, line, threshold):
    px, py = point
    x1, y1, x2, y2 = line

    dx = x2 - x1
    dy = y2 - y1
    line_lensq = dx**2 + dy**2

    if line_lensq < 1e-6:
        # The line is actually a single point, check distance to that point
        return np.hypot(px - x1, py - y1) <= threshold

    # 1. Calculate the projection scalar 't' along the infinite line
    t = ((px - x1) * dx + (py - y1) * dy) / line_lensq

    # 2. Clamp 't' to keep it strictly within the finite line segment bounds
    t_clamped = max(0.0, min(1.0, t))

    # 3. Find the coordinates of the closest point on the segment
    closest_x = x1 + t_clamped * dx
    closest_y = y1 + t_clamped * dy

    # 4. Calculate distance from the original point to this closest segment point
    distance = np.hypot(px - closest_x, py - closest_y)

    return distance <= threshold


def get_all_points_on_lines(points, lines, threshold=10.0):
    if points is None or len(points) == 0 or lines is None or len(lines) == 0:
        return np.empty((0, 2))

    # Standardize inputs to clean 2D arrays
    clean_points = np.array(points).reshape(-1, 3)[:, :2]
    clean_lines = np.array(lines).reshape(-1, 4)

    points_on_lines = []

    # Loop through every single point
    for point in clean_points:
        # Check it against every detected line segment
        for line in clean_lines:
            if _get_point_on_line(point, line, threshold=threshold):
                points_on_lines.append(point)
                break  # Found a match for this point, move to the next point

    return np.array(points_on_lines)
