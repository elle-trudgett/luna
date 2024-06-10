import arcade
import pyglet.shapes
from arcade.camera import Camera2D

from luna.core.view import View
from luna.managers.game_object_manager import GameObjectManager
from luna.managers.input_manager import InputManager
from luna.managers.state_manager import StateManager


class PlayView(View):
    """
    The "in-game" view where the player moves around and interacts with the world.

    :var state_manager: The state manager, which stores the state of the game.
    :var game_object_manager: The game object manager, which handles game object logic.
    :var camera: The camera through which the world is viewed.
    """

    state_manager: StateManager
    game_object_manager: GameObjectManager
    camera: Camera2D

    def __init__(self, input_manager: InputManager, state_manager: StateManager) -> None:
        super().__init__(input_manager)
        self.state_manager = state_manager
        self.game_object_manager = GameObjectManager(self.state_manager, self.input_manager)
        self.camera = Camera2D()

    def on_draw(self) -> None:
        self.clear(color=arcade.color.BLACK)

        with self.camera.activate():
            # Draw the level (incl. game objects)
            self.state_manager.current_map.draw()

            # draw the origin
            arcade.draw_circle_filled(0, 0, 10, arcade.color.WHITE)
            pyglet.shapes.Star(0, 0, 10, 5, 5, color=(255, 0, 0)).draw()

        self.draw_fps()

    def draw_fps(self) -> None:
        arcade.draw_text(
            f"FPS = {int(arcade.get_fps())} | Camera = {self.camera.position}",
            10,
            10,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="left",
            anchor_y="bottom",
            font_name="Metropolis",
        )

    def on_update(self, delta_time: float) -> None:
        self.game_object_manager.update(delta_time)

        # Update camera after everything else has been updated/moved around.
        self.camera.position = self.game_object_manager.get_player_position()
