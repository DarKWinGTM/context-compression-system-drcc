"""
Platform Configuration Loader
Loads and validates platform-specific configurations from JSON files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PlatformConfig:
    """Platform configuration data structure (โครงสร้างข้อมูล config แพลตฟอร์ม)"""
    name: str
    target_file: str
    output_dir: str
    header_style: str
    compression_default: str
    description: str

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.compression_default not in ["basic", "aggressive", "selective"]:
            raise ValueError(
                f"Invalid compression_default: {self.compression_default}. "
                "Must be: basic, aggressive, or selective"
            )


class PlatformConfigLoader:
    """
    Platform configuration loader and validator
    (ตัวโหลดและตรวจสอบ config แพลตฟอร์ม)
    """

    def __init__(self, config_dir: str):
        """
        Initialize platform config loader

        Args:
            config_dir: Directory containing platform JSON configs
        """
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, PlatformConfig] = {}
        self._loaded = False

    def load_all(self) -> Dict[str, PlatformConfig]:
        """
        Load all platform configurations from directory
        (โหลด config ทุกแพลตฟอร์มจากไดเรกทอรี)

        Returns:
            Dictionary mapping platform names to configurations
        """
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")

        self._configs.clear()

        # Load all JSON files in config directory
        json_files = list(self.config_dir.glob("*.json"))

        if not json_files:
            raise ValueError(f"No JSON config files found in: {self.config_dir}")

        for json_file in json_files:
            try:
                config = self._load_single(json_file)
                platform_id = json_file.stem  # filename without extension
                self._configs[platform_id] = config
            except Exception as e:
                raise ValueError(f"Failed to load {json_file.name}: {str(e)}")

        self._loaded = True
        return self._configs.copy()

    def _load_single(self, config_file: Path) -> PlatformConfig:
        """
        Load single platform configuration file
        (โหลดไฟล์ config แพลตฟอร์มเดียว)
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate required fields
        required_fields = [
            "name", "target_file", "output_dir",
            "header_style", "compression_default", "description"
        ]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return PlatformConfig(
            name=data["name"],
            target_file=data["target_file"],
            output_dir=data["output_dir"],
            header_style=data["header_style"],
            compression_default=data["compression_default"],
            description=data["description"]
        )

    def get(self, platform_id: str) -> Optional[PlatformConfig]:
        """
        Get configuration for specific platform
        (ดึง config สำหรับแพลตฟอร์มเฉพาะ)

        Args:
            platform_id: Platform identifier

        Returns:
            PlatformConfig or None if not found
        """
        if not self._loaded:
            self.load_all()

        return self._configs.get(platform_id)

    def get_all(self) -> Dict[str, PlatformConfig]:
        """
        Get all loaded configurations
        (ดึง config ทั้งหมดที่โหลดไว้)
        """
        if not self._loaded:
            self.load_all()

        return self._configs.copy()

    def list_platforms(self) -> List[str]:
        """
        List all available platform IDs
        (แสดงรายการ platform ID ทั้งหมด)
        """
        if not self._loaded:
            self.load_all()

        return list(self._configs.keys())

    def validate_output_dir(self, platform_id: str) -> bool:
        """
        Validate that output directory exists for platform
        (ตรวจสอบว่าไดเรกทอรี output มีอยู่จริง)

        Args:
            platform_id: Platform identifier

        Returns:
            True if output directory exists
        """
        config = self.get(platform_id)
        if not config:
            return False

        output_path = Path(config.output_dir)
        return output_path.exists() and output_path.is_dir()

    def get_output_path(self, platform_id: str) -> Optional[Path]:
        """
        Get full output file path for platform
        (ดึง path ไฟล์ output เต็มสำหรับแพลตฟอร์ม)

        Args:
            platform_id: Platform identifier

        Returns:
            Full path to output file or None
        """
        config = self.get(platform_id)
        if not config:
            return None

        return Path(config.output_dir) / config.target_file

    def reload(self):
        """
        Reload all configurations from disk
        (โหลด config ทั้งหมดจากดิสก์ใหม่)
        """
        self._loaded = False
        return self.load_all()

    def get_stats(self) -> Dict[str, any]:
        """
        Get loader statistics
        (ดึงสถิติ loader)
        """
        if not self._loaded:
            self.load_all()

        return {
            "total_platforms": len(self._configs),
            "platforms": list(self._configs.keys()),
            "config_directory": str(self.config_dir),
            "compression_levels": {
                pid: config.compression_default
                for pid, config in self._configs.items()
            }
        }
