import yaml
import re
import os
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache
from typing import List

# Optional caching
set_llm_cache(InMemoryCache())


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


def detect_urls(text: str) -> List[str]:
    url_pattern = r"https?://\S+"
    return re.findall(url_pattern, text)


def get_llm(config):
    model_type = config["model_type"]
    if model_type == "grok":
        return ChatXAI(
            api_key=os.getenv(config["api_key_var"]),
            model=config["model_name"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
        )
    elif model_type == "local":
        return ChatOpenAI(
            base_url=config["endpoint"],
            api_key="lm-studio",  # Dummy for local
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
        )
    else:
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
        )


def truncate_memory(messages: List[dict], max_tokens: int) -> List[dict]:
    # Simple truncation: estimate tokens (rough 4 chars per token)
    total_chars = sum(len(m["content"]) for m in messages)
    if total_chars > max_tokens * 4:
        # Keep last 50% of messages
        mid = len(messages) // 2
        return messages[mid:]
    return messages


def stream_response(response):
    # Placeholder for any post-processing; actual streaming handled in main.py
    pass
