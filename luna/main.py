import arcade

from luna.managers.game_manager import GameManager
from luna.utils.logging import configure_logging

arcade.enable_timings()
arcade.load_font("luna/metropolis.regular.otf")


def main() -> None:
    configure_logging()
    GameManager().start()
    arcade.run()


if __name__ == "__main__":
    main()
