from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WaitUtils:
    @staticmethod
    def wait_for_element_visible(
        driver: WebDriver, locator: tuple[str, str], timeout_seconds: int
    ) -> WebElement:
        return WebDriverWait(driver, timeout_seconds).until(
            EC.visibility_of_element_located(locator)
        )

    @staticmethod
    def wait_for_element_clickable(
        driver: WebDriver, locator: tuple[str, str], timeout_seconds: int
    ) -> WebElement:
        return WebDriverWait(driver, timeout_seconds).until(
            EC.element_to_be_clickable(locator)
        )

    @staticmethod
    def wait_for_title_contains(
        driver: WebDriver, title_fragment: str, timeout_seconds: int
    ) -> bool:
        return WebDriverWait(driver, timeout_seconds).until(
            EC.title_contains(title_fragment)
        )
