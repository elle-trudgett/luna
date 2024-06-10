from arcade import Window

from luna.core.view import View


class ScreenManager:
    """
    Manages the current view and what's on the screen, and transitions between them.
    """

    window: Window
    current_view: View

    def __init__(self, window: Window, initial_view: View) -> None:
        self.window = window
        self.current_view = initial_view

    def start(self) -> None:
        self.window.show_view(self.current_view)
