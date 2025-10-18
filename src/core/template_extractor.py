"""
AggressiveTemplateExtractor - Extract and compress repeated markdown patterns
Focuses on constitutional sections, headers, code blocks, and list patterns.
"""

import re
from typing import Dict, List, Tuple
from collections import defaultdict


class AggressiveTemplateExtractor:
    """
    Extract repeated markdown structures and replace with template references.

    Target patterns:
    - Constitutional sections (📜, 🎯, 📊, 🏗️, 🧠, 💡)
    - H4 headers with common structure
    - Code block wrappers
    - List patterns
    """

    def __init__(self):
        self.templates = {}
        self.template_counter = 0

    def extract_constitutional_sections(self, text: str) -> Tuple[str, int]:
        """
        Extract constitutional section patterns.

        Pattern example:
        #### **📜 Constitutional Basis:**
        **รากฐานรัธรีมนูญ**
        - **Authority**: ...
        - **Rationale**: ...

        Replace with: ¢CB{authority}{rationale}
        """
        original_length = len(text)

        # Pattern 1: Constitutional Basis
        cb_pattern = r'#### \*\*📜 Constitutional Basis:\*\*\n\*\*รากฐานรัธรีมนูญ\*\*\n- \*\*Authority\*\*: ([^\n]+)\n- \*\*Rationale\*\*: ([^\n]+)'

        def cb_replacement(match):
            authority = match.group(1)
            rationale = match.group(2)
            return f'¢CB{{{authority}}}{{{rationale}}}'

        text = re.sub(cb_pattern, cb_replacement, text)

        # Pattern 2: Core Framework (🎯)
        cf_pattern = r'#### \*\*🎯 Core ([^:]+) Framework:\*\*\n\*\*กรอบ([^*]+)\*\*'

        def cf_replacement(match):
            name = match.group(1)
            thai = match.group(2)
            return f'¢CF{{{name}}}{{{thai}}}'

        text = re.sub(cf_pattern, cf_replacement, text)

        # Pattern 3: Implementation Standards (📊)
        is_pattern = r'#### \*\*📊 Implementation Standards:\*\*\n\*\*มาตรฐานการนำไปใช้\*\*'
        text = re.sub(is_pattern, '¢IS', text)

        # Pattern 4: Quality Metrics (🏗️)
        qm_pattern = r'#### \*\*🏗️ Quality Metrics:\*\*\n\*\*เมตริกคุณภาพ\*\*'
        text = re.sub(qm_pattern, '¢QM', text)

        # Pattern 5: Visual Framework (🧠)
        vf_pattern = r'#### \*\*🧠 Visual Framework:\*\*'
        text = re.sub(vf_pattern, '¢VF', text)

        # Pattern 6: Practical Examples (💡)
        pe_pattern = r'#### \*\*💡 Practical Examples:\*\*\n\*\*ตัวอย่างการปฏิบัติ\*\*'
        text = re.sub(pe_pattern, '¢PE', text)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def extract_header_patterns(self, text: str) -> Tuple[str, int]:
        """
        Extract repeated H4 header structures.

        Common pattern: #### **🎯 Word Word Word:**
        Replace with: ¢H4{emoji}{text}
        """
        original_length = len(text)

        # Extract H4 headers with emoji and bold
        h4_pattern = r'#### \*\*([🔍📋🎯🚀⚙️🔧💻📊🌐🛡️⚠️📌📄🗂️🎭🧠]) ([^*]+)\*\*'

        def h4_replacement(match):
            emoji = match.group(1)
            text_content = match.group(2)
            return f'¢H4{{{emoji}}}{{{text_content}}}'

        text = re.sub(h4_pattern, h4_replacement, text)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def extract_code_block_wrappers(self, text: str) -> Tuple[str, int]:
        """
        Compress code block wrappers.

        ```language
        code
        ```

        Replace with: ¢C{language}¦code¦
        """
        original_length = len(text)

        # Find code blocks
        code_pattern = r'```(\w*)\n(.*?)```'

        def code_replacement(match):
            language = match.group(1) or ''
            code = match.group(2)
            return f'¢C{{{language}}}¦{code}¦'

        text = re.sub(code_pattern, code_replacement, text, flags=re.DOTALL)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def extract_list_patterns(self, text: str) -> Tuple[str, int]:
        """
        Compress common list patterns.

        - **Bold item**: description
        Replace with: ¢L{item}{desc}
        """
        original_length = len(text)

        # Pattern: Bold list item with description
        list_pattern = r'^- \*\*([^*]+)\*\*: ([^\n]+)$'

        def list_replacement(match):
            item = match.group(1)
            desc = match.group(2)
            return f'¢L{{{item}}}{{{desc}}}'

        text = re.sub(list_pattern, list_replacement, text, flags=re.MULTILINE)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def extract_repeated_phrases(self, text: str) -> Tuple[str, int]:
        """
        Extract frequently repeated phrases (≥10 chars, appears ≥5 times).
        """
        original_length = len(text)

        # Common repeated phrases in CLAUDE.md
        phrases = {
            'Constitutional Basis': '¢P1',
            'Implementation Standards': '¢P2',
            'Quality Metrics': '¢P3',
            'Visual Framework': '¢P4',
            'Practical Examples': '¢P5',
            'รากฐานรัธรีมนูญ': '¢T1',
            'มาตรฐานการนำไปใช้': '¢T2',
            'เมตริกคุณภาพ': '¢T3',
            'กรอบหลัก': '¢T4',
            'ตัวอย่างการปฏิบัติ': '¢T5',
        }

        for phrase, code in phrases.items():
            # Only replace if not already in a template code
            text = re.sub(r'(?<!¢)' + re.escape(phrase), code, text)

        chars_saved = original_length - len(text)
        return text, chars_saved

    def compress(self, text: str) -> Tuple[str, str, Dict[str, int]]:
        """
        Apply all template extraction methods.

        Returns:
            Tuple of (compressed_text, template_header, stats)
        """
        original_size = len(text)
        stats = {'original_size': original_size}

        # Layer 1: Constitutional sections
        text, constitutional_saved = self.extract_constitutional_sections(text)
        stats['constitutional_saved'] = constitutional_saved

        # Layer 2: Header patterns
        text, headers_saved = self.extract_header_patterns(text)
        stats['headers_saved'] = headers_saved

        # Layer 3: Code blocks
        text, code_saved = self.extract_code_block_wrappers(text)
        stats['code_saved'] = code_saved

        # Layer 4: List patterns
        text, list_saved = self.extract_list_patterns(text)
        stats['list_saved'] = list_saved

        # Layer 5: Repeated phrases
        text, phrase_saved = self.extract_repeated_phrases(text)
        stats['phrase_saved'] = phrase_saved

        stats['final_size'] = len(text)
        stats['total_saved'] = original_size - len(text)
        stats['compression_ratio'] = (stats['total_saved'] / original_size) * 100

        # Generate template header
        # PHASE 11.10: Header generation moved to centralized HeaderSystem
        return text, None, stats

    def decompress(self, compressed_text: str) -> str:
        """
        Decompress template-compressed text.

        Args:
            compressed_text: Text with template codes

        Returns:
            Decompressed text
        """
        text = compressed_text

        # Reverse order: phrases -> lists -> code -> headers -> constitutional

        # Phrases
        phrases = {
            '¢P1': 'Constitutional Basis',
            '¢P2': 'Implementation Standards',
            '¢P3': 'Quality Metrics',
            '¢P4': 'Visual Framework',
            '¢P5': 'Practical Examples',
            '¢T1': 'รากฐานรัธรีมนูญ',
            '¢T2': 'มาตรฐานการนำไปใช้',
            '¢T3': 'เมตริกคุณภาพ',
            '¢T4': 'กรอบหลัก',
            '¢T5': 'ตัวอย่างการปฏิบัติ',
        }
        for code, phrase in phrases.items():
            text = text.replace(code, phrase)

        # Lists
        list_pattern = r'¢L\{([^}]+)\}\{([^}]+)\}'
        text = re.sub(list_pattern, r'- **\1**: \2', text)

        # Code blocks
        code_pattern = r'¢C\{([^}]*)\}¦(.*?)¦'
        text = re.sub(code_pattern, r'```\1\n\2```', text, flags=re.DOTALL)

        # Headers
        h4_pattern = r'¢H4\{([^}]+)\}\{([^}]+)\}'
        text = re.sub(h4_pattern, r'#### **\1 \2**', text)

        # Constitutional patterns
        text = text.replace('¢PE', '#### **💡 Practical Examples:**\n**ตัวอย่างการปฏิบัติ**')
        text = text.replace('¢VF', '#### **🧠 Visual Framework:**')
        text = text.replace('¢QM', '#### **🏗️ Quality Metrics:**\n**เมตริกคุณภาพ**')
        text = text.replace('¢IS', '#### **📊 Implementation Standards:**\n**มาตรฐานการนำไปใช้**')

        cf_pattern = r'¢CF\{([^}]+)\}\{([^}]+)\}'
        text = re.sub(cf_pattern, r'#### **🎯 Core \1 Framework:**\n**กรอบ\2**', text)

        cb_pattern = r'¢CB\{([^}]+)\}\{([^}]+)\}'
        text = re.sub(cb_pattern, r'#### **📜 Constitutional Basis:**\n**รากฐานรัธรีมนูญ**\n- **Authority**: \1\n- **Rationale**: \2', text)

        return text
