from luna.core.game_object import GameObject


class SpawnPoint(GameObject):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Spawn Point"
