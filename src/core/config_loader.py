#!/usr/bin/env python3
"""
Unified Config Loader - Single Source of Truth
Loads platform configurations from platform_configs/*.json

Constitutional Basis: PROJECT.PROMPT.md - Config-Driven Architecture
Purpose: Eliminate hardcoded platform mappings, use JSON configs as source of truth
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class ConfigLoader:
    """
    Unified configuration loader for all platform configs.

    Single Source of Truth: platform_configs/*.json
    All modules should use this loader instead of hardcoding platform data.
    """

    def __init__(self, config_dir: str = "platform_configs"):
        """
        Initialize config loader.

        Args:
            config_dir: Directory containing platform config JSON files
        """
        self.config_dir = Path(config_dir)

        # Ensure config directory exists
        if not self.config_dir.exists():
            # Try relative to project root
            project_root = Path(__file__).parent.parent.parent
            self.config_dir = project_root / config_dir

        if not self.config_dir.exists():
            raise FileNotFoundError(
                f"Config directory not found: {config_dir}\n"
                f"Expected at: {self.config_dir}"
            )

        # Load all platform configs
        self.platforms = self._load_all_configs()

    def _load_all_configs(self) -> Dict[str, Dict]:
        """
        Load all platform configuration files.

        Returns:
            Dictionary mapping platform_key -> platform_config
            Example: {'claude': {'name': 'Claude Code', 'target_file': 'CLAUDE.md', ...}, ...}
        """
        platforms = {}

        config_files = list(self.config_dir.glob("*.json"))

        if not config_files:
            raise ValueError(f"No config files found in: {self.config_dir}")

        for config_file in config_files:
            platform_key = config_file.stem  # claude, openai, gemini, etc.

            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Validate required fields
                required_fields = ['name', 'target_file']
                missing_fields = [field for field in required_fields if field not in config]

                if missing_fields:
                    print(f"⚠️ Warning: {config_file.name} missing fields: {missing_fields}")
                    continue

                platforms[platform_key] = config

            except json.JSONDecodeError as e:
                print(f"⚠️ Warning: Could not parse {config_file.name}: {e}")
            except Exception as e:
                print(f"⚠️ Warning: Error loading {config_file.name}: {e}")

        return platforms

    def get_platform(self, platform_key: str) -> Optional[Dict]:
        """
        Get configuration for a specific platform.

        Args:
            platform_key: Platform identifier (claude, openai, gemini, etc.)

        Returns:
            Platform configuration dict or None if not found
        """
        return self.platforms.get(platform_key)

    def get_all_platforms(self) -> Dict[str, Dict]:
        """
        Get all platform configurations.

        Returns:
            Dictionary of all platform configs
        """
        return self.platforms

    def get_platform_keys(self) -> List[str]:
        """
        Get list of all available platform keys.

        Returns:
            List of platform keys (claude, openai, gemini, etc.)
        """
        return list(self.platforms.keys())

    def get_target_filename(self, platform_key: str) -> Optional[str]:
        """
        Get target filename for a platform.

        Args:
            platform_key: Platform identifier

        Returns:
            Target filename (CLAUDE.md, AGENTS.md, etc.) or None if not found
        """
        platform = self.get_platform(platform_key)
        return platform.get('target_file') if platform else None

    def get_all_filenames(self) -> List[str]:
        """
        Get all target filenames from all platforms.

        Returns:
            List of unique filenames (CLAUDE.md, AGENTS.md, GEMINI.md, etc.)
        """
        filenames = []
        for platform in self.platforms.values():
            if 'target_file' in platform:
                filename = platform['target_file']
                if filename not in filenames:
                    filenames.append(filename)
        return filenames

    def get_platform_display_name(self, platform_key: str) -> Optional[str]:
        """
        Get display name for a platform.

        Args:
            platform_key: Platform identifier

        Returns:
            Display name (Claude Code, OpenAI Codex, etc.) or None if not found
        """
        platform = self.get_platform(platform_key)
        return platform.get('name') if platform else None

    def validate_platform(self, platform_key: str) -> bool:
        """
        Check if a platform key is valid.

        Args:
            platform_key: Platform identifier to validate

        Returns:
            True if platform exists, False otherwise
        """
        return platform_key in self.platforms

    def list_platforms_info(self) -> List[Dict]:
        """
        Get formatted list of platform information.

        Returns:
            List of dicts with platform details for display
        """
        platforms_info = []

        for key, config in self.platforms.items():
            platforms_info.append({
                'key': key,
                'name': config.get('name', 'Unknown'),
                'filename': config.get('target_file', 'Unknown'),
                'description': config.get('description', ''),
                'header_style': config.get('header_style', 'default'),
                'compression': config.get('compression_default', 'aggressive')
            })

        return platforms_info


# Global singleton instance (lazy-loaded)
_config_loader_instance = None


def get_config_loader(config_dir: str = "platform_configs") -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.

    Args:
        config_dir: Config directory (only used for first initialization)

    Returns:
        ConfigLoader singleton instance
    """
    global _config_loader_instance

    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader(config_dir)

    return _config_loader_instance


if __name__ == '__main__':
    """Test config loader"""
    print("=" * 80)
    print("🧪 TESTING UNIFIED CONFIG LOADER")
    print("=" * 80)
    print()

    # Initialize loader
    loader = ConfigLoader()

    # Display all platforms
    print("📋 Available Platforms:")
    print()

    for info in loader.list_platforms_info():
        print(f"  🔹 {info['name']:20} ({info['key']})")
        print(f"     Target: {info['filename']}")
        print(f"     Style:  {info['header_style']}")
        print(f"     Mode:   {info['compression']}")
        print()

    # Test filename extraction
    print("=" * 80)
    print("📄 All Target Filenames:")
    print("=" * 80)
    print()

    for filename in loader.get_all_filenames():
        print(f"  • {filename}")

    print()

    # Test individual platform access
    print("=" * 80)
    print("🔍 Testing Individual Platform Access:")
    print("=" * 80)
    print()

    test_platforms = ['claude', 'openai', 'invalid_platform']

    for platform_key in test_platforms:
        if loader.validate_platform(platform_key):
            name = loader.get_platform_display_name(platform_key)
            filename = loader.get_target_filename(platform_key)
            print(f"  ✅ {platform_key:15} → {name:20} → {filename}")
        else:
            print(f"  ❌ {platform_key:15} → NOT FOUND")

    print()
    print("✅ Config loader test complete")
