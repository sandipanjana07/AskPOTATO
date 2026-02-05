from .intents import INTENTS


def detect_intent(intent: str) -> str:
    """
    Validates if the normalized intent is in our supported list
    
    Args:
        intent: The normalized intent string from the normalizer
        
    Returns:
        The intent if valid, otherwise "UNKNOWN"
    """
    return intent if intent in INTENTS else "UNKNOWN"
