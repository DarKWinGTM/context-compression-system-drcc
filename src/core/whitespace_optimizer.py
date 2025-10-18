#!/usr/bin/env python3
"""
Whitespace Optimizer - Micro-optimization Layer
Remove excessive whitespace while maintaining readability
"""

import re
from typing import Tuple, Dict


class WhitespaceOptimizer:
    """Optimize whitespace usage"""

    def optimize(self, text: str) -> Tuple[str, Dict]:
        """
        Optimize whitespace

        Args:
            text: Input text

        Returns:
            Tuple of (optimized_text, stats_dict)
        """
        original_size = len(text)

        stats = {
            'original_size': original_size,
            'optimizations': {}
        }

        # 1. Remove excessive newlines (3+ → 2)
        triple_newlines = len(re.findall(r'\n\n\n+', text))
        text = re.sub(r'\n\n\n+', '\n\n', text)
        stats['optimizations']['excessive_newlines'] = {
            'count': triple_newlines,
            'savings': original_size - len(text)
        }

        # 2. Remove trailing spaces at line ends
        trailing_before = len(text)
        text = re.sub(r' +\n', '\n', text)
        stats['optimizations']['trailing_spaces'] = {
            'savings': trailing_before - len(text)
        }

        # 3. Remove trailing whitespace at end of file
        text = text.rstrip() + '\n'

        # Calculate final statistics
        final_size = len(text)
        total_saved = original_size - final_size

        stats['final_size'] = final_size
        stats['total_saved'] = total_saved
        stats['compression_ratio'] = (total_saved / original_size * 100) if original_size > 0 else 0

        return text, stats

    def decompress(self, text: str) -> str:
        """
        No decompression needed - whitespace optimization is one-way
        Original spacing is not critical for content
        """
        return text


def main():
    """Test whitespace optimizer on final compressed file"""
    from pathlib import Path

    input_path = Path(__file__).parent.parent.parent / "outputs" / "final_compressed_with_markdown.txt"
    output_path = Path(__file__).parent.parent.parent / "outputs" / "final_optimized.txt"

    if not input_path.exists():
        print(f"❌ ERROR: Input file not found: {input_path}")
        return 1

    print("=" * 80)
    print("🔧 WHITESPACE OPTIMIZER")
    print("=" * 80)
    print()

    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    original_size = len(text)
    print(f"📖 Input: {input_path}")
    print(f"📊 Original size: {original_size:,} chars")
    print()

    # Optimize
    optimizer = WhitespaceOptimizer()
    optimized, stats = optimizer.optimize(text)

    print("✅ Optimization complete:")
    print(f"   Input:  {original_size:,} chars")
    print(f"   Output: {stats['final_size']:,} chars")
    print(f"   Saved:  {stats['total_saved']:,} chars")
    print()

    print("📊 Breakdown:")
    for name, data in stats['optimizations'].items():
        if 'count' in data:
            print(f"   {name}: {data['count']} occurrences, {data['savings']} chars saved")
        else:
            print(f"   {name}: {data['savings']} chars saved")
    print()

    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(optimized)

    print(f"💾 Saved to: {output_path}")
    print()

    # Check target
    target = 40_000
    print("=" * 80)
    print("🎯 TARGET CHECK:")
    print("=" * 80)
    print(f"Target: ≤{target:,} chars")
    print(f"Result: {stats['final_size']:,} chars")

    if stats['final_size'] <= target:
        gap = target - stats['final_size']
        print(f"✅ TARGET MET! (under by {gap} chars)")
    else:
        gap = stats['final_size'] - target
        print(f"⚠️  Still {gap} chars over target")

    return 0 if stats['final_size'] <= target else 1


if __name__ == '__main__':
    exit(main())
