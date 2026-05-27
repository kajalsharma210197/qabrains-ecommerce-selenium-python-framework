import logging
import random
import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class HomePage:
    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.product_cards = (
            By.XPATH,
            "//div[contains(@class,'products')]/div[contains(@class,'group')]",
        )
        self.product_name_relative = (
            By.XPATH,
            ".//a[contains(@class,'font-semibold')]",
        )
        self.product_price_relative = (
            By.XPATH,
            ".//span[contains(@class,'font-bold')]",
        )
        self.add_to_cart_relative = (
            By.XPATH,
            ".//button[contains(text(),'Add to cart')]",
        )
        self.cart_icon = (
            By.XPATH,
            "//header[@id='ecommerce-header']//span[@role='button']",
        )
        self.cart_panel = (By.ID, "cart")
        self._selected_product_name: str | None = None
        self._selected_product_price: str | None = None

    @allure.step("Select random product and add to cart")
    def select_random_product(self) -> None:
        products = self.wait.until(
            EC.visibility_of_all_elements_located(self.product_cards)
        )
        if not products:
            raise RuntimeError("No products found on homepage")

        product = random.choice(products)
        name_element = product.find_element(*self.product_name_relative)
        price_element = product.find_element(*self.product_price_relative)
        add_to_cart = product.find_element(*self.add_to_cart_relative)

        self._selected_product_name = name_element.text.strip()
        self._selected_product_price = price_element.text.strip()

        logger.info("Selected Product: %s", self._selected_product_name)
        logger.info("Selected Price: %s", self._selected_product_price)

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", add_to_cart
        )
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", add_to_cart)

    def get_selected_product_name(self) -> str:
        if self._selected_product_name is None:
            raise RuntimeError("No product selected yet")
        return self._selected_product_name

    def get_selected_product_price(self) -> str:
        if self._selected_product_price is None:
            raise RuntimeError("No product price captured yet")
        return self._selected_product_price

    @allure.step("Open cart panel")
    def open_cart_panel(self) -> None:
        self.driver.execute_script("window.scrollTo(0, 0);")
        cart_icon = self.wait.until(EC.presence_of_element_located(self.cart_icon))
        self.driver.execute_script("arguments[0].click();", cart_icon)
        self.wait.until(EC.visibility_of_element_located(self.cart_panel))
