#!/usr/bin/env python3
"""
Dictionary Generator - Inline Dictionary Generation
Generate Template, Phrase, and Word dictionaries from clean content
(after Thai removal and diagram removal)

This module is designed to work INLINE in the compression pipeline,
ensuring dictionaries are created from pre-cleaned content.
"""

import re
from collections import Counter, defaultdict
from typing import Dict, Tuple, List


class DictionaryGenerator:
    """
    Generate compression dictionaries from clean content.
    
    CRITICAL: Must be called AFTER Layer 1 (Thai removal) and Layer 2 (Diagram removal)
    to ensure dictionaries don't contain Thai text or diagram artifacts.
    """
    
    def __init__(self, min_template_savings=50, min_phrase_length=15, min_word_length=4,
                 min_word_frequency=2, enable_aggressive_compression=False):
        """
        Initialize dictionary generator.

        Args:
            min_template_savings: Minimum chars saved to include template
            min_phrase_length: Minimum phrase length (chars)
            min_word_length: Minimum word length (chars)
            min_word_frequency: Minimum word frequency for inclusion
            enable_aggressive_compression: Enable Option 1 aggressive compression (2+ occurrences)
        """
        self.min_template_savings = min_template_savings
        self.min_phrase_length = min_phrase_length
        self.min_word_length = min_word_length
        self.min_word_frequency = min_word_frequency
        self.enable_aggressive_compression = enable_aggressive_compression
    
    def generate_all_dictionaries(self, clean_text: str) -> Tuple[Dict, Dict, Dict, Dict]:
        """
        Generate all three dictionaries from clean content.
        
        Args:
            clean_text: Text after Layer 1 (Thai removal) and Layer 2 (Diagram removal)
        
        Returns:
            (template_dict, phrase_dict, word_dict, stats)
        """
        print("🔧 Generating dictionaries from clean content...")
        print(f"   Input size: {len(clean_text):,} chars")
        print()
        
        # Generate each dictionary
        template_dict, template_stats = self.generate_template_dictionary(clean_text)
        phrase_dict, phrase_stats = self.generate_phrase_dictionary(clean_text)
        word_dict, word_stats = self.generate_word_dictionary(clean_text)
        
        # Combined stats
        stats = {
            'template_stats': template_stats,
            'phrase_stats': phrase_stats,
            'word_stats': word_stats,
            'total_entries': len(template_dict) + len(phrase_dict) + len(word_dict)
        }
        
        print(f"✅ Dictionary generation complete:")
        print(f"   - Templates: {len(template_dict):>4} entries ({template_stats['total_savings']:,} chars potential)")
        print(f"   - Phrases:   {len(phrase_dict):>4} entries ({phrase_stats['total_savings']:,} chars potential)")
        print(f"   - Words:     {len(word_dict):>4} entries ({word_stats['total_savings']:,} chars potential)")
        print(f"   - Total:     {stats['total_entries']:>4} entries")
        print()
        
        return template_dict, phrase_dict, word_dict, stats
    
    def generate_template_dictionary(self, text: str) -> Tuple[Dict, Dict]:
        """
        Generate template dictionary from repeated structural patterns.
        
        Focus on:
        - Constitutional headers (#### **📜 Constitutional Basis:**)
        - Section headers with Thai translations
        - Repeated formatted structures
        """
        templates = {}
        
        # Pattern 1: Constitutional headers with Thai translations
        # #### **📜 Constitutional Basis:**\n**รากฐานรัธรีมนูญ**
        pattern1 = r'#### \*\*[📜📊🏗️💡🎯🧠][^*]+\*\*'
        matches1 = re.findall(pattern1, text)
        
        # Pattern 2: Bold labels with structure
        # **📜 Constitutional Basis:**
        pattern2 = r'\*\*[📜📊🏗️💡🎯🧠][^*]{10,50}\*\*'
        matches2 = re.findall(pattern2, text)
        
        # Pattern 3: List item prefixes
        # - **Success Indicators**: 
        pattern3 = r'- \*\*[A-Z][a-z]+ [A-Z][a-z]+\*\*: '
        matches3 = re.findall(pattern3, text)
        
        # Count frequencies
        all_patterns = matches1 + matches2 + matches3
        pattern_freq = Counter(all_patterns)
        
        # Filter high-value patterns
        template_id = 1
        total_savings = 0
        
        for pattern, count in pattern_freq.most_common():
            if count >= 2:  # Appears at least twice
                savings = (len(pattern) - 3) * count  # "T1" = 2 chars + newline
                if savings >= self.min_template_savings:
                    code = f"T{template_id}"
                    templates[code] = pattern
                    total_savings += savings
                    template_id += 1
                    
                    if template_id > 20:  # Limit to top 20 templates
                        break
        
        stats = {
            'total_patterns_found': len(pattern_freq),
            'templates_created': len(templates),
            'total_savings': total_savings
        }
        
        return templates, stats
    
    def generate_phrase_dictionary(self, text: str) -> Tuple[Dict, Dict]:
        """
        Generate phrase dictionary from frequently occurring multi-word phrases.

        Focus on:
        - Technical terms (2-5 words)
        - Common phrases that appear multiple times
        - Case-insensitive matching (normalized to lowercase)
        """
        # Extract all potential phrases (2-5 words) - case-insensitive
        # Changed from r'\b[A-Z][a-z]+...' (capitalized only) to r'\b[A-Za-z]+...' (all words)
        phrase_pattern = r'\b[A-Za-z]+(?:\s+[A-Za-z]+){1,4}\b'
        potential_phrases = re.findall(phrase_pattern, text)

        # Normalize to lowercase for case-insensitive counting
        potential_phrases = [p.lower() for p in potential_phrases]
        
        # Count frequencies
        phrase_freq = Counter(potential_phrases)
        
        # Filter valuable phrases
        phrases = {}
        phrase_id = 1
        total_savings = 0
        
        for phrase, count in phrase_freq.most_common():
            if len(phrase) >= self.min_phrase_length and count >= 3:
                savings = (len(phrase) - 4) * count  # "€abc" = 4 chars
                if savings > 20:  # Minimum 20 chars savings
                    # Generate compact code
                    code = self._generate_phrase_code(phrase_id)
                    phrases[code] = phrase
                    total_savings += savings
                    phrase_id += 1
                    
                    if phrase_id > 250:  # Limit to top 250 phrases
                        break
        
        stats = {
            'potential_phrases': len(phrase_freq),
            'phrases_created': len(phrases),
            'total_savings': total_savings
        }
        
        return phrases, stats
    
    def generate_word_dictionary(self, text: str) -> Tuple[Dict, Dict]:
        """
        Generate word dictionary from frequently occurring single words.

        Focus on:
        - Technical terms (≥4 chars)
        - High-frequency words
        - Case-insensitive matching (normalized to lowercase)
        - Configurable frequency threshold (default: 3, aggressive: 2)
        """
        # Extract all words (alphanumeric, 4+ chars) - case-insensitive
        # Changed from r'\b[A-Z][a-z]{3,}\b' (capitalized only) to r'\b[A-Za-z]{4,}\b' (all words)
        word_pattern = r'\b[A-Za-z]{4,}\b'
        potential_words = re.findall(word_pattern, text)

        # Normalize to lowercase for case-insensitive counting
        # This ensures "User", "user", "USER" are treated as the same word
        potential_words = [w.lower() for w in potential_words]

        # Count frequencies
        word_freq = Counter(potential_words)

        # Filter valuable words
        words = {}
        total_savings = 0

        # Use multiple tiers based on compression strategy
        dollar_id = ord('A')  # $A, $B, ... $Z
        baht_id = ord('a')    # ฿a, ฿b, ... ฿z, ฿aa, ฿ab, ...
        next_code_id = 0      # Sequential ID for aggressive mode

        # Determine frequency threshold based on mode
        # Long-term fix: Lowered default threshold from 5 to 3
        # Rationale: Captures important words like "Comprehensive" (3 occurrences)
        min_freq = 2 if self.enable_aggressive_compression else 3

        print(f"   Using word frequency threshold: {min_freq}+ occurrences")
        if self.enable_aggressive_compression:
            print("   🚀 Aggressive compression mode enabled")

        for word, count in word_freq.most_common():
            if len(word) >= self.min_word_length and count >= min_freq:
                # Calculate code length based on word length (aggressive mode)
                if self.enable_aggressive_compression:
                    word_len = len(word)
                    if word_len >= 10:
                        code_len = 2  # $##
                    elif word_len >= 7:
                        code_len = 3  # $###
                    else:
                        code_len = 4  # $####
                    savings = (word_len - code_len) * count
                    # For aggressive mode, include negative savings for very long words
                    min_savings = -5 if word_len >= 10 else 0
                else:
                    savings = (len(word) - 2) * count  # "$A" = 2 chars
                    # Long-term fix #2: Lowered savings threshold from 15 to 10
                    # Rationale: Captures medium-length words (8-10 chars) with 2-3 occurrences
                    # Example: "acceptance" (10 chars × 2 = 16), "Structure" (9 chars × 3 = 21)
                    min_savings = 10

                if savings >= min_savings:
                    # Assign code based on frequency and word length
                    if self.enable_aggressive_compression:
                        # Aggressive mode: smart code assignment
                        code = self._assign_aggressive_word_code(word, count, next_code_id)
                        next_code_id += 1
                    else:
                        # Conservative mode: simple tiering
                        # Tier 1: Very frequent (count ≥ 20) → $Code
                        if count >= 20 and dollar_id <= ord('Z'):
                            code = f"${chr(dollar_id)}"
                            dollar_id += 1
                        # Tier 2: Frequent (count ≥ 5) → ฿code
                        else:
                            if baht_id <= ord('z'):
                                code = f"฿{chr(baht_id)}"
                                baht_id += 1
                            else:
                                # Extended: ฿aa, ฿ab, ...
                                ext_id = baht_id - ord('z') - 1
                                code = f"฿{chr(ord('a') + ext_id // 26)}{chr(ord('a') + ext_id % 26)}"
                                baht_id += 1

                    words[code] = word
                    total_savings += savings

                    if len(words) >= 800:  # Higher limit for aggressive mode
                        break

        stats = {
            'potential_words': len(word_freq),
            'words_created': len(words),
            'total_savings': total_savings,
            'frequency_threshold': min_freq,
            'aggressive_mode': self.enable_aggressive_compression
        }

        return words, stats

    def _assign_aggressive_word_code(self, word: str, count: int, next_code_id: int) -> str:
        """
        Assign smart code based on word length and frequency for aggressive compression.

        Args:
            word: The word to encode
            count: Frequency of the word
            next_code_id: Sequential ID for code assignment

        Returns:
            Assigned code string
        """
        word_len = len(word)

        # Very frequent words get shortest codes regardless of length
        if count >= 20 and next_code_id < 26:
            return f"${chr(ord('A') + next_code_id)}"

        # Smart assignment based on word length
        if word_len >= 10:
            # Long words get 2-digit codes: $100, $101, ...
            return f"${100 + next_code_id}"
        elif word_len >= 7:
            # Medium words get 3-digit codes: $001, $002, ...
            return f"${1000 + next_code_id:03d}"
        else:
            # Short words get 4-digit codes: $0001, $0002, ...
            return f"${10000 + next_code_id:04d}"
    
    def _generate_phrase_code(self, phrase_id: int) -> str:
        """
        Generate compact phrase code (€aa, €ab, ..., €zz).
        
        Args:
            phrase_id: Sequential ID (1, 2, 3, ...)
        
        Returns:
            Code like "€f", "€am", "€abc"
        """
        # Single letter for first 26
        if phrase_id <= 26:
            return f"€{chr(ord('a') + phrase_id - 1)}"
        
        # Two letters for next 676 (26^2)
        elif phrase_id <= 26 + 676:
            idx = phrase_id - 27
            first = chr(ord('a') + idx // 26)
            second = chr(ord('a') + idx % 26)
            return f"€{first}{second}"
        
        # Three letters for more
        else:
            idx = phrase_id - 27 - 676
            first = chr(ord('a') + idx // 676)
            second = chr(ord('a') + (idx % 676) // 26)
            third = chr(ord('a') + idx % 26)
            return f"€{first}{second}{third}"


def main():
    """Test dictionary generation on layer2 output."""
    from pathlib import Path
    import sys

    # Parse command line arguments
    aggressive_mode = '--aggressive' in sys.argv
    conservative_mode = '--conservative' in sys.argv

    # Load layer2 output (clean content)
    layer2_path = Path(__file__).parent.parent.parent / "outputs" / "layer2_diagrams_removed.txt"

    if not layer2_path.exists():
        print(f"❌ ERROR: {layer2_path} not found")
        print("   Run compress_full_pipeline.py first to generate layer2 output")
        return 1

    print(f"📖 Loading clean content: {layer2_path}")
    with open(layer2_path, 'r', encoding='utf-8') as f:
        clean_text = f.read()

    print(f"📊 Input size: {len(clean_text):,} chars")
    print()

    # Test both modes if no specific mode requested
    if not aggressive_mode and not conservative_mode:
        print("🔄 Testing both compression modes...")
        print("=" * 80)

        # Test conservative mode (default)
        print("📊 CONSERVATIVE MODE (5+ occurrences):")
        print("=" * 80)
        generator = DictionaryGenerator(enable_aggressive_compression=False)
        template_dict_c, phrase_dict_c, word_dict_c, stats_c = generator.generate_all_dictionaries(clean_text)

        print("\n" + "=" * 80)
        print("🚀 AGGRESSIVE MODE (2+ occurrences):")
        print("=" * 80)
        generator = DictionaryGenerator(enable_aggressive_compression=True, min_word_frequency=2)
        template_dict_a, phrase_dict_a, word_dict_a, stats_a = generator.generate_all_dictionaries(clean_text)

        # Compare results
        print("\n" + "=" * 80)
        print("📈 COMPARISON RESULTS:")
        print("=" * 80)
        print(f"Conservative mode: {len(word_dict_c)} words, {stats_c['word_stats']['total_savings']:,} chars savings")
        print(f"Aggressive mode:  {len(word_dict_a)} words, {stats_a['word_stats']['total_savings']:,} chars savings")

        improvement = len(word_dict_a) - len(word_dict_c)
        savings_improvement = stats_a['word_stats']['total_savings'] - stats_c['word_stats']['total_savings']
        print(f"Improvement:      +{improvement} words, +{savings_improvement:,} chars savings")

        # Use aggressive mode results for display
        template_dict, phrase_dict, word_dict, stats = template_dict_a, phrase_dict_a, word_dict_a, stats_a

    elif aggressive_mode:
        print("🚀 AGGRESSIVE COMPRESSION MODE (2+ occurrences)")
        print("=" * 80)
        generator = DictionaryGenerator(enable_aggressive_compression=True, min_word_frequency=2)
        template_dict, phrase_dict, word_dict, stats = generator.generate_all_dictionaries(clean_text)

    else:  # conservative_mode
        print("📊 CONSERVATIVE COMPRESSION MODE (5+ occurrences)")
        print("=" * 80)
        generator = DictionaryGenerator(enable_aggressive_compression=False)
        template_dict, phrase_dict, word_dict, stats = generator.generate_all_dictionaries(clean_text)
    
    # Display samples
    print("=" * 80)
    print("📋 TEMPLATE DICTIONARY SAMPLES:")
    print("=" * 80)
    for code, pattern in list(template_dict.items())[:5]:
        preview = pattern.replace('\n', '\\n')[:60]
        print(f"{code:4} = {preview}")
    print(f"... {len(template_dict)} total templates")
    print()
    
    print("=" * 80)
    print("📋 PHRASE DICTIONARY SAMPLES:")
    print("=" * 80)
    for code, phrase in list(phrase_dict.items())[:10]:
        print(f"{code:6} = {phrase}")
    print(f"... {len(phrase_dict)} total phrases")
    print()
    
    print("=" * 80)
    print("📋 WORD DICTIONARY SAMPLES:")
    print("=" * 80)
    for code, word in list(word_dict.items())[:20]:
        print(f"{code:4} = {word}")
    print(f"... {len(word_dict)} total words")
    print()
    
    # Verify no Thai content
    print("=" * 80)
    print("🔍 VERIFICATION: Checking for Thai content in dictionaries")
    print("=" * 80)
    
    thai_pattern = r'[\u0E00-\u0E7F]'
    
    def count_thai(d):
        count = 0
        for value in d.values():
            if re.search(thai_pattern, value):
                count += 1
        return count
    
    thai_in_templates = count_thai(template_dict)
    thai_in_phrases = count_thai(phrase_dict)
    thai_in_words = count_thai(word_dict)
    
    print(f"Thai characters found:")
    print(f"  - Templates: {thai_in_templates} entries")
    print(f"  - Phrases:   {thai_in_phrases} entries")
    print(f"  - Words:     {thai_in_words} entries")
    print()
    
    if thai_in_templates + thai_in_phrases + thai_in_words == 0:
        print("✅ PERFECT: No Thai content in any dictionary!")
    else:
        print("⚠️  WARNING: Thai content found in dictionaries!")
    
    return 0


if __name__ == '__main__':
    exit(main())
