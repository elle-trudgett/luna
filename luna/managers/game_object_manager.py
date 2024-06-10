from luna.core.game_object import SpawnParameters
from luna.core.map import Map
from luna.game_objects.luna import Luna
from luna.game_objects.spawn_point import SpawnPoint
from luna.managers.input_manager import InputManager
from luna.managers.state_manager import StateManager


class GameObjectManager:
    """
    Handles logic that applies to all game objects as well as the interactions between them.

    :var map: The map that the game objects exist in.
    :var input_manager: The input manager for the game.
    """

    map: Map
    input_manager: InputManager
    state_manager: StateManager

    def __init__(self, state_manager: StateManager, input_manager: InputManager) -> None:
        self.input_manager = input_manager
        self.state_manager = state_manager

        self.load_map(state_manager.current_map)

    def load_map(self, game_map: Map) -> None:
        """
        Load a new map into the game object manager.

        :param game_map: The map to load.
        """
        self.map = game_map
        self._on_load_map()

    def update(self, delta_time: float) -> None:
        """
        Update all game objects.

        :param delta_time: Time since the last update.
        """
        for game_object in self.map.objects:
            game_object.update(delta_time)

    def _on_load_map(self) -> None:
        """
        Called when a new map is loaded into the game object manager.
        """
        self._spawn_luna()

    def _spawn_luna(self) -> None:
        """
        Spawns Luna into the map at the appropriate location.
        """

        # For right now just create her at the first spawn point
        for map_object in self.map.objects:
            if isinstance(map_object, SpawnPoint):
                luna = Luna(self.state_manager)
                self.map.spawn(luna, SpawnParameters(position=map_object.position))
                self.input_manager.register_game_object(luna)
                return

        raise RuntimeError("No spawn point found in map")

    def get_player_position(self) -> tuple[float, float]:
        for game_object in self.map.objects:
            if isinstance(game_object, Luna):
                return game_object.position
        raise RuntimeError("No player found in map")
