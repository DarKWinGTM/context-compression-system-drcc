"""
Main Context Processor - Integration Layer
Coordinates compression, header generation, and output management
"""

from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass

# PHASE 11: Cleanup - removed legacy header_styles imports
# Now using centralized HeaderSystem from header_manager.py
from .compression_engine import CompressionEngine, CompressionLevel, CompressionResult
from ..config.platform_loader import PlatformConfig, PlatformConfigLoader
from .header_config import HeaderConfig


@dataclass
class ProcessingResult:
    """Result of context processing operation (ผลลัพธ์การประมวลผล context)"""
    platform_id: str
    output_file: str
    compression_result: CompressionResult
    success: bool
    error_message: Optional[str] = None


class ContextProcessor:
    """
    Main processor coordinating all compression operations
    (ตัวประมวลผลหลักที่ประสานงานการบีบอัดทั้งหมด)
    """

    def __init__(self, config_dir: str, template_file: str):
        """
        Initialize context processor

        Args:
            config_dir: Directory containing platform configs
            template_file: Path to CONTEXT.TEMPLATE.md
        """
        self.config_loader = PlatformConfigLoader(config_dir)
        # PHASE 11: Removed legacy HeaderStyleSystem
        # Header generation now handled by centralized HeaderSystem in header_manager.py
        self.template_file = Path(template_file)

        # Load template content
        if not self.template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")

        with open(self.template_file, 'r', encoding='utf-8') as f:
            self.template_content = f.read()

        # Load platform configs
        self.config_loader.load_all()

    def process_platform(
        self,
        platform_id: str,
        custom_compression: Optional[str] = None,
        custom_patterns: Optional[List[str]] = None
    ) -> ProcessingResult:
        """
        Process context for specific platform
        (ประมวลผล context สำหรับแพลตฟอร์มเฉพาะ)

        Args:
            platform_id: Platform identifier
            custom_compression: Override default compression level
            custom_patterns: Custom patterns for selective compression

        Returns:
            ProcessingResult with operation details
        """
        try:
            # Get platform config
            config = self.config_loader.get(platform_id)
            if not config:
                return ProcessingResult(
                    platform_id=platform_id,
                    output_file="",
                    compression_result=None,
                    success=False,
                    error_message=f"Platform not found: {platform_id}"
                )

            # Determine compression level
            compression_level_str = custom_compression or config.compression_default
            compression_level = CompressionLevel(compression_level_str)

            # Compress content
            engine = CompressionEngine(compression_level)
            compression_result = engine.compress(self.template_content, custom_patterns)

            # Generate header
            header_config = HeaderConfig(
                platform_name=config.name,
                target_file=config.target_file,
                show_timestamp=True,
                show_compression_info=True,
                custom_fields={"Description": config.description}
            )

            header = self.header_system.generate(
                style=config.header_style,
                config=header_config,
                compression_ratio=compression_result.compression_ratio
            )

            # Combine header + compressed content
            final_content = header + compression_result.compressed_text

            # Write to output file
            output_path = self.config_loader.get_output_path(platform_id)
            if not output_path:
                return ProcessingResult(
                    platform_id=platform_id,
                    output_file="",
                    compression_result=compression_result,
                    success=False,
                    error_message="Could not determine output path"
                )

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            return ProcessingResult(
                platform_id=platform_id,
                output_file=str(output_path),
                compression_result=compression_result,
                success=True
            )

        except Exception as e:
            return ProcessingResult(
                platform_id=platform_id,
                output_file="",
                compression_result=None,
                success=False,
                error_message=str(e)
            )

    def process_all_platforms(
        self,
        custom_compression: Optional[Dict[str, str]] = None
    ) -> List[ProcessingResult]:
        """
        Process context for all configured platforms
        (ประมวลผล context สำหรับทุกแพลตฟอร์ม)

        Args:
            custom_compression: Dict mapping platform_id to compression level

        Returns:
            List of ProcessingResult for each platform
        """
        results = []
        platforms = self.config_loader.list_platforms()

        for platform_id in platforms:
            compression = None
            if custom_compression and platform_id in custom_compression:
                compression = custom_compression[platform_id]

            result = self.process_platform(platform_id, compression)
            results.append(result)

        return results

    def get_platform_list(self) -> List[str]:
        """Get list of available platforms (ดึงรายการแพลตฟอร์มที่ใช้ได้)"""
        return self.config_loader.list_platforms()

    def get_platform_config(self, platform_id: str) -> Optional[PlatformConfig]:
        """Get configuration for specific platform (ดึง config แพลตฟอร์ม)"""
        return self.config_loader.get(platform_id)

    def validate_platform(self, platform_id: str) -> bool:
        """Check if platform is valid (ตรวจสอบว่าแพลตฟอร์มถูกต้อง)"""
        return self.config_loader.get(platform_id) is not None

    def get_stats(self) -> Dict[str, any]:
        """Get processor statistics (ดึงสถิติ processor)"""
        return {
            "template_file": str(self.template_file),
            "template_size": len(self.template_content),
            "loader_stats": self.config_loader.get_stats(),
            "available_platforms": self.get_platform_list()
        }

    def reload_config(self):
        """Reload platform configurations (โหลด config ใหม่)"""
        self.config_loader.reload()

    def reload_template(self):
        """Reload template content (โหลด template ใหม่)"""
        if not self.template_file.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_file}")

        with open(self.template_file, 'r', encoding='utf-8') as f:
            self.template_content = f.read()
