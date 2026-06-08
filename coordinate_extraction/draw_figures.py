import random
import matplotlib.pyplot as plt
import numpy as np
import cv2


def draw_segments_on_image(image, lines=None, circles=None):

    # Create a copy to draw detected lines for visualization
    line_img = image.copy()

    if lines is not None:
        for line in lines:
            coords = line[0] if len(line.shape) > 1 else line
            x1, y1, x2, y2 = map(int, coords)

            # Generate a random BGR color for each distinct line segment
            # We cap the lower bound at 50 so the colors aren't too dark to see on a black background
            random_color = (
                random.randint(50, 255),  # Blue channel
                random.randint(50, 255),  # Green channel
                random.randint(50, 255),  # Red channel
            )

            # Draw the line segment with its unique color
            cv2.line(line_img, (x1, y1), (x2, y2), random_color, 5)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]
            # Draw the circle's center
            cv2.circle(line_img, center, 3, (255, 0, 0), -1)
            # Draw the circle's perimeter
            cv2.circle(line_img, center, radius, (255, 0, 0), 2)

    # cv2.line(line_img, (0, 0), (10, 0), random_color, 5)
    # cv2.line(line_img, (0, 30), (100, 30), random_color, 5)
    # cv2.line(line_img, (0, 60), (500, 60), random_color, 5)

    # Display right inside your notebook
    plt.imshow(cv2.cvtColor(line_img, cv2.COLOR_BGR2RGB))
    plt.title(
        f"Detected Segments (lines: {len(lines) if lines is not None else 0}, circles: {len(circles[0]) if circles is not None else 0})"
    )
    plt.axis("off")
    plt.show()


def plot_points(points):
    # Separate X and Y coordinates for plotting
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]

    # Clear any active plots
    plt.clf()

    # Plot just the points using a scatter plot
    plt.scatter(x_coords, y_coords, color="blue", s=80, zorder=5)

    plt.axis("equal")

    # Format the plot area
    plt.title("Extracted Geometric Points")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.gca().invert_yaxis()  # Invert Y-axis for image coordinates
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()
