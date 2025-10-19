from utils import detect_urls, truncate_memory


def test_detect_urls():
    text = "Check https://example.com and http://test.org"
    urls = detect_urls(text)
    assert urls == ["https://example.com", "http://test.org"]


def test_truncate_memory():
    messages = [{"content": "a" * 1000}, {"content": "b" * 1000}]
    truncated = truncate_memory(messages, 100)  # Low limit
    assert len(truncated) < len(messages)
