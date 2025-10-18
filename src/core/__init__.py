"""Core compression and processing modules"""

# PHASE 11: Removed legacy header_styles exports
# Using centralized HeaderSystem from header_manager.py instead

from .compression_engine import CompressionEngine, CompressionLevel, CompressionResult
from .processor import ContextProcessor, ProcessingResult

__all__ = [
    "CompressionEngine",
    "CompressionLevel",
    "CompressionResult",
    "ContextProcessor",
    "ProcessingResult"
]
