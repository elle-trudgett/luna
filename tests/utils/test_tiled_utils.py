from luna.utils.tiled_utils import tiled_to_luna, tile_point_to_absolute_luna_point


def test_tiled_to_luna_point() -> None:
    assert tiled_to_luna((1, 2)) == (1, -2)
    assert tiled_to_luna((0, 0)) == (0, 0)
    assert tiled_to_luna((0, 1)) == (0, -1)
    assert tiled_to_luna((1, 0)) == (1, 0)
    assert tiled_to_luna((-1, -1)) == (-1, 1)
    assert tiled_to_luna((-1, 1)) == (-1, -1)
    assert tiled_to_luna((1, -1)) == (1, 1)


def test_tile_point_to_absolute_luna_point() -> None:
    """
    Points within a tile are relative to the top-left of their tile.
    Apply translation and rotation to the point to get the world coordinate.
    Rotation happens around the tile's "position" (bottom-left of the tile).
    """
    # Point at local origin (top left)
    assert tile_point_to_absolute_luna_point(
        tile_position=(0, 0),
        tile_size=(100, 100),
        tile_point=(0, 0),
        tile_rotation=0
    ) == (0, 100)

    # Tile translation right 50 px, up 50 px
    assert tile_point_to_absolute_luna_point(
        tile_position=(50, -50),  # 50 px right, 50 px up
        tile_size=(100, 100),
        tile_point=(0, 0),
        tile_rotation=0
    ) == (50, 150)

    # Internal point in an arbitrary location
    assert tile_point_to_absolute_luna_point(
        tile_position=(0, 0),
        tile_size=(100, 100),
        tile_point=(60, 70),
        tile_rotation=0
    ) == (60, 30)

    # Internal point in a translated tile
    assert tile_point_to_absolute_luna_point(
        tile_position=(50, -50),  # 50 px right, 50 px up
        tile_size=(100, 100),
        tile_point=(60, 70),
        tile_rotation=0
    ) == (110, 80)

    # point at top left rotated 90 degrees
    assert tile_point_to_absolute_luna_point(
        tile_position=(0, 0),
        tile_size=(100, 100),
        tile_point=(0, 0),
        tile_rotation=90
    ) == (100, 0)

    # point at bottom left, rotated arbitrary degrees
    for i in range(-360, 360, 10):
        assert tile_point_to_absolute_luna_point(
            tile_position=(0, 0),
            tile_size=(100, 100),
            tile_point=(0, 100),  # bottom left
            tile_rotation=i
        ) == (0, 0)  # no change because it is at the rotation point
