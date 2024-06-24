from pathlib import Path

import arcade
import pytiled_parser
import shapely
from arcade.earclip import earclip
from pyglet.math import Vec2
from pytiled_parser import ObjectLayer, TiledMap
from pytiled_parser.tiled_object import (
    Tile as ObjectTile,
    TiledObject,
    Polygon,
    Rectangle,
    Polyline
)
from pytiled_parser.tileset import Tile
from shapely import STRtree

from luna.core.game_object import SpawnParameters
from luna.core.map import Map
from luna.core.map_tile import MapTile
from luna.core.region import Region
from luna.core.region_type import RegionType
from luna.core.spatial_tree import SpatialTree
from luna.utils.logging import LOGGER
from luna.utils.map_constants import OBJ_TYPE_MAP
from luna.utils.tiled_utils import tile_point_to_absolute_luna_point

LAYER_NAME_LEVEL = "LevelLayer"
LAYER_NAME_OBJECTS = "ObjectLayer"


class MapLoader:
    """
    Class that handles loading Tiled maps into Map files.
    """

    _map: Map
    _tiled_map: TiledMap
    _tile_gids: dict[int, Tile]

    def __init__(self) -> None:
        self._map = Map()
        self._tile_gids = {}

    def load_map(self, map_filename: str) -> Map:
        """
        Load a map from a file.

        :param map_filename: The file to load the map from.
        :return: The map object.
        """
        self._map = Map()

        self._tiled_map = pytiled_parser.parse_map(Path(map_filename))
        self._tile_gids = self._load_tile_gids()

        for layer in self._tiled_map.layers:
            if not isinstance(layer, ObjectLayer):
                # We only care about ObjectLayers, at least for now
                continue

            if layer.class_ == LAYER_NAME_LEVEL:
                # This layer is reserved for level geometry objects
                self._load_level_layer(layer)
            elif layer.class_ == LAYER_NAME_OBJECTS:
                self._load_object_layer(layer)

        # create spatial tree
        geometries = []
        regions = []
        for region in self._map.regions:
            if region.geometry_type == "polygon":
                geometries.append(shapely.Polygon(region.region_points))
                regions.append(region)
            elif region.geometry_type == "line_string":
                geometries.append(shapely.LineString(region.region_points))
                regions.append(region)

        self._map.spatial_tree = SpatialTree(geometries, regions)

        LOGGER.debug(f"Map load complete: {map_filename}")
        return self._map

    def _load_tile_gids(self) -> dict[int, Tile]:
        """
        Loads the mapping dictionary that maps global tile IDs to their respective tiles.
        :return: GID -> Tile map
        """
        tile_gids: dict[int, Tile] = {}

        for tileset in self._tiled_map.tilesets.values():
            for tile in tileset.tiles.values():
                tile_gid = tileset.firstgid + tile.id
                tile_gids[tile_gid] = tile

        return tile_gids

    def _load_object_layer(self, layer: ObjectLayer) -> None:
        """
        Load objects from an object layer into the Map.
        :param layer:
        :return:
        """
        for tiled_obj in layer.tiled_objects:
            if tiled_obj.name in OBJ_TYPE_MAP:
                new_object = OBJ_TYPE_MAP[tiled_obj.name]()
                self._map.spawn(new_object, self._to_spawn_parameters(tiled_obj))

    def _load_level_layer(self, layer: ObjectLayer) -> None:
        for tiled_obj in layer.tiled_objects:
            if isinstance(tiled_obj, ObjectTile):
                geometry_tile: Tile = self._tile_gids[tiled_obj.gid]
                self._map.tiles.append(
                    MapTile(
                        position=tile_point_to_absolute_luna_point(
                            tile_position=(tiled_obj.coordinates.x, tiled_obj.coordinates.y),
                            tile_size=(tiled_obj.size.width, tiled_obj.size.height),
                            tile_rotation=tiled_obj.rotation,
                            tile_point=(tiled_obj.size.width / 2, tiled_obj.size.height / 2),
                        ),
                        size=(tiled_obj.size.width, tiled_obj.size.height),
                        rotation=tiled_obj.rotation,
                        texture=arcade.load_texture(geometry_tile.image),
                    )
                )

                # and all regions defined inside this tile
                if geometry_tile.objects and isinstance(geometry_tile.objects, ObjectLayer):
                    # Geometry object has collision information
                    geometry_objects = geometry_tile.objects
                    for geometry_object in geometry_objects.tiled_objects:
                        self._add_level_geometry(tiled_obj, geometry_object)

    def _add_level_geometry(self, object_tile: ObjectTile, geometry_object: TiledObject) -> None:
        points = []
        geometry_type = ""
        x = geometry_object.coordinates.x
        y = geometry_object.coordinates.y

        if isinstance(geometry_object, Polygon):
            for point in geometry_object.points:
                points.append((x + point.x, y + point.y))
            geometry_type = "polygon"
        elif isinstance(geometry_object, Rectangle):
            width = geometry_object.size.width
            height = geometry_object.size.height
            points.append((x, y))
            points.append((x + width, y))
            points.append((x + width, y + height))
            points.append((x, y + height))
            geometry_type = "polygon"
        elif isinstance(geometry_object, Polyline):
            for point in geometry_object.points:
                points.append((x + point.x, y + point.y))
            geometry_type = "line_string"
        else:
            raise ValueError(f"Unsupported geometry object type {type(geometry_object)}")

        points = [
            tile_point_to_absolute_luna_point(
                tile_position=(object_tile.coordinates.x, object_tile.coordinates.y),
                tile_size=(object_tile.size.width, object_tile.size.height),
                tile_point=(x, y),
                tile_rotation=object_tile.rotation,
            )
            for x, y in points
        ]

        if geometry_type == "polygon":
            # Triangulate polygon to ensure regions are convex
            triangles = earclip(points)
            for triangle in triangles:
                geometry_region = Region(
                    region_points=triangle,
                    geometry_type="polygon",
                    designation=self._to_region_type(geometry_object.class_),
                )
                self._map.regions.append(geometry_region)
        else:
            for i in range(len(points) - 1):
                geometry_region = Region(
                    region_points=[points[i], points[i + 1]],
                    geometry_type="line_string",
                    designation=self._to_region_type(geometry_object.class_),
                )
                self._map.regions.append(geometry_region)

    def _to_region_type(self, geometry_class: str) -> RegionType:
        """
        Converts a Tiled class to the respective RegionType.
        :param geometry_class: The Tiled class
        :return: The corresponding RegionType
        """
        match geometry_class:
            case "Ground":
                return RegionType.GROUND
            case "Platform":
                return RegionType.PLATFORM
            case "Wall":
                return RegionType.WALL
            case "Ceiling":
                return RegionType.CEILING
            case "DeathZone":
                return RegionType.DEATH_ZONE
            case _:
                raise ValueError(f"Unsupported geometry class {geometry_class}")

    def _to_spawn_parameters(self, tiled_obj: TiledObject) -> SpawnParameters:
        """
        Converts a Tiled object to SpawnParameters.
        """

        return SpawnParameters(
            position=Vec2(tiled_obj.coordinates.x, -tiled_obj.coordinates.y),
        )
