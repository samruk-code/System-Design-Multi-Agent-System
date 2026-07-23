"""Command-line entry point.

Usage:
    uv run system-design "Design a URL shortener like bit.ly..."
    uv run system-design "..." --output design.md --sections
"""

import argparse
import sys

from .runner import run_design


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a system design document from a single prompt using a 9-agent CrewAI pipeline."
    )
    parser.add_argument("prompt", help="The system design prompt, e.g. 'Design a URL shortener like bit.ly'")
    parser.add_argument(
        "-o", "--output",
        help="Write the final Markdown document to this file instead of stdout",
    )
    parser.add_argument(
        "--sections",
        action="store_true",
        help="Also print each specialist agent's individual output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    print(f"Prompt: {args.prompt}\n", file=sys.stderr)
    result = run_design(args.prompt)

    if args.sections:
        for title, content in result.sections:
            print(f"\n---\n## {title}\n\n{content}")

    if args.output:
        with open(args.output, "w") as f:
            f.write(result.final_document)
        print(f"\nFinal design document written to {args.output}", file=sys.stderr)
    else:
        print(f"\n{result.final_document}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
