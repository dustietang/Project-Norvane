# Norvane Cancel Culture Experiment

LLM agent-based experiment simulating cancel culture participation dynamics on a fictional social media platform.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

```bash
# Quick test (5 agents, 2 rounds, 1 run, 1 experiment) — ~15 API calls
python run_experiment.py --n_agents 5 --n_rounds 2 --n_runs 1 --experiment experiment_1

# Full pilot (50 agents, 5 rounds, 5 runs, all 4 experiments) — ~6,000 API calls
python run_experiment.py

# Run a single experiment with defaults
python run_experiment.py --experiment experiment_2

# Custom parameters
python run_experiment.py --n_agents 30 --n_rounds 5 --n_runs 3
```

## Experiment Design

| Experiment | Condition | Persona B type | Purpose |
|------------|-----------|---------------|---------|
| experiment_1 | Network | B (cancel norm) | Test network amplification of cancel culture |
| experiment_1a | Isolated | B (cancel norm) | Baseline for experiment_1 |
| experiment_2 | Network | B' (protest-skeptic) | Test if network pulls B' back into cancelling |
| experiment_2a | Isolated | B' (protest-skeptic) | Baseline for experiment_2 |

## Output Structure

```
results/
├── experiment_1/
│   ├── aggregate_summary.csv      # Mean/std across all runs
│   ├── run_0/
│   │   ├── decisions.csv          # Every agent's decision every round
│   │   ├── round_summaries.csv    # Per-round aggregate stats
│   │   ├── internalization_log.csv # Manipulation check responses
│   │   └── agent_logs/            # Full conversation history per agent
│   │       ├── agent_0.json
│   │       └── ...
│   ├── run_1/ ...
│   └── ...
├── experiment_1a/ ...
├── experiment_2/ ...
└── experiment_2a/ ...
```

## Key Output Files

- **aggregate_summary.csv**: The main results file. Mean and standard deviation of cancel culture participation rates per round, per persona type, across all independent runs.
- **decisions.csv**: Raw data. Every agent's action, stance, content, and reasoning for every round.
- **internalization_log.csv**: Manipulation check. Each agent's response to the persona internalization prompt.
- **agent_logs/**: Full LLM conversation histories for qualitative analysis.
