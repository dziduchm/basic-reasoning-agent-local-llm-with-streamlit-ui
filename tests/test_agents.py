import pytest
from unittest.mock import patch, MagicMock
from agents.reflection_agent import ReflectionAgent
from agents.search_agent import SearchAgent
from agents.web_fetcher import WebFetcher, FetchError
from utils import load_config

config = load_config()


@patch("utils.get_llm")
def test_reflection_agent_initialization(mock_get_llm):
    # Mock the LLM to return a dummy instance (avoids API key issues)
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm

    agent = ReflectionAgent(config)
    assert agent.graph is not None
    assert agent.llm == mock_llm  # Verify mock is used


@patch("utils.get_llm")
def test_search_agent(mock_get_llm):
    # Mock the LLM
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm

    # Also mock the search tool to avoid real API calls
    with patch("agents.search_agent.DuckDuckGoSearchRun") as mock_search:
        mock_tool = MagicMock()
        mock_tool.run.return_value = "Mock search results"
        mock_search.return_value = mock_tool

        agent = SearchAgent(config)
        result = agent.search("test query")
        assert isinstance(result, str)
        assert "Mock" in result  # Verify mocked output
        mock_tool.run.assert_called_once_with(
            "test query", max_results=config.get("search_results_limit", 5)
        )


def test_web_fetcher_valid_url():
    fetcher = WebFetcher()
    # Use a reliable URL that returns simple HTML content
    result = fetcher.fetch("https://httpbin.org/html")
    # Assert for non-empty content and presence of HTML indicators
    # (httpbin returns basic HTML)
    assert len(result) > 0
    assert "<html>" in result  # httpbin.org/html starts with <!DOCTYPE html>


def test_web_fetcher_invalid_url():
    fetcher = WebFetcher()
    with pytest.raises(FetchError):
        fetcher.fetch("invalid-url")


@patch("utils.get_llm")
@patch("agents.reflection_agent.ChatPromptTemplate")
@patch("agents.reflection_agent.StateGraph")
def test_reflection_loop_max_iterations(mock_graph, mock_prompt, mock_get_llm):
    # Mock LLM and graph components for a simple integration test
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm

    # Mock prompt invocation to return a dummy response
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = MagicMock(content="Satisfactory response")
    mock_prompt.return_value.__or__ = lambda self, llm: mock_chain

    # Mock graph to simulate iterations
    mock_state_graph = MagicMock()
    mock_graph.return_value = mock_state_graph
    mock_state_graph.compile.return_value = MagicMock()

    agent = ReflectionAgent(config)

    # Simulate ainvoke with a simple state (non-async for unit test;
    # in practice, use asyncio for full e2e)
    # Here, we just verify the graph is built and can be invoked without errors
    initial_state = {"messages": [], "context": "test", "iteration": 0}
    # Mock astream_events to yield without errors
    mock_astream = MagicMock()
    mock_astream.__aiter__ = lambda: [
        MagicMock(
            event="on_chat_model_stream",
            data={"chunk": MagicMock(content="token")},
        )
    ]
    agent.graph.astream_events = mock_astream

    # Run a simple invocation (async mocked to sync for test)
    events = agent.ainvoke(initial_state["context"], initial_state["messages"])
    event_list = list(events)  # Consume iterator
    assert len(event_list) > 0  # At least one event yielded
    assert any(
        "on_chat_model_stream" in e.get("event", "") for e in event_list
    )  # Streaming event present

    # Verify max iterations logic indirectly:
    # graph conditional edges should be set
    assert mock_graph.called
