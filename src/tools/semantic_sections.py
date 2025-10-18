from __future__ import annotations

import re
from typing import Dict, List

from .semantic_metrics import StrategyResult

HEADER_REGEX = re.compile(r"^(#{2,4}\s+.+)$", re.MULTILINE)


def apply_section_aliases(text: str) -> StrategyResult:
    headers: List[str] = HEADER_REGEX.findall(text)
    if not headers:
        return StrategyResult(label="section_aliases", text=text, notes="no headers detected")

    unique = []
    for header in headers:
        if header not in unique:
            unique.append(header)

    mapping: Dict[str, str] = {}
    compressed = text
    for idx, header in enumerate(unique):
        code = f"§{idx}"
        mapping[code] = header
        compressed = compressed.replace(header, code)

    notes = f"headers={len(mapping)}"
    return StrategyResult(label="section_aliases", text=compressed, mapping=mapping, notes=notes)

