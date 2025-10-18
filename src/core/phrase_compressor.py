#!/usr/bin/env python3
"""
Phrase Compressor - Layer 4
Phrase-level compression using €code format
"""

import re
import json
from typing import Tuple, Dict
from pathlib import Path


class PhraseCompressor:
    """
    Phrase Compressor: Multi-word phrase compression
    Uses €code format (greedy longest-match algorithm)
    """

    def __init__(self, phrase_dict=None):
        """
        Initialize phrase compressor.
        
        Args:
            phrase_dict: Dictionary of phrases (if None, load from file for backward compatibility)
        """
        if phrase_dict is not None:
            # Use provided dictionary (inline mode - preferred)
            self.phrase_dict = phrase_dict
        else:
            # Load from file (backward compatibility)
            phrase_dict_path = Path(__file__).parent.parent.parent / "outputs" / "phrase_dictionary_optimized.json"

            if phrase_dict_path.exists():
                with open(phrase_dict_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.phrase_dict = data['phrase_dictionary']
            else:
                # Fallback to non-optimized version
                phrase_dict_path = Path(__file__).parent.parent.parent / "outputs" / "phrase_dictionary.json"
                if phrase_dict_path.exists():
                    with open(phrase_dict_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.phrase_dict = data['phrase_dictionary']
                else:
                    self.phrase_dict = {}

    def compress(self, text: str) -> Tuple[str, Dict]:
        """
        Compress phrases using greedy longest-match algorithm

        Args:
            text: Text after template compression

        Returns:
            (compressed_text, compression_stats)
        """
        original_size = len(text)
        result = text

        if not self.phrase_dict:
            return result, {
                'original_size': original_size,
                'final_size': original_size,
                'chars_saved': 0,
                'compression_ratio': 0.0,
                'phrases_replaced': 0
            }

        phrases_replaced = 0
        chars_saved = 0

        # Create reverse mapping: phrase -> code
        phrase_to_code = {phrase: code for code, phrase in self.phrase_dict.items()}

        # Sort phrases by length (longest first) for greedy matching
        sorted_phrases = sorted(phrase_to_code.keys(), key=len, reverse=True)

        for phrase in sorted_phrases:
            code = phrase_to_code[phrase]

            # Escape special regex characters in phrase
            escaped_phrase = re.escape(phrase)

            # Count occurrences (case-insensitive)
            count = len(re.findall(escaped_phrase, result, re.IGNORECASE))

            if count > 0:
                # Replace with code (use simple €code format, case-insensitive)
                result = re.sub(escaped_phrase, code, result, flags=re.IGNORECASE)
                phrases_replaced += count
                # Calculate savings: (phrase_length - code_length) * occurrences
                chars_saved += (len(phrase) - len(code)) * count

        final_size = len(result)

        stats = {
            'original_size': original_size,
            'final_size': final_size,
            'chars_saved': chars_saved,
            'compression_ratio': (chars_saved / original_size * 100) if original_size > 0 else 0.0,
            'phrases_replaced': phrases_replaced,
            'phrase_dict': self.phrase_dict
        }

        return result, stats

    def decompress(self, compressed_text: str) -> str:
        """
        Decompress text (restore phrases)

        Args:
            compressed_text: Compressed text with €code format

        Returns:
            Decompressed text
        """
        result = compressed_text

        # Restore phrases
        for code, phrase in self.phrase_dict.items():
            result = result.replace(code, phrase)

        return result


def main():
    """Test Phrase Compressor"""
    print("🚀 Testing Phrase Compressor (Layer 4)")
    print("=" * 80)
    print()

    # Load layer3 output (after template compression)
    layer3_path = Path(__file__).parent.parent.parent / "outputs" / "layer3_templates.txt"

    if not layer3_path.exists():
        print(f"❌ ERROR: Layer 3 output not found: {layer3_path}")
        print("   Run compress_full_pipeline.py first to generate layer3_templates.txt")
        return 1

    print(f"📖 Reading: {layer3_path}")
    with open(layer3_path, 'r', encoding='utf-8') as f:
        layer3_text = f.read()

    original_size = len(layer3_text)
    print(f"📊 Layer 3 size: {original_size:,} chars")
    print()

    # Compress
    compressor = PhraseCompressor()
    compressed_text, stats = compressor.compress(layer3_text)

    # Display results
    print("=" * 80)
    print("📊 LAYER 4 COMPRESSION RESULTS:")
    print("=" * 80)
    print()
    print(f"Input size (Layer 3):    {stats['original_size']:>10,} chars (100.0%)")
    print(f"Output size (Layer 4):   {stats['final_size']:>10,} chars ({100 - stats['compression_ratio']:>5.2f}%)")
    print()
    print(f"Phrases replaced:        {stats['phrases_replaced']:>10,} occurrences")
    print(f"Chars saved:             {stats['chars_saved']:>10,} chars")
    print(f"Compression ratio:       {stats['compression_ratio']:>10.2f}%")
    print()

    # Test lossless
    print("🔄 Testing lossless decompression...")
    decompressed_text = compressor.decompress(compressed_text)

    if decompressed_text == layer3_text:
        print("✅ LOSSLESS VERIFIED: Decompression successful!")
    else:
        print("❌ LOSSLESS FAILED: Decompression mismatch!")
        print(f"   Original length: {len(layer3_text)}")
        print(f"   Decompressed length: {len(decompressed_text)}")

    # Save output
    output_path = Path(__file__).parent.parent.parent / "outputs" / "layer4_phrases.txt"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(compressed_text)

    print()
    print(f"💾 Layer 4 output saved to: {output_path}")

    # Save stats
    stats_path = Path(__file__).parent.parent.parent / "outputs" / "layer4_stats.json"
    # Remove phrase_dict from stats before saving (too large)
    stats_to_save = {k: v for k, v in stats.items() if k != 'phrase_dict'}
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats_to_save, f, indent=2)

    print(f"📊 Stats saved to: {stats_path}")
    print()

    return 0


if __name__ == '__main__':
    exit(main())
