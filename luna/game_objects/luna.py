from dataclasses import dataclass

import arcade
import pyglet
import shapely
from arcade.experimental.input import ActionState
from pyglet.math import Vec2
from shapely import LineString, Point, Polygon
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


class Luna(GameObject):
    """
    Luna in the game world.

    :var character: The associated character data for Luna.
    :var state_manager: The state manager for the game.
    """

    character: Character
    state_manager: StateManager

    _ACCELERATION = 5000
    _MAX_SPEED = 600

    _bounding_box_width: float = 50
    _bounding_box_height: float = 160

    _inertia: Vec2 = Vec2(0, 500)
    _horizontal_input: float = 0
    _jump_strength: float = 800

    _on_ground: bool = False
    _effective_ground: EffectiveGround | None = None

    _debug_draws = []

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
                self._inertia += Vec2(0, self._jump_strength)
                self._on_ground = False
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

        for dd in self._debug_draws:
            dd()


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

        self._debug_draws.clear()

    def update_position(self, delta_time: float) -> None:
        # cap speed
        if self._inertia.x < -self._MAX_SPEED:
            self._inertia = Vec2(-self._MAX_SPEED, self._inertia.y)
        elif self._inertia.x > self._MAX_SPEED:
            self._inertia = Vec2(self._MAX_SPEED, self._inertia.y)

        self.position = self.position + self._inertia * delta_time

        # find the nearest ground beneath us
        self._effective_ground = self.find_effective_ground()
        if self._effective_ground:
            a = max(0, int(180 - self._effective_ground.distance_down * 1))
            self._debug_draws.append(
                lambda: arcade.draw_ellipse_filled(
                    self.position[0],
                    self.position[1] - self._effective_ground.distance_down,
                    self._bounding_box_width * (1 + max(0, self._effective_ground.distance_down * 0.005)),
                    10,
                    arcade.color.Color(0, 0, 0, a),
                )
            )
            if self._effective_ground.distance_down < 0 and self._inertia.y < 0:
                self._on_ground = True
                self._inertia = Vec2(self._inertia.x, 0)

        if self._on_ground and self._effective_ground:
            movement_friction = self._effective_ground.region.friction
            # snap to ground.
            self.position = self.position - Vec2(0, self._effective_ground.distance_down)
        else:
            movement_friction = 0.25

        # add input inertia
        self._inertia = self._inertia + Vec2(self._horizontal_input * movement_friction * self._ACCELERATION * delta_time, 0)

        # slow down if not giving input
        if not self._horizontal_input:
            # decelerate due to friction
            deceleration_amount = movement_friction * self._ACCELERATION * delta_time
            if self._on_ground:
                # apply against ground direction
                if deceleration_amount > abs(self._inertia):
                    self._inertia = Vec2(0, 0)
                else:
                    self._inertia = self._inertia - self._inertia.normalize() * deceleration_amount
            else:
                # only apply to horizontal
                if deceleration_amount > abs(self._inertia.x):
                    self._inertia = Vec2(0, self._inertia.y)
                else:
                    if self._inertia.x > 0:
                        self._inertia = Vec2(self._inertia.x - deceleration_amount, self._inertia.y)
                    else:
                        self._inertia = Vec2(self._inertia.x + deceleration_amount, self._inertia.y)

        # Vertical movement
        # add gravity
        self._inertia = self._inertia + Vec2(0, self.gravity * delta_time)

    def find_effective_ground(self) -> EffectiveGround | None:
        ground_check_polygon_y_offset = 80
        left_point = Point(self.position[0] - self._bounding_box_width // 2, self.position[1] + ground_check_polygon_y_offset)
        right_point = Point(self.position[0] + self._bounding_box_width // 2, self.position[1] + ground_check_polygon_y_offset)

        ground_check_poly = Polygon([
            (left_point.x, left_point.y),
            (right_point.x, right_point.y),
            (right_point.x, right_point.y - 1000),
            (left_point.x, left_point.y - 1000),
        ])

        # Find the nearest ground
        nearest_ground: BaseGeometry | None = None
        nearest_distance = float("inf")
        dd = None
        for geom, region in self.state_manager.current_map.spatial_tree.query(ground_check_poly):
            if region.designation == RegionType.LEVEL_GEOMETRY:
                intersection = ground_check_poly.intersection(geom)
                if intersection:
                    top_of_ground_poly = LineString([left_point, right_point])
                    distance = shapely.distance(top_of_ground_poly, intersection)
                    if distance < nearest_distance:
                        a, b = shapely.ops.nearest_points(top_of_ground_poly, intersection)

                        def draw_ground_contact_point():
                            pyglet.shapes.Star(b.x, b.y, 10, 5, 8, color=(255, 0, 0)).draw()

                        #self._debug_draws.append(draw_ground_contact_point)

                        nearest_distance = distance
                        nearest_ground = geom
        if dd:
            self._debug_draws.append(dd)

        if nearest_ground:
            return EffectiveGround(region=region, line=nearest_ground, distance_down=nearest_distance - ground_check_polygon_y_offset)
        else:
            return None
