from dataclasses import dataclass

import shapely
from arcade.types import PointList
from shapely import Polygon

from luna.core.region_type import RegionType


@dataclass
class Region:
    """
    Represents a convex polygon in the physical space of a map, with some properties that define its
    behaviour, such as whether it is a death zone, a camera focus zone, or a level geometry.
    Regions have no inherent rendering, they are purely abstract / mathematical.

    :var region_points: The points that make up the region, in order.
    """

    region_points: PointList
    geometry_type: str
    designation: RegionType
    friction: float

    def __init__(self, region_points: PointList, geometry_type: str, designation: RegionType) -> None:
        self.region_points = region_points
        self.geometry_type = geometry_type
        self.designation = designation
        self.friction = 1.0
