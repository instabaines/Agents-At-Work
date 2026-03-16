"""Compatibility wrapper for the demo crew.

This file used to contain the stock CrewAI template. It now points back to the
actual demo implementation in `main.py` so the repository has one consistent
source of truth.
"""

from __future__ import annotations

from crewai import Crew

from agents_at_work_demo.main import (
    DEFAULT_MARKET,
    DEFAULT_PRODUCT,
    DEFAULT_SCENARIO,
    resolve_knowledge_path,
    build_crew,
)


class AgentsAtWorkDemo:
    """Thin wrapper that exposes the demo crew with default live-demo inputs."""

    def __init__(
        self,
        product: str = DEFAULT_PRODUCT,
        market: str = DEFAULT_MARKET,
        scenario: str = DEFAULT_SCENARIO,
        web_search: str = "auto",
    ) -> None:
        self.product = product
        self.market = market
        self.scenario = scenario
        self.web_search = web_search

    def crew(self) -> Crew:
        crew, _ = build_crew(
            product=self.product,
            market=self.market,
            knowledge_path=resolve_knowledge_path(self.scenario),
            web_search_mode=self.web_search,
        )
        return crew
