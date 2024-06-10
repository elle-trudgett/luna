from dataclasses import dataclass

from luna.core.map import Map
from luna.entities.character import Character


@dataclass
class StateManager:
    """
    Stores the state of the game, which includes everything in a save file.
    """

    current_map: Map
    character: Character
