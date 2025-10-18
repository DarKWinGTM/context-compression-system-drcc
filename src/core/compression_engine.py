"""
Context Compression Engine - Core Implementation
Handles context compression with multiple strategies (basic, aggressive, selective)
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CompressionLevel(Enum):
    """Compression levels available (การระดับการบีบอัด)"""
    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    SELECTIVE = "selective"


@dataclass
class CompressionResult:
    """Result of compression operation (ผลลัพธ์การบีบอัด)"""
    compressed_text: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    sections_removed: List[str]
    metadata: Dict[str, any]


class CompressionEngine:
    """
    Core compression engine for context optimization
    (เครื่องมือบีบอัด context หลัก)
    """

    def __init__(self, level: CompressionLevel = CompressionLevel.BASIC):
        """
        Initialize compression engine

        Args:
            level: Compression level to use
        """
        self.level = level
        self.stats = {
            "total_compressed": 0,
            "total_saved_bytes": 0,
            "compression_history": []
        }

    def compress(self, text: str, custom_patterns: Optional[List[str]] = None) -> CompressionResult:
        """
        Compress text based on configured level
        (บีบอัดข้อความตามระดับที่ตั้งค่า)

        Args:
            text: Input text to compress
            custom_patterns: Optional custom patterns for selective compression

        Returns:
            CompressionResult with compressed text and metadata
        """
        original_size = len(text)
        sections_removed = []

        # Apply compression based on level
        if self.level == CompressionLevel.BASIC:
            compressed_text = self._basic_compression(text, sections_removed)
        elif self.level == CompressionLevel.AGGRESSIVE:
            compressed_text = self._aggressive_compression(text, sections_removed)
        else:  # SELECTIVE
            compressed_text = self._selective_compression(text, custom_patterns, sections_removed)

        compressed_size = len(compressed_text)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        # Update statistics
        self._update_stats(original_size, compressed_size)

        return CompressionResult(
            compressed_text=compressed_text,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            sections_removed=sections_removed,
            metadata={
                "level": self.level.value,
                "patterns_used": custom_patterns or []
            }
        )

    def _basic_compression(self, text: str, sections_removed: List[str]) -> str:
        """
        Basic compression: Remove comments, extra whitespace, empty lines
        (บีบอัดพื้นฐาน: ลบคอมเมนต์ ช่องว่างเกิน บรรทัดว่าง)
        """
        result = text

        # Remove markdown comments
        result = re.sub(r'<!--.*?-->', '', result, flags=re.DOTALL)
        sections_removed.append("HTML comments")

        # Remove multiple consecutive empty lines (keep max 1)
        result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
        sections_removed.append("Extra empty lines")

        # Remove trailing whitespace from lines
        result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)
        sections_removed.append("Trailing whitespace")

        return result

    def _aggressive_compression(self, text: str, sections_removed: List[str]) -> str:
        """
        Aggressive compression: Maximum compression while keeping AI understanding
        (บีบอัดสูงสุดโดยที่ AI ยังเข้าใจได้ 100%)
        """
        result = self._basic_compression(text, sections_removed)

        # Remove example sections with emoji
        result = re.sub(
            r'(?:^|\n)#{2,4}\s+\*\*[📋💡🎯]\s*Example[^*]+\*\*[^\n]*\n+(?:(?!#{2,4}\s+\*\*).)*?(?=\n#{2,4}\s+\*\*|\Z)',
            '',
            result,
            flags=re.DOTALL | re.MULTILINE | re.IGNORECASE
        )
        sections_removed.append("Example sections")

        # Remove code blocks
        result = re.sub(r'\n```[^\n]*\n.*?\n```\n', '\n', result, flags=re.DOTALL)
        sections_removed.append("Code blocks")

        # Remove visual diagrams (ASCII art boxes)
        result = re.sub(r'\n```[^\n]*\n[^\n]*[┌┐└┘├┤│─━]+[^\n]*\n.*?\n```\n', '\n', result, flags=re.DOTALL)
        sections_removed.append("Visual diagrams")

        # Remove blockquotes
        result = re.sub(r'\n>\s+.*$', '', result, flags=re.MULTILINE)
        sections_removed.append("Blockquotes")

        # Remove "Constitutional Basis" explanations (keep only the principles)
        result = re.sub(
            r'#### \*\*📜 Constitutional Basis:\*\*\n\*\*รากฐานรัธรีมนูญ\*\*\n.*?(?=\n####)',
            '',
            result,
            flags=re.DOTALL
        )
        sections_removed.append("Constitutional Basis explanations")

        # Remove verbose "Implementation Standards" sections (keep rules only)
        result = re.sub(
            r'#### \*\*📊 Implementation Standards:\*\*\n\*\*มาตรฐานการนำไปใช้\*\*\n\n```\n.*?\n```',
            '',
            result,
            flags=re.DOTALL
        )
        sections_removed.append("Verbose Implementation Standards")

        # Remove "Quality Metrics" sections (too verbose for AI)
        result = re.sub(
            r'#### \*\*🏗️ Quality Metrics:\*\*\n\*\*เมตริกคุณภาพ\*\*\n.*?(?=\n####)',
            '',
            result,
            flags=re.DOTALL
        )
        sections_removed.append("Quality Metrics")

        # Remove "Visual Framework" sections (diagrams not needed for AI)
        result = re.sub(
            r'#### \*\*🧠 Visual Framework:\*\*\n.*?(?=\n####)',
            '',
            result,
            flags=re.DOTALL
        )
        sections_removed.append("Visual Frameworks")

        # Deduplicate repeated sections
        result = self._deduplicate_sections(result, sections_removed)

        # Compress multiple blank lines to single
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result

    def _deduplicate_sections(self, text: str, sections_removed: List[str]) -> str:
        """
        Remove duplicate sections/headers to prevent content repetition
        (ลบ sections/headers ที่ซ้ำกันเพื่อป้องกันการทำซ้ำเนื้อหา)
        """
        lines = text.split('\n')
        seen_sections = {}
        deduplicated_lines = []
        current_section = []
        current_header = None

        for line in lines:
            # Check if line is a header
            if re.match(r'^#{1,6}\s+', line):
                # Save previous section if exists
                if current_section:
                    section_key = (current_header, '\n'.join(current_section))
                    if section_key not in seen_sections:
                        deduplicated_lines.extend(current_section)
                        seen_sections[section_key] = True
                    else:
                        sections_removed.append(f"Duplicate: {current_header[:50]}")

                current_header = line
                current_section = [line]
            else:
                current_section.append(line)

        # Add last section
        if current_section:
            section_key = (current_header, '\n'.join(current_section))
            if section_key not in seen_sections:
                deduplicated_lines.extend(current_section)

        return '\n'.join(deduplicated_lines)

    def _selective_compression(
        self,
        text: str,
        custom_patterns: Optional[List[str]],
        sections_removed: List[str]
    ) -> str:
        """
        Selective compression: Remove specific sections based on patterns
        (บีบอัดแบบเลือก: ลบส่วนเฉพาะตาม pattern)
        """
        result = self._basic_compression(text, sections_removed)

        if not custom_patterns:
            return result

        for pattern in custom_patterns:
            # Escape pattern for regex if it's a plain string
            if not self._is_regex_pattern(pattern):
                pattern = re.escape(pattern)

            # Remove sections matching pattern
            result = re.sub(
                f'(?:^|\n)##?\s+.*{pattern}.*?(?=\n##?\s+|\Z)',
                '',
                result,
                flags=re.DOTALL | re.MULTILINE | re.IGNORECASE
            )
            sections_removed.append(f"Pattern: {pattern}")

        return result

    def _is_regex_pattern(self, pattern: str) -> bool:
        """Check if string contains regex special characters"""
        regex_chars = r'[.*+?^${}()|[\]\\]'
        return bool(re.search(regex_chars, pattern))

    def _update_stats(self, original_size: int, compressed_size: int):
        """Update compression statistics (อัปเดตสถิติการบีบอัด)"""
        saved_bytes = original_size - compressed_size

        self.stats["total_compressed"] += 1
        self.stats["total_saved_bytes"] += saved_bytes
        self.stats["compression_history"].append({
            "original_size": original_size,
            "compressed_size": compressed_size,
            "saved_bytes": saved_bytes
        })

    def get_stats(self) -> Dict[str, any]:
        """Get compression statistics (ดึงสถิติการบีบอัด)"""
        return self.stats.copy()

    def reset_stats(self):
        """Reset compression statistics (รีเซ็ตสถิติ)"""
        self.stats = {
            "total_compressed": 0,
            "total_saved_bytes": 0,
            "compression_history": []
        }
