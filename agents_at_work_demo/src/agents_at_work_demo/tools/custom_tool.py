from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class LocalKnowledgeSearchInput(BaseModel):
    """Input schema for the local knowledge search tool."""

    query: str = Field(
        ...,
        description="Keywords or a short question about competitors, pricing, positioning, or market context.",
    )


class LocalKnowledgeSearchTool(BaseTool):
    name: str = "local_knowledge_search"
    description: str = (
        "Searches the local market knowledge file and returns the most relevant sections for competitor, pricing, "
        "positioning, and market analysis questions."
    )
    args_schema: Type[BaseModel] = LocalKnowledgeSearchInput

    knowledge_path: str = Field(..., description="Path to the local market knowledge file.")

    def _run(self, query: str) -> str:
        text = Path(self.knowledge_path).read_text(encoding="utf-8")
        normalized_query = [term.lower() for term in query.split() if term.strip()]
        sections = [section.strip() for section in text.split("\n\n") if section.strip()]

        if not normalized_query:
            return text[:4000]

        scored_sections: list[tuple[int, str]] = []
        for section in sections:
            lowered = section.lower()
            score = sum(lowered.count(term) for term in normalized_query)
            if score > 0:
                scored_sections.append((score, section))

        if not scored_sections:
            return text[:4000]

        scored_sections.sort(key=lambda item: item[0], reverse=True)
        best_matches = [section for _, section in scored_sections[:3]]
        return "\n\n---\n\n".join(best_matches)[:4000]
