import logging
import os
import platform
import shutil
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from framework.base.driver_factory import DriverFactory
from framework.config.config_reader import ConfigReader
from framework.pages.cart_page import CartPage
from framework.pages.home_page import HomePage
from framework.pages.login_page import LoginPage
from framework.utils.allure_utils import AllureUtils
from framework.utils.screenshot_utils import ScreenshotUtils
from framework.utils.video_recorder import VideoRecorder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLURE_RESULTS_DIR = PROJECT_ROOT / "reports/allure-results"
ALLURE_CATEGORIES = PROJECT_ROOT / "allure/categories.json"


def _sync_allure_categories() -> None:
    """Ensure categories.json is present for Allure report generation."""
    AllureUtils.copy_categories(ALLURE_CATEGORIES, ALLURE_RESULTS_DIR)


def _as_long_path(path: Path) -> str:
    """Return Windows long-path string when needed."""
    resolved = str(path.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return f"\\\\?\\{resolved}"
    return resolved


def _reset_directory(path: Path) -> None:
    """Delete a directory and recreate it (handles long Windows paths)."""
    shutil.rmtree(_as_long_path(path), ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)


def _remove_path(path: Path) -> None:
    """Remove a file or directory if it exists."""
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(_as_long_path(path), ignore_errors=True)
    else:
        path.unlink(missing_ok=True)


def _clean_previous_run_artifacts() -> None:
    """Keep only the latest run: reset screenshots, videos, and allure-results."""
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    _reset_directory(reports_dir / "screenshots")
    _reset_directory(reports_dir / "videos")
    _reset_directory(ALLURE_RESULTS_DIR)

    # Legacy folders/files no longer used
    _remove_path(reports_dir / "allure-report")
    _remove_path(reports_dir / "report.html")


@pytest.fixture(scope="session", autouse=True)
def cleanup_previous_artifacts() -> None:
    """Clean artifact folders before the test session starts."""
    _clean_previous_run_artifacts()


@pytest.fixture(scope="session")
def config() -> ConfigReader:
    return ConfigReader()


@pytest.fixture(scope="session", autouse=True)
def allure_environment(
    cleanup_previous_artifacts, config: ConfigReader
) -> None:
    """Publish run metadata visible in the Allure Environment widget."""
    AllureUtils.write_environment_properties(
        ALLURE_RESULTS_DIR,
        environment=config.environment,
        browser=config.get_browser(),
        application_url=config.get_url(),
        headless=config.is_headless(),
        timeout=config.get_timeout(),
        video_recording=config.is_video_recording_enabled(),
        video_fps=config.get_video_fps(),
        python_version=platform.python_version(),
        os_name=platform.platform(),
    )
    _sync_allure_categories()


@pytest.fixture
def driver_factory() -> DriverFactory:
    return DriverFactory()


@pytest.fixture
def driver(driver_factory: DriverFactory, config: ConfigReader) -> WebDriver:
    web_driver = driver_factory.init_driver()
    with allure.step("Attach browser session metadata"):
        AllureUtils.attach_browser_info(web_driver)
        AllureUtils.attach_json(
            {
                "browser": config.get_browser(),
                "headless": config.is_headless(),
                "timeout_seconds": config.get_timeout(),
                "video_recording": config.is_video_recording_enabled(),
                "video_fps": config.get_video_fps(),
                "base_url": config.get_url(),
                "environment": config.environment,
            },
            name="Test Run Configuration",
        )
    yield web_driver
    with allure.step("Close browser session"):
        driver_factory.quit_driver()


@pytest.fixture(autouse=True)
def save_test_screenshot(request, driver: WebDriver, config: ConfigReader):
    """Save screenshot to disk before the browser session closes."""
    yield

    rep = getattr(request.node, "rep_call", None)
    if rep is None or not config.is_screenshot_enabled():
        return

    _capture_test_screenshot(request.node, driver, config, rep)


@pytest.fixture(autouse=True)
def record_test_video(request, driver: WebDriver, config: ConfigReader):
    """Record browser session video and attach to Allure after each test."""
    if not config.is_video_recording_enabled():
        request.node._recorded_video_path = None
        yield
        return

    test_name = request.node.name
    video_dir = (PROJECT_ROOT / config.get_video_path()).resolve()
    recorder = VideoRecorder(
        driver,
        output_dir=video_dir,
        test_name=test_name,
        fps=config.get_video_fps(),
    )

    with allure.step("Start test video recording"):
        recorder.start()

    yield

    with allure.step("Stop test video recording"):
        video_path = recorder.stop_and_save()

    request.node._recorded_video_path = video_path

    if video_path and Path(video_path).is_file():
        rep = getattr(request.node, "rep_call", None)
        label = (
            "Failure Recording"
            if rep is not None and rep.failed
            else "Test Recording"
        )
        AllureUtils.attach_video(video_path, name=label)


@pytest.fixture
def login_page(
    driver: WebDriver, driver_factory: DriverFactory, config: ConfigReader
) -> LoginPage:
    return LoginPage(
        driver,
        timeout=config.get_timeout(),
        driver_factory=driver_factory,
    )


@pytest.fixture
def home_page(driver: WebDriver, config: ConfigReader) -> HomePage:
    return HomePage(driver, timeout=config.get_timeout())


@pytest.fixture
def cart_page(driver: WebDriver, config: ConfigReader) -> CartPage:
    return CartPage(driver, timeout=config.get_timeout())


def _capture_test_screenshot(
    item,
    driver: WebDriver,
    config: ConfigReader,
    report,
) -> Path | None:
    """Save screenshot to reports/screenshots and attach to Allure."""
    if not config.is_screenshot_enabled():
        return None

    screenshot_dir = (PROJECT_ROOT / config.get_screenshot_path()).resolve()
    status = "failed" if report.failed else "passed"
    label = "Failure Screenshot" if report.failed else "Pass Screenshot"

    try:
        screenshot_path = ScreenshotUtils.capture_screenshot(
            driver,
            screenshot_dir,
            item.name,
            status=status,
        )
    except (WebDriverException, OSError) as exc:
        logging.getLogger(__name__).warning(
            "Could not capture screenshot for %s: %s", item.name, exc
        )
        return None

    png_bytes = screenshot_path.read_bytes()
    with allure.step(f"Save {label.lower()}"):
        allure.attach(
            png_bytes,
            name=label,
            attachment_type=allure.attachment_type.PNG,
            extension="png",
        )

    item._screenshot_path = screenshot_path
    return screenshot_path


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when != "call":
        return

    driver_fixture = item.funcargs.get("driver")
    if driver_fixture is None:
        return

    if report.failed:
        with allure.step("Capture failure diagnostics"):
            AllureUtils.attach_failure_diagnostics(driver_fixture)


def pytest_configure(config):
    (PROJECT_ROOT / "reports").mkdir(exist_ok=True)
    (PROJECT_ROOT / "reports/screenshots").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "reports/videos").mkdir(parents=True, exist_ok=True)
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def pytest_sessionfinish(session, exitstatus):
    """Refresh categories in allure-results after the run completes."""
    _sync_allure_categories()
    _remove_path(PROJECT_ROOT / "reports" / "allure-report")
    _remove_path(PROJECT_ROOT / "reports" / "report.html")
