"""Shared runtime helpers for the customer support demo."""

from __future__ import annotations

from collections.abc import Callable
import importlib
import os
from pathlib import Path

import requests
from crewai import LLM
from crewai.tasks.task_output import TaskOutput

from customer_support.tools.custom_tool import SupportPlaybookSearchTool


ROOT_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
SUPPORT_KNOWLEDGE_PATH = KNOWLEDGE_DIR / "support_triage_playbook.txt"
OUTPUT_REPORT_PATH = ROOT_DIR / "customer_support_triage_report.md"
LOG_PATH = ROOT_DIR / "customer_support_triage.log"
LOCAL_CREWAI_HOME = ROOT_DIR / ".crewai_local"

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_LLM_MODEL = "qwen3-vl:8b"


LOCAL_CREWAI_HOME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("LOCALAPPDATA", str(LOCAL_CREWAI_HOME))
os.environ.setdefault("APPDATA", str(LOCAL_CREWAI_HOME))


def print_section(title: str) -> None:
    border = "=" * 78
    print(f"\n{border}\n{title}\n{border}")


def print_status(label: str, message: str) -> None:
    print(f"[{label}] {message}")


def build_llm() -> LLM:
    return LLM(
        model=f"ollama/{OLLAMA_LLM_MODEL}",
        base_url=f"{OLLAMA_BASE_URL}/api/generate",
        api_key="ollama",
    )


def build_support_search_tool() -> SupportPlaybookSearchTool:
    return SupportPlaybookSearchTool(
        playbook_path=str(SUPPORT_KNOWLEDGE_PATH),
    )


def collect_available_ollama_models() -> set[str]:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    response.raise_for_status()
    payload = response.json()
    models = payload.get("models", [])
    return {
        model.get("name", "")
        for model in models
        if isinstance(model, dict) and model.get("name")
    }


def check_llm_runtime_dependencies() -> None:
    try:
        importlib.import_module("litellm")
    except ImportError as exc:
        raise RuntimeError(
            "LiteLLM is not installed, so CrewAI cannot use the local Ollama model. "
            "Run `uv sync` after updating dependencies, or install it with "
            "`uv add litellm`."
        ) from exc


def run_preflight_checks() -> None:
    if not SUPPORT_KNOWLEDGE_PATH.exists():
        raise RuntimeError(
            f"Knowledge file is missing: {SUPPORT_KNOWLEDGE_PATH}. "
            "Restore it before running the demo."
        )

    check_llm_runtime_dependencies()

    try:
        available_models = collect_available_ollama_models()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {OLLAMA_BASE_URL}. "
            "Start Ollama before running the demo."
        ) from exc

    missing_models = [
        model
        for model in (OLLAMA_LLM_MODEL,)
        if model not in available_models
    ]
    if missing_models:
        raise RuntimeError(
            "Ollama is running, but the demo is missing required models: "
            f"{', '.join(missing_models)}. Pull them first, then rerun the demo."
        )


def build_task_progress_logger(task_names: list[str]) -> Callable[[TaskOutput], None]:
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
