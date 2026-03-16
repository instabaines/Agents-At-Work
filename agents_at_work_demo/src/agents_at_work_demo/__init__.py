"""Agents at Work demo package setup."""

from __future__ import annotations

import os
from pathlib import Path


_ROOT_DIR = Path(__file__).resolve().parents[2]
_LOCAL_CREWAI_HOME = _ROOT_DIR / ".crewai_local"
_LOCAL_CREWAI_HOME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("CREWAI_STORAGE_DIR", str(_LOCAL_CREWAI_HOME / "db"))
os.environ.setdefault("LOCALAPPDATA", str(_LOCAL_CREWAI_HOME))
os.environ.setdefault("APPDATA", str(_LOCAL_CREWAI_HOME))
