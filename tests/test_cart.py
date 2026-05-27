"""TDD tests for cart workflow on the QA Brains e-commerce site."""

import allure
import pytest

from framework.config.config_reader import ConfigReader
from framework.pages.cart_page import CartPage
from framework.pages.home_page import HomePage
from framework.pages.login_page import LoginPage
from tests.test_data import DEFAULT_LOGIN_USER


@allure.epic("QA Brains E-Commerce")
@allure.feature("Shopping Cart")
@allure.story("Add product to cart")
@pytest.mark.cart
class TestCart:
    """Verify adding a random product to the cart and validating cart contents."""

    @allure.title("Select random product and validate it appears in cart")
    @allure.description(
        "Logs in, picks a random product from the catalog, adds it to the cart, "
        "and validates name and price in the cart panel."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("cart", "e2e", "regression")
    def test_select_random_product_and_validate_in_cart(
        self,
        login_page: LoginPage,
        home_page: HomePage,
        cart_page: CartPage,
        config: ConfigReader,
    ) -> None:
        username, password = DEFAULT_LOGIN_USER
        allure.dynamic.parameter("username", username)

        with allure.step("Authenticate user"):
            login_page.login(config.get_url(), username, password)

        with allure.step("Select a random product and add to cart"):
            home_page.select_random_product()
            product_name = home_page.get_selected_product_name()
            product_price = home_page.get_selected_product_price()
            allure.attach(
                f"Product: {product_name}\nPrice: {product_price}",
                name="Selected Product Details",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Open cart panel"):
            home_page.open_cart_panel()

        with allure.step("Validate product in cart"):
            assert cart_page.is_product_present(product_name), (
                f"Product '{product_name}' not found in cart"
            )
            assert cart_page.validate_product_details(product_name, product_price), (
                f"Cart details mismatch. Expected: {product_name} / {product_price}"
            )
