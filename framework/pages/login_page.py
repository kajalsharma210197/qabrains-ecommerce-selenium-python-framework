import logging
from typing import TYPE_CHECKING

import allure
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if TYPE_CHECKING:
    from framework.base.driver_factory import DriverFactory

logger = logging.getLogger(__name__)


class LoginPage:
    def __init__(
        self,
        driver: WebDriver,
        timeout: int = 20,
        driver_factory: "DriverFactory | None" = None,
    ) -> None:
        self.driver = driver
        self.timeout = timeout
        self._driver_factory = driver_factory
        self._refresh_wait()

    def _refresh_wait(self) -> None:
        self.wait = WebDriverWait(
            self.driver,
            self.timeout,
            ignored_exceptions=(WebDriverException,),
        )
        self.username_input = (By.XPATH, "//input[@id='email']")
        self.password_input = (By.XPATH, "//input[@id='password']")
        self.login_button = (By.XPATH, "//button[@type='submit']")
        self.error_message = (
            By.XPATH,
            "//div[contains(@class,'alert-danger')]",
        )

    def _recover_session(self) -> None:
        if self._driver_factory is None:
            raise WebDriverException("Browser session lost and cannot be recovered")
        logger.warning("Browser session lost — recreating WebDriver")
        self.driver = self._driver_factory.init_driver(force_new=True)
        self._refresh_wait()

    def _is_invalid_session_error(self, exc: BaseException) -> bool:
        message = str(exc).lower()
        return "invalid session id" in message or "session deleted" in message

    @allure.step("Open login page: {url}")
    def open_login_page(self, url: str, max_attempts: int = 3) -> None:
        last_error: BaseException | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                if self._driver_factory and not self._driver_factory.is_session_alive():
                    self._recover_session()
                self.driver.get(url)
                self._wait_for_login_form()
                return
            except WebDriverException as exc:
                last_error = exc
                if not self._is_invalid_session_error(exc) or attempt == max_attempts:
                    raise
                logger.warning(
                    "open_login_page attempt %s/%s failed (session lost). Retrying...",
                    attempt,
                    max_attempts,
                )
                self._recover_session()
        raise last_error or WebDriverException("Failed to open login page")

    def _wait_for_login_form(self) -> None:
        self.wait.until(EC.visibility_of_element_located(self.username_input))

    @allure.step("Enter credentials for user: {username}")
    def enter_credentials(self, username: str, password: str) -> None:
        allure.dynamic.parameter("password", "********")
        user_el = self.wait.until(
            EC.visibility_of_element_located(self.username_input)
        )
        user_el.clear()
        user_el.send_keys(username)

        pass_el = self.wait.until(
            EC.visibility_of_element_located(self.password_input)
        )
        pass_el.clear()
        pass_el.send_keys(password)

    @allure.step("Click login button")
    def click_login_button(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.login_button)).click()

    @allure.step("Wait for homepage redirect")
    def wait_for_homepage_redirect(self) -> str:
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: "login" not in d.current_url.lower()
        )
        return self.driver.current_url

    @allure.step("Login as {username}")
    def login(self, url: str, username: str, password: str, max_attempts: int = 3) -> str:
        """Open login page, authenticate, and wait for redirect (with retries)."""
        allure.dynamic.parameter("password", "********")
        last_error: BaseException | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                self.open_login_page(url)
                self.enter_credentials(username, password)
                self.click_login_button()
                return self.wait_for_homepage_redirect()
            except (TimeoutException, WebDriverException) as exc:
                last_error = exc
                logger.warning(
                    "Login attempt %s/%s failed (%s). Retrying...",
                    attempt,
                    max_attempts,
                    str(exc),
                )
                if attempt < max_attempts:
                    if self._is_invalid_session_error(exc):
                        self._recover_session()
                    else:
                        try:
                            self.driver.delete_all_cookies()
                        except WebDriverException:
                            self._recover_session()
        raise last_error or TimeoutException("Login failed after retries")

    def get_current_page_url(self) -> str:
        return self.wait_for_homepage_redirect()

    def get_error_message(self) -> str:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.error_message)
            ).text
        except TimeoutException:
            return ""
