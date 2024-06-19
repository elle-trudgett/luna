from luna.core.game_object import GameObject
from luna.game_objects.spawn_point import SpawnPoint

OBJ_SPAWN_POINT = "Spawn Point"

OBJ_TYPE_MAP: dict[str, type[GameObject]] = {OBJ_SPAWN_POINT: SpawnPoint}

DEFAULT_GRAVITY = -2300
