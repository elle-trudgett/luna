from arcade import Window
from arcade.color import CORNFLOWER_BLUE

from luna.entities.character import Character
from luna.managers.input_manager import InputManager
from luna.managers.options_manager import OptionsManager
from luna.managers.screen_manager import ScreenManager
from luna.managers.state_manager import StateManager
from luna.utils.map_loader import MapLoader
from luna.views.play_view import PlayView


class GameManager:
    class GameWindow(Window):
        def __init__(self, width: int, height: int, title: str) -> None:
            super().__init__(
                width,
                height,
                title,
                update_rate=1 / 120,
                draw_rate=1 / 120,
                fullscreen=False,
            )

            self.background_color = CORNFLOWER_BLUE

    window: GameWindow
    options_manager: OptionsManager
    state_manager: StateManager
    input_manager: InputManager
    screen_manager: ScreenManager

    def __init__(self) -> None:
        self.options_manager = OptionsManager()

        width, height = self.options_manager.options.resolution
        self.window = self.GameWindow(width, height, "Luna")

        test_map = MapLoader().load_map("luna/data/maps/test_map.tmj")

        self.state_manager = StateManager(current_map=test_map, character=Character())
        self.input_manager = InputManager()
        self.screen_manager = ScreenManager(self.window, PlayView(self.input_manager, self.state_manager))

    def start(self) -> None:
        self.screen_manager.start()
