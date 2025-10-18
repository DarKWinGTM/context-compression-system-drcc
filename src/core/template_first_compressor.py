"""
Template-First Compression Strategy
Extract templates BEFORE dictionary compression
"""

import re
from typing import Tuple, Dict


class TemplateFirstCompressor:
    """Extract repeating patterns as templates before dictionary compression"""

    def __init__(self):
        self.templates = {}
        self.template_counter = 0

    def extract_templates(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Extract repeating patterns and replace with template codes
        Returns: (text_with_template_codes, template_dictionary)
        """
        result = text
        stats = {
            'constitutional_blocks': 0,
            'quality_metrics': 0,
            'core_frameworks': 0,
            'implementation_blocks': 0,
            'total_saved': 0
        }

        # Pattern 1: Constitutional Basis blocks (25 occurrences)
        constitutional_pattern = r'(#### \*\*📜 Constitutional Basis:\*\*\n\*\*รากฐานรัธรีมนูญ\*\*\n- \*\*Authority\*\*: )([^\n]+)(\n- \*\*Rationale\*\*: )([^\n]+)'

        matches = list(re.finditer(constitutional_pattern, result))
        if matches:
            # Create template
            template_id = self._new_template_id()
            self.templates[template_id] = {
                'pattern': '¢CB',  # Constitutional Basis template
                'structure': '#### **📜 Constitutional Basis:**\n**รากฐานรัธรีมนูญ**\n- **Authority**: {}\n- **Rationale**: {}'
            }

            # Replace with template references
            for match in reversed(matches):
                authority = match.group(2)
                rationale = match.group(4)
                replacement = f'¢CB{{{authority}|{rationale}}}'
                result = result[:match.start()] + replacement + result[match.end():]
                stats['constitutional_blocks'] += 1
                # Save ~200 chars per block (structure overhead)
                stats['total_saved'] += len(match.group(0)) - len(replacement)

        # Pattern 2: Quality Metrics blocks (16 occurrences)
        metrics_pattern = r'#### \*\*🏗️ Quality Metrics:\*\*\n\*\*เมตริกคุณภาพ\*\*\n'
        matches = list(re.finditer(metrics_pattern, result))
        if matches:
            template_id = self._new_template_id()
            self.templates[template_id] = {
                'pattern': '¢QM',
                'structure': '#### **🏗️ Quality Metrics:**\n**เมตริกคุณภาพ**\n'
            }

            for match in reversed(matches):
                result = result[:match.start()] + '¢QM\n' + result[match.end():]
                stats['quality_metrics'] += 1
                stats['total_saved'] += len(match.group(0)) - 4

        # Pattern 3: Core Framework headers (24 occurrences)
        framework_pattern = r'#### \*\*🎯 Core ([A-Za-z\s]+) Framework:\*\*\n\*\*กรอบ([^*]+)\*\*\n'
        matches = list(re.finditer(framework_pattern, result))
        if matches:
            template_id = self._new_template_id()
            self.templates[template_id] = {
                'pattern': '¢CF',
                'structure': '#### **🎯 Core {} Framework:**\n**กรอบ{}**\n'
            }

            for match in reversed(matches):
                eng_name = match.group(1)
                thai_name = match.group(2)
                replacement = f'¢CF{{{eng_name}|{thai_name}}}\n'
                result = result[:match.start()] + replacement + result[match.end():]
                stats['core_frameworks'] += 1
                stats['total_saved'] += len(match.group(0)) - len(replacement)

        # Pattern 4: Implementation Standards blocks
        impl_pattern = r'#### \*\*📊 Implementation Standards:\*\*\n\*\*มาตรฐานการนำไปใช้\*\*\n'
        matches = list(re.finditer(impl_pattern, result))
        if matches:
            template_id = self._new_template_id()
            self.templates[template_id] = {
                'pattern': '¢IS',
                'structure': '#### **📊 Implementation Standards:**\n**มาตรฐานการนำไปใช้**\n'
            }

            for match in reversed(matches):
                result = result[:match.start()] + '¢IS\n' + result[match.end():]
                stats['implementation_blocks'] += 1
                stats['total_saved'] += len(match.group(0)) - 4

        return result, self.templates, stats

    def _new_template_id(self) -> str:
        """Generate new template ID"""
        self.template_counter += 1
        return f"T{self.template_counter:03d}"

    def decompress_templates(self, text: str, templates: Dict) -> str:
        """Restore templates to original form"""
        result = text

        # Restore Constitutional Basis
        cb_pattern = r'¢CB\{([^|]+)\|([^}]+)\}'
        result = re.sub(
            cb_pattern,
            r'#### **📜 Constitutional Basis:**\n**รากฐานรัธรีมนูญ**\n- **Authority**: \1\n- **Rationale**: \2',
            result
        )

        # Restore Quality Metrics
        result = result.replace('¢QM\n', '#### **🏗️ Quality Metrics:**\n**เมตริกคุณภาพ**\n')

        # Restore Core Framework
        cf_pattern = r'¢CF\{([^|]+)\|([^}]+)\}'
        result = re.sub(
            cf_pattern,
            r'#### **🎯 Core \1 Framework:**\n**กรอบ\2**\n',
            result
        )

        # Restore Implementation Standards
        result = result.replace('¢IS\n', '#### **📊 Implementation Standards:**\n**มาตรฐานการนำไปใช้**\n')

        return result
