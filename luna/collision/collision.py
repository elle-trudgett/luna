"""
Useful collision wrappers
"""

from dataclasses import dataclass

import distance3d.distance
import numpy
import shapely.geometry
from arcade.types import PointList
from distance3d import colliders, mpr, gjk, epa
from pyglet.math import Vec2
from shapely import get_coordinates, Point
from shapely.ops import nearest_points
from shapely.geometry import MultiPoint, LineString

from luna.core.region import Region


def sweep_polygon(polygon: PointList, vector: Vec2) -> PointList:
    # Combine the vertices of the original and translated polygons
    translated_polygon = [(point[0] + vector.x, point[1] + vector.y) for point in polygon]

    combined_points = MultiPoint(list(polygon) + list(translated_polygon))

    # Compute the convex hull of the combined points
    swept_polygon = combined_points.convex_hull

    points: list[tuple[float, float]] = get_coordinates(swept_polygon).tolist()
    points = [(x, y) for x, y in points[:-1]]  # Last element is the same as start element, don't need it here
    return points


def to_collider(poly: PointList) -> colliders.ConvexHullVertices:
    return colliders.ConvexHullVertices(numpy.array([(x, y, -100) for x, y in poly] + [(x, y, 100) for x, y in poly]))


@dataclass
class PolygonMovementCollisionResult:
    """
    Result from `move_polygon_into_other_polygon`.

    :var collision: If there was a collision detected during the movement
    :var new_movement_vector: The scaled down movement vector if there was a collision, otherwise the original movement
         vector
    """

    collision: bool
    new_movement_vector: Vec2 | None


def experimental_collision(character: PointList, movement_vector: Vec2, regions: list[Region]) -> None:
    polygon = shapely.Polygon(character)

    # calculate AABBs
    aabb = polygon.bounds


def move_polygon_into_other_polygon_alternate_implementation(
        a: PointList, movement_vector: Vec2, b: PointList
) -> PolygonMovementCollisionResult:
    if movement_vector is None:
        movement_vector = Vec2(0, 0)

    poly_a = shapely.geometry.Polygon(a)
    poly_b = shapely.geometry.Polygon(b)

    # If already intersecting, just push out
    if poly_a.overlaps(poly_b):
        collider_a = to_collider(a)
        collider_b = to_collider(b)
        d, ca, cb, simplex = distance3d.gjk.gjk(collider_a, collider_b)
        mtv, faces, success = epa.epa(simplex, collider_a, collider_b)
        return PolygonMovementCollisionResult(collision=True, new_movement_vector=Vec2(mtv[0], mtv[1]))

    # sweep the polygon
    translated_polygon = [(point[0] + movement_vector.x, point[1] + movement_vector.y) for point in a]
    combined_points = MultiPoint(list(a) + list(translated_polygon))
    swept_a = combined_points.convex_hull
    if not shapely.overlaps(swept_a, poly_b) and not shapely.within(poly_b, swept_a):
        return PolygonMovementCollisionResult(collision=False, new_movement_vector=movement_vector)

    # there is a collision, find nearest points on both polygons
    a_closest, b_closest = shapely.ops.nearest_points(poly_a, poly_b)

    # calculate min distance between nearest points and other polygon using movement vector
    min_dist = float("inf")

    a_motion = shapely.LineString([a_closest, (a_closest.x + movement_vector.x, a_closest.y + movement_vector.y)])
    intersection = shapely.intersection(a_motion, poly_b)
    if intersection:
        min_dist = min(shapely.distance(a_closest, intersection), min_dist)

    b_motion = shapely.LineString([b_closest, (b_closest.x - movement_vector.x, b_closest.y - movement_vector.y)])
    intersection = shapely.intersection(b_motion, poly_a)
    if intersection:
        min_dist = min(shapely.distance(b_closest, intersection), min_dist)

    return PolygonMovementCollisionResult(collision=True, new_movement_vector=movement_vector.normalize() * min_dist)


def move_polygon_into_other_polygon(
    polygon: PointList, movement_vector: Vec2, other_polygon: PointList
) -> PolygonMovementCollisionResult:
    """
    Moves `polygon` by `movement` and checks if it collides with `other_polygon`.
    """
    return move_polygon_into_other_polygon_alternate_implementation(polygon, movement_vector, other_polygon)
    assert movement_vector is not None

    swept_polygon = sweep_polygon(polygon=polygon, vector=movement_vector)
    # move the polygon marginally in the movement vector's direction, to avoid detection collision on touching surfaces
    # when moving away from them
    nudge = movement_vector.normalize() * 0.0001
    swept_polygon = [(x + nudge.x, y + nudge.y) for x, y in swept_polygon]

    # Check collision between the swept polygon and the other polygon
    swept_polygon_collider = to_collider(swept_polygon)
    other_polygon_collider = to_collider(other_polygon)

    # Calculate the intersection of the swept polygon with the other polygon
    intersection, _, _, _ = mpr.mpr_penetration(swept_polygon_collider, other_polygon_collider)

    if not intersection:
        return PolygonMovementCollisionResult(collision=False, new_movement_vector=movement_vector)

    # If there was a collision, calculate the minimum distance from each point (x, y) in the polygon to each edge in the
    # other polygon in the direction of the movement vector to determine the new movement vector.
    shortest_vector = None
    shortest_length = float("inf")
    for x, y in polygon:
        for i in range(len(other_polygon)):
            p1 = other_polygon[i]
            p2 = other_polygon[(i + 1) % len(other_polygon)]

            # Calculate the distance between the two line segments
            distance, cp1, cp2 = distance3d.distance.line_segment_to_line_segment(
                # line segment from this point to where movement_vector takes it
                numpy.array([x, y, 0], dtype=float),
                numpy.array([x + movement_vector[0], y + movement_vector[1], 0], dtype=float),
                # line segment that represents the other polygon's edge
                numpy.array([p1[0], p1[1], 0], dtype=float),
                numpy.array([p2[0], p2[1], 0], dtype=float),
            )

            # if the closest points were the same, there was an intersection
            if numpy.allclose(cp1, cp2, atol=0.0000000001, rtol=0):
                shortened_vector = Vec2(cp1[0] - x, cp1[1] - y)
                if shortest_vector is None:
                    shortest_vector = shortened_vector
                else:
                    shortened_vector_length = abs(shortened_vector)
                    if shortened_vector_length < shortest_length:
                        shortest_vector = shortened_vector
                        shortest_length = shortened_vector_length

    # and in the opposite direction
    for x, y in other_polygon:
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]

            distance, cp1, cp2 = distance3d.distance.line_segment_to_line_segment(
                # line segment from this point backwards by movement_vector
                numpy.array([x, y, 0], dtype=float),
                numpy.array([x - movement_vector[0], y - movement_vector[1], 0], dtype=float),
                # line segment that represents the polygon's edge
                numpy.array([p1[0], p1[1], 0], dtype=float),
                numpy.array([p2[0], p2[1], 0], dtype=float),
            )

            if numpy.allclose(cp1, cp2, atol=0.0000000001, rtol=0):
                shortened_vector = Vec2(x - cp1[0], y - cp1[1])
                if shortest_vector is None:
                    shortest_vector = shortened_vector
                else:
                    shortened_vector_length = abs(shortened_vector)
                    if shortened_vector_length < shortest_length:
                        shortest_vector = shortened_vector
                        shortest_length = shortened_vector_length

    return PolygonMovementCollisionResult(collision=True, new_movement_vector=shortest_vector)
