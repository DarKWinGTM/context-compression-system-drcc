#!/usr/bin/env python3
"""
Selective Emoji Remover - Final optimization to reach <40,000 target
Remove only excessive/decorative emojis while keeping important ones
"""

import re
from typing import Tuple, Dict
from collections import Counter


class SelectiveEmojiRemover:
    """Remove emojis selectively to reach target size"""

    def __init__(self, target_reduction: int = 250):
        """
        Initialize with target reduction

        Args:
            target_reduction: Number of chars to remove (default 250 for safety margin)
        """
        self.target_reduction = target_reduction

    def remove(self, text: str) -> Tuple[str, Dict]:
        """
        Remove emojis selectively to reach target

        Strategy:
        1. Keep functional emojis (✅ ❌ that indicate status)
        2. Remove decorative emojis (🎯 🔧 🗜️ 🏆 🎉)
        3. Limit repetitive emojis to max 3 per type

        Args:
            text: Input text

        Returns:
            Tuple of (optimized_text, stats_dict)
        """
        original_size = len(text)

        stats = {
            'original_size': original_size,
            'target_reduction': self.target_reduction,
            'emojis_removed': {},
            'total_removed': 0
        }

        # Define emoji categories
        KEEP_ALWAYS = '✅❌⚠️'  # Status indicators - always keep
        REMOVE_DECORATIVE = '🎯🔧🗜️🏆🎉💡📁🚀🔄📈🔗🌳🕸'  # Purely decorative
        LIMIT_USAGE = '📊🧠🏗🔍📜🏛'  # Keep max 3 of each

        bytes_removed = 0

        # 1. Remove all decorative emojis
        for emoji in REMOVE_DECORATIVE:
            count_before = text.count(emoji)
            if count_before > 0:
                text = text.replace(emoji + ' ', '')  # Remove with trailing space
                text = text.replace(emoji, '')  # Remove standalone
                emoji_bytes = len(emoji.encode('utf-8'))
                removed = (emoji_bytes - 1) * count_before  # Overhead removed
                bytes_removed += removed
                stats['emojis_removed'][emoji] = {
                    'count': count_before,
                    'overhead_removed': removed
                }

        # 2. Limit repetitive emojis to max 3
        for emoji in LIMIT_USAGE:
            count = text.count(emoji)
            if count > 3:
                # Keep only first 3 occurrences
                # split(emoji, 3) creates 4 parts: before_1st, between_1st_2nd, between_2nd_3rd, after_3rd
                parts = text.split(emoji, 3)
                # Rejoin first 3 emojis and remove all others from last part
                text = emoji.join(parts[:3]) + emoji + parts[3].replace(emoji, '')
                removed_count = count - 3
                emoji_bytes = len(emoji.encode('utf-8'))
                removed = (emoji_bytes - 1) * removed_count
                bytes_removed += removed
                stats['emojis_removed'][emoji] = {
                    'count': removed_count,
                    'overhead_removed': removed
                }

        # 3. If still need more, remove excess status emojis (keep max 5 of each)
        if bytes_removed < self.target_reduction:
            for emoji in '✅❌':
                count = text.count(emoji)
                if count > 5:
                    # split(emoji, 5) creates 6 parts
                    parts = text.split(emoji, 5)
                    # Rejoin first 5 emojis and remove all others from last part
                    text = emoji.join(parts[:5]) + emoji + parts[5].replace(emoji, '')
                    removed_count = count - 5
                    emoji_bytes = len(emoji.encode('utf-8'))
                    removed = (emoji_bytes - 1) * removed_count
                    bytes_removed += removed
                    if emoji in stats['emojis_removed']:
                        stats['emojis_removed'][emoji]['count'] += removed_count
                        stats['emojis_removed'][emoji]['overhead_removed'] += removed
                    else:
                        stats['emojis_removed'][emoji] = {
                            'count': removed_count,
                            'overhead_removed': removed
                        }

        # Calculate final statistics
        final_size = len(text)
        actual_removed = original_size - final_size

        stats['final_size'] = final_size
        stats['actual_removed'] = actual_removed
        stats['bytes_overhead_removed'] = bytes_removed

        return text, stats


def main():
    """Apply selective emoji removal to reach target"""
    from pathlib import Path

    input_path = Path(__file__).parent.parent.parent / "outputs" / "final_optimized.txt"
    output_path = Path(__file__).parent.parent.parent / "outputs" / "final_target_achieved.txt"

    if not input_path.exists():
        print(f"❌ ERROR: Input file not found: {input_path}")
        return 1

    print("=" * 80)
    print("🎨 SELECTIVE EMOJI REMOVER - Final Push to <40,000")
    print("=" * 80)
    print()

    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    original_size = len(text)
    target = 40_000
    need_to_remove = original_size - target

    print(f"📖 Input: {input_path}")
    print(f"📊 Current size: {original_size:,} chars")
    print(f"🎯 Target: ≤{target:,} chars")
    print(f"⚠️  Need to remove: {need_to_remove} chars")
    print()

    # Remove emojis selectively
    remover = SelectiveEmojiRemover(target_reduction=need_to_remove + 10)  # +10 for safety
    optimized, stats = remover.remove(text)

    print("✅ Selective removal complete:")
    print(f"   Input:  {original_size:,} chars")
    print(f"   Output: {stats['final_size']:,} chars")
    print(f"   Removed: {stats['actual_removed']:,} chars")
    print()

    print("📊 Emojis removed:")
    for emoji, data in stats['emojis_removed'].items():
        print(f"   {emoji} : {data['count']} occurrences (saved {data['overhead_removed']} bytes overhead)")
    print()

    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(optimized)

    print(f"💾 Saved to: {output_path}")
    print()

    # Check target
    print("=" * 80)
    print("🎯 FINAL TARGET CHECK:")
    print("=" * 80)
    print(f"Target: ≤{target:,} chars")
    print(f"Result: {stats['final_size']:,} chars")

    if stats['final_size'] <= target:
        gap = target - stats['final_size']
        print(f"✅ TARGET ACHIEVED! (under by {gap} chars)")
        print()
        print("🏆 MISSION COMPLETE!")
        return 0
    else:
        gap = stats['final_size'] - target
        print(f"⚠️  Still {gap} chars over target")
        return 1


if __name__ == '__main__':
    exit(main())
