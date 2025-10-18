#!/usr/bin/env python3
"""
Smart Dictionary v2 - Phrase + Word Compression
Extends original dictionary with phrase-level compression
"""

import re
import json
from typing import Tuple, Dict
from pathlib import Path


class SmartDictionaryV2:
    """
    Smart Dictionary v2: Two-tier compression
    1. Phrase compression (€ codes)
    2. Word compression ($ and ฿ codes)
    """

    def __init__(self, use_optimized=True):
        # Load phrase dictionary
        if use_optimized:
            phrase_dict_path = Path(__file__).parent.parent.parent / "outputs" / "phrase_dictionary_optimized.json"
        else:
            phrase_dict_path = Path(__file__).parent.parent.parent / "outputs" / "phrase_dictionary.json"

        if phrase_dict_path.exists():
            with open(phrase_dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.phrase_dict = data['phrase_dictionary']
        else:
            self.phrase_dict = {}

        # Word dictionary (from original implementation)
        self.word_dict = {}
        self._build_word_dictionary()

    def _build_word_dictionary(self):
        """Build word-level dictionary from analysis"""
        # Load existing dictionary analysis if available
        dict_path = Path(__file__).parent.parent.parent / "outputs" / "dictionary.json"

        if dict_path.exists():
            with open(dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract word mappings
                if 'tier1' in data:
                    self.word_dict.update(data['tier1'])
                if 'tier2' in data:
                    self.word_dict.update(data['tier2'])
                if 'tier3' in data:
                    self.word_dict.update(data['tier3'])
        else:
            # Use basic dictionary as fallback
            self.word_dict = {
                '$A': 'Constitutional',
                '$B': 'Basis',
                '$C': 'Authority',
                '$D': 'Implementation',
                '$E': 'Standards',
                '$F': 'Framework',
                '$G': 'Quality',
                '$H': 'Metrics',
                '$I': 'Principle',
                '$J': 'Analysis',
                # Add more basic words
            }

    def compress(self, text: str) -> Tuple[str, Dict]:
        """
        Compress text using phrase-first, then word-level compression

        Args:
            text: Original text

        Returns:
            (compressed_text, compression_stats)
        """
        original_size = len(text)
        result = text

        # Step 1: Phrase compression (€ codes) - GREEDY LONGEST MATCH
        result, phrase_stats = self._compress_phrases(result)

        # Step 2: Word compression ($ and ฿ codes)
        result, word_stats = self._compress_words(result)

        # Calculate total stats
        final_size = len(result)
        compression_stats = {
            'original_size': original_size,
            'after_phrases': len(result) if phrase_stats else original_size,
            'final_size': final_size,
            'phrase_saved': phrase_stats.get('chars_saved', 0) if phrase_stats else 0,
            'word_saved': word_stats.get('chars_saved', 0) if word_stats else 0,
            'total_saved': original_size - final_size,
            'compression_ratio': (original_size - final_size) / original_size * 100,
            'phrase_count': phrase_stats.get('phrases_replaced', 0) if phrase_stats else 0,
            'word_count': word_stats.get('words_replaced', 0) if word_stats else 0,
            # Add dictionaries for decompression
            'phrase_dict': self.phrase_dict,
            'word_dict': self.word_dict
        }

        return result, compression_stats

    def _compress_phrases(self, text: str) -> Tuple[str, Dict]:
        """
        Compress phrases using greedy longest-match algorithm
        Uses €code§ format (3 chars) to avoid overlapping - OPTIMIZED

        Returns:
            (compressed_text, stats)
        """
        if not self.phrase_dict:
            return text, {}

        result = text
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

            # Count occurrences
            count = len(re.findall(escaped_phrase, result))

            if count > 0:
                # OPTIMIZED: Use code§ format (3 chars instead of {code} = 4 chars)
                safe_code = f"{code}§"
                result = re.sub(escaped_phrase, safe_code, result)
                phrases_replaced += count
                # Calculate savings: (phrase_length - safe_code_length) * occurrences
                chars_saved += (len(phrase) - len(safe_code)) * count

        stats = {
            'phrases_replaced': phrases_replaced,
            'chars_saved': chars_saved
        }

        return result, stats

    def _compress_words(self, text: str) -> Tuple[str, Dict]:
        """
        Compress individual words using $ and ฿ codes

        Returns:
            (compressed_text, stats)
        """
        if not self.word_dict:
            return text, {}

        result = text
        words_replaced = 0
        chars_saved = 0

        # Create reverse mapping: word -> code
        word_to_code = {word: code for code, word in self.word_dict.items()}

        # Sort words by length (longest first)
        sorted_words = sorted(word_to_code.keys(), key=len, reverse=True)

        for word in sorted_words:
            code = word_to_code[word]

            # Use word boundary matching to avoid partial replacements
            pattern = r'\b' + re.escape(word) + r'\b'

            # Count occurrences
            count = len(re.findall(pattern, result))

            if count > 0:
                # Replace all occurrences
                result = re.sub(pattern, code, result)
                words_replaced += count
                chars_saved += (len(word) - len(code)) * count

        stats = {
            'words_replaced': words_replaced,
            'chars_saved': chars_saved
        }

        return result, stats

    def decompress(self, compressed_text: str) -> str:
        """
        Decompress text (restore phrases and words)
        Handles €code§ format (OPTIMIZED)

        Args:
            compressed_text: Compressed text with €code§ and $/฿ codes

        Returns:
            Original text
        """
        result = compressed_text

        # Step 1: Restore phrases (€code§ format) - OPTIMIZED
        for code, phrase in self.phrase_dict.items():
            safe_code = f"{code}§"
            result = result.replace(safe_code, phrase)

        # Step 2: Restore words ($ and ฿ codes)
        # Sort by length to handle longer codes first
        sorted_word_codes = sorted(self.word_dict.items(),
                                   key=lambda x: (len(x[0]), x[0]),
                                   reverse=True)

        for code, word in sorted_word_codes:
            result = result.replace(code, word)

        return result


def main():
    """Test Smart Dictionary v2"""
    print("🚀 Testing Smart Dictionary v2")
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
    compressor = SmartDictionaryV2()
    compressed_text, stats = compressor.compress(original_text)

    # Display results
    print("=" * 80)
    print("📊 COMPRESSION RESULTS:")
    print("=" * 80)
    print()
    print(f"Original size:        {stats['original_size']:>10,} chars (100.0%)")
    print(f"After phrases:        {stats['after_phrases']:>10,} chars ({(stats['original_size'] - stats['after_phrases']) / stats['original_size'] * 100:>5.2f}% saved)")
    print(f"After words:          {stats['final_size']:>10,} chars ({(stats['after_phrases'] - stats['final_size']) / stats['after_phrases'] * 100:>5.2f}% saved)")
    print()
    print(f"Phrase compression:   {stats['phrase_saved']:>10,} chars ({stats['phrase_count']:,} replacements)")
    print(f"Word compression:     {stats['word_saved']:>10,} chars ({stats['word_count']:,} replacements)")
    print(f"Total saved:          {stats['total_saved']:>10,} chars")
    print(f"Compression ratio:    {stats['compression_ratio']:>10.2f}%")
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
    output_path = Path(__file__).parent.parent.parent / "outputs" / "compressed_dict_v2.txt"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(compressor.generate_header())
        f.write(compressed_text)

    print()
    print(f"💾 Compressed output saved to: {output_path}")

    # Save stats
    stats_path = Path(__file__).parent.parent.parent / "outputs" / "dict_v2_stats.json"
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
    print(f"Target size:          {target_size:>10,} chars")
    print(f"Actual size:          {stats['final_size']:>10,} chars")

    if stats['final_size'] <= target_size:
        print(f"✅ TARGET MET! (under by {target_size - stats['final_size']:,} chars)")
    else:
        print(f"⚠️  TARGET MISSED (over by {stats['final_size'] - target_size:,} chars)")

    print()
    return 0


if __name__ == '__main__':
    exit(main())
