#!/usr/bin/env python3
"""Search the transcript and print matching lines with PDF page context."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "references" / "transcript-by-page.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="keyword or regular expression")
    parser.add_argument("--context", type=int, default=3)
    parser.add_argument("--regex", action="store_true")
    args = parser.parse_args()

    text = SOURCE.read_text(encoding="utf-8")
    lines = text.splitlines()
    pattern = re.compile(args.query if args.regex else re.escape(args.query), re.I)
    current_page = "unknown"
    hits = 0

    for idx, line in enumerate(lines):
        if line.startswith("## PDF Page "):
            current_page = line.removeprefix("## PDF Page ").strip()
        if pattern.search(line):
            hits += 1
            lo = max(0, idx - args.context)
            hi = min(len(lines), idx + args.context + 1)
            print(f"\n--- PDF page {current_page}, line {idx + 1} ---")
            for item in lines[lo:hi]:
                print(item)

    if hits == 0:
        print("No matches found.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
