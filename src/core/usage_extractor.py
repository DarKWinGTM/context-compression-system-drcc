#!/usr/bin/env python3
"""
Layer 0: Usage Instructions Extractor
Separates template usage instructions from actual context content

Constitutional Basis: PROJECT.PROMPT.md - Layer 0 Implementation
Purpose: Extract lines 1-81 (TEMPLATE USAGE INSTRUCTIONS) before compression
Rationale: Usage instructions are not context content, should not be compressed
"""

import re
from typing import Dict, Tuple


class UsageInstructionsExtractor:
    """
    Extract and separate template usage instructions from context content.
    
    The CONTEXT.TEMPLATE.md file contains:
    - Lines 1-81: Usage instructions for ./THIS.md placeholder replacement
    - Lines 82+: Actual context content to be compressed
    
    This extractor identifies and separates these sections.
    """
    
    def extract(self, text: str) -> Tuple[str, str, Dict]:
        """
        Extract usage instructions from template file.
        
        Args:
            text: Full template content
            
        Returns:
            Tuple of (usage_instructions, pure_context, stats)
        """
        lines = text.split('\n')
        
        # Find the separator line (---) after usage instructions
        # Should be around line 81 based on template structure
        separator_index = self._find_separator(lines)
        
        if separator_index:
            # Split at separator
            usage_lines = lines[:separator_index+1]
            context_lines = lines[separator_index+1:]
            
            usage_instructions = '\n'.join(usage_lines)
            pure_context = '\n'.join(context_lines)
            
            stats = {
                'separator_found': True,
                'separator_line': separator_index + 1,
                'usage_lines': len(usage_lines),
                'context_lines': len(context_lines),
                'usage_chars': len(usage_instructions),
                'context_chars': len(pure_context),
                'original_chars': len(text)
            }
        else:
            # Fallback: Use first 81 lines as instructions
            usage_lines = lines[:81]
            context_lines = lines[81:]
            
            usage_instructions = '\n'.join(usage_lines)
            pure_context = '\n'.join(context_lines)
            
            stats = {
                'separator_found': False,
                'separator_line': None,
                'usage_lines': len(usage_lines),
                'context_lines': len(context_lines),
                'usage_chars': len(usage_instructions),
                'context_chars': len(pure_context),
                'original_chars': len(text),
                'warning': 'Using fallback: first 81 lines as instructions'
            }
        
        return usage_instructions, pure_context, stats
    
    def _find_separator(self, lines: list) -> int:
        """
        Find separator line (---) after usage instructions.
        
        Looking for:
        - Line that is exactly "---"
        - Appears after line 70 (around line 81)
        - Before line 100 (should not be too far)
        
        Returns:
            Line index of separator, or None if not found
        """
        for i, line in enumerate(lines):
            # Look for separator between lines 70-100
            if 70 <= i <= 100:
                if line.strip() == '---':
                    # Verify this is after usage instructions
                    # by checking if next few lines contain "Table of Contents"
                    # or other context markers
                    if i + 5 < len(lines):
                        next_lines = '\n'.join(lines[i+1:i+5])
                        if 'Table of Contents' in next_lines or 'PART I' in next_lines:
                            return i
        
        return None
    
    def count_placeholders(self, text: str) -> Dict:
        """
        Count ./THIS.md placeholders in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with placeholder statistics
        """
        placeholder_pattern = r'\./THIS\.md'
        matches = re.findall(placeholder_pattern, text)
        
        return {
            'placeholder_count': len(matches),
            'placeholder': './THIS.md',
            'needs_replacement': len(matches) > 0
        }
    
    def verify_extraction(self, usage_text: str, context_text: str) -> Dict:
        """
        Verify extraction quality.
        
        Args:
            usage_text: Extracted usage instructions
            context_text: Extracted pure context
            
        Returns:
            Verification statistics
        """
        usage_placeholders = self.count_placeholders(usage_text)
        context_placeholders = self.count_placeholders(context_text)
        
        # Check for key markers
        has_template_marker = 'TEMPLATE USAGE INSTRUCTIONS' in usage_text
        has_platform_mapping = 'AI Platform Context File Mapping' in usage_text
        has_context_start = 'Table of Contents' in context_text or 'PART I' in context_text
        
        verification = {
            'usage_section': {
                'has_template_marker': has_template_marker,
                'has_platform_mapping': has_platform_mapping,
                'placeholder_count': usage_placeholders['placeholder_count']
            },
            'context_section': {
                'has_context_start': has_context_start,
                'placeholder_count': context_placeholders['placeholder_count']
            },
            'quality_score': 0
        }
        
        # Calculate quality score
        score = 0
        if has_template_marker: score += 25
        if has_platform_mapping: score += 25
        if has_context_start: score += 25
        if usage_placeholders['placeholder_count'] > 0: score += 25
        
        verification['quality_score'] = score
        verification['status'] = 'PASS' if score >= 75 else 'FAIL'
        
        return verification


if __name__ == '__main__':
    """Test extraction on CONTEXT.TEMPLATE.md"""
    from pathlib import Path
    
    # Test file path
    template_path = Path("/home/node/workplace/AWCLOUD/TEMPLATE/CONTENT/CONTEXT.TEMPLATE.md")
    
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        exit(1)
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_text = f.read()
    
    print("=" * 80)
    print("🧪 TESTING USAGE INSTRUCTIONS EXTRACTOR")
    print("=" * 80)
    print()
    
    # Extract
    extractor = UsageInstructionsExtractor()
    usage, context, stats = extractor.extract(template_text)
    
    # Display stats
    print("📊 Extraction Statistics:")
    print(f"   Separator found:  {stats['separator_found']}")
    if stats.get('separator_line'):
        print(f"   Separator line:   {stats['separator_line']}")
    print(f"   Usage lines:      {stats['usage_lines']}")
    print(f"   Context lines:    {stats['context_lines']}")
    print(f"   Usage chars:      {stats['usage_chars']:,}")
    print(f"   Context chars:    {stats['context_chars']:,}")
    print(f"   Original chars:   {stats['original_chars']:,}")
    print()
    
    # Verify
    verification = extractor.verify_extraction(usage, context)
    print("🔍 Verification Results:")
    print(f"   Quality score:    {verification['quality_score']}/100")
    print(f"   Status:           {verification['status']}")
    print(f"   Template marker:  {verification['usage_section']['has_template_marker']}")
    print(f"   Platform mapping: {verification['usage_section']['has_platform_mapping']}")
    print(f"   Context start:    {verification['context_section']['has_context_start']}")
    print(f"   Usage placeholders: {verification['usage_section']['placeholder_count']}")
    print(f"   Context placeholders: {verification['context_section']['placeholder_count']}")
    print()
    
    # Preview
    print("📄 Preview:")
    print()
    print("Usage Instructions (first 300 chars):")
    print(usage[:300])
    print("...")
    print()
    print("Pure Context (first 300 chars):")
    print(context[:300])
    print("...")
    print()
    
    if verification['status'] == 'PASS':
        print("✅ Extraction test PASSED")
        exit(0)
    else:
        print("❌ Extraction test FAILED")
        exit(1)
