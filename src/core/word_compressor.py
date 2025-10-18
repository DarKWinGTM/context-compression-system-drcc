#!/usr/bin/env python3
"""
Word Compressor - Layer 5
Single-word compression using $Code and ฿code format
"""

import re
import json
from typing import Tuple, Dict
from pathlib import Path


class WordCompressor:
    """
    Word Compressor: Single-word compression
    Uses $Code (frequent) and ฿code (less frequent) formats
    """

    def __init__(self, word_dict=None):
        """
        Initialize word compressor.
        
        Args:
            word_dict: Dictionary of words (if None, load from file for backward compatibility)
        """
        if word_dict is not None:
            # Use provided dictionary (inline mode - preferred)
            self.word_dict = word_dict
        else:
            # Load from file (backward compatibility)
            dict_path = Path(__file__).parent.parent.parent / "outputs" / "dictionary.json"

            if dict_path.exists():
                with open(dict_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract word mappings from all tiers
                    self.word_dict = {}
                    if 'tier1' in data:
                        self.word_dict.update(data['tier1'])
                    if 'tier2' in data:
                        self.word_dict.update(data['tier2'])
                    if 'tier3' in data:
                        self.word_dict.update(data['tier3'])
            else:
                self.word_dict = {}

    def compress(self, text: str) -> Tuple[str, Dict]:
        """
        Compress individual words using $ and ฿ codes

        Args:
            text: Text after phrase compression

        Returns:
            (compressed_text, compression_stats)
        """
        original_size = len(text)
        result = text

        if not self.word_dict:
            return result, {
                'original_size': original_size,
                'final_size': original_size,
                'chars_saved': 0,
                'compression_ratio': 0.0,
                'words_replaced': 0
            }

        words_replaced = 0
        chars_saved = 0

        # Create reverse mapping: word -> code
        word_to_code = {word: code for code, word in self.word_dict.items()}

        # Sort words by length (longest first) to avoid partial replacements
        sorted_words = sorted(word_to_code.keys(), key=len, reverse=True)

        for word in sorted_words:
            code = word_to_code[word]

            # Use word boundary matching to avoid partial replacements
            pattern = r'\b' + re.escape(word) + r'\b'

            # Count occurrences
            count = len(re.findall(pattern, result, re.IGNORECASE))

            if count > 0:
                # Replace all occurrences (case-insensitive)
                result = re.sub(pattern, code, result, flags=re.IGNORECASE)
                words_replaced += count
                chars_saved += (len(word) - len(code)) * count

        final_size = len(result)

        stats = {
            'original_size': original_size,
            'final_size': final_size,
            'chars_saved': chars_saved,
            'compression_ratio': (chars_saved / original_size * 100) if original_size > 0 else 0.0,
            'words_replaced': words_replaced,
            'word_dict': self.word_dict
        }

        return result, stats

    def decompress(self, compressed_text: str) -> str:
        """
        Decompress text (restore words)

        Args:
            compressed_text: Compressed text with $/฿ codes

        Returns:
            Decompressed text
        """
        result = compressed_text

        # Sort by code length to handle longer codes first
        sorted_word_codes = sorted(self.word_dict.items(),
                                   key=lambda x: (len(x[0]), x[0]),
                                   reverse=True)

        for code, word in sorted_word_codes:
            result = result.replace(code, word)

        return result


def main():
    """Test Word Compressor"""
    print("🚀 Testing Word Compressor (Layer 5)")
    print("=" * 80)
    print()

    # Load layer4 output (after phrase compression)
    layer4_path = Path(__file__).parent.parent.parent / "outputs" / "layer4_phrases.txt"

    if not layer4_path.exists():
        print(f"❌ ERROR: Layer 4 output not found: {layer4_path}")
        print("   Run phrase_compressor.py first to generate layer4_phrases.txt")
        return 1

    print(f"📖 Reading: {layer4_path}")
    with open(layer4_path, 'r', encoding='utf-8') as f:
        layer4_text = f.read()

    original_size = len(layer4_text)
    print(f"📊 Layer 4 size: {original_size:,} chars")
    print()

    # Compress
    compressor = WordCompressor()
    compressed_text, stats = compressor.compress(layer4_text)

    # Display results
    print("=" * 80)
    print("📊 LAYER 5 COMPRESSION RESULTS:")
    print("=" * 80)
    print()
    print(f"Input size (Layer 4):    {stats['original_size']:>10,} chars (100.0%)")
    print(f"Output size (Layer 5):   {stats['final_size']:>10,} chars ({100 - stats['compression_ratio']:>5.2f}%)")
    print()
    print(f"Words replaced:          {stats['words_replaced']:>10,} occurrences")
    print(f"Chars saved:             {stats['chars_saved']:>10,} chars")
    print(f"Compression ratio:       {stats['compression_ratio']:>10.2f}%")
    print()

    # Test lossless
    print("🔄 Testing lossless decompression...")
    decompressed_text = compressor.decompress(compressed_text)

    if decompressed_text == layer4_text:
        print("✅ LOSSLESS VERIFIED: Decompression successful!")
    else:
        print("❌ LOSSLESS FAILED: Decompression mismatch!")
        print(f"   Original length: {len(layer4_text)}")
        print(f"   Decompressed length: {len(decompressed_text)}")

    # Save output
    output_path = Path(__file__).parent.parent.parent / "outputs" / "layer5_words.txt"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(compressed_text)

    print()
    print(f"💾 Layer 5 output saved to: {output_path}")

    # Save stats
    stats_path = Path(__file__).parent.parent.parent / "outputs" / "layer5_stats.json"
    # Remove word_dict from stats before saving (too large)
    stats_to_save = {k: v for k, v in stats.items() if k != 'word_dict'}
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats_to_save, f, indent=2)

    print(f"📊 Stats saved to: {stats_path}")
    print()

    return 0


if __name__ == '__main__':
    exit(main())
