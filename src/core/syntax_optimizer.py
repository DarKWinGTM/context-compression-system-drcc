"""
SyntaxOptimizer - Aggressive whitespace and markdown syntax optimization
Layer 3 of hybrid compression: Dictionary → Template → Syntax Optimization
"""

import re
from typing import Tuple, Dict


class AggressiveSyntaxOptimizer:
    """
    Aggressive syntax optimization for markdown files.

    Target optimizations:
    - Excessive whitespace removal
    - Markdown syntax shortcuts
    - Header simplification
    - List marker optimization
    - Code fence optimization
    """

    def __init__(self):
        pass

    def optimize_whitespace(self, text: str) -> Tuple[str, int]:
        """
        Remove excessive whitespace while preserving structure.

        Rules:
        - Multiple blank lines → single blank line
        - Trailing whitespace → removed
        - Leading whitespace (except in code blocks) → removed
        - Space before punctuation → removed
        """
        original_length = len(text)

        # Remove trailing whitespace from lines
        text = re.sub(r' +$', '', text, flags=re.MULTILINE)

        # Multiple blank lines → single blank line (but preserve intentional structure)
        # Keep max 2 blank lines for major sections
        text = re.sub(r'\n{4,}', '\n\n\n', text)

        # Remove space before punctuation
        text = re.sub(r' +([,.:;!?])', r'\1', text)

        # Remove leading spaces from non-code lines (careful not to break code blocks)
        # Skip lines that start with ```
        lines = []
        in_code_block = False
        for line in text.split('\n'):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                lines.append(line)
            elif in_code_block:
                lines.append(line)  # Preserve code block formatting
            else:
                # Remove leading whitespace from markdown
                lines.append(line.lstrip(' '))

        text = '\n'.join(lines)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def optimize_markdown_syntax(self, text: str) -> Tuple[str, int]:
        """
        Optimize markdown syntax to shorter forms.

        Optimizations:
        - **bold** → *b
        - __italic__ → _i  (if safe)
        - Remove unnecessary markdown (like excessive **)
        - Shorten common patterns
        """
        original_length = len(text)

        # NOTE: Be very careful with bold/italic optimization
        # For now, focus on safe optimizations

        # Remove excessive markdown emphasis
        # **word**word**word** → can be simplified
        # But this is risky - skip for now

        # Optimize lists: remove extra spaces after markers
        text = re.sub(r'^(\s*)- {2,}', r'\1- ', text, flags=re.MULTILINE)
        text = re.sub(r'^(\s*)\* {2,}', r'\1* ', text, flags=re.MULTILINE)

        # Optimize headers: remove extra spaces
        text = re.sub(r'^(#{1,6}) {2,}', r'\1 ', text, flags=re.MULTILINE)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def optimize_repeated_patterns(self, text: str) -> Tuple[str, int]:
        """
        Optimize repeated markdown patterns.

        Examples:
        - "---\n---\n" → "---\n"
        - Repeated section markers
        """
        original_length = len(text)

        # Remove repeated horizontal rules
        text = re.sub(r'(-{3,}\n){2,}', '---\n', text)

        # Remove repeated equal signs (markdown alternative header)
        text = re.sub(r'(={3,}\n){2,}', '===\n', text)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def optimize_code_blocks(self, text: str) -> Tuple[str, int]:
        """
        Optimize code block markers.

        Rules:
        - Remove language specifier if empty
        - Remove extra blank lines in code blocks
        """
        original_length = len(text)

        # ``` \n → ```\n (remove space after fence)
        text = re.sub(r'``` \n', '```\n', text)

        # Remove blank lines at start/end of code blocks
        def clean_code_block(match):
            fence_start = match.group(1)  # ``` or ```lang
            code = match.group(2)

            # Remove leading/trailing blank lines
            code_lines = code.split('\n')
            while code_lines and not code_lines[0].strip():
                code_lines.pop(0)
            while code_lines and not code_lines[-1].strip():
                code_lines.pop()

            code = '\n'.join(code_lines)
            return f'{fence_start}\n{code}\n```'

        text = re.sub(r'(```\w*)\n(.*?)\n```', clean_code_block, text, flags=re.DOTALL)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def optimize_headers(self, text: str) -> Tuple[str, int]:
        """
        Optimize header formatting.

        Rules:
        - Remove excessive decoration
        - Simplify emoji usage (if repeated)
        """
        original_length = len(text)

        # Remove duplicate emojis in headers
        # "🎯🎯 Header" → "🎯 Header"
        text = re.sub(r'([\U0001F000-\U0001FFFF])\1+', r'\1', text)

        # Remove excessive asterisks around headers
        # "**🎯 Header:**" → "🎯 Header:"
        # This is risky - only do if we're sure
        # Skip for now

        chars_saved = original_length - len(text)
        return text, chars_saved

    def optimize(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Apply all syntax optimizations.

        Returns:
            Tuple of (optimized_text, stats)
        """
        original_size = len(text)
        stats = {'original_size': original_size}

        # Layer 1: Whitespace optimization
        text, whitespace_saved = self.optimize_whitespace(text)
        stats['whitespace_saved'] = whitespace_saved

        # Layer 2: Markdown syntax
        text, markdown_saved = self.optimize_markdown_syntax(text)
        stats['markdown_saved'] = markdown_saved

        # Layer 3: Repeated patterns
        text, pattern_saved = self.optimize_repeated_patterns(text)
        stats['pattern_saved'] = pattern_saved

        # Layer 4: Code blocks
        text, code_saved = self.optimize_code_blocks(text)
        stats['code_saved'] = code_saved

        # Layer 5: Headers
        text, header_saved = self.optimize_headers(text)
        stats['header_saved'] = header_saved

        stats['final_size'] = len(text)
        stats['total_saved'] = original_size - len(text)
        stats['compression_ratio'] = (stats['total_saved'] / original_size) * 100 if original_size > 0 else 0

        return text, stats
