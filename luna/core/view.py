from arcade import View as ArcadeView

from luna.managers.input_manager import InputManager


class View(ArcadeView):
    """
    Base class for all views in Luna. Wraps Arcade's View.

    :var input_manager: Reference to the input manager so views can be interacted with.
    """

    input_manager: InputManager

    def __init__(self, input_manager: InputManager) -> None:
        super().__init__()
        self.input_manager = input_manager
