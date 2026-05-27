"""Allure report helpers — attachments, browser metadata, and diagnostics."""

from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import allure
from selenium.webdriver.remote.webdriver import WebDriver


class AllureUtils:
    """Attach rich diagnostics to the current Allure test."""

    @staticmethod
    def attach_screenshot(driver: WebDriver, name: str = "Screenshot") -> None:
        try:
            png = driver.get_screenshot_as_png()
            allure.attach(
                png,
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as exc:
            allure.attach(
                str(exc),
                name=f"{name} (failed)",
                attachment_type=allure.attachment_type.TEXT,
            )

    @staticmethod
    def attach_screenshot_file(
        screenshot_path: str | Path, name: str = "Screenshot"
    ) -> None:
        path = Path(screenshot_path).resolve()
        if not path.is_file():
            AllureUtils.attach_text(
                f"Screenshot file not found: {path}",
                name=f"{name} (missing)",
            )
            return
        with path.open("rb") as image_file:
            allure.attach(
                image_file.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG,
                extension="png",
            )

    @staticmethod
    def attach_page_source(driver: WebDriver, name: str = "Page Source") -> None:
        try:
            allure.attach(
                driver.page_source,
                name=name,
                attachment_type=allure.attachment_type.HTML,
            )
        except Exception as exc:
            allure.attach(
                str(exc),
                name=f"{name} (failed)",
                attachment_type=allure.attachment_type.TEXT,
            )

    @staticmethod
    def attach_current_url(driver: WebDriver) -> None:
        try:
            allure.attach(
                driver.current_url,
                name="Current URL",
                attachment_type=allure.attachment_type.URI_LIST,
            )
        except Exception as exc:
            allure.attach(
                str(exc),
                name="Current URL (failed)",
                attachment_type=allure.attachment_type.TEXT,
            )

    @staticmethod
    def attach_browser_logs(driver: WebDriver) -> None:
        try:
            logs = driver.get_log("browser")
            if logs:
                allure.attach(
                    json.dumps(logs, indent=2),
                    name="Browser Console Logs",
                    attachment_type=allure.attachment_type.JSON,
                )
        except Exception:
            pass

    @staticmethod
    def attach_browser_info(driver: WebDriver) -> None:
        try:
            caps = driver.capabilities or {}
            browser_info = {
                "browserName": caps.get("browserName"),
                "browserVersion": caps.get("browserVersion")
                or caps.get("version"),
                "platformName": caps.get("platformName")
                or caps.get("platform"),
                "driver": caps.get("chrome", caps.get("msedge", caps.get("moz:firefoxOptions", {}))),
            }
            allure.attach(
                json.dumps(browser_info, indent=2, default=str),
                name="Browser Capabilities",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception as exc:
            allure.attach(
                str(exc),
                name="Browser Capabilities (failed)",
                attachment_type=allure.attachment_type.TEXT,
            )

    @staticmethod
    def attach_text(content: str, name: str) -> None:
        allure.attach(
            content,
            name=name,
            attachment_type=allure.attachment_type.TEXT,
        )

    @staticmethod
    def attach_json(data: dict, name: str) -> None:
        allure.attach(
            json.dumps(data, indent=2),
            name=name,
            attachment_type=allure.attachment_type.JSON,
        )

    @staticmethod
    def attach_video(video_path: str | Path, name: str = "Test Recording") -> None:
        path = Path(video_path).resolve()
        if not path.is_file():
            AllureUtils.attach_text(
                f"Video file not found: {path}",
                name=f"{name} (missing)",
            )
            return
        suffix = path.suffix.lower()
        attachment_type = (
            allure.attachment_type.WEBM
            if suffix == ".webm"
            else allure.attachment_type.MP4
        )
        with path.open("rb") as video_file:
            allure.attach(
                video_file.read(),
                name=name,
                attachment_type=attachment_type,
                extension=suffix.lstrip("."),
            )

    @staticmethod
    def attach_failure_diagnostics(driver: WebDriver) -> None:
        """Attach full failure context: URL, page source, logs (screenshot saved separately)."""
        AllureUtils.attach_current_url(driver)
        AllureUtils.attach_page_source(driver, name="Failure Page Source")
        AllureUtils.attach_browser_logs(driver)

    @staticmethod
    def write_environment_properties(
        results_dir: str | Path,
        *,
        environment: str,
        browser: str,
        application_url: str,
        headless: bool,
        timeout: int,
        video_recording: bool = False,
        video_fps: int = 8,
        python_version: str | None = None,
        os_name: str | None = None,
    ) -> None:
        """Write environment.properties consumed by Allure report generation."""
        directory = Path(results_dir)
        directory.mkdir(parents=True, exist_ok=True)
        lines = [
            f"Environment={environment}",
            f"Browser={browser}",
            f"Application.URL={application_url}",
            f"Headless={str(headless).lower()}",
            f"Video.Recording={str(video_recording).lower()}",
            f"Video.FPS={video_fps}",
            f"Timeout.Seconds={timeout}",
            f"Python.Version={python_version or platform.python_version()}",
            f"OS={os_name or platform.platform()}",
            f"Report.Generated.At={datetime.now(timezone.utc).isoformat()}",
        ]
        (directory / "environment.properties").write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def copy_categories(categories_source: Path, results_dir: Path) -> None:
        """Copy categories.json into allure-results for defect grouping."""
        if categories_source.exists():
            (results_dir / "categories.json").write_text(
                categories_source.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
