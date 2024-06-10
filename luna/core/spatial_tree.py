from shapely import STRtree
from shapely.geometry.base import BaseGeometry

from luna.core.region import Region


class SpatialTree:
    """
    Wraps STRtree in shapely for convenience.
    """

    _tree: STRtree
    _geometries: list[BaseGeometry]
    _regions: list[Region]

    def __init__(self, geometries: list[BaseGeometry], regions: list[Region]) -> None:
        self._geometries = geometries
        self._regions = regions
        self._tree = STRtree(geometries)

    def query(self, geometry: BaseGeometry) -> list[tuple[BaseGeometry, Region]]:
        return [(self._geometries[idx], self._regions[idx]) for idx in self._tree.query(geometry)]
