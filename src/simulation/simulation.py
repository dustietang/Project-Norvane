# Core simulation loop, run one experiment
import random
import time
from typing import Dict, List

from config import (
    FEED_SAMPLE_SIZE,
    N_AGENTS,
    N_ROUNDS,
    SHUFFLE_AGENT_ORDER_EACH_ROUND,
)
from src.agents.agent import Agent
from src.agents.persona import assign_personas

# Build a Pulse-style feed
def build_feed_summary_for_agent(
    agent_id: int,
    previous_round_decisions: List[dict],
    rng: random.Random,
    sample_size: int = FEED_SAMPLE_SIZE,
) -> str:

    visible_decisions = [
        d for d in previous_round_decisions
        if d["agent_id"] != agent_id and d.get("action", 0) >= 1
    ]

    if not visible_decisions:
        return ""

    like_count = sum(1 for d in visible_decisions if d["action"] == 1)
    share_count = sum(1 for d in visible_decisions if d["action"] in (2, 4))
    comment_count = sum(1 for d in visible_decisions if d["action"] == 3)

    parts = []
    if like_count > 0:
        parts.append(f"{like_count} likes")
    if share_count > 0:
        parts.append(f"{share_count} shares")
    if comment_count > 0:
        parts.append(f"{comment_count} comments")

    if not parts:
        return ""

    feed = f"The post has {', '.join(parts)}.\n"

    content_actions = [
        d for d in visible_decisions
        if d["action"] in (3, 4, 5) and d.get("content", "").strip()
    ]

    if not content_actions:
        return feed

    min_examples = min(5, len(content_actions))
    max_examples = min(sample_size, len(content_actions))

    if max_examples <= 0:
        return feed

    if max_examples < min_examples:
        example_count = max_examples
    else:
        example_count = rng.randint(min_examples, max_examples)

    weights = [item["action"] for item in content_actions]

    sampled_actions = rng.choices(
        content_actions,
        weights=weights,
        k=example_count
    )

    action_labels = {
        3: "commented",
        4: "shared and wrote",
        5: "posted",
    }

    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"
    used_names = set()

    def make_username() -> str:
        while True:
            name = "@"
            name += rng.choice(consonants) + rng.choice(vowels)
            name += rng.choice(consonants) + rng.choice(vowels)
            name += str(rng.randint(10, 99))
            if name not in used_names:
                used_names.add(name)
                return name

    feed += "\nSome of what people are saying:\n"
    for item in sampled_actions:
        username = make_username()
        label = action_labels[item["action"]]
        feed += f'- {username} {label}: "{item["content"]}"\n'

    return feed


# Run a single experiment (one condition, one seed)
def run_single_experiment(
    persona_ratios: Dict[str, float],
    condition: str,
    n_agents: int = N_AGENTS,
    n_rounds: int = N_ROUNDS,
    seed: int = 42,
) -> Dict:
    rng = random.Random(seed)

    print(f"  Assigning {n_agents} agents with seed {seed}...")
    persona_list = assign_personas(n_agents, persona_ratios, seed)

    agents = [
        Agent(agent_id=i, persona_type=persona_type)
        for i, persona_type in enumerate(persona_list)
    ]

    print(f"  Running internalization phase for {n_agents} agents...")
    internalization_start = time.time()
    for agent in agents:
        agent.internalize()
    internalization_time = time.time() - internalization_start
    print(f"  Internalization completed in {internalization_time:.1f}s")

    all_decisions = []
    round_summaries = []
    previous_round_decisions: List[dict] = []

    for round_num in range(1, n_rounds + 1):
        round_start = time.time()
        print(f"  Round {round_num}/{n_rounds}...")

        agent_order = agents[:]
        if SHUFFLE_AGENT_ORDER_EACH_ROUND:
            rng.shuffle(agent_order)

        round_decisions = []
        for agent in agent_order:
            if condition == "network" and round_num > 1:
                feed_summary = build_feed_summary_for_agent(
                    agent_id=agent.agent_id,
                    previous_round_decisions=previous_round_decisions,
                    rng=rng,
                    sample_size=FEED_SAMPLE_SIZE,
                )
            else:
                feed_summary = ""

            decision = agent.decide_action(round_num, feed_summary)
            round_decisions.append(decision)

        round_decisions.sort(key=lambda d: d["agent_id"])

        previous_round_decisions = round_decisions[:]
        all_decisions.extend(round_decisions)

        summary = _compute_round_summary(round_decisions, round_num)
        round_summaries.append(summary)

        round_time = time.time() - round_start
        print(
            f"    Round {round_num} done in {round_time:.1f}s | "
            f"Participation: {summary['participation_rate']:.1%} | "
            f"Actions taken: {summary['total_actions']}/{n_agents}"
        )

    return {
        "agents": agents,
        "round_summaries": round_summaries,
        "all_decisions": all_decisions,
    }


# Compute aggregate statistics for a single round
def _compute_round_summary(decisions: List[dict], round_num: int) -> dict:
    total = len(decisions)

    # Mutually exclusive categories
    participants = [
        d for d in decisions
        if d["stance"] == "support" and d["action"] >= 1
    ]
    support_no_action = [
        d for d in decisions
        if d["stance"] == "support" and d["action"] == 0
    ]
    opposers = [
        d for d in decisions
        if d["stance"] == "oppose"
    ]
    neutrals = [
        d for d in decisions
        if d["stance"] == "neutral"
    ]

    participation_count = len(participants)
    support_no_action_count = len(support_no_action)
    opposition_count = len(opposers)
    neutral_count = len(neutrals)

    total_actions = sum(1 for d in decisions if d["action"] >= 1)

    persona_breakdown = {}
    persona_types = set(d["persona_type"] for d in decisions)

    for pt in persona_types:
        pt_decisions = [d for d in decisions if d["persona_type"] == pt]
        pt_total = len(pt_decisions)

        pt_participants = [
            d for d in pt_decisions
            if d["stance"] == "support" and d["action"] >= 1
        ]
        pt_support_no_action = [
            d for d in pt_decisions
            if d["stance"] == "support" and d["action"] == 0
        ]
        pt_opposers = [
            d for d in pt_decisions
            if d["stance"] == "oppose"
        ]
        pt_neutrals = [
            d for d in pt_decisions
            if d["stance"] == "neutral"
        ]

        persona_breakdown[pt] = {
            "total": pt_total,
            "participants": len(pt_participants),
            "participation_rate": len(pt_participants) / pt_total if pt_total else 0.0,

            "support_no_action": len(pt_support_no_action),
            "support_no_action_rate": len(pt_support_no_action) / pt_total if pt_total else 0.0,

            "opposers": len(pt_opposers),
            "opposition_rate": len(pt_opposers) / pt_total if pt_total else 0.0,

            "neutrals": len(pt_neutrals),
            "neutral_rate": len(pt_neutrals) / pt_total if pt_total else 0.0,
        }

    # Raw stance counts, separate from behavioral categories
    stance_counts = {
        "support": sum(1 for d in decisions if d["stance"] == "support"),
        "oppose": sum(1 for d in decisions if d["stance"] == "oppose"),
        "neutral": sum(1 for d in decisions if d["stance"] == "neutral"),
    }

    action_counts = {}
    for action_type in range(6):
        action_counts[action_type] = sum(
            1 for d in decisions if d["action"] == action_type
        )

    cobra_counts = {"consuming": 0, "contributing": 0, "creating": 0}
    for d in participants:
        if d["action"] == 1:
            cobra_counts["consuming"] += 1
        elif d["action"] in (2, 3):
            cobra_counts["contributing"] += 1
        elif d["action"] in (4, 5):
            cobra_counts["creating"] += 1

    return {
        "round": round_num,
        "total_agents": total,

        "participation_count": participation_count,
        "participation_rate": participation_count / total if total else 0.0,

        "support_no_action_count": support_no_action_count,
        "support_no_action_rate": support_no_action_count / total if total else 0.0,

        "opposition_count": opposition_count,
        "opposition_rate": opposition_count / total if total else 0.0,

        "neutral_count": neutral_count,
        "neutral_rate": neutral_count / total if total else 0.0,

        "total_actions": total_actions,
        "persona_breakdown": persona_breakdown,
        "stance_counts": stance_counts,
        "action_counts": action_counts,
        "cobra_counts": cobra_counts,
    }

#Run one experiment starting from a internalized agent population for both conditions
def run_single_experiment_with_agents(
    agents: List[Agent],
    condition: str,
    n_rounds: int = N_ROUNDS,
    seed: int = 42,
) -> Dict:

    rng = random.Random(seed)

    all_decisions = []
    round_summaries = []
    previous_round_decisions: List[dict] = []

    for round_num in range(1, n_rounds + 1):
        round_start = time.time()
        print(f"  Round {round_num}/{n_rounds}...")

        agent_order = agents[:]
        if SHUFFLE_AGENT_ORDER_EACH_ROUND:
            rng.shuffle(agent_order)

        round_decisions = []
        for agent in agent_order:
            if condition == "network" and round_num > 1:
                feed_summary = build_feed_summary_for_agent(
                    agent_id=agent.agent_id,
                    previous_round_decisions=previous_round_decisions,
                    rng=rng,
                    sample_size=FEED_SAMPLE_SIZE,
                )
            else:
                feed_summary = ""

            decision = agent.decide_action(round_num, feed_summary)
            round_decisions.append(decision)

        round_decisions.sort(key=lambda d: d["agent_id"])

        previous_round_decisions = round_decisions[:]
        all_decisions.extend(round_decisions)

        summary = _compute_round_summary(round_decisions, round_num)
        round_summaries.append(summary)

        round_time = time.time() - round_start
        print(
            f"    Round {round_num} done in {round_time:.1f}s | "
            f"Participation: {summary['participation_rate']:.1%} | "
            f"Actions taken: {summary['total_actions']}/{len(agents)}"
        )

    return {
        "agents": agents,
        "round_summaries": round_summaries,
        "all_decisions": all_decisions,
    }