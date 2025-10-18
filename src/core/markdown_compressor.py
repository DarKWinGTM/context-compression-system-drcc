#!/usr/bin/env python3
"""
Markdown Compressor - Additional Optimization Layer
Compress markdown syntax overhead

Compression strategies:
1. Bold markers: ** → ‡ (1 char vs 2 chars per marker, 4 chars per bold phrase)
2. List bullets: - → • (ASCII dash to Unicode bullet, 1 char)
3. Headers: ### → ≡3 (compress header levels)
4. Code blocks: ``` → ¶ (start/end markers)
"""

import re
from typing import Tuple, Dict


class MarkdownCompressor:
    """Compress markdown syntax overhead"""

    def __init__(self):
        """Initialize markdown compressor with symbol mappings"""
        # Use Unicode symbols that are unlikely to appear in normal text
        self.BOLD_START = '‡'   # Double dagger
        self.BOLD_END = '‡'     # Same symbol for symmetry
        self.BULLET = '•'       # Bullet point
        self.CODE_BLOCK = '¶'   # Pilcrow
        self.HEADER_PREFIX = '≡' # Identical to

    def compress(self, text: str) -> Tuple[str, Dict]:
        """
        Compress markdown syntax

        Args:
            text: Input text with markdown

        Returns:
            Tuple of (compressed_text, stats_dict)
        """
        original_size = len(text)

        stats = {
            'original_size': original_size,
            'compressions': {}
        }

        # 1. Compress bold markers (** → ‡)
        # **text** → ‡text‡
        bold_pattern = r'\*\*([^\*]+)\*\*'
        bold_matches = re.findall(bold_pattern, text)
        text = re.sub(bold_pattern, r'‡\1‡', text)
        stats['compressions']['bold_markers'] = {
            'count': len(bold_matches),
            'savings': len(bold_matches) * 2  # Save 2 chars per bold phrase (4 stars → 2 daggers)
        }

        # 2. Compress list bullets (- → •)
        # Lines starting with "- " → "• "
        bullet_pattern = r'^- '
        bullet_lines = len(re.findall(bullet_pattern, text, re.MULTILINE))
        text = re.sub(bullet_pattern, '• ', text, flags=re.MULTILINE)
        stats['compressions']['list_bullets'] = {
            'count': bullet_lines,
            'savings': 0  # Same length, but more compact visually
        }

        # 3. Compress code blocks (``` → ¶)
        # ```language\n → ¶language\n
        # ``` → ¶
        code_block_pattern = r'```([^\n]*)'
        code_blocks = re.findall(code_block_pattern, text)
        text = re.sub(code_block_pattern, r'¶\1', text)
        stats['compressions']['code_blocks'] = {
            'count': len(code_blocks),
            'savings': len(code_blocks) * 2  # Save 2 chars per block marker (3 backticks → 1 pilcrow)
        }

        # 4. Compress headers (### → ≡3)
        # #### text → ≡4 text
        # ### text → ≡3 text
        # ## text → ≡2 text
        header_savings = 0
        for level in [4, 3, 2]:  # Process from longest to shortest
            header_pattern = f"^{'#' * level} "
            header_matches = len(re.findall(header_pattern, text, re.MULTILINE))
            text = re.sub(header_pattern, f'≡{level} ', text, flags=re.MULTILINE)
            # Savings: level hashes → 1 symbol + 1 digit = (level - 2) chars saved
            header_savings += header_matches * (level - 2)

        stats['compressions']['headers'] = {
            'count': sum(len(re.findall(f"^≡{l} ", text, re.MULTILINE)) for l in [2, 3, 4]),
            'savings': header_savings
        }

        # Calculate final statistics
        final_size = len(text)
        total_saved = original_size - final_size

        stats['final_size'] = final_size
        stats['total_saved'] = total_saved
        stats['compression_ratio'] = (total_saved / original_size * 100) if original_size > 0 else 0

        return text, stats

    def decompress(self, text: str) -> str:
        """
        Decompress markdown syntax

        Args:
            text: Compressed text

        Returns:
            Decompressed text with original markdown
        """
        # Reverse all compressions

        # 1. Restore headers (≡3 → ###)
        for level in [2, 3, 4]:
            text = re.sub(f'^≡{level} ', '#' * level + ' ', text, flags=re.MULTILINE)

        # 2. Restore code blocks (¶ → ```)
        text = re.sub(r'¶', '```', text)

        # 3. Restore list bullets (• → -)
        text = re.sub(r'^• ', '- ', text, flags=re.MULTILINE)

        # 4. Restore bold markers (‡ → **)
        text = re.sub(r'‡([^‡]+)‡', r'**\1**', text)

        return text


def main():
    """Test markdown compressor"""
    import json

    # Sample markdown text
    sample = """### Header 3
**This is bold text** with some content.
- List item 1
- List item 2
- **Bold item**

```python
print("code block")
```

#### Header 4
More **bold text** here.
"""

    print("=" * 80)
    print("🔧 MARKDOWN COMPRESSOR TEST")
    print("=" * 80)
    print()

    compressor = MarkdownCompressor()

    # Compress
    print("📝 Original:")
    print(sample)
    print(f"Length: {len(sample)} chars")
    print()

    compressed, stats = compressor.compress(sample)

    print("🗜️  Compressed:")
    print(compressed)
    print(f"Length: {len(compressed)} chars")
    print(f"Saved: {stats['total_saved']} chars ({stats['compression_ratio']:.2f}%)")
    print()

    print("📊 Compression breakdown:")
    for name, data in stats['compressions'].items():
        print(f"  {name}: {data['count']} occurrences, {data['savings']} chars saved")
    print()

    # Decompress
    decompressed = compressor.decompress(compressed)

    print("🔄 Decompressed:")
    print(decompressed)
    print()

    # Verify lossless
    if decompressed == sample:
        print("✅ LOSSLESS VERIFIED: Decompressed matches original")
    else:
        print("❌ ERROR: Decompressed doesn't match original")

    return 0


if __name__ == '__main__':
    exit(main())
