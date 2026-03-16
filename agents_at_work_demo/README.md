# Agents at Work Demo 1

This folder contains Demo 1: a CrewAI-powered strategic research swarm for live presentations.

The workflow researches a market, compares competitors, identifies positioning gaps, and writes an executive memo to `strategic_research_swarm_memo.md`.

## Run from this folder

```bash
uv sync
uv run run_crew --scenario saas_ops --product "OrbitFlow" --market "mid-market SaaS operations teams"
```

You can also run the module directly:

```bash
uv run python -m agents_at_work_demo.main --scenario saas_ops --product "OrbitFlow" --market "mid-market SaaS operations teams"
```

## Requirements

- Python 3.10 to 3.13
- Ollama running locally
- Ollama models:
  - `qwen3-vl:8b`
  - `nomic-embed-text:latest`

## Scenarios

Built-in scenarios:

- `saas_ops`
- `healthcare_ops`
- `higher_ed`
- `nonprofit`

Scenario files live in `knowledge/scenarios/`.

## Web search

Web search is optional and only activates when `SERPER_API_KEY` is available.

Example:

```bash
SERPER_API_KEY=your_key uv run run_crew --scenario healthcare_ops --product "OrbitFlow" --market "healthcare operations teams" --web-search on
```

PowerShell:

```powershell
$env:SERPER_API_KEY="your_key"
uv run run_crew --scenario healthcare_ops --product "OrbitFlow" --market "healthcare operations teams" --web-search on
```

## Troubleshooting

If Ollama is not running, or a required model is missing, the app stops early with a setup message.

To bypass startup checks:

```bash
uv run run_crew --skip-preflight
```

If `crewai run` fails with `ModuleNotFoundError`, run:

```bash
PYTHONPATH=src crewai run
```

PowerShell:

```powershell
$env:PYTHONPATH="src"
crewai run
```

## Output

- `strategic_research_swarm_memo.md`: final memo
- `crew_run.log`: execution log
