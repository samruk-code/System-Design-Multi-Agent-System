"""Assembles the 9 agents and 9 tasks into a sequential Crew."""

from crewai import Crew, Process

from .agents import (
    api_designer,
    capacity_estimator,
    critic,
    data_modeler,
    reliability_engineer,
    requirements_analyst,
    scalability_engineer,
    synthesizer,
    system_architect,
)
from .tasks import ALL_TASKS

crew = Crew(
    agents=[
        requirements_analyst,
        capacity_estimator,
        system_architect,
        data_modeler,
        api_designer,
        scalability_engineer,
        reliability_engineer,
        critic,
        synthesizer,
    ],
    tasks=ALL_TASKS,
    process=Process.sequential,
    verbose=True,
)
