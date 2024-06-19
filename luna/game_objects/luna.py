from dataclasses import dataclass

import arcade
import shapely
from arcade.experimental.input import ActionState
from pyglet.math import Vec2
from shapely import LineString, Point
import shapely.ops
from shapely.geometry.base import BaseGeometry

from luna.core.game_object import GameObject
from luna.core.input_action import InputAction
from luna.core.region import Region
from luna.core.region_type import RegionType
from luna.entities.character import Character
from luna.managers.state_manager import StateManager
from luna.utils.logging import LOGGER


@dataclass
class EffectiveGround:
    region: Region
    line: LineString
    distance_down: float


@dataclass
class DebugDraw:
    line: LineString = LineString()
    color: arcade.color.Color = arcade.color.RED


class Luna(GameObject):
    """
    Luna in the game world.

    :var character: The associated character data for Luna.
    :var state_manager: The state manager for the game.
    """

    character: Character
    state_manager: StateManager

    _ACCELERATION = 10000
    _MAX_SPEED = 600

    _bounding_box_width: float = 50
    _bounding_box_height: float = 160

    _inertia: Vec2 = Vec2(0, 500)
    _horizontal_input = 0

    _on_ground: bool = False
    _effective_ground: EffectiveGround | None = None

    _debug_draws: list[DebugDraw] = []

    def __init__(self, state_manager: StateManager) -> None:
        super().__init__()
        self.name = "Luna"
        self.character = state_manager.character
        self.state_manager = state_manager

    def update(self, delta_time: float) -> None:
        super().update(delta_time)
        self.update_position(delta_time)

    def on_action(self, action: InputAction, state: ActionState) -> None:
        LOGGER.debug(f"Got action {action} with state {state} for Luna")
        if action == InputAction.JUMP and state == ActionState.PRESSED:
            if self._on_ground:
                self._inertia += Vec2(0, 600)
                self._on_ground = False
                self._ground_line = None
                self._ground_region = None
        elif action == InputAction.LEFT:
            if state == ActionState.PRESSED:
                self._horizontal_input = -1
            elif state == ActionState.RELEASED:
                self._horizontal_input = max(self._horizontal_input, 0)
        elif action == InputAction.RIGHT:
            if state == ActionState.PRESSED:
                self._horizontal_input = 1
            elif state == ActionState.RELEASED:
                self._horizontal_input = min(self._horizontal_input, 0)

    def draw(self) -> None:
        state_color = arcade.color.BLUE
        if not self._on_ground:
            state_color = arcade.color.YELLOW
        arcade.draw_lrbt_rectangle_filled(
            self.position[0] - self._bounding_box_width // 2,
            self.position[0] + self._bounding_box_width // 2,
            self.position[1],
            self.position[1] + self._bounding_box_height,
            state_color,
        )

        for dd in self._debug_draws:
            arcade.draw_line(dd.line.coords[0][0], dd.line.coords[0][1], dd.line.coords[1][0], dd.line.coords[1][1], dd.color, 2)

        self._debug_draws.clear()

    def update_position(self, delta_time: float) -> None:
        self.position = self.position + Vec2(self._horizontal_input * self._ACCELERATION * delta_time * 0.1, 0)
        # find the nearest ground beneath us
        self._effective_ground = self.find_effective_ground()
        print(f"{self._effective_ground = }")
        self.position = self.position - Vec2(0, self._effective_ground.distance_down)


    def find_effective_ground(self) -> EffectiveGround | None:
        # Ray down from left side
        ray_y_offset = 20  # start ray above the ground, to account for inclines
        left_point = Point(self.position[0] - self._bounding_box_width // 2, self.position[1] + ray_y_offset)
        left_ray = LineString([left_point, left_point + Vec2(0, -1000)])

        # Ray down from right side
        right_point = Point(self.position[0] + self._bounding_box_width // 2, self.position[1] + ray_y_offset)
        right_ray = LineString([right_point, right_point + Vec2(0, -1000)])

        # Find the nearest ground
        nearest_ground: BaseGeometry | None = None
        nearest_distance = float("inf")
        dd = None
        for ray in [left_ray, right_ray]:
            for geom, region in self.state_manager.current_map.spatial_tree.query(ray):
                if region.designation == RegionType.LEVEL_GEOMETRY:
                    intersection = ray.intersection(geom)
                    if intersection:
                        distance = shapely.distance(Point(ray.coords[0]), intersection)
                        if distance < nearest_distance:
                            dd = DebugDraw(
                                line=ray,
                                color=arcade.color.RED
                            )
                            nearest_distance = distance
                            nearest_ground = geom
        if dd:
            self._debug_draws.append(dd)

        if nearest_ground:
            return EffectiveGround(region=region, line=nearest_ground, distance_down=nearest_distance - ray_y_offset)
        else:
            return None
