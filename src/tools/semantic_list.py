from __future__ import annotations

from collections import Counter
from typing import Dict, List, Tuple

from .semantic_metrics import StrategyResult


def _extract_lists(text: str, min_length: int = 4) -> List[Tuple[int, List[str]]]:
    lines = text.splitlines()
    results: List[Tuple[int, List[str]]] = []
    current: List[str] = []
    start = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith("-"):
            if not current:
                start = idx
            current.append(line)
        else:
            if len(current) >= min_length:
                results.append((start, current))
            current = []
    if len(current) >= min_length:
        results.append((start, current))
    return results


def apply_list_aliases(text: str, min_length: int = 4, min_occurrences: int = 2) -> StrategyResult:
    lists = _extract_lists(text, min_length=min_length)
    if not lists:
        return StrategyResult(label="list_aliases", text=text, notes="no lists")

    counter = Counter(tuple(chunk) for _, chunk in lists)
    candidates = [chunk for chunk, count in counter.items() if count >= min_occurrences]
    if not candidates:
        return StrategyResult(label="list_aliases", text=text, notes="no repeated lists")

    mapping: Dict[str, str] = {}
    new_text = text
    for idx, chunk in enumerate(candidates):
        code = f"^L{idx}"
        mapping[code] = "\n".join(chunk)
        block = "\n".join(chunk)
        new_text = new_text.replace(block, code)

    notes = f"lists={len(mapping)}"
    return StrategyResult(label="list_aliases", text=new_text, mapping=mapping, notes=notes)
