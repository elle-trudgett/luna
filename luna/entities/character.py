class Character:
    """
    Represents the player's character state such as level, skills, inventory, and so on. This
    data is separate from the Player sprite, which handles things like physics, animations, appearance,
    and so on. A character can exist without a Player but a Player will always be linked to a Character.

    :var _experience: The player's experience points. This builds up to increase the player's level.
    :var _level: The player's level. This is the driver of the player's strength and abilities.
    """

    _experience: int = 0
    _level: int = 1

    @property
    def level(self) -> int:
        """
        The level of the character.
        """
        return self._level

    @property
    def experience(self) -> int:
        """
        The experience points of the character.
        """
        return self._experience

    def gain_experience(self, amount: int) -> None:
        """
        Gain experience points.

        :param amount: The amount of experience points to gain.
        """
        self._experience += amount
        self._on_update_experience()

    def _on_update_experience(self) -> None:
        """
        Recompute experience-driven stats.
        """
