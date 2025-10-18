from __future__ import annotations

import re
from typing import Dict, List

from .semantic_metrics import StrategyResult

BULLET_PATTERN = re.compile(r"((?:^\s*[-*].+\n){2,})", re.MULTILINE)


def apply_loop_tokens(text: str) -> StrategyResult:
    """Compress bullet lists by introducing repeat tokens."""
    mapping: Dict[str, str] = {}

    def repl(match: re.Match) -> str:
        block = match.group(1)
        lines = [line.rstrip("\n") for line in block.splitlines() if line.strip()]
        count = len(lines)
        if count < 3:
            return block
        code = f"[[repeat:{count}|{lines[0]}]]"
        mapping[code] = "\n".join(lines)
        return code + "\n"

    compressed = BULLET_PATTERN.sub(repl, text)
    if not mapping:
        return StrategyResult(label="loop_tokens", text=text, notes="no bullet sequences replaced")
    notes = f"loops={len(mapping)}"
    return StrategyResult(label="loop_tokens", text=compressed, mapping=mapping, notes=notes)

