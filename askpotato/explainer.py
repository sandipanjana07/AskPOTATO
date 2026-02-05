import requests
import json
import logging
from functools import lru_cache
from config import Config

logger = logging.getLogger(__name__)


@lru_cache(maxsize=100)
def _cached_ai_call(prompt_hash: str, prompt: str) -> str:
    """
    Cached wrapper for AI calls to avoid duplicate processing
    Note: This uses prompt hash as key since dicts aren't hashable
    """
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            Config.OLLAMA_URL,
            json=payload,
            timeout=Config.OLLAMA_TIMEOUT
        )

        if response.status_code != 200:
            logger.error(f"Ollama returned HTTP {response.status_code}")
            return f"AI error: HTTP {response.status_code}"

        result = response.json()
        return result.get("response", "AI returned no response.").strip()

    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out")
        return "AI is taking too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama")
        return "Cannot connect to AI service. Make sure Ollama is running."
    except Exception as e:
        logger.error(f"AI explanation error: {e}")
        return f"AI explanation failed: {str(e)}"


def explain_with_ai(question: str, intent: str, data) -> str:
    """
    Use Ollama to generate human-friendly explanation of the data
    This implements RAG (Retrieval Augmented Generation)
    
    Args:
        question: Original user question
        intent: Detected intent type
        data: Retrieved data from database
        
    Returns:
        AI-generated explanation
    """

    if not data:
        return "No relevant data found to explain."

    # build the prompt
    prompt = f"""
You are AskPOTATO, an internal QA assistant.

Rules:
- Explain ONLY using the provided data
- Do NOT invent facts
- Be concise and clear
- No greetings or sign-offs
- Use bullet points if listing multiple items

User question:
{question}

Intent:
{intent}

Data:
{json.dumps(data, indent=2)}

Answer:
"""

    # create hash of prompt for caching
    prompt_hash = str(hash(prompt))
    
    return _cached_ai_call(prompt_hash, prompt)
