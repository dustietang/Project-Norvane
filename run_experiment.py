
import argparse
import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import EXPERIMENTS, N_AGENTS, N_ROUNDS, N_RUNS, BASE_SEED
from src.simulation.experiment_runner import run_all_experiments


def main():
    parser = argparse.ArgumentParser(
        description="Norvane Cancel Culture LLM Agent Experiment"
    )
    parser.add_argument(
        "--experiment",
        type=str,
        default=None,
        choices=list(EXPERIMENTS.keys()),
        help="Run a specific experiment only. If not set, runs all 4.",
    )
    parser.add_argument(
        "--n_agents",
        type=int,
        default=N_AGENTS,
        help=f"Number of agents per experiment (default: {N_AGENTS})",
    )
    parser.add_argument(
        "--n_rounds",
        type=int,
        default=N_ROUNDS,
        help=f"Number of decision rounds (default: {N_ROUNDS})",
    )
    parser.add_argument(
        "--n_runs",
        type=int,
        default=N_RUNS,
        help=f"Independent runs per experiment (default: {N_RUNS})",
    )
    parser.add_argument(
        "--base_seed",
        type=int,
        default=BASE_SEED,
        help=f"Starting random seed (default: {BASE_SEED})",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Output directory for results (default: results/)",
    )

    args = parser.parse_args()

    # Select experiments to run
    if args.experiment:
        experiments = {args.experiment: EXPERIMENTS[args.experiment]}
    else:
        experiments = EXPERIMENTS

    # Estimate API calls
    total_calls = (
        args.n_agents * (1 + args.n_rounds)  # internalization + rounds
        * args.n_runs
        * len(experiments)
    )
    print(f"\nEstimated API calls: ~{total_calls}")
    print(f"(Could be higher with retries on failed JSON parsing)\n")

    run_all_experiments(
        experiments=experiments,
        n_agents=args.n_agents,
        n_rounds=args.n_rounds,
        n_runs=args.n_runs,
        base_seed=args.base_seed,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
