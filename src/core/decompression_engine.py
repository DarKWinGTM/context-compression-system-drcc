"""
Decompression Engine for Context Compression System
Provides lossless decompression of dictionary-compressed content
"""

import re
from typing import Dict, List, Tuple
from pathlib import Path


class DecompressionEngine:
    """
    Lossless decompression engine for dictionary-compressed content.
    Supports Template (T1-T19), Phrase (€a-€€ai), and Word ($A-$V, ฿a-฿฿cp) dictionaries.
    """

    def __init__(self):
        """Initialize decompression engine with empty dictionaries"""
        self.template_dict: Dict[str, str] = {}
        self.phrase_dict: Dict[str, str] = {}
        self.word_dict: Dict[str, str] = {}

    def load_dictionaries_from_text(self, text: str) -> None:
        """
        Load dictionaries from DEPLOYABLE file text.

        Args:
            text: Full text of DEPLOYABLE file containing dictionary sections
        """
        # Extract dictionary sections
        template_section = self._extract_section(text, "Template Dictionary")
        phrase_section = self._extract_section(text, "Phrase Dictionary")
        word_section = self._extract_section(text, "Word Dictionary")

        # Parse each dictionary
        if template_section:
            self.template_dict = self._parse_template_dictionary(template_section)
        if phrase_section:
            self.phrase_dict = self._parse_phrase_dictionary(phrase_section)
        if word_section:
            self.word_dict = self._parse_word_dictionary(word_section)

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific dictionary section from text"""
        pattern = rf"### \*\*{section_name} \(\d+ entries\)\*\*\n```\n(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1) if match else ""

    def _parse_template_dictionary(self, section: str) -> Dict[str, str]:
        """
        Parse template dictionary (T1-T19 format).

        Example:
            T1 = **📜 Constitutional Basis:**
            T2 = #### **📜 Constitutional Basis:**
        """
        template_dict = {}
        for line in section.strip().split('\n'):
            if '=' in line:
                code, value = line.split(' = ', 1)
                template_dict[code.strip()] = value.strip()
        return template_dict

    def _parse_phrase_dictionary(self, section: str) -> Dict[str, str]:
        """
        Parse phrase dictionary (€a-€€ai format).

        Example:
            €a = Constitutional Basis | €aa = Agent Framework | €ab = System
        """
        phrase_dict = {}
        for line in section.strip().split('\n'):
            # Split by pipe separator
            entries = line.split(' | ')
            for entry in entries:
                if ' = ' in entry:
                    code, value = entry.split(' = ', 1)
                    phrase_dict[code.strip()] = value.strip()
        return phrase_dict

    def _parse_word_dictionary(self, section: str) -> Dict[str, str]:
        """
        Parse word dictionary ($A-$V and ฿a-฿฿cp formats).

        Example:
            $A = Constitutional | $B = Framework | $C = Principle
            ฿a = Compliance | ฿aa = Task | ฿ab = Efficiency
        """
        word_dict = {}
        for line in section.strip().split('\n'):
            # Split by pipe separator
            entries = line.split(' | ')
            for entry in entries:
                if ' = ' in entry:
                    code, value = entry.split(' = ', 1)
                    word_dict[code.strip()] = value.strip()
        return word_dict

    def decompress(self, compressed_text: str) -> str:
        """
        Decompress text using loaded dictionaries.

        Args:
            compressed_text: Compressed text containing dictionary codes

        Returns:
            Fully decompressed text

        Process:
            1. Apply template dictionary (T1-T19)
            2. Apply phrase dictionary (€a-€€ai)
            3. Apply word dictionary ($A-$V, ฿a-฿฿cp)
        """
        if not self.template_dict or not self.phrase_dict or not self.word_dict:
            raise ValueError("Dictionaries not loaded. Call load_dictionaries_from_text() first.")

        text = compressed_text

        # Step 1: Template decompression (T1-T19)
        text = self._decompress_templates(text)

        # Step 2: Phrase decompression (€a-€€ai)
        text = self._decompress_phrases(text)

        # Step 3: Word decompression ($A-$V, ฿a-฿฿cp)
        text = self._decompress_words(text)

        return text

    def _decompress_templates(self, text: str) -> str:
        """Replace template codes (T1-T19) with full templates"""
        # Sort by length (longest first) to handle T1, T10, T11, T18, T19 correctly
        # T18 must be replaced before T1, T19 before T1, T10 before T1, etc.
        sorted_codes = sorted(self.template_dict.keys(), key=len, reverse=True)

        for code in sorted_codes:
            value = self.template_dict[code]
            # Simple replacement (order matters - longer codes first)
            text = text.replace(code, value)

        return text

    def _decompress_phrases(self, text: str) -> str:
        """Replace phrase codes (€a-€€ai) with full phrases"""
        # Sort by length (longest first) to handle €a, €aa, €€ai correctly
        sorted_codes = sorted(self.phrase_dict.keys(), key=len, reverse=True)

        for code in sorted_codes:
            value = self.phrase_dict[code]
            # Phrase codes can appear in various contexts
            text = text.replace(code, value)

        return text

    def _decompress_words(self, text: str) -> str:
        """Replace word codes ($A-$V, ฿a-฿฿cp) with full words"""
        # Sort by length (longest first) to handle $A, ฿a, ฿aa, ฿฿cp correctly
        sorted_codes = sorted(self.word_dict.keys(), key=len, reverse=True)

        for code in sorted_codes:
            value = self.word_dict[code]
            # Word codes can appear in various contexts:
            # - Standalone: "$A " or " $A" or "$A\n"
            # - In compounds: "$A-based" or "$A:" or "$A‡"
            # Use simple string replacement (dictionaries are ordered by length, so longer codes replaced first)
            text = text.replace(code, value)

        return text

    def decompress_file(self, deployable_path: Path, output_path: Path) -> Dict:
        """
        Decompress a complete DEPLOYABLE file.

        Args:
            deployable_path: Path to DEPLOYABLE_*.md file
            output_path: Path to save decompressed output

        Returns:
            Statistics about decompression process
        """
        # Read DEPLOYABLE file
        with open(deployable_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        # Load dictionaries from file
        self.load_dictionaries_from_text(full_text)

        # Extract compressed content (after "# 📄 **COMPRESSED CONTENT BEGINS HERE**")
        content_marker = "# 📄 **COMPRESSED CONTENT BEGINS HERE**"
        if content_marker in full_text:
            parts = full_text.split(content_marker, 1)
            compressed_content = parts[1] if len(parts) > 1 else ""
        else:
            raise ValueError(f"Content marker not found in {deployable_path}")

        # Decompress content
        decompressed_content = self.decompress(compressed_content)

        # Save decompressed output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(decompressed_content)

        # Calculate statistics
        stats = {
            'deployable_file': str(deployable_path),
            'output_file': str(output_path),
            'compressed_size': len(compressed_content),
            'decompressed_size': len(decompressed_content),
            'template_entries': len(self.template_dict),
            'phrase_entries': len(self.phrase_dict),
            'word_entries': len(self.word_dict),
            'total_dictionary_entries': len(self.template_dict) + len(self.phrase_dict) + len(self.word_dict),
            'expansion_ratio': round(len(decompressed_content) / len(compressed_content), 2) if compressed_content else 0
        }

        return stats

    def get_dictionary_stats(self) -> Dict:
        """Get statistics about loaded dictionaries"""
        return {
            'template_codes': len(self.template_dict),
            'phrase_codes': len(self.phrase_dict),
            'word_codes': len(self.word_dict),
            'total_codes': len(self.template_dict) + len(self.phrase_dict) + len(self.word_dict),
            'template_codes_list': list(self.template_dict.keys())[:10],  # Sample
            'phrase_codes_list': list(self.phrase_dict.keys())[:10],
            'word_codes_list': list(self.word_dict.keys())[:10]
        }


def decompress_all_platforms(deployable_dir: Path = Path("outputs"),
                            output_dir: Path = Path("outputs/decompressed")) -> List[Dict]:
    """
    Decompress all DEPLOYABLE_*.md files in directory.

    Args:
        deployable_dir: Directory containing DEPLOYABLE files
        output_dir: Directory to save decompressed files

    Returns:
        List of decompression statistics for each platform
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    deployable_files = sorted(deployable_dir.glob("DEPLOYABLE_*.md"))

    for deployable_path in deployable_files:
        # Generate output filename
        platform_name = deployable_path.stem.replace("DEPLOYABLE_", "")
        output_path = output_dir / f"DECOMPRESSED_{platform_name}.md"

        # Decompress
        engine = DecompressionEngine()
        try:
            stats = engine.decompress_file(deployable_path, output_path)
            stats['status'] = 'SUCCESS'
            print(f"✅ {platform_name}: {stats['compressed_size']} → {stats['decompressed_size']} chars "
                  f"({stats['expansion_ratio']}x expansion)")
        except Exception as e:
            stats = {
                'deployable_file': str(deployable_path),
                'output_file': str(output_path),
                'status': 'FAILED',
                'error': str(e)
            }
            print(f"❌ {platform_name}: Decompression failed - {e}")

        results.append(stats)

    return results


if __name__ == "__main__":
    """Test decompression engine with DEPLOYABLE files"""
    print("🔄 Context Decompression Engine - Test Mode\n")

    # Test decompression
    results = decompress_all_platforms()

    # Summary
    print(f"\n📊 Decompression Summary:")
    print(f"{'='*60}")

    success_count = sum(1 for r in results if r.get('status') == 'SUCCESS')
    print(f"Total files processed: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")

    if success_count > 0:
        avg_expansion = sum(r.get('expansion_ratio', 0) for r in results if r.get('status') == 'SUCCESS') / success_count
        print(f"Average expansion ratio: {avg_expansion:.2f}x")
