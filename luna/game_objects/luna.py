import arcade
from arcade.experimental.input import ActionState
from pyglet.math import Vec2

from luna.collision import collision
from luna.core.game_object import GameObject
from luna.core.input_action import InputAction
from luna.core.region_type import RegionType
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

    _bounding_box_width: float = 50
    _bounding_box_height: float = 160

    _inertia: Vec2 = Vec2(0, 500)
    _horizontal_input = 0

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
            self._inertia = Vec2(0, 600)
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
        # Apply gravity
        self._inertia += Vec2(0, self.gravity * delta_time)

        # Apply horizontal motion
        self._inertia += Vec2(self._horizontal_input * 20, 0)

        # just for testing purposes, apply collision to ALL the things
        my_poly = [
            (self.position[0] - self._bounding_box_width // 2, self.position[1]),
            (self.position[0] - self._bounding_box_width // 2, self.position[1] + self._bounding_box_height),
            (self.position[0] + self._bounding_box_width // 2, self.position[1] + self._bounding_box_height),
            (self.position[0] + self._bounding_box_width // 2, self.position[1]),
        ]

        movement_vector = self._inertia * delta_time
        for region in self.state_manager.current_map.regions:
            if region.designation == RegionType.LEVEL_GEOMETRY:
                collision_result = collision.move_polygon_into_other_polygon(
                    my_poly, movement_vector, region.region_points
                )
                movement_vector = collision_result.new_movement_vector
                if collision_result.collision:
                    self._inertia = Vec2(0, 0)

        self.position = (self.position[0] + movement_vector.x, self.position[1] + movement_vector.y)
