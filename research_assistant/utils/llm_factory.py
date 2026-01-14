from langchain_ollama import ChatOllama

def get_llm():
    """
    Returns the configured LLM instance.
    Uses 'gemma:latest' by default as per requirements.
    """
    return ChatOllama(model="gemma:latest", temperature=0)
