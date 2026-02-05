import requests
import re
import logging
from config import Config

logger = logging.getLogger(__name__)

# Valid intents we can normalize to
VALID_INTENTS = {
    "LIST_SCENARIOS",
    "MOST_DEFECTS_SCENARIO",
    "OPEN_DEFECTS",
    "FAILED_STEPS",
    "NO_PROOF_STEPS",
}


def normalize_question(question: str) -> str:
    """
    Uses Ollama to convert natural language into a structured intent key
    
    Args:
        question: User's natural language question
        
    Returns:
        Normalized intent key or "UNKNOWN" if can't determine
    """
    
    prompt = f"""
Normalize the user question into EXACTLY ONE of the following intent KEYS:

- LIST_SCENARIOS
- MOST_DEFECTS_SCENARIO
- OPEN_DEFECTS
- FAILED_STEPS
- NO_PROOF_STEPS

Rules:
- Output ONLY the intent key
- No punctuation
- No explanation
- If unsure, output UNKNOWN

User question:
{question}

Output:
""".strip()

    try:
        response = requests.post(
            Config.OLLAMA_URL,
            json={
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=Config.OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()

        raw = result.get("response", "")

        # sanitize the response - remove everything except letters and underscores
        intent = raw.strip().upper()
        intent = re.sub(r"[^A-Z_]", "", intent)

        # validate it's in our list
        if intent in VALID_INTENTS:
            logger.info(f"Normalized '{question}' to '{intent}'")
            return intent
        else:
            logger.warning(f"Unknown intent extracted: {intent}")
            return "UNKNOWN"

    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out")
        return "UNKNOWN"
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to Ollama - is it running?")
        return "UNKNOWN"
    except Exception as e:
        logger.error(f"Normalizer error: {e}")
        return "UNKNOWN"
