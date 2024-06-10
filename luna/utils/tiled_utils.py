"""
Utility functions for working with co-ordinates in Tiled.

The origin in Tiled ((0, 0)) will be mapped to Luna's origin ((0, 0)).
The X-coordinate is the same in both co-ordinate systems.
The Y-coordinate is flipped:
  * Tiled uses positive Y going down.
  * Luna uses positive Y going up (as the underlying engine does.)
"""

import math

import pyglet.math
from arcade.types import Point, Size2D


def round_epsilon(x: float) -> float:
    """
    Round a float to 10 decimal places.
    :param x: The float to round.
    :return: The rounded float.
    """
    return round(x, 10)


def tiled_to_luna(point: Point) -> Point:
    """
    Convert a point from Tiled co-ordinate space to Luna co-ordinate space.
    :param point: The point to convert.
    :return: The point in Luna co-ordinate space.
    """
    return round_epsilon(point[0]), -round_epsilon(point[1])


def tile_point_to_absolute_luna_point(
    tile_position: Point, tile_size: Size2D[float], tile_point: Point, tile_rotation: float
) -> Point:
    """
    Points within a tile are relative. Apply translation and rotation to the point to get the world coordinate.

    :var tile_position: The position of the tile (from Tiled.) Corresponds to the bottom left corner of the tile.
    :var tile_size: The size of the tile (from Tiled.)
    :var tile_point: The point within the tile to convert. Origin is the top left of the tile.
    :var tile_rotation: The (clockwise) rotation of the tile, in degrees.

    :return: The point in Luna world space.
    """

    # Create a vector from the tile's origin (its bottom left) to the internal point
    tile_origin_to_point_vec = pyglet.math.Vec2(tile_point[0], tile_point[1] - tile_size[1])
    # rotate it to get the new position
    rotated_origin_to_point_vec = tile_origin_to_point_vec.rotate(math.radians(tile_rotation))
    # add it to the tile's world position to get the absolute world position
    tiled_world_pos = tile_position[0] + rotated_origin_to_point_vec.x, tile_position[1] + rotated_origin_to_point_vec.y
    # convert to Luna's co-ordinate space
    return tiled_to_luna(tiled_world_pos)
