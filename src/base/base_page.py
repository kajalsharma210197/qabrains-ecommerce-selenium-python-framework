from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from framework.utils.wait_utils import WaitUtils


class BasePage:
    """Shared page interactions built on explicit waits."""

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        self.driver = driver
        self.timeout = timeout

    def find_element(self, locator: tuple[str, str]) -> WebElement:
        return WaitUtils.wait_for_element_visible(
            self.driver, locator, self.timeout
        )

    def click(self, locator: tuple[str, str]) -> None:
        WaitUtils.wait_for_element_clickable(
            self.driver, locator, self.timeout
        ).click()

    def send_keys(self, locator: tuple[str, str], text: str) -> None:
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text

    def is_displayed(self, locator: tuple[str, str]) -> bool:
        return self.find_element(locator).is_displayed()

    def open_url(self, url: str) -> None:
        self.driver.get(url)
