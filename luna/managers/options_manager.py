from luna.core.options import Options


class OptionsManager:
    """
    Manages access to the active Options.
    """

    _options: Options

    def __init__(self, options: Options | None = None) -> None:
        if not options:
            options = Options.create_default()
        self._options = options

    @property
    def options(self) -> Options:
        return self._options
