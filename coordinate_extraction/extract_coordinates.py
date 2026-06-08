import cv2
import numpy as np
from combine_geometry import (
    combine_lines,
    get_distinct_points,
    rescale_points,
    align_points,
    get_all_intersection_points,
)


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
    _, img_binary = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)

    return img_binary


def extract_coordinates(IMAGE_PATH):
    img_binary = _preprocess_image(IMAGE_PATH)

    # extract lines
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

    # get distinct points
    distinct_points = get_distinct_points(points, threshold=60)

    # rescale and align points
    rescaled_points = rescale_points(distinct_points)[0]
    aligned_points = align_points(rescaled_points)

    return aligned_points
