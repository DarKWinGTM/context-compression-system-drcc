#!/usr/bin/env python3
"""Semantic compression experimentation harness.

This script loads a context file (default: DEPLOYABLE_CLAUDE.md) and applies
several semantic compression strategies defined under src/tools to evaluate
potential improvements without altering production code.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List

from tools.semantic_blocks import apply_block_macros
from tools.semantic_loop import apply_loop_tokens
from tools.semantic_metrics import StrategyResult, load_text, tighten_dictionaries
from tools.semantic_token_map import apply_token_mapping
from tools.semantic_sentence import apply_sentence_macros
from tools.semantic_sections import apply_section_aliases
from tools.semantic_phrase import apply_phrase_aliases
from tools.semantic_bpe import apply_bpe_pairs
from tools.semantic_blank import apply_blank_squeeze
from tools.semantic_headers import apply_header_compact
from tools.semantic_list import apply_list_aliases

StrategyFunc = Callable[[str], StrategyResult]

TOKEN_JOIN_PATTERN = re.compile(r'([$\u0e3f][A-Za-z0-9]+) (?=[$\u0e3f][A-Za-z0-9]+)')

DEFAULT_LAYER_PATHS: List[str] = [
    "outputs/layer0_pure_context.txt",
    "outputs/layer0_usage_instructions.txt",
    "outputs/layer1_thai_removed.txt",
    "outputs/layer2_diagrams_removed.txt",
    "outputs/layer3_combined_compression.txt",
    "outputs/layer3_templates.txt",
    "outputs/layer4_markdown.txt",
    "outputs/layer4_phrases.txt",
    "outputs/layer5_5_token_join.txt",
    "outputs/layer5_FINAL.txt",
    "outputs/layer5_words.txt",
    "outputs/layer6_markdown.txt",
    "outputs/layer7_FINAL.txt",
    "outputs/DEPLOYABLE_CLAUDE.md",
    "/home/node/workplace/AWCLOUD/TEMPLATE/CONTENT/CONTEXT.TEMPLATE.md",
]

def apply_token_join_strategy(text: str) -> StrategyResult:
    joined_text, count = TOKEN_JOIN_PATTERN.subn(lambda m: m.group(1), text)
    notes = f'joined={count}' if count else 'no joins'
    return StrategyResult(label='token_join', text=joined_text, notes=notes)

DEFAULT_STRATEGIES: List[tuple[str, StrategyFunc]] = [
    ("tighten_dictionaries", tighten_dictionaries),
    ("block_macros", apply_block_macros),
    ("loop_tokens", apply_loop_tokens),
    ("token_mapping", apply_token_mapping),
    ("token_join", apply_token_join_strategy),
    ("sentence_macros", apply_sentence_macros),
    ("section_aliases", apply_section_aliases),
    ("phrase_aliases", apply_phrase_aliases),
    ("bpe_pairs", apply_bpe_pairs),
    ("blank_squeeze", apply_blank_squeeze),
    ("header_compact", apply_header_compact),
    ("list_aliases", apply_list_aliases),
]

SUMMARY_COLUMNS: List[str] = [
    "baseline",
    "tighten_dictionaries",
    "block_macros",
    "loop_tokens",
    "token_mapping",
    "token_join",
    "sentence_macros",
    "section_aliases",
    "phrase_aliases",
    "bpe_pairs",
    "blank_squeeze",
]


def run_strategies(text: str, strategies: Iterable[tuple[str, StrategyFunc]]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for name, func in strategies:
        result = func(text)
        data = result.as_dict()
        data["strategy"] = name
        results.append(data)
    return results


def _default_output_dir() -> Path:
    return Path("report/semantic_trials")


def save_report(stats: List[Dict[str, object]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = output_dir / f"semantic_report_{timestamp}.json"
    path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return path


def append_summary(stats: List[Dict[str, object]], input_path: Path, output_dir: Path) -> Path:
    summary_path = output_dir / "semantic_summary.md"
    header = (
        "| File | "
        + " | ".join(f"{column} (chars)" for column in SUMMARY_COLUMNS)
        + " |\n|------|"
        + "|".join(["------------------"] * len(SUMMARY_COLUMNS))
        + "|\n"
    )

    existing: Dict[str, List[str]] = {}
    order: List[str] = []
    if summary_path.exists():
        for line in summary_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line.startswith("|") or line.startswith("| File ") or line.startswith("|------"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells:
                continue
            file_name = cells[0]
            if set(file_name.replace(' ', '')) == {'-'}:
                continue
            values = cells[1:]
            existing[file_name] = values
            if file_name not in order:
                order.append(file_name)

    totals = {entry.get("strategy", entry["label"]): entry["total_chars"] for entry in stats}
    current_values: List[str] = []
    for column in SUMMARY_COLUMNS:
        value = totals.get(column)
        current_values.append(f"{value:,}" if value is not None else "-")
    existing[input_path.name] = current_values
    if input_path.name not in order:
        order.append(input_path.name)

    order.sort(key=str.lower)
    lines = [header]
    for file_name in order:
        values = existing.get(file_name, ["-"] * len(SUMMARY_COLUMNS))
        if len(values) < len(SUMMARY_COLUMNS):
            values = values + ["-"] * (len(SUMMARY_COLUMNS) - len(values))
        elif len(values) > len(SUMMARY_COLUMNS):
            values = values[: len(SUMMARY_COLUMNS)]
        line = "| " + " | ".join([file_name] + values) + " |\n"
        lines.append(line)

    summary_path.write_text("".join(lines), encoding="utf-8")
    return summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Semantic compression tester")
    parser.add_argument(
        "--file",
        help="Path to a single input context file (defaults to outputs/DEPLOYABLE_CLAUDE.md when omitted)",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Optional additional input files to process",
    )
    parser.add_argument(
        "--file-list",
        help="Path to a text file containing one input path per line (lines starting with # are ignored)",
    )
    parser.add_argument(
        "--all-layers",
        action="store_true",
        help="Process all default pipeline layer outputs and the template context file",
    )
    parser.add_argument(
        "--report-dir",
        default=str(_default_output_dir()),
        help="Directory to store JSON/summary reports",
    )
    parser.add_argument(
        "--strategies",
        nargs="*",
        choices=[name for name, _ in DEFAULT_STRATEGIES],
        help="Subset of strategies to run",
    )
    return parser.parse_args()


def _collect_input_paths(args: argparse.Namespace) -> List[Path]:
    targets: List[Path] = []
    seen: set[Path] = set()

    def _add(path_str: str) -> None:
        candidate = Path(path_str).expanduser()
        if candidate not in seen:
            seen.add(candidate)
            targets.append(candidate)

    if args.file:
        _add(args.file)

    if args.files:
        for item in args.files:
            _add(item)

    if args.all_layers:
        for item in DEFAULT_LAYER_PATHS:
            _add(item)

    if args.file_list:
        list_path = Path(args.file_list).expanduser()
        if list_path.exists():
            for line in list_path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                _add(stripped)
        else:
            print(f"Warning: --file-list '{list_path}' does not exist and will be ignored.")

    if not targets:
        _add(str(Path("outputs/DEPLOYABLE_CLAUDE.md")))

    return targets


def _process_file(
    input_path: Path,
    report_dir: Path,
    strategies: Iterable[tuple[str, StrategyFunc]],
) -> None:
    text = load_text(input_path)

    if strategies:
        chosen = list(strategies)
    else:
        chosen = DEFAULT_STRATEGIES

    baseline = StrategyResult(label="baseline", text=text).as_dict()
    stats = [baseline]
    stats.extend(run_strategies(text, chosen))

    report_path = save_report(stats, report_dir)
    summary_path = append_summary(stats, input_path, report_dir)
    print(f"[semantic_lab] Input: {input_path}")
    print(f"  Report generated: {report_path}")
    print(f"  Summary updated: {summary_path}")
    print(json.dumps(stats, indent=2))


def main() -> None:
    args = parse_args()

    if args.strategies:
        chosen = [item for item in DEFAULT_STRATEGIES if item[0] in args.strategies]
    else:
        chosen = DEFAULT_STRATEGIES

    inputs = _collect_input_paths(args)
    if not inputs:
        print("No input files provided.")
        return

    report_dir = Path(args.report_dir)
    for input_path in inputs:
        _process_file(input_path, report_dir, chosen)


if __name__ == "__main__":
    main()
