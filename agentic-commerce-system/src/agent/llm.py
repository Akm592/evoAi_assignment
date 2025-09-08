import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

def get_llm():
    """
    Configures and returns a ChatOpenAI instance for OpenRouter.
    """
    # Load environment variables from .env file
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL")
    model_name = os.getenv("OPENROUTER_MODEL_NAME")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables.")
    if not base_url:
        raise ValueError("OPENROUTER_BASE_URL not found in environment variables.")
    if not model_name:
        raise ValueError("OPENROUTER_MODEL_NAME not found in environment variables.")

    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0,  # Set to 0 for deterministic outputs
        streaming=True
    )