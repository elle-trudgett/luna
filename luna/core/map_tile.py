from dataclasses import dataclass

import arcade
from arcade import Texture


@dataclass
class MapTile:
    """
    Represents a tile in the map which is used only for rendering purposes

    :var position: The position of the tile in the map. Corresponds to the center of the texture.
    :var size: The width and height of the element in the map (may be different from the texture, if
               it's scaled.)
    :var rotation: The rotation of the tile in degrees.
    :var texture: The texture of the tile to render.
    """

    position: tuple[float, float]
    size: tuple[float, float]
    rotation: float
    texture: Texture

    def draw(self) -> None:
        """
        Draw the tile to the screen.
        """
        # LOGGER.debug(f"Drawing texture at {self.position} with size {self.size} and rotation {self.rotation}")
        arcade.draw_texture_rectangle(
            self.position[0], self.position[1], self.size[0], self.size[1], self.texture, self.rotation
        )
