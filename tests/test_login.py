"""TDD tests for QA Brains login functionality."""

import allure
import pytest

from framework.config.config_reader import ConfigReader
from framework.pages.login_page import LoginPage
from tests.test_data import HOMEPAGE_URL, LOGIN_USERS


@allure.epic("QA Brains E-Commerce")
@allure.feature("Authentication")
@allure.story("Valid user login")
@pytest.mark.smoke
class TestLogin:
    """Verify successful authentication with valid credentials."""

    @allure.title("Successful login with valid credentials — {username}")
    @allure.description(
        "Opens the login page, submits valid credentials, and verifies "
        "the user is redirected to the e-commerce homepage."
    )
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "login", "regression")
    @pytest.mark.parametrize("username,password", LOGIN_USERS)
    def test_successful_login_with_valid_credentials(
        self,
        login_page: LoginPage,
        config: ConfigReader,
        username: str,
        password: str,
    ) -> None:
        allure.dynamic.parameter("username", username)
        allure.dynamic.parameter("password", "********")

        with allure.step(f"Open login page: {config.get_url()}"):
            login_page.open_login_page(config.get_url())

        with allure.step("Enter credentials and submit login form"):
            login_page.enter_credentials(username, password)
            login_page.click_login_button()

        with allure.step("Verify redirect to homepage"):
            current_url = login_page.wait_for_homepage_redirect()
            allure.attach(
                current_url,
                name="Redirect URL",
                attachment_type=allure.attachment_type.TEXT,
            )

        assert HOMEPAGE_URL in current_url, (
            f"Expected redirect to homepage, got: {current_url}"
        )
        assert "login" not in current_url.lower()
