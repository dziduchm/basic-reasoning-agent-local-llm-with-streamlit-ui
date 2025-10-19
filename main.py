import streamlit as st
import asyncio
from dotenv import load_dotenv
from agents.reflection_agent import ReflectionAgent
from utils import load_config, detect_urls, truncate_memory

# Load environment variables
load_dotenv()

# Load config
config = load_config()

# Initialize agent
agent = ReflectionAgent(config)

# Streamlit UI
st.title("Reflective Reasoning Agent")
st.sidebar.header("Settings")
clear_button = st.sidebar.button("Clear Conversation History")

if clear_button:
    st.session_state.messages = []
    st.success("History cleared!")

# Initialize memory in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Enter your message (include URLs if needed)...")

if user_input:
    # Append user message to memory
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Detect and fetch URLs if present
    urls = detect_urls(user_input)
    context = user_input
    if urls:
        st.info("Fetching URL content...")
        for url in urls:
            try:
                fetched = agent.fetch_url(url)
                context += f"\n\nFetched from {url}:\n{fetched}"
            except Exception as e:
                st.error(f"Error fetching {url}: {str(e)}")

    # Truncate memory if needed
    st.session_state.messages = truncate_memory(
        st.session_state.messages, config["max_tokens"]
    )

    # Invoke agent with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = [""]  # Use a list to make it mutable across scopes

        async def run_agent():
            async for event in agent.ainvoke(
                context, st.session_state.messages
            ):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    full_response[0] += chunk
                    response_placeholder.markdown(full_response[0] + "▌")

        asyncio.run(run_agent())
        response_placeholder.markdown(full_response[0])

    # Append assistant response to memory
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response[0]}
    )
