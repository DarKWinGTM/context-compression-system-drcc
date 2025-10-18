from __future__ import annotations

import re
from collections import Counter
from typing import Dict

from .semantic_metrics import StrategyResult

TOKEN_REGEX = re.compile(r"฿[A-Za-z]+")
DEFAULT_PREFIXES = ["¤", "§", "¨", "©", "µ", "¶", "ß", "Ð", "Ñ"]
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+_/"


def apply_token_mapping(text: str, top_n: int = 120) -> StrategyResult:
    tokens = TOKEN_REGEX.findall(text)
    if not tokens:
        return StrategyResult(label="token_mapping", text=text, notes="no ฿ tokens detected")

    counts = Counter(tokens)
    candidates = [tok for tok, cnt in counts.items() if len(tok) >= 3]
    if not candidates:
        return StrategyResult(label="token_mapping", text=text, notes="no tokens over threshold")

    candidates.sort(key=lambda t: (-counts[t], -len(t), t))
    chosen = candidates[:top_n]

    codes = []
    for prefix in DEFAULT_PREFIXES:
        for char in ALPHABET:
            codes.append(prefix + char)
            if len(codes) >= len(chosen):
                break
        if len(codes) >= len(chosen):
            break

    mapping: Dict[str, str] = dict(zip(chosen, codes[: len(chosen)]))
    compressed = text
    for token in sorted(mapping, key=len, reverse=True):
        compressed = compressed.replace(token, mapping[token])

    notes = f"mapped={len(mapping)}"
    return StrategyResult(label="token_mapping", text=compressed, mapping=mapping, notes=notes)

