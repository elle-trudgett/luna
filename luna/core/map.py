from dataclasses import dataclass, field

import arcade

from luna.core.game_object import GameObject, SpawnParameters
from luna.core.map_tile import MapTile
from luna.core.region import Region
from luna.core.region_type import RegionType
from luna.utils.map_constants import DEFAULT_GRAVITY


@dataclass
class Map:
    """
    Container for all the game objects and map data for one contiguous area of the world.

    :var name: The name of the map, shown on entering the map if it is different to the previously
               shown name.
    :var objects: Active objects in the game to draw.
    :var regions: Areas in the map that affect gameplay, such as level geometry, death zones,
                  camera focus zones, and so on.
    :var tiles: Graphical tiles (back/middle/foreground) that make up the visible world in the map.

    """

    name: str = ""
    objects: list[GameObject] = field(default_factory=list)
    regions: list[Region] = field(default_factory=list)
    tiles: list[MapTile] = field(default_factory=list)
    gravity: float = DEFAULT_GRAVITY

    _draw_regions: bool = True

    def spawn(self, game_object: GameObject, spawn_parameters: SpawnParameters) -> None:
        """
        Add a game object to the map.

        :param game_object: The game object to add.
        :param spawn_parameters: The parameters to spawn the game object with.
        """
        game_object.gravity = self.gravity
        game_object.on_spawn(spawn_parameters)
        self.objects.append(game_object)

    def draw(self) -> None:
        """
        Draw the map to the screen.
        """
        # Draw map tiles
        for tile in self.tiles:
            tile.draw()

        # Draw regions
        if self._draw_regions:
            self.draw_regions()

        # Draw game objects
        for game_object in self.objects:
            game_object.draw()

    def draw_regions(self) -> None:
        """
        For debugging purposes, draw the map geometry as outlined polygons.
        """
        for region in self.regions:
            color = arcade.color.BLACK
            match region.designation:
                case RegionType.LEVEL_GEOMETRY:
                    color = arcade.color.GREEN
                case RegionType.DEATH_ZONE:
                    color = arcade.color.RED
            arcade.draw_polygon_outline(region.region_points, color, 2)
