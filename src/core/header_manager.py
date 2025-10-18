"""
Unified Header System Manager
=============================

Central manager for header generation.
Replaces all 5 scattered header generators with 1 unified system.

Responsibilities:
- Centralized entry point for all header generation
- Dynamic strategy registration and management
- Backward compatibility with old function names
- Complete validation system
"""

import time
from typing import Tuple, Optional, Dict
# PHASE 11: Import from renamed modules (config -> header_config, etc.)
from .header_config import HeaderConfig, HeaderStatistics
from .header_strategies import (
    HeaderStrategy,
    NormalModeStrategy,
    ZipModeStrategy,
    CustomModeStrategy,
)
from .header_factory import HeaderStrategyFactory


class HeaderSystem:
    """
    Central unified header system.

    Consolidates header generation from scattered modules:
    - platform_deployer.py (generate_header)
    - unified_header_system.py (create_header)

    All now route through this single entry point (Phase 11: Centralized).
    """

    def __init__(self, dictionaries: Dict = None):
        """
        Initialize with built-in strategies.

        PHASE 11 FIX: Accept optional dictionaries parameter for dynamic header generation.
        This ensures headers are built from actual compressed dictionaries, not hard-coded values.

        Args:
            dictionaries: Optional dict containing 'template_dict', 'phrase_dict', 'word_dict'
                        If provided, strategies will use these to build dynamic DICTIONARY TABLES.
                        If None, strategies will use hard-coded dictionaries (backward compatible).
        """
        self.factory = HeaderStrategyFactory()
        self.dictionaries = dictionaries  # Store for use by strategies
        self._setup_builtin_strategies()
        self.statistics = HeaderStatistics()

    def _setup_builtin_strategies(self) -> None:
        """Register built-in strategies at initialization"""
        self.factory.register('normal', NormalModeStrategy)
        self.factory.register('zip', ZipModeStrategy)
        self.factory.register('custom', CustomModeStrategy)
        print("✅ HeaderSystem initialized with 3 built-in strategies")

    def create_header(
        self,
        mode: str,
        config: HeaderConfig
    ) -> Tuple[str, Optional[str]]:
        """
        Create header using specified strategy.

        This is the MAIN API - replaces all 5 scattered generators.

        Args:
            mode: Strategy mode ('normal', 'zip', 'custom')
            config: HeaderConfig object with strategy parameters

        Returns:
            Tuple[header_string, error_message]
            - header_string: Generated header (or empty if error)
            - error_message: Error description (or None if success)

        Example:
            config = HeaderConfig(mode='normal', dictionary_set='1599')
            header, error = header_system.create_header('normal', config)
            if error:
                print(f"Error: {error}")
            else:
                print(f"Generated header: {len(header)} bytes")
        """
        start_time = time.time()

        try:
            # PHASE 11 FIX: Pass dictionaries through config metadata
            # This ensures strategies use actual dictionaries from compression pipeline
            # instead of hard-coded values
            if self.dictionaries:
                config.metadata['dictionaries'] = self.dictionaries

            # Get strategy from factory
            strategy = self.factory.get_strategy(mode)

            # Generate header
            header = strategy.generate(config)

            # Validate
            if not strategy.validate(header):
                error_msg = f"Header validation failed for mode: {mode}"
                self._record_statistics(
                    success=False,
                    error=error_msg,
                    strategy_name=mode,
                    start_time=start_time
                )
                return "", error_msg

            # Record success statistics
            self._record_statistics(
                success=True,
                original_size=len(header),
                compressed_size=len(header),
                strategy_name=mode,
                start_time=start_time
            )

            return header, None

        except ValueError as e:
            error_msg = f"Strategy error: {str(e)}"
            self._record_statistics(
                success=False,
                error=error_msg,
                strategy_name=mode,
                start_time=start_time
            )
            return "", error_msg

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._record_statistics(
                success=False,
                error=error_msg,
                strategy_name=mode,
                start_time=start_time
            )
            return "", error_msg

    def get_available_modes(self) -> list:
        """Get list of available header modes"""
        return self.factory.list_strategies()

    def register_strategy(self, name: str, strategy_class) -> None:
        """
        Register a new custom strategy.

        For Phase 11+ when new header types are needed.

        Args:
            name: Strategy name
            strategy_class: HeaderStrategy subclass
        """
        self.factory.register(name, strategy_class)

    def validate_header(self, mode: str, header: str) -> bool:
        """Validate header using specific strategy"""
        try:
            strategy = self.factory.get_strategy(mode)
            return strategy.validate(header)
        except ValueError:
            return False

    def get_strategy_info(self, mode: str) -> dict:
        """Get information about a specific strategy"""
        return self.factory.describe(mode)

    def list_all_strategies(self) -> dict:
        """List all registered strategies with descriptions"""
        strategies = {}
        for name in self.get_available_modes():
            strategies[name] = self.get_strategy_info(name)
        return strategies

    def _record_statistics(
        self,
        success: bool,
        strategy_name: str,
        start_time: float,
        original_size: int = 0,
        compressed_size: int = 0,
        error: Optional[str] = None
    ) -> None:
        """Record statistics for header generation"""
        self.statistics = HeaderStatistics(
            original_size=original_size,
            compressed_size=compressed_size,
            processing_time=time.time() - start_time,
            strategy_used=strategy_name,
            success=success,
            error_message=error,
        )


# ============================================================================
# BACKWARD COMPATIBILITY LAYER
# All old function names now route through HeaderSystem
# ============================================================================

# Global instance (singleton-like)
_header_system = HeaderSystem()


def generate_header(mode: str, config: HeaderConfig) -> Tuple[str, Optional[str]]:
    """
    OLD: platform_deployer.generate_header()
    NOW: Centralized via HeaderSystem
    """
    return _header_system.create_header(mode, config)


def create_header(mode: str, config: HeaderConfig) -> Tuple[str, Optional[str]]:
    """
    OLD: unified_header_system.create_header()
    NOW: Centralized via HeaderSystem
    """
    return _header_system.create_header(mode, config)


def make_header(mode: str, config: HeaderConfig) -> Tuple[str, Optional[str]]:
    """
    Compatibility wrapper for header generation (Phase 11: HeaderSystem).
    All header creation now routes through centralized HeaderSystem.
    """
    return _header_system.create_header(mode, config)


def header_gen(mode: str, config: HeaderConfig) -> Tuple[str, Optional[str]]:
    """
    OLD: orphaned_module1.header_gen()
    NOW: Centralized via HeaderSystem
    """
    return _header_system.create_header(mode, config)


def build_header(mode: str, config: HeaderConfig) -> Tuple[str, Optional[str]]:
    """
    OLD: orphaned_module2.build_header()
    NOW: Centralized via HeaderSystem
    """
    return _header_system.create_header(mode, config)


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    'HeaderSystem',
    'HeaderConfig',
    'HeaderStrategy',
    'HeaderStrategyFactory',
    'HeaderStatistics',
    # Backward compatibility functions
    'generate_header',
    'create_header',
    'make_header',
    'header_gen',
    'build_header',
]
