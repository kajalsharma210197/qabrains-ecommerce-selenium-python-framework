import logging

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class CartPage:
    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        self.wait = WebDriverWait(driver, timeout)
        self.cart_container = (By.ID, "cart")
        self.cart_item_rows = (
            By.XPATH,
            "//div[@id='cart']//div[contains(@class,'cart-list')]/div",
        )
        self.cart_item_name = (
            By.XPATH,
            ".//h3[contains(@class,'font-bold')]",
        )
        self.cart_item_price = (
            By.XPATH,
            ".//p[text()='Price']/parent::div/p[contains(@class,'font-bold')]",
        )

    def get_cart_items(self):
        return self.wait.until(
            EC.visibility_of_all_elements_located(self.cart_item_rows)
        )

    @allure.step("Check product present in cart: {product_name}")
    def is_product_present(self, product_name: str) -> bool:
        for item in self.get_cart_items():
            name = item.find_element(*self.cart_item_name).text.strip()
            logger.info("Cart item name: %s", name)
            if name.lower() == product_name.lower():
                return True
        return False

    @allure.step("Validate cart item: {expected_name} @ {expected_price}")
    def validate_product_details(
        self, expected_name: str, expected_price: str
    ) -> bool:
        for item in self.get_cart_items():
            actual_name = item.find_element(*self.cart_item_name).text.strip()
            actual_price = item.find_element(*self.cart_item_price).text.strip()
            logger.info("Cart Name: %s", actual_name)
            logger.info("Cart Price: %s", actual_price)
            if (
                actual_name.lower() == expected_name.lower()
                and actual_price == expected_price
            ):
                return True
        return False
