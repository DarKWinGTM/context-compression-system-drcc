import pytest

from src.core.compression_engine import CompressionEngine, CompressionLevel


@pytest.mark.parametrize("level", [
    CompressionLevel.BASIC,
    CompressionLevel.AGGRESSIVE,
])
def test_compression_reduces_whitespace(level):
    sample_text = """# Title\n\n\nParagraph with trailing spaces.   \n\n<!-- comment -->\nNext line."""

    engine = CompressionEngine(level=level)
    result = engine.compress(sample_text)

    assert result.original_size > result.compressed_size
    assert "Trailing whitespace" in result.sections_removed
    assert result.compression_ratio > 0


def test_selective_compression_uses_patterns():
    text = "Keep this.\nRemove ME please.\nKeep again."
    engine = CompressionEngine(level=CompressionLevel.SELECTIVE)
    result = engine.compress(text, custom_patterns=["Remove ME please."])

    assert "Remove ME please." not in result.compressed_text
    assert result.metadata["patterns_used"] == ["Remove ME please."]
