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

## Setup
```bash
# Install dependencies
pip install -r requirements_openai.txt

# Set API key
export OPENAI_API_KEY="your-key-here"
```

## Running Experiments
```bash
# Quick test (5 agents)
python run_experiment.py --n_agents 5 --n_rounds 2 --n_runs 1 --experiment experiment_1

# Single experiment (50 agents)
python run_experiment.py --n_agents 50 --n_rounds 5 --n_runs 1 --experiment experiment_2

# Full experiment (all 4 experiments, 5 runs each)
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
│       └── llm_utils.py           # Open AI API wrapper with retry logic
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

```

## Model

All agents use **GPT-4.1** (`GPT-4.1`) via the Open AI API. Temperature is 0.6 for experiments run; 0.2 for internalization of personas. 

## Citation

Tang, Dustie. Project Norvane: LLM agent-based simulation for studying cancel culture participation.
https://github.com/dustietang/Project-Norvane

## Acknowledgements

The code structure of this project was inspired by the [LLM-SocioPol](https://github.com/CausalMP/LLM-SocioPol) framework by Shirani & Bayati (2025). No code was copied from the original repository.

> Shirani, S., & Bayati, M. (2025). Simulating and Experimenting with Social Media Mobilization Using LLM Agents. ArXiv.org. https://arxiv.org/abs/2510.26494
