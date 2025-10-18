from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover
    tiktoken = None


@dataclass
class StrategyResult:
    label: str
    text: str
    mapping: Optional[Dict[str, str]] = None
    notes: Optional[str] = None

    def as_dict(self) -> Dict[str, object]:
        mapping_chars = 0
        if self.mapping:
            mapping_chars = len("\n".join(f"{k}={v}" for k, v in self.mapping.items()))
        return {
            "label": self.label,
            "chars": len(self.text),
            "tokens": _count_tokens(self.text),
            "mapping_chars": mapping_chars,
            "total_chars": len(self.text) + mapping_chars,
            "notes": self.notes or "",
        }


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tighten_dictionaries(text: str) -> StrategyResult:
    """Normalize dictionary tables by removing redundant spacing."""
    import re

    def _tighten(block: str) -> str:
        return block.replace(" = ", "=").replace(" | ", "|")

    tightened = text
    pattern = re.compile(r"(### \\*\\*.*?Dictionary.*?```)(.*?)(```)", re.DOTALL)
    for match in pattern.finditer(text):
        prefix, body, suffix = match.groups()
        tightened_body = _tighten(body)
        if body != tightened_body:
            tightened = tightened.replace(prefix + body + suffix, prefix + tightened_body + suffix, 1)
    return StrategyResult(label="tighten_dictionaries", text=tightened)


def _count_tokens(text: str) -> Optional[int]:  # pragma: no cover - debugging helper
    if tiktoken:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    return None

