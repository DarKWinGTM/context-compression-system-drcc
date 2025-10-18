from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

from .semantic_metrics import StrategyResult


def apply_block_macros(
    text: str,
    min_lines: int = 4,
    min_occurrences: int = 3,
) -> StrategyResult:
    """Replace repeated multi-line blocks with macro codes.

    Args:
        text: full document content.
        min_lines: minimum number of consecutive lines that qualify as a block.
        min_occurrences: minimum number of times a block must appear.
    """
    lines = text.splitlines()
    n = len(lines)
    block_positions: Dict[Tuple[int, Tuple[str, ...]], List[int]] = defaultdict(list)

    for length in range(min_lines, min_lines + 3):
        for idx in range(n - length + 1):
            block = tuple(lines[idx : idx + length])
            # ignore empty blocks
            if not any(line.strip() for line in block):
                continue
            block_positions[(length, block)].append(idx)

    candidates: List[Tuple[int, Tuple[str, ...], List[int]]] = []
    for (length, block), positions in block_positions.items():
        if len(positions) >= min_occurrences:
            candidates.append((length, block, positions))

    if not candidates:
        return StrategyResult(label="block_macros", text=text, notes="no repeated blocks found")

    # Prioritise larger blocks first
    candidates.sort(key=lambda item: (-item[0], -len("\n".join(item[1]))))

    used_indices = set()
    mapping: Dict[str, str] = {}
    new_lines = lines[:]
    macro_index = 0

    for length, block, positions in candidates:
        block_text = "\n".join(block)
        code = f"@B{macro_index}"
        macro_index += 1

        # skip if overlaps existing macro replacements
        if any(idx in used_indices for pos in positions for idx in range(pos, pos + length)):
            continue

        mapping[code] = block_text
        for pos in positions:
            used_indices.update(range(pos, pos + length))
            new_lines[pos] = code
            for offset in range(1, length):
                new_lines[pos + offset] = ""

    compressed = "\n".join(line for line in new_lines if line != "")
    notes = f"macros={len(mapping)}"
    return StrategyResult(label="block_macros", text=compressed, mapping=mapping or None, notes=notes)

