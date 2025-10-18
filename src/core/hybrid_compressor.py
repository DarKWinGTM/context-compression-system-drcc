"""
HybridCompressor - Combines all compression layers
Layer 1: Special Prefix Dictionary (29.44%)
Layer 2: Template Extraction (5-10%)
Layer 3: Syntax Optimization (5-10%)
Target: ≥62.8% combined compression
"""

from typing import Tuple, Dict
from .special_prefix_compressor import SafeSpecialPrefixCompressor
from .template_extractor import AggressiveTemplateExtractor
from .syntax_optimizer import AggressiveSyntaxOptimizer


class HybridCompressor:
    """
    Combines Dictionary + Template + Syntax optimization for maximum compression.
    """

    def __init__(self):
        self.dict_compressor = SafeSpecialPrefixCompressor()
        self.template_extractor = AggressiveTemplateExtractor()
        self.syntax_optimizer = AggressiveSyntaxOptimizer()
        self.dictionary = {}

    def compress(self, text: str) -> Tuple[str, str, Dict[str, int]]:
        """
        Apply all compression layers in sequence.

        Process:
        1. Dictionary compression (Special prefix codes)
        2. Template extraction (Pattern replacement)
        3. Syntax optimization (Whitespace/markdown)

        Returns:
            Tuple of (compressed_text, headers, stats)
        """
        original_size = len(text)
        stats = {
            'original_size': original_size,
            'layer1_dict': {},
            'layer2_template': {},
            'layer3_syntax': {}
        }

        # Layer 1: Special Prefix Dictionary
        print("  🔧 Layer 1: Special Prefix Dictionary...")
        dict_compressed, dict_header, dict_stats = self.dict_compressor.compress(text)
        stats['layer1_dict'] = dict_stats
        stats['after_dict'] = dict_stats['final_size']
        self.dictionary = self.dict_compressor.dictionary
        print(f"     → {dict_stats['final_size']:,} chars ({dict_stats['compression_ratio']:.2f}% saved)")

        # Layer 2: Template Extraction
        print("  🔧 Layer 2: Template Extraction...")
        template_compressed, template_header, template_stats = self.template_extractor.compress(dict_compressed)
        stats['layer2_template'] = template_stats
        stats['after_template'] = template_stats['final_size']
        print(f"     → {template_stats['final_size']:,} chars ({template_stats['compression_ratio']:.2f}% saved)")

        # Layer 3: Syntax Optimization
        print("  🔧 Layer 3: Syntax Optimization...")
        syntax_optimized, syntax_stats = self.syntax_optimizer.optimize(template_compressed)
        stats['layer3_syntax'] = syntax_stats
        stats['final_size'] = syntax_stats['final_size']
        print(f"     → {syntax_stats['final_size']:,} chars ({syntax_stats['compression_ratio']:.2f}% saved)")

        # Calculate combined statistics
        stats['total_saved'] = original_size - stats['final_size']
        stats['compression_ratio'] = (stats['total_saved'] / original_size) * 100

        # Generate combined header
        combined_header = self._generate_combined_header(dict_header, template_header, stats)

        return syntax_optimized, combined_header, stats

    def decompress(self, compressed_text: str) -> str:
        """
        Decompress in reverse order:
        Syntax → Template → Dictionary

        Note: Syntax optimization is lossy (whitespace changes)
        Template and Dictionary are lossless
        """
        # Layer 3: Syntax optimization is lossy - cannot fully reverse
        # We can only reverse Layer 2 and Layer 1

        # Layer 2 (Template): Decompress template codes
        template_decompressed = self.template_extractor.decompress(compressed_text)

        # Layer 1 (Dictionary): Decompress dictionary codes
        dict_decompressed = self.dict_compressor.decompress(template_decompressed, self.dictionary)

        return dict_decompressed
