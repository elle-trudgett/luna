import arcade
import shapely
from arcade.experimental.input import ActionState
from pyglet.math import Vec2
from shapely import LineString, Point
import shapely.ops

from luna.core.game_object import GameObject
from luna.core.input_action import InputAction
from luna.core.region import Region
from luna.entities.character import Character
from luna.managers.state_manager import StateManager
from luna.utils.logging import LOGGER


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
    _ground_line: LineString | None = None
    _ground_region: Region | None = None

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
        arcade.draw_lrbt_rectangle_filled(
            self.position[0] - self._bounding_box_width // 2,
            self.position[0] + self._bounding_box_width // 2,
            self.position[1],
            self.position[1] + self._bounding_box_height,
            arcade.color.BLUE,
        )

    def update_position(self, delta_time: float) -> None:
        # Vertical movement
        if not self._on_ground:
            self._inertia += Vec2(0, self.gravity * delta_time)
            if self._inertia.y < 0:
                # Falling
                # Use our position to see when we hit ground

                amount_to_fall = abs(self._inertia.y * delta_time)

                trace = LineString([self.position, self.position + Vec2(0, -amount_to_fall)])

                amount_can_fall = amount_to_fall
                ground_geometry = None
                ground_region = None

                def check_trace(trace: LineString) -> None:
                    nonlocal amount_can_fall, ground_geometry, ground_region
                    for geom, region in self.state_manager.current_map.spatial_tree.query(trace):
                        intersection = shapely.intersection(trace, geom)
                        if intersection:
                            distance = shapely.distance(Point(trace.coords[0]), intersection)
                            if distance < amount_can_fall:
                                amount_can_fall = min(amount_can_fall, distance)
                                self._on_ground = True
                                self._inertia = Vec2(self._inertia.x, 0)
                                ground_geometry = geom
                                ground_region = region

                check_trace(trace)

                # Move down
                self.position += Vec2(0, -amount_can_fall)

                if ground_geometry is not None:
                    # Cache the LineString of the edge we're on.
                    point_geom = Point(self.position)
                    exterior_coords = ground_geometry.exterior.coords
                    min_distance = float("inf")
                    closest_edge = None
                    for i in range(len(exterior_coords) - 1):
                        edge = LineString([exterior_coords[i], exterior_coords[i + 1]])
                        distance = point_geom.distance(edge)
                        if distance < min_distance:
                            min_distance = distance
                            closest_edge = edge

                    # always have co-ordinates go from left to right
                    if closest_edge.coords[0][0] > closest_edge.coords[1][0]:
                        closest_edge = LineString([closest_edge.coords[1], closest_edge.coords[0]])
                    self._ground_line = closest_edge
                    self._ground_region = ground_region

        # Horizontal movement
        if self._on_ground:
            # Move along the ground
            if self._horizontal_input != 0 and self._ground_line:
                x1, y1 = self._ground_line.coords[0]
                x2, y2 = self._ground_line.coords[1]
                # Move along the slope
                direction = Vec2(x2 - x1, y2 - y1).normalize()
                LOGGER.debug(f"Moving along the ground in direction: {direction}")
                self._inertia += direction * self._horizontal_input * self._ACCELERATION * self._ground_region.friction * delta_time

                if self._inertia.x < -self._MAX_SPEED:
                    self._inertia = Vec2(-self._MAX_SPEED, self._inertia.y)
                elif self._inertia.x > self._MAX_SPEED:
                    self._inertia = Vec2(self._MAX_SPEED, self._inertia.y)
            # Apply friction of the ground region
            if not self._horizontal_input:
                deceleration_to_apply = self._ACCELERATION * self._ground_region.friction * delta_time
                if deceleration_to_apply > abs(self._inertia[0]):
                    self._inertia = Vec2(0, self._inertia.y)
                elif self._inertia[0] < 0:
                    self._inertia += Vec2(deceleration_to_apply, 0)
                else:
                    self._inertia -= Vec2(deceleration_to_apply, 0)

        else:
            # Aerial movement
            ...

        # Move horizontally
        self.position += self._inertia * delta_time

        if self._on_ground:
            # Kill y-inertia
            self._inertia = Vec2(self._inertia.x, 0)
            # Snap to the nearest point on the ground
            # First find the nearest point on the line
            point_geom = Point(self.position)
            ground_nearest_point, _ = shapely.ops.nearest_points(self._ground_line, point_geom)
            self.position = Vec2(ground_nearest_point.x, ground_nearest_point.y)
