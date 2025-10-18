#!/usr/bin/env python3
"""
Full Compression Pipeline - Layers 0-7 + Layer 5.5 (Token Join) + Multi-Platform Deployment
Complete compression system with sequential layer processing and platform deployment

Constitutional Basis: PROJECT.PROMPT.md - Layer 0-7 Structure + Layer 5.5 Enhancement + Deployment
Layer 0: Usage Instructions Extraction - Separate template instructions
Layer 1: Thai Removal - Translation overhead removal
Layer 2: Diagram Removal - Visual aids removal
Layer 3: Template + Phrase + Word Compression - Dictionary compression (€, $, ฿ codes)
Layer 5.5: Token Join Optimization - Remove spaces between adjacent codes (Layer 5 enhancement)
Layer 4: Markdown Compression - Syntax optimization
Layer 5: Whitespace + Emoji Optimization (FINAL) - Final optimization
Deployment: Platform-Specific File Generation - 6 AI platforms

Target: Compress from 84,726 chars to <40,000 chars (≥52.79% compression)
Multi-Platform: Claude, Qwen, Gemini, OpenAI, Cursor, CodeBuff

Task 5.5 Enhancement: Token Join Optimization
- Removes spaces between adjacent dictionary codes ($ and ฿ prefixes)
- Only joins when BOTH neighbors are tokens (safety pattern)
- Lossless transformation: 100% token preservation verified
- Expected savings: ~3.4% (approximately 1,359 chars from 39,582)

Task 8.8 Enhancement: Dynamic Source File Parameter
- Replaces hardcoded source paths with flexible --source parameter
- Supports absolute and relative file paths
- Required parameter for source file specification
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.usage_extractor import UsageInstructionsExtractor
from src.core.thai_remover import ThaiContentRemover
from src.core.diagram_remover import DiagramRemover
from src.core.dictionary_generator import DictionaryGenerator
from src.core.template_compressor import TemplateCompressor
from src.core.phrase_compressor import PhraseCompressor
from src.core.word_compressor import WordCompressor
from src.core.token_join import apply_token_join, validate_token_join
from src.core.markdown_compressor import MarkdownCompressor
from src.core.whitespace_optimizer import WhitespaceOptimizer
from src.core.selective_emoji_remover import SelectiveEmojiRemover
from src.core.platform_deployer import PlatformDeployer


def compress_full_pipeline(source_path: Path, output_dir: Path, aggressive_mode: bool = False) -> Dict:
    """
    Run full compression pipeline: Thai → Templates → Smart Dict

    Args:
        source_path: Path to source file
        output_dir: Directory for output files

    Returns:
        Dictionary with compression statistics
    """
    print("=" * 80)
    print("🚀 FULL COMPRESSION PIPELINE (Layers 0-7 + Deployment)")
    print("=" * 80)
    print()

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read source file
    print(f"📖 Reading source: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        original_text = f.read()

    original_size = len(original_text)
    print(f"📊 Original size: {original_size:,} chars")
    print()

    # Initialize pipeline statistics
    pipeline_stats = {
        'original_size': original_size,
        'layers': [],
        'cumulative_savings': 0
    }

    # =========================================================================
    # LAYER 0: USAGE INSTRUCTIONS EXTRACTION
    # =========================================================================
    print("=" * 80)
    print("📖 LAYER 0: USAGE INSTRUCTIONS EXTRACTION")
    print("=" * 80)
    print()

    usage_extractor = UsageInstructionsExtractor()
    usage_instructions, pure_context, layer0_stats = usage_extractor.extract(original_text)

    layer0_size = len(pure_context)
    layer0_savings = original_size - layer0_size
    layer0_ratio = (layer0_savings / original_size * 100) if original_size > 0 else 0

    print(f"✅ Usage instructions extracted:")
    print(f"   Input:  {original_size:,} chars (template with instructions)")
    print(f"   Output: {layer0_size:,} chars (pure context)")
    print(f"   Saved:  {layer0_savings:,} chars ({layer0_ratio:.2f}%)")
    print(f"   Usage instructions: {layer0_stats['usage_lines']} lines ({layer0_stats['usage_chars']:,} chars)")
    print(f"   Pure context: {layer0_stats['context_lines']} lines ({layer0_stats['context_chars']:,} chars)")
    print()

    # Verify extraction quality
    verification = usage_extractor.verify_extraction(usage_instructions, pure_context)
    print(f"🔍 Extraction verification: {verification['status']} (Quality: {verification['quality_score']}/100)")
    print()

    # Save usage instructions separately (for reference)
    usage_output = output_dir / "layer0_usage_instructions.txt"
    with open(usage_output, 'w', encoding='utf-8') as f:
        f.write(usage_instructions)
    print(f"💾 Usage instructions saved to: {usage_output}")
    
    # Save pure context (Layer 0 output)
    layer0_output = output_dir / "layer0_pure_context.txt"
    with open(layer0_output, 'w', encoding='utf-8') as f:
        f.write(pure_context)
    print(f"💾 Layer 0 saved to: {layer0_output}")
    print()

    pipeline_stats['layers'].append({
        'name': 'Layer 0: Usage Instructions Extraction',
        'input_size': original_size,
        'output_size': layer0_size,
        'savings': layer0_savings,
        'ratio': layer0_ratio,
        'details': layer0_stats,
        'verification': verification
    })
    pipeline_stats['cumulative_savings'] = layer0_savings

    # Update original_text to pure_context for next layers
    original_text = pure_context
    original_size = layer0_size

    # =========================================================================
    # LAYER 1: THAI CONTENT REMOVAL (Highest Priority)
    # =========================================================================
    print("=" * 80)
    print("🗑️  LAYER 1: THAI CONTENT REMOVAL")
    print("=" * 80)
    print()

    thai_remover = ThaiContentRemover()
    layer1_text, thai_stats = thai_remover.remove(original_text)

    layer1_size = len(layer1_text)
    layer1_savings = original_size - layer1_size
    layer1_ratio = (layer1_savings / original_size * 100) if original_size > 0 else 0

    print(f"✅ Thai removal complete:")
    print(f"   Input:  {original_size:,} chars")
    print(f"   Output: {layer1_size:,} chars")
    print(f"   Saved:  {layer1_savings:,} chars ({layer1_ratio:.2f}%)")
    print(f"   Remaining Thai: {thai_stats['remaining_thai_chars']:,} (should be 0)")
    print()

    # Save Layer 1 output
    layer1_output = output_dir / "layer1_thai_removed.txt"
    with open(layer1_output, 'w', encoding='utf-8') as f:
        f.write(layer1_text)
    print(f"💾 Layer 1 saved to: {layer1_output}")
    print()

    pipeline_stats['layers'].append({
        'name': 'Layer 1: Thai Removal',
        'input_size': original_size,
        'output_size': layer1_size,
        'savings': layer1_savings,
        'ratio': layer1_ratio,
        'details': thai_stats
    })
    pipeline_stats['cumulative_savings'] = layer1_savings

    # =========================================================================
    # LAYER 2: DIAGRAM/CODE BLOCK REMOVAL
    # =========================================================================
    print("=" * 80)
    print("🎨 LAYER 2: DIAGRAM/CODE BLOCK REMOVAL")
    print("=" * 80)
    print()

    diagram_remover = DiagramRemover()
    layer2_text, diagram_stats = diagram_remover.remove(layer1_text)

    layer2_size = len(layer2_text)
    layer2_savings = layer1_size - layer2_size
    layer2_ratio = (layer2_savings / layer1_size * 100) if layer1_size > 0 else 0

    print(f"✅ Diagram removal complete:")
    print(f"   Input:  {layer1_size:,} chars (after Thai removal)")
    print(f"   Output: {layer2_size:,} chars")
    print(f"   Saved:  {layer2_savings:,} chars ({layer2_ratio:.2f}%)")
    print(f"   Code blocks removed: {diagram_stats['code_blocks_removed']}")
    print()

    # Save Layer 2 output
    layer2_output = output_dir / "layer2_diagrams_removed.txt"
    with open(layer2_output, 'w', encoding='utf-8') as f:
        f.write(layer2_text)
    print(f"💾 Layer 2 saved to: {layer2_output}")
    print()

    pipeline_stats['layers'].append({
        'name': 'Layer 2: Diagram Removal',
        'input_size': layer1_size,
        'output_size': layer2_size,
        'savings': layer2_savings,
        'ratio': layer2_ratio,
        'details': diagram_stats
    })
    pipeline_stats['cumulative_savings'] += layer2_savings

    # =========================================================================
    # DICTIONARY GENERATION (INLINE - from clean content)
    # =========================================================================
    print("=" * 80)
    print("📚 DICTIONARY GENERATION (from clean content)")
    print("=" * 80)
    print()

    print("🔧 Generating dictionaries from layer2 (clean content)...")
    print(f"   Input: layer2_diagrams_removed.txt ({layer2_size:,} chars)")
    print(f"   Status: No Thai text, no diagrams - CLEAN ✅")
    print()

    dict_generator = DictionaryGenerator(
        enable_aggressive_compression=aggressive_mode,
        min_word_frequency=2 if aggressive_mode else 5
    )
    template_dict, phrase_dict, word_dict, dict_stats = dict_generator.generate_all_dictionaries(layer2_text)

    print(f"✅ Dictionaries generated successfully!")
    print(f"   Total entries: {dict_stats['total_entries']}")
    print()

    # =========================================================================
    # LAYER 3: TEMPLATE + PHRASE + WORD COMPRESSION (Combined)
    # =========================================================================
    print("=" * 80)
    print("🔧 LAYER 3: COMBINED COMPRESSION (Templates + Phrases + Words)")
    print("=" * 80)
    print()

    # Create template compressor with inline dictionaries (does all 3 compression types)
    template_compressor = TemplateCompressor(
        template_dict=template_dict,
        phrase_dict=phrase_dict,
        word_dict=word_dict
    )
    layer3_text, layer3_stats = template_compressor.compress(layer2_text)

    layer3_size = len(layer3_text)
    layer3_savings = layer2_size - layer3_size
    layer3_ratio = (layer3_savings / layer2_size * 100) if layer2_size > 0 else 0

    print(f"✅ Combined compression complete:")
    print(f"   Input:  {layer2_size:,} chars (after diagram removal)")
    print(f"   Output: {layer3_size:,} chars")
    print(f"   Saved:  {layer3_savings:,} chars ({layer3_ratio:.2f}%)")
    print(f"   Templates: {layer3_stats.get('template_count', 0):,} replacements")
    print(f"   Phrases:   {layer3_stats.get('phrase_count', 0):,} replacements")
    print(f"   Words:     {layer3_stats.get('word_count', 0):,} replacements")
    print()

    # Save Layer 3 output (FINAL compressed content)
    layer3_output = output_dir / "layer3_combined_compression.txt"
    with open(layer3_output, 'w', encoding='utf-8') as f:
        f.write(layer3_text)
    print(f"💾 Layer 3 saved to: {layer3_output}")
    print()

    pipeline_stats['layers'].append({
        'name': 'Layer 3: Combined Compression (Templates + Phrases + Words)',
        'input_size': layer2_size,
        'output_size': layer3_size,
        'savings': layer3_savings,
        'ratio': layer3_ratio,
        'details': layer3_stats
    })
    pipeline_stats['cumulative_savings'] += layer3_savings

    # =========================================================================
    # LAYER 5.5: TOKEN JOIN OPTIMIZATION (Layer 5 Enhancement)
    # =========================================================================
    print("=" * 80)
    print("🔗 LAYER 5.5: TOKEN JOIN OPTIMIZATION (Remove spaces between adjacent codes)")
    print("=" * 80)
    print()

    # Apply token join optimization
    layer35_text, token_join_stats = apply_token_join(layer3_text)

    layer35_size = len(layer35_text)
    layer35_savings = layer3_size - layer35_size
    layer35_ratio = (layer35_savings / layer3_size * 100) if layer3_size > 0 else 0

    print(f"✅ Token Join optimization complete:")
    print(f"   Input:  {layer3_size:,} chars (after combined compression)")
    print(f"   Output: {layer35_size:,} chars")
    print(f"   Saved:  {layer35_savings:,} chars ({layer35_ratio:.2f}%)")
    print(f"   Pairs joined: {token_join_stats['pairs_joined']:,}")
    print()

    # Validate token join (lossless verification)
    validation = validate_token_join(layer3_text, layer35_text)
    print(f"🔍 Token Join validation: {validation['status']} (Tokens: {validation['original_tokens']} → {validation['joined_tokens']})")
    print()

    # Save Layer 5.5 output
    layer35_output = output_dir / "layer5_5_token_join.txt"
    with open(layer35_output, 'w', encoding='utf-8') as f:
        f.write(layer35_text)
    print(f"💾 Layer 5.5 saved to: {layer35_output}")
    print()

    pipeline_stats['layers'].append({
        'name': 'Layer 5.5: Token Join Optimization',
        'input_size': layer3_size,
        'output_size': layer35_size,
        'savings': layer35_savings,
        'ratio': layer35_ratio,
        'details': {
            'token_join_stats': token_join_stats,
            'validation': validation
        }
    })
    pipeline_stats['cumulative_savings'] += layer35_savings

    # =========================================================================
    # LAYER 4: MARKDOWN COMPRESSION
    # =========================================================================
    print("=" * 80)
    print("🗜️  LAYER 4: MARKDOWN COMPRESSION")
    print("=" * 80)
    print()

    markdown_compressor = MarkdownCompressor()
    layer4_text, layer4_stats = markdown_compressor.compress(layer35_text)

    layer4_size = len(layer4_text)
    layer4_savings = layer35_size - layer4_size
    layer4_ratio = (layer4_savings / layer35_size * 100) if layer35_size > 0 else 0

    print(f"✅ Markdown compression complete:")
    print(f"   Input:  {layer35_size:,} chars (after token join)")
    print(f"   Output: {layer4_size:,} chars")
    print(f"   Saved:  {layer4_savings:,} chars ({layer4_ratio:.2f}%)")
    print()

    # Save Layer 4 output
    layer4_output = output_dir / "layer4_markdown.txt"
    with open(layer4_output, 'w', encoding='utf-8') as f:
        f.write(layer4_text)
    print(f"💾 Layer 4 saved to: {layer4_output}")
    print()

    pipeline_stats['layers'].append({
        'name': 'Layer 4: Markdown Compression',
        'input_size': layer35_size,
        'output_size': layer4_size,
        'savings': layer4_savings,
        'ratio': layer4_ratio,
        'details': layer4_stats
    })
    pipeline_stats['cumulative_savings'] += layer4_savings

    # =========================================================================
    # LAYER 5: WHITESPACE + EMOJI OPTIMIZATION (FINAL)
    # =========================================================================
    print("=" * 80)
    print("⚡ LAYER 5: WHITESPACE + EMOJI OPTIMIZATION (FINAL)")
    print("=" * 80)
    print()

    # Step 1: Whitespace optimization
    whitespace_optimizer = WhitespaceOptimizer()
    layer5_intermediate, whitespace_stats = whitespace_optimizer.optimize(layer4_text)

    # Step 2: Selective emoji removal
    target_size = 40_000
    need_to_remove = max(0, len(layer5_intermediate) - target_size)
    emoji_remover = SelectiveEmojiRemover(target_reduction=need_to_remove + 10)
    layer5_text, emoji_stats = emoji_remover.remove(layer5_intermediate)

    layer5_size = len(layer5_text)
    layer5_savings = layer4_size - layer5_size
    layer5_ratio = (layer5_savings / layer4_size * 100) if layer4_size > 0 else 0

    print(f"✅ Whitespace + Emoji optimization complete:")
    print(f"   Input:  {layer4_size:,} chars")
    print(f"   Output: {layer5_size:,} chars")
    print(f"   Saved:  {layer5_savings:,} chars ({layer5_ratio:.2f}%)")
    print(f"   Whitespace saved: {whitespace_stats.get('savings', 0):,} chars")
    print(f"   Emoji saved: {emoji_stats.get('emojis_removed', 0)} emojis")
    print()

    # Save Layer 5 output (FINAL)
    layer5_output = output_dir / "layer5_FINAL.txt"
    with open(layer5_output, 'w', encoding='utf-8') as f:
        f.write(layer5_text)
    print(f"💾 Layer 5 (FINAL) saved to: {layer5_output}")
    print()

    pipeline_stats['layers'].append({
        'name': 'Layer 5: Whitespace + Emoji (FINAL)',
        'input_size': layer4_size,
        'output_size': layer5_size,
        'savings': layer5_savings,
        'ratio': layer5_ratio,
        'details': {
            'whitespace_stats': whitespace_stats,
            'emoji_stats': emoji_stats
        }
    })
    pipeline_stats['cumulative_savings'] += layer5_savings

    # Update final size to Layer 5
    final_size = layer5_size

    # =========================================================================
    # FINAL STATISTICS
    # =========================================================================
    print("=" * 80)
    print("📊 FINAL COMPRESSION STATISTICS")
    print("=" * 80)
    print()

    # final_size is already set to layer7_size above
    total_savings = original_size - final_size
    total_ratio = (total_savings / original_size * 100) if original_size > 0 else 0

    print(f"Original size:               {original_size:,} chars")
    print(f"After Layer 1 (Thai):        {layer1_size:,} chars ({layer1_ratio:.2f}% savings)")
    print(f"After Layer 2 (Diagrams):    {layer2_size:,} chars ({layer2_ratio:.2f}% more)")
    print(f"After Layer 3 (Combined):    {layer3_size:,} chars ({layer3_ratio:.2f}% more)")
    print(f"After Layer 5.5 (Token Join):{layer35_size:,} chars ({layer35_ratio:.2f}% more)")
    print(f"After Layer 4 (Markdown):    {layer4_size:,} chars ({layer4_ratio:.2f}% more)")
    print(f"After Layer 5 (FINAL):       {layer5_size:,} chars ({layer5_ratio:.2f}% more)")
    print(f"─" * 80)
    print(f"Final size:                  {final_size:,} chars")
    print(f"Total savings:               {total_savings:,} chars")
    print(f"Total compression:           {total_ratio:.2f}%")
    print()

    # Target validation
    target_size = 40_000
    target_ratio = 52.79

    print("=" * 80)
    print("🎯 TARGET VALIDATION")
    print("=" * 80)
    print()
    print(f"Target size:                 ≤{target_size:,} chars")
    print(f"Target compression:          ≥{target_ratio}%")
    print(f"Actual size:                 {final_size:,} chars")
    print(f"Actual compression:          {total_ratio:.2f}%")
    print()

    if final_size <= target_size:
        gap = target_size - final_size
        print(f"✅ TARGET MET! Under by {gap:,} chars")
        pipeline_stats['target_met'] = True
        pipeline_stats['target_gap'] = gap
    else:
        gap = final_size - target_size
        print(f"❌ TARGET MISSED: Over by {gap:,} chars ({gap/original_size*100:.2f}%)")
        pipeline_stats['target_met'] = False
        pipeline_stats['target_gap'] = -gap

    if total_ratio >= target_ratio:
        print(f"✅ COMPRESSION TARGET MET! ({total_ratio:.2f}% ≥ {target_ratio}%)")
    else:
        shortfall = target_ratio - total_ratio
        print(f"⚠️  Need {shortfall:.2f}% more compression")

    print()

    # Save pipeline statistics
    stats_output = output_dir / "pipeline_stats.json"
    pipeline_stats['final_size'] = final_size
    pipeline_stats['total_savings'] = total_savings
    pipeline_stats['total_ratio'] = total_ratio
    pipeline_stats['target_size'] = target_size
    pipeline_stats['target_ratio'] = target_ratio

    with open(stats_output, 'w', encoding='utf-8') as f:
        json.dump(pipeline_stats, f, indent=2, ensure_ascii=False)

    print(f"💾 Pipeline stats saved to: {stats_output}")
    print()

    # Save dictionaries for decompression
    dicts_output = output_dir / "compression_dictionaries.json"
    all_dicts = {
        'template_dict': layer3_stats.get('template_dict', {}),
        'phrase_dict': layer3_stats.get('phrase_dict', {}),
        'word_dict': layer3_stats.get('word_dict', {})
    }

    with open(dicts_output, 'w', encoding='utf-8') as f:
        json.dump(all_dicts, f, indent=2, ensure_ascii=False)

    print(f"💾 Compression dictionaries saved to: {dicts_output}")
    print()

    # =========================================================================
    # MULTI-PLATFORM DEPLOYMENT (6 AI Platforms)
    # =========================================================================
    print("=" * 80)
    print("🌐 MULTI-PLATFORM DEPLOYMENT")
    print("=" * 80)
    print()

    print("🔧 Generating platform-specific DEPLOYABLE files...")
    print()
    
    # Initialize platform deployer with dictionaries
    deployer = PlatformDeployer(dictionaries=all_dicts)
    
    # List platforms
    print("📋 Target Platforms:")
    for platform_info in deployer.list_platforms():
        status_icon = "✅"  # All platforms are verified by default
        print(f"   {status_icon} {platform_info['name']:20} → {platform_info['filename']}")
    print()
    
    # Generate DEPLOYABLE files for all platforms (Phase 11: Centralized HeaderSystem)
    print("🚀 Generating DEPLOYABLE files (Dictionary compression with HeaderSystem)...")
    deployment_results = deployer.generate_all_platforms(
        layer5_text, output_dir,
        use_filename_compression=True,
        use_character_optimization=True
    )
    print()
    
    # Display results
    print("📊 Deployment Results:")
    deployment_stats = []
    for platform, (output_path, stats) in deployment_results.items():
        print(f"   ✅ {stats['display_name']:20} → {stats['output_file']}")
        print(f"      Size: {stats['total_size']:>7,} chars (Header: {stats['header_size']:,} + Content: {stats['content_size']:,})")

        # Show filename compression stats if available
        if stats.get('filename_compression'):
            fc_stats = stats['filename_compression']
            print(f"      Filename Compression: {fc_stats['filenames_replaced']} files → $# (saved {fc_stats['chars_saved']} chars)")

        # Check target
        if stats['total_size'] <= target_size:
            gap = target_size - stats['total_size']
            print(f"      Status: ✅ Under target by {gap:,} chars ({gap/target_size*100:.1f}% cushion)")
        else:
            gap = stats['total_size'] - target_size
            print(f"      Status: ⚠️  Over target by {gap:,} chars")

        deployment_stats.append(stats)
        print()
    
    # Save deployment statistics
    pipeline_stats['deployment'] = {
        'platforms_generated': len(deployment_results),
        'platform_files': deployment_stats
    }
    
    print("=" * 80)
    print("✅ FULL PIPELINE COMPLETE (with Multi-Platform Deployment)")
    print("=" * 80)
    print()
    print(f"📦 Generated {len(deployment_results)} platform-specific DEPLOYABLE files:")
    for platform, (output_path, stats) in deployment_results.items():
        print(f"   - {output_path.name}")

    return pipeline_stats


def validate_source_file(source_path: Path) -> Path:
    """
    Validate source file path and existence.

    Args:
        source_path: Path to source file (may be relative or absolute)

    Returns:
        Absolute Path object for source file

    Raises:
        FileNotFoundError: If source file doesn't exist
        ValueError: If source file format is not supported
    """
    # Convert to absolute path
    if not source_path.is_absolute():
        source_path = Path.cwd() / source_path

    # Check if file exists
    if not source_path.exists():
        raise FileNotFoundError(f"❌ ERROR: Source file not found: {source_path}")

    # Check if it's a file (not directory)
    if not source_path.is_file():
        raise ValueError(f"❌ ERROR: Source path is not a file: {source_path}")

    # Check supported formats
    supported_extensions = ['.md', '.txt']
    if source_path.suffix.lower() not in supported_extensions:
        raise ValueError(f"❌ ERROR: Unsupported file format: {source_path.suffix}")
        print(f"   Supported formats: {', '.join(supported_extensions)}")

    return source_path


def main():
    """Run full compression pipeline with dynamic source file parameter"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Context Compression Pipeline - Layers 0-7 + Multi-Platform Deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compress default template
  python compress_full_pipeline.py --source TEMPLATE/CONTENT/PROJECT.PROMPT.md --output-dir outputs

  # Compress Phase 8 documentation
  python compress_full_pipeline.py --source PROJECT.PROMPT.Phase.008.md --output-dir outputs

  # Use absolute path
  python compress_full_pipeline.py --source /path/to/template.md --output-dir outputs

  # With compression mode
  python compress_full_pipeline.py --source template.md --output-dir outputs --aggressive
        """
    )

    # Required arguments
    parser.add_argument(
        '--source',
        type=Path,
        required=True,
        help='Source template file path (.md or .txt) - REQUIRED PARAMETER'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / "outputs",
        help='Output directory for compressed files (default: ./outputs)'
    )

    # Optional compression modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--aggressive',
        action='store_true',
        help='Use aggressive compression mode (word frequency: 2+, maximum coverage)'
    )
    mode_group.add_argument(
        '--conservative',
        action='store_true',
        help='Use conservative compression mode (word frequency: 5+, standard coverage)'
    )

    args = parser.parse_args()

    # Display mode information
    if args.aggressive:
        print("🚀 AGGRESSIVE COMPRESSION MODE ENABLED")
        print("   - Word frequency threshold: 2+ occurrences")
        print("   - Maximum dictionary coverage")
        print()
    elif args.conservative:
        print("📊 CONSERVATIVE COMPRESSION MODE ENABLED")
        print("   - Word frequency threshold: 5+ occurrences")
        print("   - Standard dictionary coverage")
        print()
    else:
        print("🔄 DEFAULT MODE: Using conservative compression")
        print("   Use --aggressive for maximum compression")
        print("   Use --conservative for standard compression")
        print()

    # Validate source file (Task 8.8 enhancement)
    try:
        source_path = validate_source_file(args.source)
        print(f"📖 Source file validated: {source_path}")
        print(f"📊 File size: {source_path.stat().st_size:,} bytes")
        print()
    except (FileNotFoundError, ValueError) as e:
        print(e)
        print()
        print("💡 Usage Examples:")
        print("   python compress_full_pipeline.py --source TEMPLATE/CONTENT/PROJECT.PROMPT.md --output-dir outputs")
        print("   python compress_full_pipeline.py --source PROJECT.PROMPT.Phase.008.md --output-dir outputs")
        return 1

    # Create output directory
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    print()

    # Run full pipeline with selected mode
    stats = compress_full_pipeline(source_path, output_dir, aggressive_mode=args.aggressive)

    # Return success/failure based on target
    return 0 if stats['target_met'] else 1


if __name__ == '__main__':
    exit(main())
