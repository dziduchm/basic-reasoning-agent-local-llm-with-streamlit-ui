from langchain_community.tools import DuckDuckGoSearchRun
from utils import get_llm
from prompts.search_prompts import SEARCH_PROMPTS, DEFAULT_VERSION


class SearchAgent:
    def __init__(self, config):
        self.config = config
        self.llm = get_llm(config)
        self.search_tool = DuckDuckGoSearchRun()
        # Use default prompt version; can be overridden via config if needed
        self.prompt = SEARCH_PROMPTS.get(
            self.config.get("prompt_version", DEFAULT_VERSION),
            SEARCH_PROMPTS[DEFAULT_VERSION],
        )

    def search(self, query: str) -> str:
        results = self.search_tool.run(
            query, max_results=self.config.get("search_results_limit", 5)
        )
        return results

    def reasoned_search(self, context: str) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({"context": context})
        if "search" in response.content.lower():
            query = response.content.split("query:")[-1].strip()
            return self.search(query)
        return "No search needed."
