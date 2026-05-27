import os
from pathlib import Path


class ConfigReader:
    """Loads framework settings from config/config.properties."""

    def __init__(self, config_path: str | None = None) -> None:
        self._properties: dict[str, str] = {}
        path = (
            Path(config_path)
            if config_path
            else Path(__file__).resolve().parents[2] / "config" / "config.properties"
        )
        if not path.exists():
            raise FileNotFoundError(f"config.properties not found at {path}")

        with path.open(encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                self._properties[key.strip().lower()] = value.strip()

        self.environment = os.environ.get(
            "env", self._properties.get("env", "qa")
        )

    def get_browser(self) -> str:
        return self._properties.get("browser", "chrome")

    def get_url(self) -> str:
        env_key = f"{self.environment}.url"
        return self._properties.get(env_key, self._properties.get("url", ""))

    def get_timeout(self) -> int:
        return int(self._properties.get("timeout", "20"))

    def is_headless(self) -> bool:
        return self._properties.get("headless", "false").lower() == "true"

    def get_screenshot_path(self) -> str:
        return self._properties.get("screenshotpath", "reports/screenshots")

    def is_screenshot_enabled(self) -> bool:
        return self._properties.get("savescreenshots", "true").lower() == "true"

    def get_allure_results_path(self) -> str:
        return self._properties.get("allureresultspath", "reports/allure-results")

    def is_video_recording_enabled(self) -> bool:
        return self._properties.get("videorecording", "true").lower() == "true"

    def get_video_path(self) -> str:
        return self._properties.get("videopath", "reports/videos")

    def get_video_fps(self) -> int:
        return int(self._properties.get("videofps", "8"))
