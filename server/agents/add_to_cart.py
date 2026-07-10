from server.agents.browser_agent import add_to_cart as browser_add_to_cart, add_to_wishlist as browser_add_to_wishlist


def ask_add_to_shopping_cart(product_url: str, add_to_wishlist: str = "") -> bool:
    if add_to_wishlist:
        return browser_add_to_wishlist(product_url, list_name=add_to_wishlist)
    return browser_add_to_cart(product_url)
