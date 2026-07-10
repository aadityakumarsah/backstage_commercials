from server.agents.browser_agent import search_and_collect


def ask_search_similar_agent(product_description: str, k: int = 2) -> list[str]:
    return search_and_collect(product_description, k=k)
