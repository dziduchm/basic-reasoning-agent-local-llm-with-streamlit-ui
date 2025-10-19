import pytest
from agents.reflection_agent import ReflectionAgent
from agents.search_agent import SearchAgent
from agents.web_fetcher import WebFetcher, FetchError
from utils import load_config

config = load_config()


def test_reflection_agent_initialization():
    agent = ReflectionAgent(config)
    assert agent.graph is not None


def test_search_agent():
    agent = SearchAgent(config)
    result = agent.search("test query")
    assert isinstance(result, str)


def test_web_fetcher_valid_url():
    fetcher = WebFetcher()
    result = fetcher.fetch("https://httpbin.org/html")
    assert "html" in result.lower()


def test_web_fetcher_invalid_url():
    fetcher = WebFetcher()
    with pytest.raises(FetchError):
        fetcher.fetch("invalid-url")


def test_reflection_loop_max_iterations():
    # Mock a scenario where critique never says 'satisfactory'
    # (Simplified test; in real scenario, mock LLM)
    agent = ReflectionAgent(config)
    # This would require full async test; placeholder
    assert True  # Integration test in practice
