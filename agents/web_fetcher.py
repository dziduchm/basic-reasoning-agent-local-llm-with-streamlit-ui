import requests
from langchain_community.document_loaders import WebBaseLoader


class FetchError(Exception):
    pass


class WebFetcher:
    def __init__(self, max_content_size=10240):  # 10KB limit
        self.max_content_size = max_content_size

    def fetch(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            raise FetchError("Invalid URL")
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            content = docs[0].page_content if docs else ""
            if len(content) > self.max_content_size:
                content = content[: self.max_content_size] + "... (truncated)"
            return content
        except requests.exceptions.Timeout:
            raise FetchError("Request timed out")
        except Exception as e:
            raise FetchError(f"Fetch failed: {str(e)}")
