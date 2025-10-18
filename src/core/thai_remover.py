#!/usr/bin/env python3
"""
Thai Content Remover - Layer 1 (Highest Priority)
Remove Thai language translations from bilingual documents

Constitutional Basis: PART III Principle IV - Reality-Based Systematic Analysis
Rationale: Thai content is DUPLICATION (translations), not unique content.
          Simple removal is more effective than compression (21.85% savings).

Process Order (CRITICAL):
Layer 1: Thai Removal (21.85%) ← THIS MODULE
Layer 2: Diagram Removal (40.03%)
Layer 3-5: Templates + Phrases + Words (39.80%)
Layer 6-7: Markdown + Whitespace + Emoji
"""

import re
from pathlib import Path
from typing import Tuple, Dict


class ThaiContentRemover:
    """Remove Thai language content from bilingual documents"""

    def __init__(self):
        """Initialize Thai Content Remover"""
        # Thai Unicode range: U+0E00-U+0E7F
        self.thai_pattern = r'[\u0E00-\u0E7F]+'

    def remove(self, text: str) -> Tuple[str, Dict]:
        """
        Remove Thai content from text

        Args:
            text: Source text with Thai translations

        Returns:
            Tuple of (cleaned_text, stats_dict)
        """
        original_size = len(text)

        # Track statistics
        stats = {
            'original_size': original_size,
            'patterns_removed': {},
            'total_thai_chars': 0,
            'total_overhead': 0
        }

        # Pattern 1: Header translations (markdown headers with Thai on next line)
        # Example: **Constitutional Basis:**\n**รากฐานรัธรีมนูญ**
        pattern1 = r'\*\*([^\*]+)\*\*\n\*\*[\u0E00-\u0E7F]+\*\*'
        matches1 = re.findall(pattern1, text)
        text = re.sub(pattern1, r'**\1**', text)
        stats['patterns_removed']['header_translations'] = len(matches1)

        # Pattern 2: Standalone Thai headers (bold Thai on separate line)
        # Example: **ข้อมูลผู้ใช้ส่วนบุคคล**
        pattern2 = r'\n\*\*[\u0E00-\u0E7F\s]+\*\*(?=\n)'
        matches2 = re.findall(pattern2, text)
        text = re.sub(pattern2, '', text)
        stats['patterns_removed']['standalone_thai_headers'] = len(matches2)

        # Pattern 3: Inline translations in parentheses with Thai
        # Example: (คำอธิบายไทย) or (Context/คำอธิบาย)
        pattern3 = r'\s*\([^)]*[\u0E00-\u0E7F][^)]*\)'
        matches3 = re.findall(pattern3, text)
        text = re.sub(pattern3, '', text)
        stats['patterns_removed']['inline_translations'] = len(matches3)

        # Pattern 4: Mixed Thai-English lines - Remove Thai portions from same line
        # Example: `./THIS.md` เป็น **Universal Placeholder** (ตัวแทนสากล) ที่ใช้แทน...
        # This is tricky - need to preserve English while removing Thai
        def clean_mixed_line(match):
            line = match.group(0)
            # Remove Thai characters and surrounding punctuation
            cleaned = re.sub(r'[\u0E00-\u0E7F]+', '', line)
            # Clean up extra spaces and punctuation
            cleaned = re.sub(r'\s+', ' ', cleaned)
            cleaned = re.sub(r'\s*→\s*', ' → ', cleaned)  # Preserve arrows
            return cleaned.strip()

        # Apply to lines that contain both English and Thai
        lines = text.split('\n')
        cleaned_lines = []
        mixed_count = 0

        for line in lines:
            if re.search(r'[\u0E00-\u0E7F]', line):
                # Line contains Thai
                if re.search(r'[a-zA-Z]', line):
                    # Also contains English - it's a mixed line
                    cleaned_line = re.sub(r'[\u0E00-\u0E7F]+', '', line)
                    # Clean up extra spaces
                    cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()
                    # Only keep if there's still content after Thai removal
                    if cleaned_line and cleaned_line not in ['**', '-', '→']:
                        cleaned_lines.append(cleaned_line)
                        mixed_count += 1
                # else: pure Thai line, skip it
            else:
                # No Thai, keep as is
                cleaned_lines.append(line)

        text = '\n'.join(cleaned_lines)
        stats['patterns_removed']['mixed_bilingual_lines'] = mixed_count

        # Cleanup: Remove extra whitespace and blank lines
        # Replace 3+ newlines with 2 newlines
        text = re.sub(r'\n\n\n+', '\n\n', text)
        # Remove trailing spaces
        text = re.sub(r' +\n', '\n', text)
        # Remove lines with only punctuation
        text = re.sub(r'\n[-–—→]+\n', '\n', text)

        # Count remaining Thai characters (for verification)
        remaining_thai = len(re.findall(self.thai_pattern, text))

        # Calculate final statistics
        final_size = len(text)
        total_removed = original_size - final_size

        stats['final_size'] = final_size
        stats['total_removed'] = total_removed
        stats['compression_ratio'] = (total_removed / original_size * 100) if original_size > 0 else 0
        stats['remaining_thai_chars'] = remaining_thai
        stats['success'] = remaining_thai == 0  # Success if no Thai remains

        return text, stats

    def analyze(self, text: str) -> Dict:
        """
        Analyze Thai content without removing

        Args:
            text: Source text with Thai translations

        Returns:
            Dictionary with analysis results
        """
        # Count Thai characters
        thai_matches = re.findall(self.thai_pattern, text)
        total_thai_chars = sum(len(match) for match in thai_matches)
        thai_segments = len(thai_matches)

        # Estimate formatting overhead (average 6 chars per segment: **, (), \n)
        formatting_overhead = thai_segments * 6

        # Pattern analysis
        patterns = {
            'header_translations': len(re.findall(r'\*\*([^\*]+)\*\*\n\*\*[\u0E00-\u0E7F]+\*\*', text)),
            'inline_translations': len(re.findall(r'\s*\([\u0E00-\u0E7F\s]+\)', text)),
            'list_translations': len(re.findall(r'(\*\*[^:]+\*\*:?)\s*\([\u0E00-\u0E7F]+\)', text)),
            'standalone_headers': len(re.findall(r'\n\*\*[\u0E00-\u0E7F\s]+\*\*(?=\n)', text))
        }

        return {
            'total_thai_chars': total_thai_chars,
            'thai_segments': thai_segments,
            'formatting_overhead': formatting_overhead,
            'total_savings_estimate': total_thai_chars + formatting_overhead,
            'patterns': patterns,
            'original_size': len(text)
        }


def main():
    """Test Thai Content Remover on actual CONTEXT.TEMPLATE.md"""

    source_path = Path("/home/node/workplace/AWCLOUD/TEMPLATE/CONTENT/CONTEXT.TEMPLATE.md")

    if not source_path.exists():
        print(f"❌ ERROR: Source file not found: {source_path}")
        return 1

    print("=" * 80)
    print("🗑️  THAI CONTENT REMOVER - Layer 1 (Highest Priority)")
    print("=" * 80)
    print()

    # Read source file
    print(f"📖 Reading: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        text = f.read()

    original_size = len(text)
    print(f"📊 Original size: {original_size:,} chars")
    print()

    # Initialize remover
    remover = ThaiContentRemover()

    # Analyze before removal
    print("🔍 Analyzing Thai content...")
    analysis = remover.analyze(text)

    print()
    print("=" * 80)
    print("📊 ANALYSIS RESULTS:")
    print("=" * 80)
    print(f"Thai characters:         {analysis['total_thai_chars']:,} chars")
    print(f"Thai segments:           {analysis['thai_segments']:,} segments")
    print(f"Formatting overhead:     {analysis['formatting_overhead']:,} chars")
    print(f"Estimated savings:       {analysis['total_savings_estimate']:,} chars ({analysis['total_savings_estimate']/original_size*100:.2f}%)")
    print()
    print("Pattern breakdown:")
    for pattern_name, count in analysis['patterns'].items():
        print(f"  - {pattern_name:30s}: {count:,} occurrences")
    print()

    # Perform removal
    print("🗑️  Removing Thai content...")
    cleaned_text, stats = remover.remove(text)

    print()
    print("=" * 80)
    print("✅ REMOVAL RESULTS:")
    print("=" * 80)
    print(f"Original size:           {stats['original_size']:,} chars")
    print(f"Final size:              {stats['final_size']:,} chars")
    print(f"Total removed:           {stats['total_removed']:,} chars")
    print(f"Compression ratio:       {stats['compression_ratio']:.2f}%")
    print(f"Remaining Thai chars:    {stats['remaining_thai_chars']:,}")
    print(f"Success (no Thai left):  {'✅ YES' if stats['success'] else '❌ NO'}")
    print()

    print("Patterns removed:")
    for pattern_name, count in stats['patterns_removed'].items():
        print(f"  - {pattern_name:30s}: {count:,} occurrences")
    print()

    # Save cleaned output
    output_path = Path(__file__).parent.parent.parent / "outputs" / "thai_removed.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    print(f"💾 Cleaned text saved to: {output_path}")
    print()

    # Validation: Compare with projection
    print("=" * 80)
    print("📊 VALIDATION vs PROJECTION:")
    print("=" * 80)

    projected_savings = 22_062  # From analyze_thai_content.py
    actual_savings = stats['total_removed']
    difference = actual_savings - projected_savings
    accuracy = (actual_savings / projected_savings * 100) if projected_savings > 0 else 0

    print(f"Projected savings:       {projected_savings:,} chars (26.04%)")
    print(f"Actual savings:          {actual_savings:,} chars ({stats['compression_ratio']:.2f}%)")
    print(f"Difference:              {difference:+,} chars")
    print(f"Projection accuracy:     {accuracy:.1f}%")
    print()

    if abs(difference) <= 1000:  # Within 1000 chars tolerance
        print("✅ VALIDATION PASSED: Actual savings match projection")
    else:
        print(f"⚠️  VALIDATION WARNING: Difference of {abs(difference):,} chars")
        if difference > 0:
            print("   → Removed more than projected (better compression)")
        else:
            print("   → Removed less than projected (check patterns)")

    print()
    print("=" * 80)
    print("🎯 LAYER 1 COMPLETE - Ready for Layer 2 (Diagram Removal)")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    exit(main())
