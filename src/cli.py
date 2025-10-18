#!/usr/bin/env python3
"""
Context Compression System - CLI Interface
Command-line interface for context compression operations
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .core import ContextProcessor, CompressionLevel


def print_success(message: str):
    """Print success message (แสดงข้อความสำเร็จ)"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message (แสดงข้อความ error)"""
    print(f"❌ {message}", file=sys.stderr)


def print_info(message: str):
    """Print info message (แสดงข้อความ info)"""
    print(f"ℹ️  {message}")


def print_warning(message: str):
    """Print warning message (แสดงข้อความเตือน)"""
    print(f"⚠️  {message}")


def compress_command(args):
    """Handle compress command (จัดการคำสั่ง compress)"""
    try:
        processor = ContextProcessor(
            config_dir=args.config_dir,
            template_file=args.template
        )

        if args.platform == "all":
            print_info("Processing all platforms...")
            results = processor.process_all_platforms()

            success_count = sum(1 for r in results if r.success)
            total_count = len(results)

            print("\n" + "="*60)
            print(f"Processed {total_count} platforms ({success_count} successful)")
            print("="*60 + "\n")

            for result in results:
                if result.success:
                    ratio = result.compression_result.compression_ratio
                    print_success(
                        f"{result.platform_id}: {result.output_file} "
                        f"(Compressed {ratio:.1f}%)"
                    )
                else:
                    print_error(f"{result.platform_id}: {result.error_message}")

        else:
            print_info(f"Processing platform: {args.platform}")
            result = processor.process_platform(
                platform_id=args.platform,
                custom_compression=args.level
            )

            if result.success:
                ratio = result.compression_result.compression_ratio
                saved = result.compression_result.original_size - result.compression_result.compressed_size

                print_success(f"Compression completed!")
                print(f"\n📊 Statistics:")
                print(f"  Original size: {result.compression_result.original_size:,} bytes")
                print(f"  Compressed size: {result.compression_result.compressed_size:,} bytes")
                print(f"  Saved: {saved:,} bytes ({ratio:.1f}%)")
                print(f"  Output file: {result.output_file}")
            else:
                print_error(f"Compression failed: {result.error_message}")
                return 1

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return 1

    return 0


def list_command(args):
    """Handle list command (จัดการคำสั่ง list)"""
    try:
        processor = ContextProcessor(
            config_dir=args.config_dir,
            template_file=args.template
        )

        platforms = processor.get_platform_list()

        if not platforms:
            print_warning("No platforms configured")
            return 0

        print("\n" + "="*60)
        print("Available Platforms")
        print("="*60 + "\n")

        for platform_id in sorted(platforms):
            config = processor.get_platform_config(platform_id)
            print(f"🔹 {platform_id}")
            print(f"   Name: {config.name}")
            print(f"   Target: {config.target_file}")
            print(f"   Compression: {config.compression_default}")
            print(f"   Description: {config.description}")
            print()

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return 1

    return 0


def stats_command(args):
    """Handle stats command (จัดการคำสั่ง stats)"""
    try:
        processor = ContextProcessor(
            config_dir=args.config_dir,
            template_file=args.template
        )

        stats = processor.get_stats()

        print("\n" + "="*60)
        print("System Statistics")
        print("="*60 + "\n")

        print(f"📁 Template file: {stats['template_file']}")
        print(f"📏 Template size: {stats['template_size']:,} bytes")
        print(f"📦 Total platforms: {stats['loader_stats']['total_platforms']}")
        print(f"📂 Config directory: {stats['loader_stats']['config_directory']}")
        print()

        print("🔧 Compression levels by platform:")
        for platform_id, level in sorted(stats['loader_stats']['compression_levels'].items()):
            print(f"   {platform_id}: {level}")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return 1

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Context Compression System - Multi-Platform Context Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s compress cursor              # Compress for Cursor platform
  %(prog)s compress all                 # Compress for all platforms
  %(prog)s compress cursor -l aggressive  # Use aggressive compression
  %(prog)s list                         # List available platforms
  %(prog)s stats                        # Show system statistics
        """
    )

    # Global arguments
    parser.add_argument(
        '--config-dir',
        default='./platform_configs',
        help='Platform configuration directory (default: ./platform_configs)'
    )
    parser.add_argument(
        '--template',
        default='./CONTEXT.TEMPLATE.md',
        help='Template file path (default: ./CONTEXT.TEMPLATE.md)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress context for platform(s)')
    compress_parser.add_argument(
        'platform',
        help='Platform ID or "all" for all platforms'
    )
    compress_parser.add_argument(
        '-l', '--level',
        choices=['basic', 'aggressive', 'selective'],
        help='Override compression level'
    )

    # List command
    list_parser = subparsers.add_parser('list', help='List available platforms')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == 'compress':
        return compress_command(args)
    elif args.command == 'list':
        return list_command(args)
    elif args.command == 'stats':
        return stats_command(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
