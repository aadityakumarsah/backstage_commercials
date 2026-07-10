import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

AMAZON_DOMAIN = os.getenv("AMAZON_DOMAIN", "https://www.amazon.ca")
HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"


def _start_browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=HEADLESS)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    )
    page = context.new_page()
    return p, browser, page


def _stop_browser(p, browser):
    browser.close()
    p.stop()


def search_and_collect(product_description: str, k: int = 2) -> list[str]:
    p, browser, page = _start_browser()
    try:
        page.goto(AMAZON_DOMAIN, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        search_box = page.locator("input#twotabsearchtextbox")
        search_box.wait_for(timeout=10000)
        search_box.fill(product_description)
        search_box.press("Enter")
        page.wait_for_timeout(3000)

        urls: list[str] = []
        for i in range(k):
            result_links = page.locator(
                "[data-component-type='s-search-result'] h2 a"
            )
            count = result_links.count()
            if count == 0 or i >= count:
                break

            href = result_links.nth(i).get_attribute("href")
            if href:
                full_url = href if href.startswith("http") else f"{AMAZON_DOMAIN}{href}"
                urls.append(full_url)

        return urls
    finally:
        _stop_browser(p, browser)


def add_to_cart(product_url: str) -> bool:
    p, browser, page = _start_browser()
    try:
        page.goto(product_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        add_to_cart_btn = page.locator("#add-to-cart-button")
        if add_to_cart_btn.is_visible(timeout=5000):
            add_to_cart_btn.click()
            page.wait_for_timeout(3000)
            return True

        return False
    finally:
        _stop_browser(p, browser)


def add_to_wishlist(product_url: str, list_name: str = "wishlist") -> bool:
    p, browser, page = _start_browser()
    try:
        page.goto(product_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        add_to_list_btn = page.locator("#add-to-wishlist-button-submit")
        if add_to_list_btn.is_visible(timeout=5000):
            add_to_list_btn.click()
            page.wait_for_timeout(3000)
            return True

        return False
    finally:
        _stop_browser(p, browser)
