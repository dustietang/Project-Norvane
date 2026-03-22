import random
from typing import Dict, List

#Assign persona types to agents
def assign_personas(
    n_agents: int, #total number of agents
    persona_ratios: Dict[str, float],
    seed: int,
) -> List[str]:

    rng = random.Random(seed)

    persona_list = []
    remaining = n_agents

    # Sort persona types for deterministic ordering
    sorted_types = sorted(persona_ratios.keys())

    for i, persona_type in enumerate(sorted_types):
        if i == len(sorted_types) - 1:
            # Last type gets whatever remains (avoids rounding issues)
            count = remaining
        else:
            count = round(n_agents * persona_ratios[persona_type])
            remaining -= count
        persona_list.extend([persona_type] * count)

    # Shuffle so personas are not grouped by type
    rng.shuffle(persona_list)

    return persona_list
