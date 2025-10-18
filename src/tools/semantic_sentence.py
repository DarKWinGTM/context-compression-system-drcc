from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

from .semantic_metrics import StrategyResult


def _split_sentences(text: str) -> List[str]:
    sentences: List[str] = []
    buffer: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if buffer:
                sentences.append(" ".join(buffer))
                buffer.clear()
            sentences.append("\n")
            continue
        buffer.append(stripped)
        if stripped.endswith((".", "!", "?")):
            sentences.append(" ".join(buffer))
            buffer.clear()
    if buffer:
        sentences.append(" ".join(buffer))
    return sentences


def apply_sentence_macros(text: str, min_chars: int = 80, min_occ: int = 3) -> StrategyResult:
    sentences = _split_sentences(text)
    filtered = [s for s in sentences if len(s) >= min_chars and s != "\n"]
    counts = Counter(filtered)
    candidates = [s for s, c in counts.items() if c >= min_occ]
    if not candidates:
        return StrategyResult(label="sentence_macros", text=text, notes="no repeated sentences")

    mapping: Dict[str, str] = {}
    compressed = text
    for idx, sentence in enumerate(sorted(candidates, key=lambda s: (-len(s), s))):
        code = f"#S{idx}"
        mapping[code] = sentence
        compressed = compressed.replace(sentence, code)

    notes = f"sentences={len(mapping)}"
    return StrategyResult(label="sentence_macros", text=compressed, mapping=mapping, notes=notes)
