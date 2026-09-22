# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A CrewAI-based multi-agent pipeline that takes a single system design prompt (e.g. "Design a URL shortener like bit.ly") and produces a full system design document. Nine specialized agents run strictly sequentially, each receiving the accumulated output of every agent before it, and a final Synthesizer merges everything into one 9-section Markdown document.

## Commands

```bash
uv sync                        # install dependencies

# Run the CLI (requires OPENAI_API_KEY in .env or the shell env)
uv run system-design "Design a URL shortener like bit.ly. It needs to handle \
100 million stored URLs and 1 billion redirects per day. Redirection latency \
must be under 10ms at p99."

uv run system-design "<prompt>" --output design.md   # write final doc to a file
uv run system-design "<prompt>" --sections            # also print each specialist's raw output
```

There is no test suite, linter, or type checker configured in this repo.

## Architecture

The pipeline is a strict sequential chain of 9 CrewAI `Agent`/`Task` pairs (`Process.sequential`), each specialist building on the full accumulated context of prior tasks via CrewAI's `context=[...]` mechanism:

1. Requirements Analyst → functional/non-functional requirements
2. Capacity Estimator → QPS, storage, bandwidth, server counts (uses `llm_fast`, gpt-4o-mini)
3. System Architect → component diagram (Mermaid) + request flow
4. Data Modeler → database choices, schemas, indexing, sharding
5. API Designer → endpoint specs, auth, rate limiting
6. Scalability Engineer → caching, load balancing, auto-scaling
7. Reliability Engineer → fault tolerance, DR plan, observability
8. Critic → bottlenecks, SPOFs, trade-off analysis
9. Synthesizer → merges all 8 prior outputs into the final Markdown document

All agents except the Capacity Estimator use `llm` (gpt-4o); the Capacity Estimator uses `llm_fast` (gpt-4o-mini) since its task is structured arithmetic rather than open-ended reasoning (`src/system_design_multi_agent_system/llms.py`).

Module responsibilities:
- `agents.py` — the 9 `Agent` definitions (role/goal/backstory/llm)
- `tasks.py` — the 9 `Task` definitions (description/expected_output/context chain); also exports `ALL_TASKS` (ordered list fed to the Crew) and `SPECIALIST_SECTIONS` (the 8 specialist tasks, excluding synthesis, used to expose per-agent output)
- `crew.py` — assembles `agents.py` + `ALL_TASKS` into the `Crew` with `Process.sequential`
- `runner.py` — `run_design()`: loads `.env`, validates `OPENAI_API_KEY`, kicks off the crew inside a `ThreadPoolExecutor`, and returns a `DesignResult(final_document, sections)`
- `main.py` — argparse CLI entry point (`system-design` script), wraps `run_design()`

### Design decisions worth knowing before changing this code

- **Sequential, not parallel**: CrewAI 1.x requires async tasks to only reference sync tasks in their `context`. Since later agents (Data Modeler, API Designer, ...) depend on the Architect's output, the whole pipeline stays sequential rather than mixing sync/async.
- **`ThreadPoolExecutor` in `run_design()`**: CrewAI's sync execution bridge (`loop.run_until_complete`) raises `RuntimeError: This event loop is already running` when called from a context that already has an asyncio event loop running (e.g. Jupyter). Running the crew in a worker thread sidesteps this — do not "simplify" this away without checking that call context.
- To add or reorder a pipeline stage: add the `Agent` in `agents.py`, add the corresponding `Task` in `tasks.py` with the correct `context=[...]` dependencies, add it to `ALL_TASKS` (and `SPECIALIST_SECTIONS` if it should appear in `--sections` output), and wire it into `crew.py`'s `agents=[...]` list.

Note: the README references a Jupyter notebook under `notebook/`, but that notebook has been removed from the repo (see git history) — the CLI / `run_design()` library call are the only current entry points.
