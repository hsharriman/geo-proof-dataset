import cv2
import numpy as np
from combine_geometry import (
    mask_circles,
    combine_lines,
    get_distinct_points,
    rescale_points,
    align_points,
    get_all_intersection_points,
    get_all_tangency_points,
    get_line_circle_intersection_points,
    get_all_points_on_lines,
    get_all_points_on_circles,
)
from draw_figures import plot_points


def _preprocess_image(IMAGE_PATH):
    # load image
    img_bgr = cv2.imread(IMAGE_PATH)

    # scale image so that longest side is 1000 pixels
    width, height = img_bgr.shape[1], img_bgr.shape[0]
    max_dim = max(height, width)
    scale_factor = 1000 / max_dim
    img_bgr = cv2.resize(
        img_bgr,
        (int(width * scale_factor), int(height * scale_factor)),
        interpolation=cv2.INTER_AREA,
    )

    # preprocess image
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    _, img_binary = cv2.threshold(img_blur, 127, 255, cv2.THRESH_BINARY_INV)

    return img_blur, img_binary


def extract_coordinates(IMAGE_PATH):
    img_blur, img_binary = _preprocess_image(IMAGE_PATH)

    dots = cv2.HoughCircles(
        img_blur,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=100,
        param2=15,
        minRadius=15,
        maxRadius=30,
    )

    # extract circles and lines
    circles = cv2.HoughCircles(
        img_blur,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=200,
        param1=100,
        param2=50,
        minRadius=100,
        maxRadius=500,
    )

    if circles is not None:
        if dots is not None:
            points_on_circles = get_all_points_on_circles(dots, circles, 5)

        cleaned_binary = mask_circles(img_binary, circles)
        lines = cv2.HoughLinesP(
            cleaned_binary,
            rho=1,
            theta=np.pi / 180,
            threshold=250,
            minLineLength=100,
            maxLineGap=0,
        )

    else:
        lines = cv2.HoughLinesP(
            img_binary,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=100,
            maxLineGap=0,
        )

    # combine lines
    combined_lines = combine_lines(lines)

    # get points from lines
    points = combined_lines.reshape(-1, 4)[:, :2].tolist()
    points.extend(combined_lines.reshape(-1, 4)[:, 2:4].tolist())

    # add intersection points
    intersection_points = get_all_intersection_points(combined_lines)
    points.extend(intersection_points)

    # points on line
    if dots is not None:
        points_on_lines = get_all_points_on_lines(dots, combined_lines, 5)
        points.extend(points_on_lines)

    # points from circle & tangency
    if circles is not None:
        points.extend(points_on_circles)
        circle_center_points = np.array(circles, dtype=np.float32).reshape(-1, 3)[:, :2]
        points.extend(circle_center_points)
        tangency_points = get_all_tangency_points(combined_lines, circles)
        points.extend(tangency_points)
        circle_intersection_points = get_line_circle_intersection_points(
            combined_lines, circles, threshold=-10
        )
        points.extend(circle_intersection_points)

    # get distinct points
    distinct_points = get_distinct_points(points, threshold=60)

    # rescale and align points
    rescaled_points, scale = rescale_points(distinct_points)
    flipped_points = np.array(rescaled_points)
    flipped_points[:, 1] = img_blur.shape[0] * scale - flipped_points[:, 1]

    # aligned_points = align_points(rescaled_points) # TODO: Fix alignment logic

    return flipped_points


if __name__ == "__main__":
    selected_image = input("Please select your image: ")
    points = extract_coordinates(f"diagram_sample_image/{selected_image}.jpg")
    print("There are ", len(points), "points")
    print(points)
    plot_points(points, f"Extracted Coordinates ({len(points)} points)")
