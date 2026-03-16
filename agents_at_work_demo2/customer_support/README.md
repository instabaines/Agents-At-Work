# Customer Support Triage Demo

This folder contains Demo 2: a customer support triage swarm built with CrewAI.

It simulates a company receiving a high volume of customer messages and uses four agents to process each message:

- `Classifier Agent`: categorizes the issue as Billing, Bug, Account, or Other
- `Priority Agent`: assigns urgency as Low, Medium, or High
- `Routing Agent`: decides which team should handle the issue
- `Supervisor Agent`: flags risky or ambiguous cases and produces the final triage card

## Run from this folder

```bash
uv sync
uv run run_crew --preset billing_lockout
```

Run with fully custom inputs:

```bash
uv run run_crew --customer-name "Northstar Health" --customer-tier enterprise --channel email --message "Our finance team cannot access invoices after yesterday's login policy change."
```

List all canned presets:

```bash
uv run run_crew --list-presets
```

## Requirements

- Python 3.10 to 3.13
- Ollama running locally
- Ollama model `qwen3-vl:8b`

This demo uses `crewai[tools,litellm]` so CrewAI can call the local Ollama model.

## Presets

Available canned presets:

- `billing_lockout`
- `sso_failure`
- `integration_outage`
- `double_charge`
- `unclear_request`
- `refund_escalation`
- `api_regression`

Recommended on-stage examples:

- `billing_lockout`: easy to understand, clearly urgent, usually routes to Billing Operations
- `sso_failure`: high-visibility account-access issue that should route to Identity and Access Support
- `integration_outage`: product-support workflow failure that should route to Product Support Engineering
- `refund_escalation`: strong executive-escalation example for the Supervisor Agent
- `api_regression`: strong engineering-oriented example with obvious business impact

You can still override any preset field live:

```bash
uv run run_crew --preset sso_failure --customer-name "Westlake Bank" --channel chat
```

## Troubleshooting

If `crewai run` fails with `ModuleNotFoundError`, run:

```bash
PYTHONPATH=src crewai run
```

If the crew starts but no report is generated, sync the updated dependencies again:

```bash
uv sync
```

## Knowledge base

The triage rules live in `knowledge/support_triage_playbook.txt`.

## Output

- `customer_support_triage_report.md`: final triage card
- `customer_support_triage.log`: crew execution log
