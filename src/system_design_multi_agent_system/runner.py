"""Runs the crew end-to-end and returns the final document plus per-agent outputs."""

import concurrent.futures
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .crew import crew
from .tasks import SPECIALIST_SECTIONS

load_dotenv()


@dataclass
class DesignResult:
    final_document: str
    sections: list[tuple[str, str]]  # (title, markdown) for each specialist task


def _check_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to a .env file or export it in your shell."
        )


def run_design(user_prompt: str) -> DesignResult:
    """Kick off the 9-agent crew for the given prompt and return the results.

    Runs inside a ThreadPoolExecutor because CrewAI's synchronous execution bridge
    (`loop.run_until_complete`) raises `RuntimeError: This event loop is already
    running` when called from a context that already has an asyncio event loop
    running (e.g. Jupyter).
    """
    _check_api_key()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(
            lambda: crew.kickoff(inputs={"user_prompt": user_prompt})
        ).result()

    sections = [
        (title, task.output.raw) for title, task in SPECIALIST_SECTIONS if task.output
    ]
    return DesignResult(final_document=result.raw, sections=sections)
