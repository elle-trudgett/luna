from shapely import STRtree, Polygon

from luna.core.map import Map
from luna.core.region_type import RegionType


class CollisionManager:
    map: Map
    spatial_tree: STRtree

    def __init__(self):
        ...

    def set_map(self, map: Map) -> None:
        self.map = map
        self.on_set_map()

    def on_set_map(self) -> None:
        geometries = []

        for region in self.map.regions:
            if region.designation == RegionType.LEVEL_GEOMETRY:
                geometries.append(Polygon(region.region_points))

        self.spatial_tree = STRtree(geometries)
