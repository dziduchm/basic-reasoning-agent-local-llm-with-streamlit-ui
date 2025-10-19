from langchain_core.prompts import ChatPromptTemplate

# Prompt versioning: Dictionary with versions for the reasoned search prompt
SEARCH_PROMPTS = {
    "v1": ChatPromptTemplate.from_template(
        "Determine if a web search is needed based on the context. If yes, \
            generate a search query.\n\nContext: {context}"
    ),
    "v2": ChatPromptTemplate.from_template(
        "Based on the context, determine if a web search is needed. If yes,\
              generate a search query and perform it.\n\nContext: {context}"
    ),
}

# Default version (current)
DEFAULT_VERSION = "v2"
