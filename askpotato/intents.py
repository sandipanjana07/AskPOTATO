# Supported question intents with example phrasings
INTENTS = {
    "LIST_SCENARIOS": {
        "description": "List all test scenarios",
        "examples": [
            "list scenarios",
            "show scenarios", 
            "what scenarios are there",
            "all scenarios",
            "show me all scenarios"
        ]
    },
    "MOST_DEFECTS_SCENARIO": {
        "description": "Find scenario with most defects",
        "examples": [
            "most defects",
            "scenario with most defects",
            "which scenario is worst",
            "most buggy scenario",
            "highest defect count"
        ]
    },
    "OPEN_DEFECTS": {
        "description": "List all open/unresolved defects",
        "examples": [
            "open defects",
            "show open bugs",
            "pending defects",
            "unresolved issues"
        ]
    },
    "FAILED_STEPS": {
        "description": "Find all failed test steps",
        "examples": [
            "failed steps",
            "failing steps",
            "steps that failed",
            "which steps are failing"
        ]
    },
    "NO_PROOF_STEPS": {
        "description": "Find steps missing proof uploads",
        "examples": [
            "no proof",
            "steps without proof",
            "missing proof",
            "steps need evidence"
        ]
    }
}
