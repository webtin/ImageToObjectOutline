def mirror_points_around_center(points):
    # Calculate the center of the points
    total_x = 0
    total_y = 0
    for point in points:
        total_x += point[0]
        total_y += point[1]
    center_x = total_x / len(points)
    center_y = total_y / len(points)

    # Mirror the points around the center
    mirrored_points = []
    for point in points:
        mirrored_x = 2 * center_x - point[0]
        mirrored_y = 2 * center_y - point[1]
        mirrored_points.append((mirrored_x, mirrored_y))

    return mirrored_points

# Example usage
points = [(1, 2), (3, 4), (5, 6)]
mirrored_points = mirror_points_around_center(points)
print(mirrored_points)