from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

from .semantic_metrics import StrategyResult

WORD_REGEX = re.compile(r"\b[\w/-]+\b")


def apply_phrase_aliases(
    text: str,
    min_words: int = 3,
    max_words: int = 6,
    min_occurrences: int = 3,
    top_n: int = 25,
) -> StrategyResult:
    words = WORD_REGEX.findall(text)
    if len(words) < min_words:
        return StrategyResult(label="phrase_aliases", text=text, notes="insufficient words")

    phrase_counts: Counter[str] = Counter()
    word_count = len(words)

    for length in range(min_words, max_words + 1):
        for idx in range(word_count - length + 1):
            phrase = " ".join(words[idx : idx + length])
            if len(phrase) < 12:  # skip very short strings
                continue
            phrase_counts[phrase] += 1

    candidates = [phrase for phrase, count in phrase_counts.items() if count >= min_occurrences]
    if not candidates:
        return StrategyResult(label="phrase_aliases", text=text, notes="no repeated phrases")

    candidates.sort(key=lambda p: (-len(p), -phrase_counts[p], p))
    selected = candidates[:top_n]

    mapping: Dict[str, str] = {}
    compressed = text
    for idx, phrase in enumerate(selected):
        code = f"~P{idx}"
        mapping[code] = phrase
        compressed = re.sub(rf"\b{re.escape(phrase)}\b", code, compressed)

    notes = f"phrases={len(mapping)}"
    return StrategyResult(label="phrase_aliases", text=compressed, mapping=mapping, notes=notes)

