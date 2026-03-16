"""Console entrypoint for the Agents at Work demo.

This module keeps the demo logic in one place so it can be launched with:

- `python -m agents_at_work_demo.main`
- `agents_at_work_demo`
- `run_crew`

The focus is a clean, presenter-friendly run:
- simple banner/progress output
- live CLI overrides for product and market
- optional web search that only activates when an API key is present
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tasks.task_output import TaskOutput
import requests

from agents_at_work_demo.tools.custom_tool import LocalKnowledgeSearchTool

try:
    from crewai_tools import SerperDevTool
except ImportError:  # pragma: no cover - dependency is installed in the demo env
    SerperDevTool = None


ROOT_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
KNOWLEDGE_BASE_PATH = KNOWLEDGE_DIR / "market_notes.txt"
SCENARIOS_DIR = KNOWLEDGE_DIR / "scenarios"
OUTPUT_MEMO_PATH = ROOT_DIR / "strategic_research_swarm_memo.md"
CREW_LOG_PATH = ROOT_DIR / "crew_run.log"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_LLM_MODEL = "qwen3-vl:8b"

DEFAULT_PRODUCT = "OrbitFlow"
DEFAULT_MARKET = "mid-market SaaS operations teams"
DEFAULT_SCENARIO = "saas_ops"


def print_section(title: str) -> None:
    border = "=" * 78
    print(f"\n{border}\n{title}\n{border}")


def print_status(label: str, message: str) -> None:
    print(f"[{label}] {message}")


def available_scenarios() -> list[str]:
    """Return the sorted list of available scenario names."""
    if not SCENARIOS_DIR.exists():
        return [DEFAULT_SCENARIO]

    scenario_names = sorted(
        path.stem
        for path in SCENARIOS_DIR.glob("*.txt")
        if path.is_file()
    )
    return scenario_names or [DEFAULT_SCENARIO]


def resolve_knowledge_path(scenario: str) -> Path:
    """Resolve a scenario name to its knowledge file."""
    candidate = SCENARIOS_DIR / f"{scenario}.txt"
    if candidate.exists():
        return candidate
    if scenario == DEFAULT_SCENARIO:
        return KNOWLEDGE_BASE_PATH
    raise ValueError(
        f"Unknown scenario '{scenario}'. Available scenarios: "
        f"{', '.join(available_scenarios())}"
    )


def build_llm() -> LLM:
    """Create the local Ollama-backed LLM used for the demo."""
    return LLM(
        model=f"ollama/{OLLAMA_LLM_MODEL}",
        base_url=f"{OLLAMA_BASE_URL}/api/generate",
        api_key="ollama",
    )


def build_txt_search_tool(knowledge_path: Path) -> LocalKnowledgeSearchTool:
    """Create the local knowledge-base search tool."""
    return LocalKnowledgeSearchTool(knowledge_path=str(knowledge_path))


def maybe_build_web_search_tool(mode: str) -> tuple[Any | None, str]:
    """Return an optional web search tool plus a human-readable status string."""
    if mode == "off":
        return None, "disabled"

    has_api_key = bool(os.getenv("SERPER_API_KEY"))
    if not has_api_key:
        if mode == "on":
            return None, "requested, but SERPER_API_KEY is not set"
        return None, "not enabled (SERPER_API_KEY not set)"

    if SerperDevTool is None:
        return None, "not available (Serper tool import failed)"

    return SerperDevTool(n_results=5), "enabled via SERPER_API_KEY"


def collect_available_ollama_models() -> set[str]:
    """Return the locally available Ollama model tags."""
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    response.raise_for_status()
    payload = response.json()
    models = payload.get("models", [])
    return {
        model.get("name", "")
        for model in models
        if isinstance(model, dict) and model.get("name")
    }


def run_preflight_checks() -> None:
    """Fail early with a readable message when the local model setup is missing."""
    run_preflight_checks_for_path(KNOWLEDGE_BASE_PATH)


def run_preflight_checks_for_path(knowledge_path: Path) -> None:
    """Fail early with a readable message when the selected setup is missing."""
    if not knowledge_path.exists():
        raise RuntimeError(
            f"Knowledge file is missing: {knowledge_path}. "
            "Restore it before running the demo."
        )

    try:
        available_models = collect_available_ollama_models()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not reach Ollama at "
            f"{OLLAMA_BASE_URL}. Start Ollama before running the demo."
        ) from exc

    missing_models = [
        model
        for model in (OLLAMA_LLM_MODEL,)
        if model not in available_models
    ]
    if missing_models:
        missing_list = ", ".join(missing_models)
        raise RuntimeError(
            "Ollama is running, but the demo is missing required models: "
            f"{missing_list}. Pull them first, then rerun the demo."
        )


def build_researcher(
    llm: LLM,
    product: str,
    market: str,
    knowledge_path: Path,
    web_search_mode: str,
) -> tuple[Agent, str]:
    """Create the researcher agent and attach tools based on runtime options."""
    tools: list[Any] = [build_txt_search_tool(knowledge_path)]
    web_tool, web_status = maybe_build_web_search_tool(web_search_mode)
    if web_tool is not None:
        tools.append(web_tool)

    tool_note = (
        "Use the local knowledge base first. Use web search only if it is available "
        "and the knowledge base is missing important competitor or pricing details."
    )

    researcher = Agent(
        role="Senior Market Research Analyst",
        goal=(
            f"Identify the top competitors to {product} in the {market} market, "
            "their pricing models, and the most important strategic context."
        ),
        backstory=(
            "You are a methodical market researcher. You prefer grounded facts, "
            "clear comparisons, and concise synthesis. "
            f"{tool_note}"
        ),
        tools=tools,
        verbose=False,
        allow_delegation=False,
        llm=llm,
    )
    return researcher, web_status


def build_strategist(llm: LLM, product: str, market: str) -> Agent:
    return Agent(
        role="Business Growth Consultant",
        goal=(
            f"Analyze the competitor landscape around {product} in {market} and find "
            "a clear strategic gap we can exploit."
        ),
        backstory=(
            "You think in terms of differentiation, positioning, and go-to-market. "
            "You are concise and focus on what actually moves revenue."
        ),
        verbose=False,
        allow_delegation=False,
        llm=llm,
    )


def build_writer(llm: LLM, product: str, market: str) -> Agent:
    return Agent(
        role="Chief Communications Officer",
        goal=(
            f"Write a crisp executive memo explaining how {product} should compete in "
            f"{market}."
        ),
        backstory=(
            "You turn complex analysis into clear business language. "
            "You prefer headings, bullets, and short paragraphs."
        ),
        verbose=False,
        allow_delegation=False,
        llm=llm,
    )


def build_tasks(
    researcher: Agent,
    strategist: Agent,
    writer: Agent,
    product: str,
    market: str,
) -> list[Task]:
    research_task = Task(
        name="Competitor Scan",
        description=(
            f"Using the knowledge base, identify 3-5 key competitors relevant to "
            f"{product}, which serves {market}. If web search is available, use it "
            "only to fill obvious gaps in competitor or pricing information.\n\n"
            "For each competitor, extract:\n"
            "- Product focus\n"
            "- Target customers\n"
            "- Pricing model (for example: per seat, usage-based, or tiered)\n"
            "- Any notable strengths or differentiators\n\n"
            "Respond with a markdown table with columns:\n"
            "Competitor | Product | Target Customers | Pricing Model | Notes"
        ),
        expected_output=(
            "A markdown table with 3-5 rows and factual notes grounded in the "
            "available sources."
        ),
        agent=researcher,
    )

    strategy_task = Task(
        name="Gap Analysis",
        description=(
            f"Based on the competitor table, identify one clear strategic gap or "
            f"weakness for each competitor relative to {product} in {market}. "
            "Think in terms of underserved segments, missing features, painful "
            "onboarding, weak integrations, or pricing friction.\n\n"
            "Return a bullet list in the format:\n"
            "- Competitor: <name>\n"
            "- Gap: <1-2 sentence description>\n"
            "- Why it matters: <1-2 sentence impact explanation>"
        ),
        expected_output=(
            "A concise bullet list of competitor gaps or weaknesses, each with a "
            "clear explanation of why it matters."
        ),
        agent=strategist,
    )

    writing_task = Task(
        name="Executive Memo",
        description=(
            f"Write a one-page executive memo for the CEO about {product} in "
            f"{market}.\n"
            "The memo should:\n"
            "1. Briefly describe the market and where the product sits.\n"
            "2. Summarize the top competitors and how they charge.\n"
            "3. Highlight the main gaps or weaknesses identified.\n"
            "4. Recommend 1-2 strategic angles to pursue over the next 6-12 months.\n\n"
            "Constraints:\n"
            "- Use clear, non-technical business language.\n"
            "- Use headings and bullets for easy skimming.\n"
            "- Keep it to roughly 500-800 words."
        ),
        expected_output="A polished markdown memo suitable for an email or doc.",
        agent=writer,
        markdown=True,
        output_file=str(OUTPUT_MEMO_PATH),
    )

    return [research_task, strategy_task, writing_task]


def build_task_progress_logger(task_names: list[str]) -> Callable[[TaskOutput], None]:
    """Build a completion logger that reflects real task progress."""
    total_tasks = len(task_names)
    task_positions = {
        task_name: index for index, task_name in enumerate(task_names, start=1)
    }

    def log_task_completion(output: TaskOutput) -> None:
        preview = " ".join(output.raw.split())
        trimmed_preview = preview[:140] + ("..." if len(preview) > 140 else "")
        task_name = output.name or output.agent
        task_position = task_positions.get(task_name)

        if task_position is None:
            print_status("done", f"{task_name} complete")
        else:
            print_status("done", f"{task_position}/{total_tasks} {task_name} complete")

        if trimmed_preview:
            print(f"       {trimmed_preview}")

    return log_task_completion


def build_crew(
    product: str,
    market: str,
    knowledge_path: Path,
    web_search_mode: str,
) -> tuple[Crew, str]:
    """Create the demo crew for the chosen live scenario."""
    llm = build_llm()
    researcher, web_status = build_researcher(
        llm=llm,
        product=product,
        market=market,
        knowledge_path=knowledge_path,
        web_search_mode=web_search_mode,
    )
    strategist = build_strategist(llm=llm, product=product, market=market)
    writer = build_writer(llm=llm, product=product, market=market)
    tasks = build_tasks(
        researcher=researcher,
        strategist=strategist,
        writer=writer,
        product=product,
        market=market,
    )
    progress_logger = build_task_progress_logger(
        [task.name or f"Task {index}" for index, task in enumerate(tasks, start=1)]
    )

    crew = Crew(
        name="Strategic Research Swarm",
        agents=[researcher, strategist, writer],
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
        tracing=False,
        output_log_file=str(CREW_LOG_PATH),
        task_callback=progress_logger,
    )
    return crew, web_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the projected Agents at Work market research demo."
    )
    parser.add_argument(
        "--scenario",
        choices=available_scenarios(),
        default=DEFAULT_SCENARIO,
        help="Preset knowledge scenario to use for the live demo.",
    )
    parser.add_argument(
        "--product",
        default=DEFAULT_PRODUCT,
        help="Product name to analyze live during the demo.",
    )
    parser.add_argument(
        "--market",
        default=DEFAULT_MARKET,
        help="Target market or audience for the product.",
    )
    parser.add_argument(
        "--web-search",
        choices=("auto", "on", "off"),
        default="auto",
        help=(
            "Enable optional web search. 'auto' only turns it on when "
            "SERPER_API_KEY is present."
        ),
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip Ollama/model checks if you already know the environment is ready.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    """Run the strategic research demo from the console."""
    args = parse_args(argv)

    print_section("Agents at Work: Strategic Research Swarm")
    knowledge_path = resolve_knowledge_path(args.scenario)
    print_status("scenario", f"Product: {args.product}")
    print_status("scenario", f"Market: {args.market}")
    print_status("scenario", f"Preset: {args.scenario}")

    if args.skip_preflight:
        print_status("preflight", "Skipped by request")
    else:
        print_status("preflight", "Checking Ollama and local models")
        try:
            run_preflight_checks_for_path(knowledge_path)
        except RuntimeError as exc:
            print_status("error", str(exc))
            return 1
        print_status("preflight", "Environment looks ready")

    try:
        crew, web_status = build_crew(
            product=args.product,
            market=args.market,
            knowledge_path=knowledge_path,
            web_search_mode=args.web_search,
        )
    except Exception as exc:
        print_status("error", f"An error occurred while preparing the crew: {exc}")
        return 1

    print_status("tools", f"Knowledge base: {knowledge_path.name}")
    print_status("tools", f"Web search: {web_status}")
    print_status("output", f"Memo will be saved to: {OUTPUT_MEMO_PATH.name}")
    print_status("output", f"Crew logs will be saved to: {CREW_LOG_PATH.name}")

    print_section("Running Crew")
    print_status("run", "Starting 1/3 Competitor Scan")
    print_status("run", "Progress updates will appear as each task actually completes")
    print_status("run", "The first completion can take a few minutes on local Ollama")

    try:
        result = crew.kickoff()
    except Exception as exc:
        print_status("error", f"An error occurred while running the crew: {exc}")
        return 1

    print_section("Final Executive Memo")
    print(result.raw)
    return 0


def train() -> int:
    raise NotImplementedError("Training is not configured for this demo.")


def replay() -> int:
    raise NotImplementedError("Replay is not configured for this demo.")


def test() -> int:
    raise NotImplementedError("Automated crew test mode is not configured for this demo.")


def run_with_trigger() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))

