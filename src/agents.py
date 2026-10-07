"""The 9 specialist agents in the system design pipeline.

Each agent has a role (its identity), a goal (what it must achieve), and a
backstory (the expertise perspective it reasons from). The prompt text lives in
`prompts/agents.yaml`; this module only builds the `Agent` objects from it.
"""

from pathlib import Path

import yaml
from crewai import Agent

import llms

_CONFIG = yaml.safe_load((Path(__file__).parent / "prompts" / "agents.yaml").read_text(encoding="utf-8"))


def _build(key: str) -> Agent:
    cfg = dict(_CONFIG[key])
    cfg["llm"] = getattr(llms, cfg["llm"])
    return Agent(**cfg, verbose=True)


requirements_analyst = _build("requirements_analyst")
capacity_estimator = _build("capacity_estimator")
system_architect = _build("system_architect")
data_modeler = _build("data_modeler")
api_designer = _build("api_designer")
scalability_engineer = _build("scalability_engineer")
reliability_engineer = _build("reliability_engineer")
critic = _build("critic")
synthesizer = _build("synthesizer")


