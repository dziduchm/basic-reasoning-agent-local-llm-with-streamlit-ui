import logging
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, List
from utils import get_llm
from .web_fetcher import WebFetcher
from .search_agent import SearchAgent

logger = logging.getLogger(__name__)


class State(TypedDict):
    messages: List[dict]
    context: str
    iteration: int


class ReflectionAgent:
    def __init__(self, config):
        self.config = config
        self.llm = get_llm(config)
        self.web_fetcher = WebFetcher()
        self.search_agent = SearchAgent(config)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(State)

        # Node: Generate initial response
        def generate(state: State) -> dict:
            prompt = ChatPromptTemplate.from_template(
                "System: You are a reflective reasoning agent. Use context and previous messages to respond. "
                "If needed, perform searches or fetches.\n\n{context}\n\nMessages: {messages}"
            )
            chain = prompt | self.llm
            response = chain.invoke(
                {"context": state["context"], "messages": state["messages"]}
            )
            new_messages = state["messages"] + [AIMessage(content=response.content)]
            return {"messages": new_messages, "iteration": state["iteration"] + 1}

        # Node: Critique and reflect
        def critique(state: State) -> dict:
            prompt = ChatPromptTemplate.from_template(
                "Critique the latest response for accuracy and completeness. If 'good', respond 'satisfactory'; else, provide feedback.\n\nResponse: {response}"
            )
            last_msg = state["messages"][-1].content
            chain = prompt | self.llm
            critique_response = chain.invoke({"response": last_msg})
            return {
                "feedback": critique_response.content,
                "iteration": state["iteration"],
            }

        graph.add_node("generate", generate)
        graph.add_node("critique", critique)

        graph.add_edge("generate", "critique")
        graph.add_conditional_edges(
            "critique",
            lambda state: (
                "generate"
                if "satisfactory" not in state.get("feedback", "").lower()
                and state["iteration"] < self.config["max_iterations"]
                else END
            ),
        )
        graph.set_entry_point("generate")
        return graph.compile()

    def fetch_url(self, url: str) -> str:
        return self.web_fetcher.fetch(url)

    async def ainvoke(self, context: str, messages: List[dict]):
        # Convert messages to LangChain format
        lc_messages = [
            (
                HumanMessage(content=m["content"])
                if m["role"] == "user"
                else AIMessage(content=m["content"])
            )
            for m in messages
        ]
        initial_state = {"messages": lc_messages, "context": context, "iteration": 0}
        async for event in self.graph.astream_events(initial_state, version="v2"):
            yield event
