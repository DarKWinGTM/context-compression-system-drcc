"""
Header Configuration Classes
=============================

Configuration objects for header generation strategies.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class HeaderConfig:
    """
    Configuration for header generation

    Attributes:
        mode: Strategy mode ('normal', 'zip', 'custom')
        dictionary_set: Dictionary size ('1599', '2000', 'minimal')
        compression_level: Compression level (0-7)
        include_decompression: Include decompression instructions
        metadata: Additional strategy-specific metadata
    """
    mode: str  # 'normal', 'zip', 'custom'
    dictionary_set: str = '1599'  # '1599', '2000', 'minimal'
    compression_level: int = 0  # 0-7, default uncompressed
    include_decompression: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration"""
        valid_modes = ['normal', 'zip', 'custom']
        if self.mode not in valid_modes:
            raise ValueError(f"Invalid mode '{self.mode}'. Must be one of {valid_modes}")

        valid_dict_sets = ['1599', '2000', 'minimal']
        if self.dictionary_set not in valid_dict_sets:
            raise ValueError(f"Invalid dictionary_set '{self.dictionary_set}'. Must be one of {valid_dict_sets}")

        if not (0 <= self.compression_level <= 7):
            raise ValueError(f"Compression level must be 0-7, got {self.compression_level}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'mode': self.mode,
            'dictionary_set': self.dictionary_set,
            'compression_level': self.compression_level,
            'include_decompression': self.include_decompression,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HeaderConfig':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class HeaderStatistics:
    """Statistics for header generation"""
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0
    processing_time: float = 0.0
    strategy_used: str = ''
    success: bool = True
    error_message: Optional[str] = None

    def calculate_ratio(self) -> float:
        """Calculate compression ratio as percentage"""
        if self.original_size == 0:
            return 0.0
        return ((self.original_size - self.compressed_size) / self.original_size) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'original_size': self.original_size,
            'compressed_size': self.compressed_size,
            'compression_ratio': self.calculate_ratio(),
            'processing_time': self.processing_time,
            'strategy_used': self.strategy_used,
            'success': self.success,
            'error_message': self.error_message,
        }
