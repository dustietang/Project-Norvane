# Configuration parameters for the Norvane cancel culture experiment.

# LLM Settings
LLM_MODEL = "gpt-4.1"
LLM_TEMPERATURE = 0.6
LLM_INTERNALIZATION_TEMPERATURE = 0.6
LLM_DECISION_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1024

# Experiment Parameters
N_AGENTS = 50
N_ROUNDS = 5
N_RUNS = 5
BASE_SEED = 42
SHUFFLE_AGENT_ORDER_EACH_ROUND = True

# Network Feed Parameters
FEED_SAMPLE_SIZE = 10
VISIBILITY_WEIGHTS = {
    0: 0,  # no action
    1: 1,  # like
    2: 2,  # share
    3: 2,  # comment
    4: 3,  # share with caption
    5: 4,  # original post
}

# Persona Distribution Ratios
PERSONA_RATIOS = {
    "A": 0.15,
    "B": 0.70,
    "C": 0.15,
}

PERSONA_RATIOS_PROTEST = {
    "A": 0.15,
    "B_prime": 0.70,
    "C": 0.15,
}


# Experiment Definitions
EXPERIMENTS = {
    "experiment_1": {
        "description": "Cancel culture norm - Network Condition",
        "condition": "network",
        "persona_ratios": PERSONA_RATIOS,
    },
    "experiment_1a": {
        "description": "Cancel culture norm - Isolated Condition (baseline)",
        "condition": "isolated",
        "persona_ratios": PERSONA_RATIOS,
    },
    "experiment_2": {
        "description": "Increased protest memory - Network Condition",
        "condition": "network",
        "persona_ratios": PERSONA_RATIOS_PROTEST,
    },
    "experiment_2a": {
        "description": "Increased protest memory - Isolated Condition (baseline)",
        "condition": "isolated",
        "persona_ratios": PERSONA_RATIOS_PROTEST,
    },
}

# Action Types
ACTION_TYPES = {
    0: "No action taken",
    1: "Like the post",
    2: "Share the post to network",
    3: "Comment on the post",
    4: "Share the post with caption",
    5: "Publish an original post",
}

VALID_STANCES = ["support", "oppose", "neutral"]

# COBRA Classification
COBRA_TIERS = {
    "consuming": [1],
    "contributing": [2, 3],
    "creating": [4, 5],
}
