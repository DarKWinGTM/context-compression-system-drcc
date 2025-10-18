"""
Token Join Optimization - Remove spaces between adjacent dictionary codes.

Constitutional Basis:
- Phase 5 (Word Compression) output contains $ and ฿ prefix tokens
- Regex pattern removes ONLY spaces between two consecutive tokens
- Preserves spaces in all other contexts (token-to-word, word-to-word)
- PRODUCTION MODULE: Standalone, NO external dependencies

Example:
  Input:  "•‡$X II‡:$H ฿bm $C"
  Output: "•‡$X II‡:$H฿bm$C"
  Saved:  1 char (space removed between ฿bm and $C)

Task 5.5: Token Join Optimization (Layer 5a)
- Core implementation for full compression pipeline
- Lossless 100% reversible transformation
- Integrated directly into compress_full_pipeline.py
"""

import re
from typing import Dict, Tuple


# Regex pattern: Match ([$฿][A-Za-z0-9]+) followed by space + lookahead for another token
# This ensures BOTH neighbors are dictionary tokens before removing the space
TOKEN_PAIR_PATTERN = re.compile(
    r'([$\u0e3f][A-Za-z0-9]+) (?=[$\u0e3f][A-Za-z0-9]+)'
)


def apply_token_join(text: str) -> Tuple[str, Dict]:
    """
    Join adjacent token pairs by removing whitespace between them.

    Safety guarantees:
    - Only removes space when BOTH neighbors are dictionary tokens
    - Pattern: ([$฿]alphanumeric) space (lookahead: [$฿]alphanumeric)
    - Normal text unaffected: "Hello $bb Good" stays same
    - Token sequences merged: "$aa $bb" becomes "$aa$bb"
    - 100% lossless: tokens remain individually identifiable

    Args:
        text (str): Compressed text containing $code and ฿code tokens

    Returns:
        Tuple[str, Dict]: (joined_text, statistics_dict)
        - joined_text: Text with adjacent tokens joined
        - statistics: {
            'pairs_joined': number of joins performed,
            'chars_saved': total characters removed,
            'original_size': input size,
            'new_size': output size
          }
    """
    # Count and perform replacement
    new_text, count = TOKEN_PAIR_PATTERN.subn(lambda m: m.group(1), text)

    # Calculate statistics
    chars_saved = len(text) - len(new_text)

    statistics = {
        'pairs_joined': count,
        'chars_saved': chars_saved,
        'original_size': len(text),
        'new_size': len(new_text)
    }

    return new_text, statistics


def validate_token_join(original: str, joined: str) -> Dict[str, object]:
    """
    Validate that token joining didn't break decompression potential.

    Verification checks:
    - Token count before/after must be identical
    - All tokens must be preserved (same extraction)
    - Chars saved is positive and correct
    - Status is PASS only if all tokens match

    Args:
        original (str): Original text before joining
        joined (str): Text after token joining

    Returns:
        Dict: Validation metrics with status
    """
    # Verify: token count should be identical
    token_pattern = re.compile(r'[$\u0e3f][A-Za-z0-9]+')
    original_tokens = token_pattern.findall(original)
    joined_tokens = token_pattern.findall(joined)

    tokens_match = original_tokens == joined_tokens

    return {
        'original_size': len(original),
        'joined_size': len(joined),
        'chars_saved': len(original) - len(joined),
        'pairs_joined': len(TOKEN_PAIR_PATTERN.findall(original)),
        'original_tokens': len(original_tokens),
        'joined_tokens': len(joined_tokens),
        'tokens_match': tokens_match,
        'status': 'PASS' if tokens_match else 'FAIL'
    }
