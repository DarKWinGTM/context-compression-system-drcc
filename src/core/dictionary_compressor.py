"""
Dictionary Compression Engine
Lossless compression using 3-tier dictionary system
"""

import re
from typing import Dict, Tuple, Counter as CounterType
from collections import Counter


class DictionaryCompressor:
    """
    Dictionary-based lossless compression engine

    3-Tier Dictionary System (FIXED - excludes 'a' and 'i'):
    - Tier 1 (b-h,j-z): Top 24 highest-frequency words → 1-char codes (excludes 'a','i')
    - Tier 2 (aa-zz): Next 676 words → 2-char codes
    - Tier 3 (w001-w999): Remaining 999 words → 4-char codes
    - Total capacity: 1,699 unique words (safe for English text)
    """

    def __init__(self):
        # CRITICAL FIX: NO TIER 1 (single-letter codes) to avoid conflicts with:
        # - Programming variables (x, y, i, j, k)
        # - Articles/pronouns (a, i)
        # - File extensions first letter
        # Only use Tier 2 (2-char) and Tier 3 (4-char w###)

        all_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]

        # CRITICAL FIX: Exclude file extensions and other reserved 2-char codes
        # Common file extensions that would conflict: md, py, js, ts, go, rs, sh, rb, etc.
        reserved_codes = {
            'md', 'py', 'js', 'ts', 'go', 'rs', 'sh', 'rb',  # file extensions
            'id', 'in', 'on', 'at', 'by', 'to', 'of', 'or',  # common words we want to preserve
            'if', 'is', 'it', 'as', 'be', 'we', 'me', 'he',  # more common short words
        }

        self.tier1_codes = []  # DISABLED - no single-letter codes
        self.tier2_codes = [f"{c1}{c2}" for c1 in all_letters
                           for c2 in all_letters
                           if f"{c1}{c2}" not in reserved_codes]  # Exclude reserved codes

        self.tier3_codes = [f"w{i:03d}" for i in range(1, 1000)]  # w001-w999 (999)

        self.dictionary = {}  # code -> word (for decompression)
        self.reverse_dict = {}  # word -> code (for compression)

    def analyze_frequency(self, text: str, min_length: int = 4) -> CounterType[str]:
        """
        Analyze word frequency in text

        Args:
            text: Input text to analyze
            min_length: Minimum word length (default: 4)

        Returns:
            Counter object with word frequencies
        """
        # Extract words (alphanumeric, min_length+ chars)
        words = re.findall(rf'\b[A-Za-z]{{{min_length},}}\b', text)
        # Convert to lowercase for case-insensitive counting
        words_lower = [word.lower() for word in words]
        return Counter(words_lower)

    def build_dictionary(self, text: str) -> Dict[str, str]:
        """
        Build 3-tier dictionary from frequency analysis

        Args:
            text: Input text to analyze

        Returns:
            Dictionary mapping codes to words
        """
        # Analyze frequencies
        freq = self.analyze_frequency(text)
        # FIXED: Tier 1 disabled, so total capacity = Tier 2 + Tier 3
        total_capacity = len(self.tier2_codes) + len(self.tier3_codes)
        top_words = freq.most_common(total_capacity)

        # Clear existing dictionaries
        self.dictionary = {}
        self.reverse_dict = {}

        # Tier 1: DISABLED (was causing single-letter variable conflicts)
        tier1_limit = 0  # No Tier 1 codes

        # Tier 2: Top N words → 2-char codes (excluding reserved codes like md, py, js)
        tier2_limit = min(len(self.tier2_codes), len(top_words))
        for i, (word, count) in enumerate(top_words[:tier2_limit]):
            code = self.tier2_codes[i]
            self.dictionary[code] = word
            self.reverse_dict[word] = code

        # Tier 3: Remaining words → w001-w999
        tier3_start = tier2_limit
        tier3_limit = min(len(self.tier3_codes), len(top_words) - tier3_start)
        for i, (word, count) in enumerate(top_words[tier3_start:tier3_start + tier3_limit]):
            code = self.tier3_codes[i]
            self.dictionary[code] = word
            self.reverse_dict[word] = code

        return self.dictionary

    def compress(self, text: str) -> Tuple[str, str]:
        """
        Compress text using dictionary codes

        Args:
            text: Input text to compress

        Returns:
            Tuple of (compressed_text, dictionary_header)
        """
        if not self.reverse_dict:
            raise ValueError("Dictionary not built. Call build_dictionary() first.")

        compressed = text

        # Sort by word length (longest first) to avoid partial replacements
        sorted_words = sorted(self.reverse_dict.items(),
                             key=lambda x: len(x[0]),
                             reverse=True)

        # Replace each word with its code (CASE-SENSITIVE to preserve original case)
        for word, code in sorted_words:
            # Use word boundaries to avoid partial replacements
            # CRITICAL: No re.IGNORECASE - we only compress lowercase words
            pattern = r'\b' + re.escape(word) + r'\b'
            compressed = re.sub(pattern, code, compressed)

        # PHASE 11.10: Header generation moved to centralized HeaderSystem
        # Return compressed text only - let HeaderSystem handle header creation
        return compressed, None

    def decompress(self, compressed: str, dictionary: Dict[str, str]) -> str:
        """
        Decompress text using dictionary

        Args:
            compressed: Compressed text
            dictionary: Dictionary mapping codes to words

        Returns:
            Decompressed text
        """
        decompressed = compressed

        # CRITICAL FIX: Group codes by tier for proper processing order
        # Tier 3 (w###) -> Tier 2 (##) -> Tier 1 (#)
        tier3_codes = [(k, v) for k, v in dictionary.items() if k.startswith('w')]
        tier2_codes = [(k, v) for k, v in dictionary.items() if len(k) == 2 and not k.startswith('w')]
        tier1_codes = [(k, v) for k, v in dictionary.items() if len(k) == 1]

        # Process in order: longest codes first to prevent partial matches
        for tier in [tier3_codes, tier2_codes, tier1_codes]:
            for code, word in tier:
                # Use word boundaries - works because all codes are ≥4 chars (except tier1/2)
                # And file extensions like .md, .py are not in our dictionary
                pattern = r'\b' + re.escape(code) + r'\b'
                decompressed = re.sub(pattern, word, decompressed)

        return decompressed

    def get_compression_stats(self, original: str, compressed: str) -> Dict[str, any]:
        """
        Calculate compression statistics

        Args:
            original: Original text
            compressed: Compressed text

        Returns:
            Dictionary with compression statistics
        """
        original_size = len(original)
        compressed_size = len(compressed)
        saved_bytes = original_size - compressed_size
        ratio = (saved_bytes / original_size * 100) if original_size > 0 else 0

        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'saved_bytes': saved_bytes,
            'compression_ratio': ratio,
            'dictionary_size': len(self.dictionary)
        }
