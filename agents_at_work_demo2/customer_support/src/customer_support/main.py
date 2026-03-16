#!/usr/bin/env python
import argparse
import sys

from customer_support.crew import CustomerSupport
from customer_support.presets import DEFAULT_PRESET, PRESETS, preset_names
from customer_support.runtime import (
    LOG_PATH,
    OUTPUT_REPORT_PATH,
    SUPPORT_KNOWLEDGE_PATH,
    print_section,
    print_status,
    run_preflight_checks,
)

DEFAULT_CUSTOMER_NAME = PRESETS[DEFAULT_PRESET]["customer_name"]
DEFAULT_CUSTOMER_TIER = PRESETS[DEFAULT_PRESET]["customer_tier"]
DEFAULT_CHANNEL = PRESETS[DEFAULT_PRESET]["channel"]
DEFAULT_MESSAGE = PRESETS[DEFAULT_PRESET]["message"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Demo 2: the Customer Support Triage Agent."
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List the available canned presets and exit.",
    )
    parser.add_argument(
        "--preset",
        choices=preset_names(),
        default=DEFAULT_PRESET,
        help="Use a canned customer message scenario for the demo.",
    )
    parser.add_argument("--customer-name")
    parser.add_argument("--customer-tier")
    parser.add_argument("--channel")
    parser.add_argument("--message")
    parser.add_argument("--skip-preflight", action="store_true")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.list_presets:
        for preset_name in preset_names():
            print(f"{preset_name}: {PRESETS[preset_name]['description']}")
        return 0

    preset = PRESETS[args.preset]
    customer_name = args.customer_name or preset["customer_name"]
    customer_tier = args.customer_tier or preset["customer_tier"]
    channel = args.channel or preset["channel"]
    message = args.message or preset["message"]
    inputs = {
        "customer_name": customer_name,
        "customer_tier": customer_tier,
        "channel": channel,
        "message": message,
    }

    print_section("Demo 2: The Customer Support Triage Agent")
    print_status("scenario", f"Preset: {args.preset}")
    print_status("scenario", f"Customer: {customer_name}")
    print_status("scenario", f"Tier: {customer_tier}")
    print_status("scenario", f"Channel: {channel}")

    if args.skip_preflight:
        print_status("preflight", "Skipped by request")
    else:
        print_status("preflight", "Checking Ollama and local models")
        try:
            run_preflight_checks()
        except RuntimeError as exc:
            print_status("error", str(exc))
            return 1
        print_status("preflight", "Environment looks ready")

    print_status("input", f"Message: {message}")
    print_status("tools", f"Knowledge base: {SUPPORT_KNOWLEDGE_PATH.name}")
    print_status("output", f"Report will be saved to: {OUTPUT_REPORT_PATH.name}")
    print_status("output", f"Crew logs will be saved to: {LOG_PATH.name}")

    print_section("Running Crew")
    print_status("run", "Progress updates will appear as each task actually completes")

    try:
        result = CustomerSupport().crew().kickoff(inputs=inputs)
    except Exception as exc:
        print_status("error", f"An error occurred while running the crew: {exc}")
        return 1

    print_section("Final Triage Report")
    print(result.raw)
    return 0


def train() -> int:
    raise NotImplementedError("Training is not configured for this demo.")


def replay() -> int:
    raise NotImplementedError("Replay is not configured for this demo.")


def test() -> int:
    raise NotImplementedError("Automated test mode is not configured for this demo.")


def run_with_trigger() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
