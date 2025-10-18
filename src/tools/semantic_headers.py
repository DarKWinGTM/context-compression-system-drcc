from __future__ import annotations

import re

from .semantic_metrics import StrategyResult

HEADER_PATTERN = re.compile(r"((^###?\s+\*\*[^\n]+\*\*)\n)(?:-\s+\*\*[^\n]+\*\*: ?\n){2,}", re.MULTILINE)


def apply_header_compact(text: str) -> StrategyResult:
    def repl(match: re.Match) -> str:
        block = match.group(0)
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        header = lines[0]
        items = [line.split("**")[-2] for line in lines[1:]]
        compact = header + " " + "|".join(items) + "\n"
        return compact

    new_text, count = HEADER_PATTERN.subn(repl, text)
    notes = f"headers_compacted={count}" if count else "no headers"
    return StrategyResult(label="header_compact", text=new_text, notes=notes)
