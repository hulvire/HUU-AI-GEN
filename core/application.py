from typing import Any

from services.config_service import load_app_config


class Application:
    """
    Provides access to application metadata and configuration.
    """

    def __init__(self) -> None:
        self._config = load_app_config()

    @property
    def name(self) -> str:
        return str(
            self._config.get(
                "name",
                "HUU-AI-GEN",
            )
        )

    @property
    def version(self) -> str:
        return str(
            self._config.get(
                "version",
                "0.0.0",
            )
        )

    @property
    def release_date(self) -> str:
        return str(
            self._config.get(
                "release_date",
                "unknown",
            )
        )

    @property
    def description(self) -> str:
        return str(
            self._config.get(
                "description",
                "",
            )
        )

    @property
    def environment(self) -> str:
        return str(
            self._config.get(
                "environment",
                "production",
            )
        )

    @property
    def debug(self) -> bool:
        return bool(
            self._config.get(
                "debug",
                False,
            )
        )

    def get_config(self) -> dict[str, Any]:
        """
        Return a copy of the complete application configuration.
        """
        return dict(self._config)

    def get_display_version(self) -> str:
        """
        Return a human-readable application version.
        """
        return f"v{self.version}"

    def get_display_title(self) -> str:
        """
        Return the title used by the user interface.
        """
        return f"{self.name} {self.get_display_version()}"


application = Application()