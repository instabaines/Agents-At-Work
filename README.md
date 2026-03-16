# Agents at Work: Accelerating & Innovating Business Processes
### NSBE 2026 Workshop Masterclass

Welcome to the **Agents at Work** repository. This workshop is designed to move beyond simple prompting and into **agentic orchestration**: using AI as a digital workforce that can reason across steps, collaborate across roles, and support real business workflows.

---

## Workshop Overview

In this session, we explore the architecture, ethics, and implementation of AI agents through practical demos.

- **The Shift:** Moving from rigid automation and scripts to adaptive reasoning systems.
- **The Tools:** Hands-on work with multi-agent workflows built with CrewAI.
- **The Goal:** Show how agent-based systems can support business process innovation in realistic scenarios.

---

## Getting Started

This repository contains two live demos. Each demo is self-contained and should be run from its own folder.

### Demo 1: Strategic Research Swarm
Location: `agents_at_work_demo/`

```bash
cd agents_at_work_demo
uv sync
uv run run_crew --scenario saas_ops --product "OrbitFlow" --market "mid-market SaaS operations teams"
```

### Demo 2: Customer Support Triage Agent
Location: `agents_at_work_demo2/customer_support/`

```bash
cd agents_at_work_demo2/customer_support
uv sync
uv run run_crew --preset billing_lockout
```

If `crewai run` fails with `ModuleNotFoundError`, run from the relevant demo folder with:

```bash
PYTHONPATH=src crewai run
```

---

## Project Structure

- `agents_at_work_demo/`: Demo 1 source code, knowledge files, and tests
- `agents_at_work_demo2/customer_support/`: Demo 2 source code, knowledge files, and tests
- `README.md`: repository-level overview and entrypoint guide

---

## Demo Guide

### Demo 1: Strategic Research Swarm

This demo simulates a multi-agent market intelligence workflow.

- Researches a target market using local knowledge and optional web search
- Supports multiple scenarios such as `saas_ops`, `healthcare_ops`, `higher_ed`, and `nonprofit`
- Produces an executive memo in `strategic_research_swarm_memo.md`

### Demo 2: Customer Support Triage Agent

This demo simulates a high-volume support triage workflow.

- Uses four agents: Classifier, Priority, Routing, and Supervisor
- Includes canned presets for realistic support incidents
- Produces a triage report in `customer_support_triage_report.md`

---

## Requirements

- Python 3.10 to 3.13
- `uv`
- Ollama running locally
- Ollama model `qwen3-vl:8b`

Additional demo-specific requirements:

- Demo 1 also uses `nomic-embed-text:latest`
- Demo 1 web search is optional and only activates when `SERPER_API_KEY` is set
- Demo 2 uses `crewai[tools,litellm]` so CrewAI can call the local Ollama model

See each demo README for setup details, scenario options, presets, and troubleshooting.

---

## Feedback & Connection

Your feedback helps improve this session for the next generation of engineers.

-> **[Complete the 1-Minute Feedback Form](https://forms.gle/D5UpxZU8BhpdhRsR9)**

Feel free to connect with me on **[LinkedIn](https://linkedin.com/in/ridwan-amure)** to discuss AI agents, business process innovation, career pivots, or collaboration.

---



