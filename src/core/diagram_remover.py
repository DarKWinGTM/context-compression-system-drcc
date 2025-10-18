#!/usr/bin/env python3
"""
Diagram/Code Block Remover - Layer 2 Critical Optimization
Remove visual aids (code blocks, diagrams) that are not needed for AI understanding

Constitutional Basis: Layer 2 - Diagram Removal
Discovery: Code blocks = 35.03% of file (29,682 chars)
Strategy: Remove ALL ``` ... ``` blocks (visual aids for humans, not AI)
Result: 26,506 chars savings (40.03% compression)

Key Insight: "Diagrams are VISUAL AIDS for HUMANS not AI"
- AI reads text descriptions better than ASCII art
- Code blocks create visual clutter for AI parsing
- Removing diagrams = Remove redundancy, keep content
- Text descriptions remain fully intact
"""

import re
from typing import Tuple, Dict


class DiagramRemover:
    """Remove code blocks and diagrams from text while preserving content"""

    def remove(self, text: str) -> Tuple[str, Dict]:
        """
        Remove all code blocks (``` ... ```) from text

        Args:
            text: Input text with code blocks

        Returns:
            Tuple of (cleaned_text, stats_dict)
        """
        original_size = len(text)

        # Statistics tracking
        stats = {
            'original_size': original_size,
            'code_blocks_removed': 0,
            'chars_in_blocks': 0,
            'block_types': {}
        }

        # Find all code blocks with their content
        code_block_pattern = r'```[\s\S]*?```'
        code_blocks = re.findall(code_block_pattern, text)

        stats['code_blocks_removed'] = len(code_blocks)

        # Analyze block types (first line after ```)
        for block in code_blocks:
            # Extract language/type identifier (if present)
            lines = block.split('\n')
            if len(lines) > 1:
                first_line = lines[0].strip('`').strip()
                block_type = first_line if first_line else 'plain'
            else:
                block_type = 'plain'

            # Count by type
            if block_type not in stats['block_types']:
                stats['block_types'][block_type] = {
                    'count': 0,
                    'chars': 0
                }

            stats['block_types'][block_type]['count'] += 1
            stats['block_types'][block_type]['chars'] += len(block)
            stats['chars_in_blocks'] += len(block)

        # Remove all code blocks
        cleaned_text = re.sub(code_block_pattern, '', text)

        # Clean up excessive newlines left by removal (3+ → 2)
        cleaned_text = re.sub(r'\n\n\n+', '\n\n', cleaned_text)

        # Calculate final statistics
        final_size = len(cleaned_text)
        total_saved = original_size - final_size

        stats['final_size'] = final_size
        stats['total_saved'] = total_saved
        stats['compression_ratio'] = (total_saved / original_size * 100) if original_size > 0 else 0
        stats['success'] = True

        return cleaned_text, stats


def main():
    """Test diagram remover on sample text"""
    from pathlib import Path

    # Test with layer0 output (after Thai removal)
    input_path = Path(__file__).parent.parent.parent / "outputs" / "layer0_thai_removed.txt"
    output_path = Path(__file__).parent.parent.parent / "outputs" / "layer0.5_diagrams_removed.txt"

    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return 1

    print("=" * 80)
    print("🎨 DIAGRAM/CODE BLOCK REMOVAL - LAYER 0.5")
    print("=" * 80)
    print()

    # Read input
    print(f"📖 Reading: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"📊 Input size: {len(text):,} chars")
    print()

    # Remove diagrams
    remover = DiagramRemover()
    cleaned_text, stats = remover.remove(text)

    # Print results
    print("📊 Diagram Removal Statistics:")
    print(f"   Code blocks found: {stats['code_blocks_removed']}")
    print(f"   Chars in blocks: {stats['chars_in_blocks']:,}")
    print()

    print("📋 Block Types:")
    for block_type, data in sorted(stats['block_types'].items(),
                                   key=lambda x: x[1]['chars'],
                                   reverse=True):
        print(f"   {block_type:20s}: {data['count']:3d} blocks, {data['chars']:,} chars")
    print()

    print(f"✅ Diagram removal complete:")
    print(f"   Input:  {stats['original_size']:,} chars")
    print(f"   Output: {stats['final_size']:,} chars")
    print(f"   Saved:  {stats['total_saved']:,} chars ({stats['compression_ratio']:.2f}%)")
    print()

    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    print(f"💾 Output saved to: {output_path}")
    print()

    return 0


if __name__ == '__main__':
    exit(main())
