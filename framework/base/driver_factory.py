import logging
import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from framework.config.config_reader import ConfigReader

logger = logging.getLogger(__name__)


class DriverFactory:
    """Thread-local WebDriver lifecycle management with session recovery."""

    _driver_pool = threading.local()

    def __init__(self) -> None:
        self._config = ConfigReader()

    def is_session_alive(self) -> bool:
        driver = getattr(self._driver_pool, "driver", None)
        if driver is None:
            return False
        try:
            _ = driver.current_window_handle
            return True
        except Exception:
            return False

    def init_driver(self, force_new: bool = False) -> webdriver.Remote:
        if force_new or not self.is_session_alive():
            self.quit_driver()

        if getattr(self._driver_pool, "driver", None) is None:
            browser = (self._config.get_browser() or "chrome").strip().lower()
            headless = self._config.is_headless()
            timeout = self._config.get_timeout()

            if browser == "firefox":
                logger.info("Starting Firefox browser")
                options = FirefoxOptions()
                options.page_load_strategy = "eager"
                if headless:
                    options.add_argument("--headless")
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
            elif browser == "edge":
                logger.info("Starting Edge browser")
                options = EdgeOptions()
                options.page_load_strategy = "eager"
                if headless:
                    options.add_argument("--headless=new")
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
            else:
                logger.info("Starting Chrome browser")
                options = ChromeOptions()
                options.page_load_strategy = "eager"
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-extensions")
                options.add_argument("--remote-allow-origins=*")
                options.add_argument("--window-size=1920,1080")
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                if headless:
                    options.add_argument("--headless=new")
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)

            driver.maximize_window()
            # Use explicit waits only — implicit wait causes flaky sessions.
            driver.implicitly_wait(0)
            driver.set_page_load_timeout(timeout)
            driver.set_script_timeout(timeout)
            self._driver_pool.driver = driver

        return self._driver_pool.driver

    @classmethod
    def get_driver(cls) -> webdriver.Remote:
        driver = getattr(cls._driver_pool, "driver", None)
        if driver is None:
            raise RuntimeError("WebDriver is not initialized. Call init_driver() first.")
        return driver

    def quit_driver(self) -> None:
        driver = getattr(self._driver_pool, "driver", None)
        if driver is not None:
            logger.info("Closing browser instance")
            try:
                driver.quit()
            except Exception as exc:
                logger.debug("Driver quit ignored: %s", exc)
            self._driver_pool.driver = None
