import hashlib
import re
from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver


class ScreenshotUtils:
    @staticmethod
    def capture_screenshot(
        driver: WebDriver,
        screenshot_dir: str | Path,
        scenario_name: str,
        status: str = "passed",
    ) -> Path:
        """Save a PNG screenshot to disk and return its absolute path."""
        directory = Path(screenshot_dir).resolve()
        directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status_prefix = re.sub(r"[^\w]+", "_", status.lower())
        name_hash = hashlib.md5(scenario_name.encode("utf-8")).hexdigest()[:8]
        file_path = directory / f"{status_prefix}_{name_hash}_{timestamp}.png"

        png_bytes = driver.get_screenshot_as_png()
        file_path.write_bytes(png_bytes)

        if not file_path.is_file() or file_path.stat().st_size == 0:
            raise OSError(f"Screenshot was not written: {file_path}")

        return file_path.resolve()
