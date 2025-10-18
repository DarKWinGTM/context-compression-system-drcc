#!/usr/bin/env python3
"""
Template Compressor for Templates++
Hybrid compression: Smart Dictionary v2 + Template patterns
"""

import re
import json
import sys
from typing import Tuple, Dict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.phrase_compressor import PhraseCompressor
from src.core.word_compressor import WordCompressor


class TemplateCompressor:
    """
    Template Compressor: Multi-layer compression with inline dictionaries
    1. Template compression (T codes)
    2. Phrase compression (€ codes)
    3. Word compression ($ and ฿ codes)
    """

    def __init__(self, template_dict=None, phrase_dict=None, word_dict=None):
        """
        Initialize template compressor with inline dictionaries.

        Args:
            template_dict: Dictionary of templates
            phrase_dict: Dictionary of phrases
            word_dict: Dictionary of words
        """
        # Use provided dictionaries (inline mode - preferred)
        self.template_dict = template_dict or {}
        self.phrase_dict = phrase_dict or {}
        self.word_dict = word_dict or {}

        # Initialize phrase and word compressors with inline dictionaries
        self.phrase_compressor = PhraseCompressor(phrase_dict=self.phrase_dict)
        self.word_compressor = WordCompressor(word_dict=self.word_dict)

    def compress(self, text: str) -> Tuple[str, Dict]:
        """
        Compress text using templates, phrases, then words

        Args:
            text: Original text

        Returns:
            (compressed_text, compression_stats)
        """
        original_size = len(text)
        result = text

        # Step 1: Template compression (T codes)
        result, template_stats = self._compress_templates(result)

        # Step 2: Phrase compression (€ codes)
        result, phrase_stats = self.phrase_compressor.compress(result)

        # Step 3: Word compression ($ and ฿ codes)
        result, word_stats = self.word_compressor.compress(result)

        # Calculate total stats
        final_size = len(result)
        compression_stats = {
            'original_size': original_size,
            'after_templates': template_stats.get('size_after', len(result)) if template_stats else len(result),
            'after_phrases': len(result),
            'final_size': final_size,
            'template_saved': template_stats.get('chars_saved', 0) if template_stats else 0,
            'phrase_saved': phrase_stats.get('chars_saved', 0),
            'word_saved': word_stats.get('chars_saved', 0),
            'total_saved': original_size - final_size,
            'compression_ratio': (original_size - final_size) / original_size * 100,
            'template_count': template_stats.get('templates_replaced', 0) if template_stats else 0,
            'phrase_count': phrase_stats.get('phrases_replaced', 0),
            'word_count': word_stats.get('words_replaced', 0),
            # Add dictionaries for decompression
            'template_dict': self.template_dict,
            'phrase_dict': self.phrase_dict,
            'word_dict': self.word_dict
        }

        return result, compression_stats

    def _compress_templates(self, text: str) -> Tuple[str, Dict]:
        """
        Compress templates using T codes

        Returns:
            (compressed_text, stats)
        """
        if not self.template_dict:
            return text, {}

        result = text
        templates_replaced = 0
        chars_saved = 0

        # Create reverse mapping: pattern -> code
        pattern_to_code = {pattern: code for code, pattern in self.template_dict.items()}

        # Sort patterns by length (longest first) for greedy matching
        sorted_patterns = sorted(pattern_to_code.keys(), key=len, reverse=True)

        for pattern in sorted_patterns:
            code = pattern_to_code[pattern]

            # Escape special regex characters in pattern
            escaped_pattern = re.escape(pattern)

            # Count occurrences
            count = len(re.findall(escaped_pattern, result))

            if count > 0:
                # Replace with template code
                # Use code format: T1, T2, etc. (2-3 chars)
                result = re.sub(escaped_pattern, code, result)
                templates_replaced += count
                # Calculate savings: (pattern_length - code_length) * occurrences
                chars_saved += (len(pattern) - len(code)) * count

        size_after = len(result)

        stats = {
            'templates_replaced': templates_replaced,
            'chars_saved': chars_saved,
            'size_after': size_after
        }

        return result, stats

    def decompress(self, compressed_text: str) -> str:
        """
        Decompress text (restore templates, phrases, and words)

        Args:
            compressed_text: Compressed text with T/€/$/฿ codes

        Returns:
            Original text
        """
        result = compressed_text

        # Step 1: Restore word compression ($ and ฿ codes)
        result = self.word_compressor.decompress(result)

        # Step 2: Restore phrase compression (€ codes)
        result = self.phrase_compressor.decompress(result)

        # Step 3: Restore templates (T codes)
        # Sort by code number to handle T10, T11, etc. before T1
        sorted_template_codes = sorted(self.template_dict.items(),
                                       key=lambda x: int(x[0][1:]),
                                       reverse=True)

        for code, pattern in sorted_template_codes:
            result = result.replace(code, pattern)

        return result


def main():
    """Test Template Compressor"""
    print("🚀 Testing Template Compressor (Templates++ & Smart Dictionary v2)")
    print("=" * 80)
    print()

    # Load source file
    template_path = Path("/home/node/workplace/AWCLOUD/TEMPLATE/CONTENT/CONTEXT.TEMPLATE.md")

    if not template_path.exists():
        print(f"❌ ERROR: Source file not found: {template_path}")
        return 1

    print(f"📖 Reading: {template_path}")
    with open(template_path, 'r', encoding='utf-8') as f:
        original_text = f.read()

    original_size = len(original_text)
    print(f"📊 Original size: {original_size:,} chars")
    print()

    # Compress
    compressor = TemplateCompressor()
    compressed_text, stats = compressor.compress(original_text)

    # Display results
    print("=" * 80)
    print("📊 COMPRESSION RESULTS:")
    print("=" * 80)
    print()
    print(f"Original size:           {stats['original_size']:>10,} chars (100.0%)")
    print(f"After templates:         {stats['after_templates']:>10,} chars ({(stats['original_size'] - stats['after_templates']) / stats['original_size'] * 100:>5.2f}% saved)")
    print(f"After Smart Dict:        {stats['final_size']:>10,} chars ({(stats['after_templates'] - stats['final_size']) / stats['after_templates'] * 100:>5.2f}% saved)")
    print()
    print(f"Template compression:    {stats['template_saved']:>10,} chars ({stats['template_count']:,} replacements)")
    print(f"Phrase compression:      {stats['phrase_saved']:>10,} chars ({stats['phrase_count']:,} replacements)")
    print(f"Word compression:        {stats['word_saved']:>10,} chars ({stats['word_count']:,} replacements)")
    print(f"Total saved:             {stats['total_saved']:>10,} chars")
    print(f"Compression ratio:       {stats['compression_ratio']:>10.2f}%")
    print()

    # Test lossless
    print("🔄 Testing lossless decompression...")
    decompressed_text = compressor.decompress(compressed_text)

    if decompressed_text == original_text:
        print("✅ LOSSLESS VERIFIED: Decompression successful!")
    else:
        print("❌ LOSSLESS FAILED: Decompression mismatch!")
        print(f"   Original length: {len(original_text)}")
        print(f"   Decompressed length: {len(decompressed_text)}")
        # Find first difference
        for i, (c1, c2) in enumerate(zip(original_text, decompressed_text)):
            if c1 != c2:
                print(f"   First diff at position {i}: '{c1}' != '{c2}'")
                print(f"   Context: ...{original_text[max(0,i-20):i+20]}...")
                break

    # Save compressed output
    output_path = Path(__file__).parent.parent.parent / "outputs" / "compressed_templates_plus.txt"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(compressor.generate_header())
        f.write(compressed_text)

    print()
    print(f"💾 Compressed output saved to: {output_path}")

    # Save stats
    stats_path = Path(__file__).parent.parent.parent / "outputs" / "templates_plus_stats.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    print(f"📊 Stats saved to: {stats_path}")
    print()

    # Check against target
    target_size = 40_000
    print("=" * 80)
    print("🎯 TARGET VALIDATION:")
    print("=" * 80)
    print()
    print(f"Target size:             {target_size:>10,} chars")
    print(f"Actual size:             {stats['final_size']:>10,} chars")

    if stats['final_size'] <= target_size:
        print(f"✅ TARGET MET! (under by {target_size - stats['final_size']:,} chars)")
    else:
        gap = stats['final_size'] - target_size
        gap_percent = gap / original_size * 100
        print(f"⚠️  TARGET MISSED (over by {gap:,} chars / {gap_percent:.2f}%)")
        print()
        print("💡 Need additional compression layers:")
        print(f"   - Current: {stats['compression_ratio']:.2f}%")
        print(f"   - Required: {(1 - target_size/original_size)*100:.2f}%")
        print(f"   - Gap: {gap_percent:.2f}%")

    print()
    return 0


if __name__ == '__main__':
    exit(main())
