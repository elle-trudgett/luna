import enum


class RegionType(enum.Enum):
    """
    Represents the type of region, which determines its behaviour in the game world.

    :var GROUND: Static geometry that the player can collide with.
    :var DEATH_ZONE: Touch it, you die
    """

    GROUND = 0
    DEATH_ZONE = 1
    PLATFORM = 2
    WALL = 3
    CEILING = 4
