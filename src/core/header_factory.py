"""
Header Strategy Factory
=======================

Factory pattern for creating and managing header strategies.
Enables dynamic registration of new strategies at runtime.
"""

from typing import Dict, Type, Optional
# PHASE 11: Import from renamed modules
from .header_strategies import HeaderStrategy


class HeaderStrategyFactory:
    """
    Factory for creating and managing header strategies.

    Supports:
    - Dynamic strategy registration
    - Runtime strategy lookup
    - Strategy discovery and listing
    """

    _strategies: Dict[str, Type[HeaderStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_class: Type[HeaderStrategy]) -> None:
        """
        Register a new strategy

        Args:
            name: Strategy name (e.g., 'normal', 'zip', 'custom')
            strategy_class: HeaderStrategy subclass

        Raises:
            TypeError: If strategy_class is not a HeaderStrategy subclass
            ValueError: If strategy name already registered
        """
        if not issubclass(strategy_class, HeaderStrategy):
            raise TypeError(f"{strategy_class} must be a HeaderStrategy subclass")

        if name in cls._strategies:
            print(f"⚠️  Overwriting existing strategy: {name}")

        cls._strategies[name] = strategy_class
        print(f"✅ Registered strategy: {name} ({strategy_class.__name__})")

    @classmethod
    def get_strategy(cls, name: str) -> HeaderStrategy:
        """
        Get a registered strategy instance

        Args:
            name: Strategy name

        Returns:
            Instantiated strategy object

        Raises:
            ValueError: If strategy not found
        """
        if name not in cls._strategies:
            available = ", ".join(cls.list_strategies())
            raise ValueError(
                f"Unknown strategy '{name}'. "
                f"Available strategies: {available}"
            )

        strategy_class = cls._strategies[name]
        return strategy_class()

    @classmethod
    def list_strategies(cls) -> list:
        """List all registered strategy names"""
        return list(cls._strategies.keys())

    @classmethod
    def get_strategies(cls) -> Dict[str, Type[HeaderStrategy]]:
        """Get all registered strategies"""
        return cls._strategies.copy()

    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        Unregister a strategy

        Args:
            name: Strategy name to unregister

        Returns:
            True if unregistered, False if not found
        """
        if name in cls._strategies:
            del cls._strategies[name]
            print(f"✅ Unregistered strategy: {name}")
            return True
        return False

    @classmethod
    def clear(cls) -> None:
        """Clear all registered strategies"""
        cls._strategies.clear()
        print("✅ Cleared all registered strategies")

    @classmethod
    def describe(cls, name: str) -> Dict:
        """
        Get description of a registered strategy

        Args:
            name: Strategy name

        Returns:
            Dictionary with strategy information
        """
        if name not in cls._strategies:
            return {}

        strategy_class = cls._strategies[name]
        try:
            instance = strategy_class()
            return {
                'name': name,
                'class': strategy_class.__name__,
                'docstring': strategy_class.__doc__,
                'metadata': instance.get_metadata(),
            }
        except Exception as e:
            return {'error': str(e)}

    @classmethod
    def validate_strategy(cls, name: str, header_content: str) -> bool:
        """
        Validate header using a specific strategy

        Args:
            name: Strategy name
            header_content: Header string to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If strategy not found
        """
        strategy = cls.get_strategy(name)
        return strategy.validate(header_content)

    @classmethod
    def has_strategy(cls, name: str) -> bool:
        """Check if strategy is registered"""
        return name in cls._strategies

    @classmethod
    def count_strategies(cls) -> int:
        """Get number of registered strategies"""
        return len(cls._strategies)

    @classmethod
    def print_registry(cls) -> None:
        """Print formatted registry of all strategies"""
        print("\n" + "="*60)
        print("📋 HEADER STRATEGY REGISTRY")
        print("="*60)

        if not cls._strategies:
            print("No strategies registered")
            return

        for name in sorted(cls._strategies.keys()):
            desc = cls.describe(name)
            strategy_class = desc.get('class', 'Unknown')
            docstring = desc.get('docstring', 'No description').split('\n')[0]
            print(f"\n✅ {name}")
            print(f"   Class: {strategy_class}")
            print(f"   Info: {docstring}")

        print("\n" + "="*60 + "\n")
