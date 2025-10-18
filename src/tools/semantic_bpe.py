from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Tuple

from .semantic_metrics import StrategyResult

WORD_REGEX = re.compile(r"\b[\w/-]+\b")


def apply_bpe_pairs(
    text: str,
    min_occurrences: int = 4,
    top_n: int = 40,
) -> StrategyResult:
    words = WORD_REGEX.findall(text)
    if len(words) < 2:
        return StrategyResult(label="bpe_pairs", text=text, notes="insufficient words")

    bigram_counts: Counter[Tuple[str, str]] = Counter()
    for first, second in zip(words, words[1:]):
        bigram_counts[(first, second)] += 1

    candidates = [pair for pair, count in bigram_counts.items() if count >= min_occurrences]
    if not candidates:
        return StrategyResult(label="bpe_pairs", text=text, notes="no frequent pairs")

    candidates.sort(key=lambda pair: (-bigram_counts[pair], -(len(pair[0]) + len(pair[1]))))
    selected = candidates[:top_n]

    mapping: Dict[str, str] = {}
    compressed = text
    for idx, (first, second) in enumerate(selected):
        phrase = f"{first} {second}"
        code = f"^B{idx}"
        mapping[code] = phrase
        compressed = re.sub(rf"\b{re.escape(first)}\s+{re.escape(second)}\b", code, compressed)

    notes = f"pairs={len(mapping)}"
    return StrategyResult(label="bpe_pairs", text=compressed, mapping=mapping or None, notes=notes)

