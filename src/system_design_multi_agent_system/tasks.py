"""The 9 pipeline tasks.

Tasks run strictly sequentially. Each task passes its output forward via the
`context` list, so every agent builds on the full accumulated knowledge of all
prior agents. The prompt text and context wiring live in `prompts/task.yaml`.
"""

from pathlib import Path

import yaml
from crewai import Task

from . import agents

_CONFIG = yaml.safe_load((Path(__file__).parent / "prompts" / "task.yaml").read_text(encoding="utf-8"))

# Tasks are listed in dependency order, so each context task already exists when built.
_TASKS: dict[str, Task] = {}
for _key, _cfg in _CONFIG.items():
    _TASKS[_key] = Task(
        description=_cfg["description"],
        expected_output=_cfg["expected_output"],
        agent=getattr(agents, _cfg["agent"]),
        context=[_TASKS[c] for c in _cfg["context"]] or None,
    )

requirements_task = _TASKS["requirements_task"]
capacity_task = _TASKS["capacity_task"]
architecture_task = _TASKS["architecture_task"]
data_model_task = _TASKS["data_model_task"]
api_design_task = _TASKS["api_design_task"]
scalability_task = _TASKS["scalability_task"]
reliability_task = _TASKS["reliability_task"]
critique_task = _TASKS["critique_task"]
synthesis_task = _TASKS["synthesis_task"]

# Ordered list matching the sequential pipeline
ALL_TASKS = [
    requirements_task,
    capacity_task,
    architecture_task,
    data_model_task,
    api_design_task,
    scalability_task,
    reliability_task,
    critique_task,
    synthesis_task,
]

# (title, task) pairs for the 8 specialist tasks — excludes the final synthesis
SPECIALIST_SECTIONS = [
    ("1. Requirements Analysis", requirements_task),
    ("2. Capacity Estimation", capacity_task),
    ("3. System Architecture", architecture_task),
    ("4. Data Model", data_model_task),
    ("5. API Design", api_design_task),
    ("6. Scalability", scalability_task),
    ("7. Reliability", reliability_task),
    ("8. Critique", critique_task),
]
