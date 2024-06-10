import timeit

from arcade.types import PointList
from pyglet.math import Vec2

from luna.collision import collision


def test_sweep_polygon() -> None:
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom right corner at origin
    polygon_motion = Vec2(5, 5)  # move up and right by 5 units each

    swept_polygon: PointList = collision.sweep_polygon(polygon=polygon, vector=polygon_motion)

    assert len(swept_polygon) == 6
    assert (0, 0) in swept_polygon
    assert (0, 1) in swept_polygon
    assert (5, 6) in swept_polygon
    assert (6, 6) in swept_polygon
    assert (6, 5) in swept_polygon
    assert (1, 0) in swept_polygon


def test_no_collision() -> None:
    """
    Case where a square moves with no collision
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(10, 0)  # move right by 10 units

    # unit square with bottom left corner at (0, 5)
    other_polygon = [(0, 5), (0, 6), (1, 6), (1, 5)]

    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    assert not result.collision
    assert result.new_movement_vector == Vec2(10, 0)


def test_move_simple() -> None:
    """
    Case where a square moves into another square
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(10, 0)  # move it way over to the right

    # unit square with bottom left corner at (2, 0)
    other_polygon = [(2, 0), (2, 1), (3, 1), (3, 0)]

    # check that the polygon hits the other polygon (after moving 1 unit to the right)
    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    assert result.collision
    assert result.new_movement_vector == Vec2(1, 0)


def test_move_complex() -> None:
    """
    Case where a square moves into a triangle at an angle
    :return:
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(6, 8)  # move it north-north-east-ish

    # triangle that has the point (4, 5) on one of its edges
    # creating a 3-4-5 pythagorean triangle with the polygon's top-right corner
    other_polygon = [(2, 6), (7, 6), (6, 4)]

    # the square's top right corner should hit the triangle's lower face right in the middle,
    # resulting in a new movement vector of (3, 4)
    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    assert result.collision
    assert result.new_movement_vector == Vec2(3, 4)


def test_move_touching() -> None:
    """
    Case where two polygons are touching and one tries to move into the other
    :return:
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(0.1, 0)  # move it a bit to the right

    # unit square touching the right side of the first square, and raised up a bit
    other_polygon = [(1, 0.1), (1, 1.1), (2, 1.1), (2, 0.1)]

    # check that the polygon hits the other polygon (after moving any amount to the right)
    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    # there should be a collision, but no movement can be added
    assert result.collision
    assert result.new_movement_vector == Vec2(0, 0)


def test_touching_move_away() -> None:
    """
    Case where two polygons are touching, but moving away from each other
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(-1, 0)  # move it to the left

    # unit square touching the right side of the first square, and raised up a bit
    other_polygon = [(1, 0.1), (1, 1.1), (2, 1.1), (2, 0.1)]

    # check that the polygon hits the other polygon (after moving any amount to the right)
    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    # there should be no collision since they are moving away, and the movement should not be impeded
    assert not result.collision
    assert result.new_movement_vector == Vec2(-1, 0)


def test_move_along() -> None:
    """
    Case where an object shares an edge and moves along it
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(2, 0)  # move it to the right

    # Ground underneath the square
    other_polygon = [(0, 0), (10, 0), (10, -1), (0, -1)]

    # the polygon should be free to move to the right
    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    # there should be no collision
    assert not result.collision
    assert result.new_movement_vector == Vec2(2, 0)


def test_move_from_inside() -> None:
    """
    Case where moving a polygon in a direction when it's already inside another polygon
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(1, 0)  # move it to the right

    # unit square with bottom left corner at (0.5, 0.5)
    other_polygon = [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)]

    # there should be a collision
    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    assert result.collision
    # and the new movement vector should be in the opposite direction
    # just enough to get out of the other polygon
    assert result.new_movement_vector == Vec2(-0.5, 0)


def test_hit_small_thing_from_side() -> None:
    """
    This case is where a square moves into a small triangle from the side
    such that the movement vector added to each point on the square never
    intersect any edge of the small triangle
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(10, 0)  # move it to the right

    # small triangle that would fit inside the square is in its path
    other_polygon = [(3, 0.5), (4, 0.75), (4, 0.25)]

    # the square should stop after moving 2 units when the right edge
    # touches the left vertex of the triangle
    result = collision.move_polygon_into_other_polygon(
        polygon=polygon,
        movement_vector=movement_vector,
        other_polygon=other_polygon
    )

    assert result.collision
    assert result.new_movement_vector == Vec2(2, 0)


def test_performance() -> None:
    """
    Test the performance of the collision detection
    """
    polygon = [(0, 0), (0, 1), (1, 1), (1, 0)]  # unit square with bottom left corner at origin
    movement_vector = Vec2(10, 0)  # move it to the right

    # unit square with bottom left corner at (2, 0)
    other_polygon = [(2, 0), (2, 1), (3, 1), (3, 0)]

    print("Speed score:", int(100/timeit.timeit(
        lambda: collision.move_polygon_into_other_polygon(
            polygon=polygon,
            movement_vector=movement_vector,
            other_polygon=other_polygon
        ),
        number=1000
    )))