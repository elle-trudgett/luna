from dataclasses import dataclass

from arcade.experimental.input import ActionState
from arcade.types import Point

from luna.core.input_action import InputAction
from luna.utils.logging import LOGGER


@dataclass
class SpawnParameters:
    position: Point


class GameObject:
    """
    Represents an object in the physical space of the game world, including things like
    its appearance and behavior. This is a base class that should be extended by specific core of
    game_objects. For any logic that lives outside the lifecycle of a single map,
    put that in a linked Entity.

    :var name: The internal name of the game object, mostly for debugging purposes.
    :var position: The position of the game object in the game world. It is up to the GameObject
                   to decide what this location means in relation to itself; it comes straight from
                   the map data.
    """

    name: str
    position: Point
    gravity: float = 0

    def on_spawn(self, parameters: SpawnParameters) -> None:
        """
        Called when the game object is spawned into the game world.
        """
        self.position = parameters.position
        LOGGER.debug(f"Spawned game object {self.name}")

    def update(self, delta_time: float) -> None:
        """
        Process logic for the game object, this is called once per frame.
        Subclasses should override this method to implement their own logic.

        :param delta_time: Time passed since the last update.
        """
        ...

    def draw(self) -> None:
        """
        Draw the game object to the screen.
        Subclasses should override this method to implement their own logic.
        """
        ...

    def on_action(self, action: InputAction, state: ActionState) -> None:
        """
        Handle an action from the input manager.
        Subclasses should override this method to implement their own logic.
        :param action: The action type to handle.
        :param state: Whether the action is pressed or released.
        """
        ...
