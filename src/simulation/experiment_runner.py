# Experiment Orchestrator
import csv
import json
import os
import time
from copy import deepcopy
from datetime import datetime,timedelta
from pathlib import Path
from typing import Dict, List

from config import BASE_SEED, EXPERIMENTS, N_AGENTS, N_ROUNDS, N_RUNS
from src.agents.agent import Agent
from src.agents.persona import assign_personas
from src.simulation.simulation import run_single_experiment_with_agents


def format_time(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))

def create_run_output_dir(base_output_dir: str = "results") -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_output_dir = Path(base_output_dir) / timestamp
    run_output_dir.mkdir(parents=True, exist_ok=True)
    return run_output_dir

def _persona_signature(persona_ratios: Dict[str, float]) -> str:
    return json.dumps(persona_ratios, sort_keys=True)

#Paired experiments with same persona distribution
def _group_experiments_by_population(experiments: Dict) -> Dict[str, List[tuple]]:

    grouped: Dict[str, List[tuple]] = {}
    for exp_name, exp_config in experiments.items():
        sig = _persona_signature(exp_config["persona_ratios"])
        grouped.setdefault(sig, []).append((exp_name, exp_config))
    return grouped


def _create_internalized_agents(
    persona_ratios: Dict[str, float],
    n_agents: int,
    seed: int,
) -> List[Agent]:
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

    return agents


# Save each agent's decision
def save_decisions_csv(decisions: List[dict], filepath: str):
    if not decisions:
        return

    fieldnames = [
        "agent_id",
        "persona_type",
        "round",
        "action",
        "stance",
        "content",
        "reasoning",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(decisions)


# Save per-round summary statistics
def save_round_summaries_csv(summaries: List[dict], filepath: str):
    rows = []
    for s in summaries:
        row = {
            "round": s["round"],
            "total_agents": s["total_agents"],

            "participation_count": s["participation_count"],
            "participation_rate": f"{s['participation_rate']:.4f}",

            "support_no_action_count": s["support_no_action_count"],
            "support_no_action_rate": f"{s['support_no_action_rate']:.4f}",

            "opposition_count": s["opposition_count"],
            "opposition_rate": f"{s['opposition_rate']:.4f}",

            "neutral_count": s["neutral_count"],
            "neutral_rate": f"{s['neutral_rate']:.4f}",

            "total_actions": s["total_actions"],
        }

        for pt, info in s["persona_breakdown"].items():
            row[f"persona_{pt}_total"] = info["total"]

            row[f"persona_{pt}_participants"] = info["participants"]
            row[f"persona_{pt}_participation_rate"] = f"{info['participation_rate']:.4f}"

            row[f"persona_{pt}_support_no_action"] = info["support_no_action"]
            row[f"persona_{pt}_support_no_action_rate"] = f"{info['support_no_action_rate']:.4f}"

            row[f"persona_{pt}_opposers"] = info["opposers"]
            row[f"persona_{pt}_opposition_rate"] = f"{info['opposition_rate']:.4f}"

            row[f"persona_{pt}_neutrals"] = info["neutrals"]
            row[f"persona_{pt}_neutral_rate"] = f"{info['neutral_rate']:.4f}"

        for stance, count in s["stance_counts"].items():
            row[f"stance_{stance}"] = count

        for action_type, count in s["action_counts"].items():
            row[f"action_{action_type}"] = count

        for tier, count in s["cobra_counts"].items():
            row[f"cobra_{tier}"] = count

        rows.append(row)

    if not rows:
        return

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

# Save each agent's internalization response
def save_internalization_log(agents, filepath: str):
    rows = []
    for agent in agents:
        rows.append(
            {
                "agent_id": agent.agent_id,
                "persona_type": agent.persona_type,
                "internalization_response": agent.internalization_response,
            }
        )

    if not rows:
        return

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


# Save the whole conversation history for each agent
def save_conversation_logs(agents, dirpath: str):
    os.makedirs(dirpath, exist_ok=True)
    for agent in agents:
        filepath = os.path.join(dirpath, f"agent_{agent.agent_id}.json")
        log = {
            "agent_id": agent.agent_id,
            "persona_type": agent.persona_type,
            "conversation_history": agent.conversation_history,
            "action_history": agent.action_history,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

#Save one long-format CSV with all experiments and runs
def save_long_format_round_data(
    experiment_name: str,
    run_idx: int,
    round_summaries: List[dict],
    filepath: str,
):
    rows = []

    for s in round_summaries:
        rows.append(
            {
                "experiment": experiment_name,
                "run": run_idx,
                "round": s["round"],
                "persona": "ALL",

                "participation_rate": f"{s['participation_rate']:.4f}",
                "support_no_action_rate": f"{s['support_no_action_rate']:.4f}",
                "opposition_rate": f"{s['opposition_rate']:.4f}",
                "neutral_rate": f"{s['neutral_rate']:.4f}",

                "participation_count": s["participation_count"],
                "support_no_action_count": s["support_no_action_count"],
                "opposition_count": s["opposition_count"],
                "neutral_count": s["neutral_count"],

                "total_agents": s["total_agents"],
            }
        )

        for pt, info in s["persona_breakdown"].items():
            rows.append(
                {
                    "experiment": experiment_name,
                    "run": run_idx,
                    "round": s["round"],
                    "persona": pt,

                    "participation_rate": f"{info['participation_rate']:.4f}",
                    "support_no_action_rate": f"{info['support_no_action_rate']:.4f}",
                    "opposition_rate": f"{info['opposition_rate']:.4f}",
                    "neutral_rate": f"{info['neutral_rate']:.4f}",

                    "participation_count": info["participants"],
                    "support_no_action_count": info["support_no_action"],
                    "opposition_count": info["opposers"],
                    "neutral_count": info["neutrals"],

                    "total_agents": info["total"],
                }
            )

    if not rows:
        return

    file_exists = os.path.exists(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "experiment",
                "run",
                "round",
                "persona",
                "participation_rate",
                "support_no_action_rate",
                "opposition_rate",
                "neutral_rate",
                "participation_count",
                "support_no_action_count",
                "opposition_count",
                "neutral_count",
                "total_agents",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# Compute aggregate statistics across all runs, per round
def compute_aggregate_summary(all_run_summaries: List[List[dict]]) -> List[dict]:
    if not all_run_summaries:
        return []

    import statistics

    n_rounds = len(all_run_summaries[0])
    aggregate = []

    for round_idx in range(n_rounds):
        round_num = round_idx + 1

        overall_participation_rates = []
        overall_support_no_action_rates = []
        overall_opposition_rates = []
        overall_neutral_rates = []

        persona_participation_rates: Dict[str, list] = {}
        persona_support_no_action_rates: Dict[str, list] = {}
        persona_opposition_rates: Dict[str, list] = {}
        persona_neutral_rates: Dict[str, list] = {}

        for run_summaries in all_run_summaries:
            s = run_summaries[round_idx]

            overall_participation_rates.append(s["participation_rate"])
            overall_support_no_action_rates.append(s["support_no_action_rate"])
            overall_opposition_rates.append(s["opposition_rate"])
            overall_neutral_rates.append(s["neutral_rate"])

            for pt, info in s["persona_breakdown"].items():
                if pt not in persona_participation_rates:
                    persona_participation_rates[pt] = []
                    persona_support_no_action_rates[pt] = []
                    persona_opposition_rates[pt] = []
                    persona_neutral_rates[pt] = []

                persona_participation_rates[pt].append(info["participation_rate"])
                persona_support_no_action_rates[pt].append(info["support_no_action_rate"])
                persona_opposition_rates[pt].append(info["opposition_rate"])
                persona_neutral_rates[pt].append(info["neutral_rate"])

        row = {
            "round": round_num,

            "mean_participation_rate": statistics.mean(overall_participation_rates),
            "std_participation_rate": (
                statistics.stdev(overall_participation_rates)
                if len(overall_participation_rates) > 1
                else 0.0
            ),

            "mean_support_no_action_rate": statistics.mean(overall_support_no_action_rates),
            "std_support_no_action_rate": (
                statistics.stdev(overall_support_no_action_rates)
                if len(overall_support_no_action_rates) > 1
                else 0.0
            ),

            "mean_opposition_rate": statistics.mean(overall_opposition_rates),
            "std_opposition_rate": (
                statistics.stdev(overall_opposition_rates)
                if len(overall_opposition_rates) > 1
                else 0.0
            ),

            "mean_neutral_rate": statistics.mean(overall_neutral_rates),
            "std_neutral_rate": (
                statistics.stdev(overall_neutral_rates)
                if len(overall_neutral_rates) > 1
                else 0.0
            ),
        }

        for pt in sorted(persona_participation_rates.keys()):
            p_rates = persona_participation_rates[pt]
            s_rates = persona_support_no_action_rates[pt]
            o_rates = persona_opposition_rates[pt]
            n_rates = persona_neutral_rates[pt]

            row[f"mean_persona_{pt}_participation_rate"] = statistics.mean(p_rates)
            row[f"std_persona_{pt}_participation_rate"] = (
                statistics.stdev(p_rates) if len(p_rates) > 1 else 0.0
            )

            row[f"mean_persona_{pt}_support_no_action_rate"] = statistics.mean(s_rates)
            row[f"std_persona_{pt}_support_no_action_rate"] = (
                statistics.stdev(s_rates) if len(s_rates) > 1 else 0.0
            )

            row[f"mean_persona_{pt}_opposition_rate"] = statistics.mean(o_rates)
            row[f"std_persona_{pt}_opposition_rate"] = (
                statistics.stdev(o_rates) if len(o_rates) > 1 else 0.0
            )

            row[f"mean_persona_{pt}_neutral_rate"] = statistics.mean(n_rates)
            row[f"std_persona_{pt}_neutral_rate"] = (
                statistics.stdev(n_rates) if len(n_rates) > 1 else 0.0
            )

        aggregate.append(row)

    return aggregate


def save_aggregate_csv(aggregate: List[dict], filepath: str):
    if not aggregate:
        return

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(aggregate[0].keys()))
        writer.writeheader()
        writer.writerows(
            {
                k: f"{v:.4f}" if isinstance(v, float) else v
                for k, v in row.items()
            }
            for row in aggregate
        )

def run_all_experiments(
    experiments: Dict = None,
    n_agents: int = N_AGENTS,
    n_rounds: int = N_ROUNDS,
    n_runs: int = N_RUNS,
    base_seed: int = BASE_SEED,
    output_dir: str = "results",
):
    if experiments is None:
        experiments = EXPERIMENTS

    # Create a fresh folder for this whole execution
    output_root = create_run_output_dir(output_dir)

    grouped_experiments = _group_experiments_by_population(experiments)
    total_start = time.time()

    print("=" * 60)
    print("NORVANE CANCEL CULTURE EXPERIMENT")
    print(f"Agents: {n_agents} | Rounds: {n_rounds} | Runs: {n_runs}")
    print(f"Experiments: {list(experiments.keys())}")
    print(f"Saving results to: {output_root}")
    print("=" * 60)

    # Master file for this execution only
    long_format_path = output_root / "all_round_data_long.csv"

    experiment_summaries: Dict[str, List[List[dict]]] = {}
    experiment_configs: Dict[str, dict] = {}

    for exp_name, exp_config in experiments.items():
        exp_dir = output_root / exp_name
        exp_dir.mkdir(parents=True, exist_ok=True)
        experiment_summaries[exp_name] = []
        experiment_configs[exp_name] = exp_config

    for run_idx in range(n_runs):
        run_seed = base_seed + run_idx
        run_start = time.time()

        print(f"\n{'=' * 60}")
        print(f"GLOBAL RUN {run_idx + 1}/{n_runs} (seed={run_seed})")
        print(f"{'=' * 60}")

        for family_signature, family_experiments in grouped_experiments.items():
            representative_name, representative_config = family_experiments[0]

            print(f"\n--- Building shared base population for family: {representative_name} ---")
            base_agents = _create_internalized_agents(
                persona_ratios=representative_config["persona_ratios"],
                n_agents=n_agents,
                seed=run_seed,
            )

            for exp_name, exp_config in family_experiments:
                exp_cond = exp_config["condition"]

                print(f"\nRunning {exp_name} | condition={exp_cond}")

                exp_dir = output_root / exp_name
                run_dir = exp_dir / f"run_{run_idx + 1}"
                run_dir.mkdir(parents=True, exist_ok=True)

                agents_for_condition = deepcopy(base_agents)

                result = run_single_experiment_with_agents(
                    agents=agents_for_condition,
                    condition=exp_cond,
                    n_rounds=n_rounds,
                    seed=run_seed,
                )

                save_decisions_csv(
                    result["all_decisions"],
                    str(run_dir / "decisions.csv"),
                )
                save_round_summaries_csv(
                    result["round_summaries"],
                    str(run_dir / "round_summaries.csv"),
                )
                save_internalization_log(
                    result["agents"],
                    str(run_dir / "internalization_log.csv"),
                )
                save_conversation_logs(
                    result["agents"],
                    str(run_dir / "agent_logs"),
                )

                save_long_format_round_data(
                    experiment_name=exp_name,
                    run_idx=run_idx + 1,
                    round_summaries=result["round_summaries"],
                    filepath=str(long_format_path),
                )

                experiment_summaries[exp_name].append(result["round_summaries"])

        run_time = time.time() - run_start
        print(f"\nGlobal run {run_idx + 1} completed in {format_time(run_time)}")

    for exp_name, all_run_summaries in experiment_summaries.items():
        exp_config = experiment_configs[exp_name]
        exp_dir = output_root / exp_name

        aggregate = compute_aggregate_summary(all_run_summaries)
        save_aggregate_csv(aggregate, str(exp_dir / "aggregate_summary.csv"))

        print(f"\n{'=' * 60}")
        print(f"EXPERIMENT: {exp_name}")
        print(f"Description: {exp_config['description']}")
        print(f"Condition: {exp_config['condition']}")
        print(f"{'=' * 60}")

        for row in aggregate:
            print(
                f"  Round {row['round']}: "
                f"participation = {row['mean_participation_rate']:.1%} "
                f"(±{row['std_participation_rate']:.1%}) | "
                f"support_no_action = {row['mean_support_no_action_rate']:.1%} "
                f"(±{row['std_support_no_action_rate']:.1%}) | "
                f"opposition = {row['mean_opposition_rate']:.1%} "
                f"(±{row['std_opposition_rate']:.1%}) | "
                f"neutral = {row['mean_neutral_rate']:.1%} "
                f"(±{row['std_neutral_rate']:.1%})"
            )

            for key, val in row.items():
                if key.startswith("mean_persona_") and key.endswith("_participation_rate"):
                    pt = key.replace("mean_persona_", "").replace("_participation_rate", "")

                    p_std_key = f"std_persona_{pt}_participation_rate"

                    s_key = f"mean_persona_{pt}_support_no_action_rate"
                    s_std_key = f"std_persona_{pt}_support_no_action_rate"

                    o_key = f"mean_persona_{pt}_opposition_rate"
                    o_std_key = f"std_persona_{pt}_opposition_rate"

                    n_key = f"mean_persona_{pt}_neutral_rate"
                    n_std_key = f"std_persona_{pt}_neutral_rate"

                    print(
                        f"    Persona {pt}: "
                        f"participation {val:.1%} (±{row.get(p_std_key, 0):.1%}) | "
                        f"support_no_action {row.get(s_key, 0):.1%} (±{row.get(s_std_key, 0):.1%}) | "
                        f"opposition {row.get(o_key, 0):.1%} (±{row.get(o_std_key, 0):.1%}) | "
                        f"neutral {row.get(n_key, 0):.1%} (±{row.get(n_std_key, 0):.1%})"
                    )

    total_time = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"ALL EXPERIMENTS COMPLETED in {format_time(total_time)}")
    print(f"Results saved to: {output_root}/")
    print(f"{'=' * 60}")

