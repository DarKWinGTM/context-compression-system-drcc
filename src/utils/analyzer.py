"""
Template Analysis Utilities
"""

import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


class TemplateAnalyzer:
    """Analyze source template for compression planning"""

    def analyze_template(self, file_path: str) -> Dict[str, any]:
        """
        Comprehensive analysis of source template

        Args:
            file_path: Path to template file

        Returns:
            Dictionary with analysis results
        """
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Basic statistics
        total_chars = len(content)
        total_lines = content.count('\n')
        total_words = len(content.split())

        # Word frequency analysis (words ≥4 chars)
        words = re.findall(r'\b[A-Za-z]{4,}\b', content)
        words_lower = [w.lower() for w in words]
        unique_words = len(set(words_lower))
        word_freq = Counter(words_lower)

        # Thai content detection
        thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', content))
        thai_percentage = (thai_chars / total_chars * 100) if total_chars > 0 else 0

        # Estimate compression potential
        layer1_reduction = thai_chars  # Thai removal

        # Layer 4 estimation (dictionary replacement)
        top_1701 = word_freq.most_common(1701)
        layer4_savings = 0
        for i, (word, count) in enumerate(top_1701):
            if i < 26:  # Tier 1: word -> 1 char
                layer4_savings += (len(word) - 1) * count
            elif i < 702:  # Tier 2: word -> 2 chars
                layer4_savings += (len(word) - 2) * count
            else:  # Tier 3: word -> 4 chars (w001)
                layer4_savings += (len(word) - 4) * count

        estimated_final_size = total_chars - layer1_reduction - layer4_savings

        return {
            'file_path': file_path,
            'total_chars': total_chars,
            'total_lines': total_lines,
            'total_words': total_words,
            'unique_words': unique_words,
            'thai_chars': thai_chars,
            'thai_percentage': thai_percentage,
            'layer1_reduction': layer1_reduction,
            'layer4_savings': layer4_savings,
            'estimated_final_size': estimated_final_size,
            'estimated_ratio': ((total_chars - estimated_final_size) / total_chars * 100) if total_chars > 0 else 0,
            'top_words': word_freq.most_common(100),  # Top 100 for review
            'dictionary_candidates': len([w for w, c in word_freq.items() if c >= 5])
        }

    def generate_report(self, analysis: Dict[str, any]) -> str:
        """
        Generate human-readable analysis report

        Args:
            analysis: Analysis results from analyze_template()

        Returns:
            Formatted report string
        """
        report = f"""
# Template Analysis Report

## File Information
- **Path**: {analysis['file_path']}
- **Total Characters**: {analysis['total_chars']:,}
- **Total Lines**: {analysis['total_lines']:,}
- **Total Words**: {analysis['total_words']:,}
- **Unique Words**: {analysis['unique_words']:,}

## Thai Content
- **Thai Characters**: {analysis['thai_chars']:,}
- **Thai Percentage**: {analysis['thai_percentage']:.1f}%

## Compression Estimation
- **Layer 1 Reduction** (Thai removal): -{analysis['layer1_reduction']:,} chars
- **Layer 4 Savings** (Dictionary replacement): -{analysis['layer4_savings']:,} chars
- **Estimated Final Size**: {analysis['estimated_final_size']:,} chars
- **Estimated Compression Ratio**: {analysis['estimated_ratio']:.1f}%

## Dictionary Analysis
- **Words with frequency ≥5**: {analysis['dictionary_candidates']:,}
- **Dictionary capacity**: 1,701 words
- **Dictionary coverage**: {"✅ Sufficient" if analysis['dictionary_candidates'] >= 1701 else "⚠️ May need adjustment"}

## Top 20 Most Frequent Words
"""
        for i, (word, count) in enumerate(analysis['top_words'][:20], 1):
            tier = "Tier 1 (a-z)" if i <= 26 else "Tier 2 (aa-zz)" if i <= 702 else "Tier 3 (w###)"
            report += f"{i:3d}. {word:20s} ({count:4d} times) - {tier}\n"

        return report

    def save_report(self, analysis: Dict[str, any], output_path: str):
        """Save analysis report to file"""
        report = self.generate_report(analysis)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
