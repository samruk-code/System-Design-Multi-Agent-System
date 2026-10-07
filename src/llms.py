"""LLM configuration shared across all agents."""

from crewai import LLM

# Primary LLM for all reasoning-heavy agents
llm = LLM(model="gpt-4o", temperature=0.7)

# Faster, cheaper LLM for the structured capacity estimation task
llm_fast = LLM(model="gpt-4o-mini", temperature=0.3)
