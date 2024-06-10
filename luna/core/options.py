from dataclasses import dataclass


@dataclass
class Options:
    """
    Represents all the options in the game you can set.
    """

    resolution: tuple[int, int]
    fullscreen: bool

    @classmethod
    def create_default(cls) -> "Options":
        """
        Create a default set of options.
        """
        return cls(
            resolution=(1280, 720),
            fullscreen=False,
        )
