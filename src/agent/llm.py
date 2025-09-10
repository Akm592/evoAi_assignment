import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

def get_llm():
    """
    Configures and returns a Chat model instance based on the provider
    specified in the environment variables.
    """
    load_dotenv()

    provider = os.getenv("LLM_PROVIDER", "openrouter").lower()

    if provider == "groq":
        print("--- Using Groq LLM ---")
        api_key = os.getenv("GROQ_API_KEY")
        model_name = os.getenv("GROQ_MODEL_NAME")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        if not model_name:
            raise ValueError("GROQ_MODEL_NAME not found in environment variables.")
        
        return ChatGroq(
            model_name=model_name,
            groq_api_key=api_key,
            temperature=0.0,  # Maximum determinism
            streaming=False,
            max_tokens=1000,  # Consistent output length limit
            
        )
    
    elif provider == "openrouter":
        print("--- Using OpenRouter LLM ---")
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
            temperature=0.0,  # Maximum determinism
            streaming=False,  # Disable streaming for more consistent outputs
            max_tokens=1000,  # Consistent output length limit
            seed=42  # Fixed seed for reproducibility where supported
        )
    
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}. Please use 'openrouter' or 'groq'.")
