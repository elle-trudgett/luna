import enum


class RegionType(enum.Enum):
    """
    Represents the type of region, which determines its behaviour in the game world.

    :var LEVEL_GEOMETRY: Static geometry that the player can collide with.
    :var DEATH_ZONE: Touch it, you die
    """

    LEVEL_GEOMETRY = 0
    DEATH_ZONE = 1
