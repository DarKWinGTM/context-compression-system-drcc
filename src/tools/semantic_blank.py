from __future__ import annotations

import re

from .semantic_metrics import StrategyResult

BLANK_PATTERN = re.compile(r"\n{3,}")


def apply_blank_squeeze(text: str) -> StrategyResult:
    """Collapse sequences of >=3 blank lines into a double newline."""
    new_text, count = BLANK_PATTERN.subn("\n\n", text)
    notes = f"collapsed={count}" if count else "no collapses"
    return StrategyResult(label="blank_squeeze", text=new_text, notes=notes)
