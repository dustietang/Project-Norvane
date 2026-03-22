# Project Norvane - LLM Agents Simulation on Cancel Culture

This codebase is the second part of my undergraduate final year research project. 
The first part of the paper aims to answer why cancel culture based on perceived political incorrectness is observed in certain liberal democracies but not others. Second part of the paper aims to answer why cancel culture is relatively sticky in society, despite increase in mobilisation options for the electrorates. 

The second part of the paper utilised LLM agent-based simulation examining the effect of social network visibility on cancel culture participation among citizens of liberal democracies.

This project simulates a fictional liberal democracy (Norvane) where LLM-powered agents with distinct personas interact on a social media platform (Pulse) after a public figure makes discriminatory statements towards a fictional minority group (Veltari). The experiment tests whether observing others' responses on social media pulls initially skeptical citizens back into cancel culture participation.
 
## Paper
[WIP at the moment]

## Experiment Design

The population of Norvane consists of three persona types:
- **Persona A (Political Apath)** — Control group. Does not participate in any political mobilisation.
- **Persona B (Regular Citizen)** — Believes calling out public figures is morally right. Used to cancel culture norms.
- **Persona B' (Protest-Skeptic)** — Former cancel culture participant who became skeptical after witnessing successful offline mass protests.
- **Persona C (Political Zealot)** — Always participates in calling out. Sees it as moral duty.

Four experiments compare network vs isolated conditions:

| Experiment | Condition | Persona B type | Purpose |
|------------|-----------|---------------|---------|
| Experiment 1 | Network | B (cancel norm) | Test network effect on committed participants |
| Experiment 1A | Isolated | B (cancel norm) | Baseline for Experiment 1 |
| Experiment 2 | Network | B' (protest-skeptic) | Test if network pulls B' back into cancelling |
| Experiment 2A | Isolated | B' (protest-skeptic) | Baseline for Experiment 2 |

Each experiment runs with 50 agents, 5 rounds, and 5 independent runs. Population ratio: 15% Persona A, 70% Persona B/B', 15% Persona C.

LLM Model used is GPT-4.1
## Setup
```bash
# Install dependencies
pip install -r requirements_openai.txt

# Set API key
export OPENAI_API_KEY="your-key-here"
```

## Running Experiments
```bash
# Quick test (5 agents, ~15 API calls, ~2 min)
python run_experiment.py --n_agents 5 --n_rounds 2 --n_runs 1 --experiment experiment_1

# Single experiment (50 agents, ~300 API calls, ~20 min)
python run_experiment.py --n_agents 50 --n_rounds 5 --n_runs 1 --experiment experiment_2

# Full experiment (all 4 experiments, 5 runs each, ~6,000 API calls, ~6 hours)
caffeinate -i python run_experiment.py --n_agents 50 --n_rounds 5 --n_runs 5
```

## Project Structure
```
├── run_experiment.py              # Entry point — CLI to run experiments
├── config.py                      # All experiment parameters
├── src/
│   ├── agents/
│   │   ├── agent.py               # Agent class — LLM-driven decision making
│   │   └── persona.py             # Persona assignment by ratio
│   ├── incidents/
│   │   └── incident.py            # Norvane context, persona descriptions, prompts
│   ├── simulation/
│   │   ├── simulation.py          # Core round loop and feed construction
│   │   └── experiment_runner.py   # Orchestrates experiments × runs, saves outputs
│   └── utils/
│       └── llm_utils.py           # Anthropic Claude API wrapper with retry logic
├── results/                       # Experiment output data
│   ├── all_round_data_long.csv    # Combined data across all experiments and runs
│   ├── experiment_1/
│   │   ├── aggregate_summary.csv  # Mean ± SD across runs
│   │   ├── run_1/
│   │   │   ├── decisions.csv      # Every agent's action, stance, content, reasoning
│   │   │   ├── round_summaries.csv
│   │   │   └── internalization_log.csv
│   │   └── ...
│   ├── experiment_1a/ ...
│   ├── experiment_2/ ...
│   └── experiment_2a/ ...
└── figures/                       # Generated figures (not in repo — regenerate locally)
```

## Analysis Scripts

Analysis scripts are not included in this repository but can be provided on request. They include:
- `generate_figures.py` — Publication-quality figures (participation rates, heatmaps, COBRA charts)
- `statistical_tests.py` — T-tests and Cohen's d for condition comparisons
- `content_analysis.py` — Theme analysis of agent-generated content
- `reasoning_analysis_all.py` — Theme analysis of agent reasoning

## Key Results

- **Persona validation**: Persona A = 0% participation (all rounds), Persona C ≈ 100% (early rounds), confirming control and zealot behavior.
- **B' holdback**: 0% participation in round 1 across both conditions, confirming protest memory persona.
- **Network effect on B'**: Participation jumped from 0% to 100% in round 2 (network) vs 61% (isolated), t(4) = 12.12, p < .001, d = 7.66.
- **Bystander effect on B**: Network B agents participated less than isolated B agents in rounds 3–4 (p < .01), suggesting seeing others act reduced individual engagement.
- **Engagement intensity**: Network B' agents chose higher COBRA tiers (contributing, creating) while isolated B' agents predominantly liked (consuming).

## Model

All agents use **Claude Sonnet 4.6** (`claude-sonnet-4-6`) via the Anthropic API. Temperature = 0.7.

## Citation
```
[Citation when available]
```
