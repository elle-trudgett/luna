from arcade import ControllerManager
from arcade.experimental import input

from luna.core.game_object import GameObject
from luna.core.input_action import InputAction
from luna.utils.logging import LOGGER


class InputManager:
    """
    Handles the input for the game. Wraps the experimental arcade InputManager.

    :var _internal_input_manager: Reference to the experimental arcade InputManager.
    """

    _internal_input_manager: input.InputManager
    _controller_manager: ControllerManager

    def __init__(self) -> None:
        self._controller_manager = ControllerManager()

        controller = None
        if self._controller_manager.get_controllers():
            controller = self._controller_manager.get_controllers()[0]
        self._internal_input_manager = input.InputManager(controller=controller)

        self._internal_input_manager.new_action(InputAction.JUMP.value)
        self._internal_input_manager.add_action_input(InputAction.JUMP.value, input.Keys.SPACE)
        self._internal_input_manager.add_action_input(InputAction.JUMP.value, input.ControllerButtons.BOTTOM_FACE)

        self._internal_input_manager.new_action(InputAction.LEFT.value)
        self._internal_input_manager.add_action_input(InputAction.LEFT.value, input.Keys.A)
        self._internal_input_manager.add_action_input(InputAction.LEFT.value, input.ControllerButtons.DPAD_LEFT)

        self._internal_input_manager.new_action(InputAction.RIGHT.value)
        self._internal_input_manager.add_action_input(InputAction.RIGHT.value, input.Keys.D)
        self._internal_input_manager.add_action_input(InputAction.RIGHT.value, input.ControllerButtons.DPAD_RIGHT)

        LOGGER.debug("Initialized InputManager")
        LOGGER.debug(f"Controllers detected: {self._controller_manager.get_controllers()}")

    def register_game_object(self, game_object: GameObject) -> None:
        """
        Register a game object with the input manager.

        :param game_object: The game object to register.
        """

        def game_object_on_action(action: str, state: input.ActionState) -> None:
            game_object.on_action(InputAction(action), state)

        self._internal_input_manager.register_action_handler(game_object_on_action)
