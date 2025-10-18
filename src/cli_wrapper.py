#!/usr/bin/env python3
"""
Context Compression System - CLI Wrapper Class
Manual Installation CLI Tool for generating DEPLOYABLE files
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config_loader import ConfigLoader
from src.compress_full_pipeline import compress_full_pipeline, validate_source_file


class ContextCLI:
    """
    CLI tool for generating DEPLOYABLE files - Manual Installation Only

    ความเข้าใจ: ไม่มีการติดตั้งอัตโนมัติ
    - Generate compressed files เท่านั้น
    - ผู้ใช้นำไปติดตั้งเอง (Manual Installation)
    - User control 100%
    """

    def __init__(self, config_dir: str = "./platform_configs"):
        """Initialize CLI with configuration directory"""
        self.config_dir = config_dir
        self.config_loader = ConfigLoader(config_dir)

    def _setup_logger(self):
        """Setup logging for CLI operations"""
        # Simple logging - just return for now
        return None

    def compress(self, platform: str, source: str, output_dir: str = None) -> bool:
        """
        Compress file for specific platform - Manual Installation

        การทำงาน:
        1. Validate source file and platform
        2. Run compression pipeline with existing compress_full_pipeline.py
        3. Generate DEPLOYABLE file in outputs/[platform]/ directory
        4. Show manual installation instructions
        5. Display compression statistics

        Args:
            platform: "claude", "qwen", "gemini", "openai", "cursor", "codebuff"
            source: path ไฟล์ต้นทาง (.md, .txt)
            output_dir: directory สำหรับ output (default: outputs)

        Returns:
            bool: True=success, False=failure
        """
        try:
            # 1. Validation
            if not os.path.exists(source):
                raise FileNotFoundError(f"Source file not found: {source}")

            # Validate platform exists
            available_platforms = self.get_platform_list()
            if platform not in available_platforms:
                raise ValueError(f"Platform not supported: {platform}. Available: {', '.join(available_platforms)}")

            # 2. Validate source file format
            source_path = Path(source)
            if source_path.suffix.lower() not in ['.md', '.txt']:
                raise ValueError(f"Unsupported file format: {source_path.suffix}. Supported: .md, .txt")

            # 3. Set output directory
            if output_dir is None:
                output_dir = Path("outputs")
            else:
                output_dir = Path(output_dir)

            # 4. Process using existing pipeline
            print(f"🔄 Compressing {source} for {platform}...")

            # Run compression pipeline
            source_path_abs = validate_source_file(source_path)
            pipeline_stats = compress_full_pipeline(
                source_path=source_path_abs,
                output_dir=output_dir
            )

            # 5. Check if compression was successful
            if not pipeline_stats.get('target_met', False):
                print(f"⚠️  Warning: Compression target not met, but continuing...")

            # 6. Find the generated DEPLOYABLE file
            platform_deployer = pipeline_stats.get('deployment', {}).get('platform_files', [])
            target_file = None

            for platform_info in platform_deployer:
                if platform_info['platform'].lower() == platform.lower():
                    target_file = platform_info.get('output_file')
                    break

            if target_file:
                output_file_path = output_dir / target_file
                print(f"✅ Compression completed!")
                print(f"📁 Output file: {output_file_path}")
                print(f"📊 Final size: {pipeline_stats['final_size']:,} chars")
                print(f"📈 Total compression: {pipeline_stats['total_ratio']:.1f}%")

                # Manual installation instructions
                print(f"\n📋 Manual Installation Instructions:")
                print(f"1. Copy: {output_file_path}")
                print(f"2. Paste to: Your AI platform's config directory")

                # Platform-specific instructions
                platform_config = self.config_loader.get_platform(platform)
                target_filename = platform_config.get('target_file', 'CLAUDE.md')

                if platform.lower() == 'claude':
                    print(f"3. For Claude Code: ~/.claude/{target_filename}")
                elif platform.lower() == 'cursor':
                    print(f"3. For Cursor: ~/.cursor/{target_filename}")
                elif platform.lower() == 'openai':
                    print(f"3. For ChatGPT: ~/chatgpt/{target_filename}")
                else:
                    print(f"3. For {platform_config.get('name', platform)}: [platform config directory]/{target_filename}")

                print(f"4. Restart your AI platform to load new context")

                return True
            else:
                print(f"❌ Error: DEPLOYABLE file for {platform} not found")
                return False

        except FileNotFoundError as e:
            print(f"❌ Error: {str(e)}")
            return False
        except ValueError as e:
            print(f"❌ Error: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False

    def list_platforms(self) -> List[str]:
        """
        List all available platforms with detailed information

        Returns:
            List[str]: List of platform IDs
        """
        platforms = self.config_loader.get_platform_keys()

        print("\n" + "="*60)
        print("🌐 Available Platforms (6 supported)")
        print("="*60 + "\n")

        for platform_id in sorted(platforms):
            try:
                config = self.config_loader.get_platform(platform_id)
                print(f"🔹 {platform_id}")
                print(f"   Name: {config.get('name', 'Unknown')}")
                print(f"   Target: {config.get('target_file', 'Unknown')}")
                print(f"   Compression: {config.get('compression_default', 'Unknown')}")
                print(f"   Description: {config.get('description', 'No description')}")
                print()
            except Exception as e:
                print(f"❌ Error loading {platform_id}: {str(e)}")

        return platforms

    def get_platform_list(self) -> List[str]:
        """Get list of available platform IDs"""
        return self.config_loader.get_platform_keys()

    def get_platform_config(self, platform_id: str) -> Dict:
        """Get platform configuration by ID"""
        return self.config_loader.get_platform(platform_id)

    def validate(self, platform: str, source: str) -> Dict:
        """
        Validate source file and platform compatibility

        Args:
            platform: Platform ID to validate against
            source: Source file path to validate

        Returns:
            Dict: validation results with recommendations
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": [],
            "file_info": {}
        }

        # File existence check
        if not os.path.exists(source):
            results["errors"].append(f"File not found: {source}")
            results["valid"] = False
            return results

        # File format validation
        source_path = Path(source)
        if source_path.suffix.lower() not in ['.md', '.txt']:
            results["errors"].append(f"File must be .md or .txt format (found: {source_path.suffix})")
            results["valid"] = False

        # Platform validation
        available_platforms = self.get_platform_list()
        if platform not in available_platforms:
            results["errors"].append(f"Platform not supported: {platform}. Available: {', '.join(available_platforms)}")
            results["valid"] = False

        # File size analysis
        try:
            file_size = source_path.stat().st_size
            results["file_info"]["size"] = file_size
            results["file_info"]["size_readable"] = f"{file_size:,} bytes"

            if file_size > 10 * 1024 * 1024:  # 10MB
                results["warnings"].append("Large file detected (>10MB) - compression may take longer")
            elif file_size < 1000:
                results["warnings"].append("Very small file detected (<1KB) - minimal compression expected")

            # Content preview
            with open(source_path, 'r', encoding='utf-8') as f:
                preview = f.read(500)
                if len(preview) < 100:
                    results["warnings"].append("File seems very short - may not have enough content for compression")

        except Exception as e:
            results["errors"].append(f"Cannot read file: {str(e)}")
            results["valid"] = False

        # Platform-specific recommendations
        try:
            platform_config = self.get_platform_config(platform)
            results["recommendations"].append(f"Target file for {platform}: {platform_config.get('target_file', 'Unknown')}")
        except Exception:
            pass

        return results

    def deploy_all(self, source: str, output_dir: str = None) -> Dict:
        """
        Deploy to all platforms - Generate all DEPLOYABLE files

        Args:
            source: Source file path
            output_dir: Output directory (default: outputs)

        Returns:
            Dict: ผลการ deploy ทั้งหมด
        """
        platforms = self.get_platform_list()
        results = {
            "total": len(platforms),
            "successful": 0,
            "failed": 0,
            "details": {}
        }

        print(f"🚀 Deploying to all {len(platforms)} platforms...")
        print("="*60)

        for platform in platforms:
            print(f"\n🔄 Processing {platform}...")
            success = self.compress(platform, source, output_dir)

            results["details"][platform] = success
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1

        # Summary
        print("\n" + "="*60)
        print("📊 Deployment Summary")
        print("="*60)
        print(f"✅ Successful: {results['successful']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📈 Success Rate: {results['successful']/results['total']*100:.1f}%")

        return results

    def show_help(self):
        """Display help information"""
        help_text = """
🤖 Context Compression System CLI - Manual Installation Tool

📋 Available Commands:
  compress <platform> --source <file>     Compress for specific platform
  compress all --source <file>            Deploy to all platforms
  list                                   List available platforms
  validate <platform> --source <file>   Validate file and platform
  help                                   Show this help message

🌐 Supported Platforms:
  claude, qwen, gemini, openai, cursor, codebuff

📁 Output Location:
  Files are saved to: ./outputs/[platform]/DEPLOYABLE_[platform].md
  Manual installation required - see output for instructions

💡 Usage Examples:
  python -m src.cli_wrapper compress claude --source ./myfile.md
  python -m src.cli_wrapper compress all --source ./myfile.md
  python -m src.cli_wrapper list
  python -m src.cli_wrapper validate claude --source ./myfile.md

🔧 Key Features:
  ✅ Manual Installation Only (no automatic AI config changes)
  ✅ User Control (you decide where to install)
  ✅ Clear Instructions (step-by-step guidance)
  ✅ Comprehensive Validation (file format, size, platform support)
        """
        print(help_text)

    def interactive_mode(self):
        """
        Interactive Menu Mode - รัน CLI ผ่านเมนู interactive

        เปิดใช้งาน: python3 -m src.cli interactive
        """
        while True:
            self._show_main_menu()
            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == '1':
                self._menu_list_platforms()
            elif choice == '2':
                self._menu_validate_file()
            elif choice == '3':
                self._menu_compress_context()
            elif choice == '4':
                self._menu_deploy_all()
            elif choice == '5':
                self._menu_system_info()
            elif choice == '6':
                self._menu_settings()
            elif choice == '7':
                print("\n👋 Goodbye! Thank you for using Context Compression System")
                break
            else:
                print("\n❌ Invalid choice! Please enter a number between 1-7")
                input("Press Enter to continue...")

    def _show_main_menu(self):
        """แสดงเมนูหลัก"""
        print("\n" + "="*60)
        print("🚀 Context Compression System - Interactive Mode")
        print("="*60)
        print("\nPlease select an action:\n")
        print("1. 📋 List available platforms")
        print("2. ✅ Validate source file")
        print("3. 🗜️  Compress context")
        print("4. 🚀 Deploy to all platforms")
        print("5. 📊 System information")
        print("6. ⚙️  Settings")
        print("7. ❌ Exit")

    def _menu_list_platforms(self):
        """เมนูแสดงรายการ platforms"""
        print("\n" + "="*60)
        print("📋 Available Platforms")
        print("="*60)

        platforms = self.list_platforms()

        print(f"\n🔢 Total platforms: {len(platforms)}")
        print("💡 Use these platform IDs when compressing context")

        input("\nPress Enter to return to main menu...")

    def _menu_validate_file(self):
        """เมนู validate ไฟล์"""
        print("\n" + "="*60)
        print("✅ Validate Source File")
        print("="*60)

        # Get source file
        source_file = input("📁 Enter source file path: ").strip()
        if not source_file:
            print("❌ No file path provided!")
            input("Press Enter to continue...")
            return

        # Get platform
        platforms = self.get_platform_list()
        print(f"\n🌐 Available platforms: {', '.join(platforms)}")
        platform = input("🎯 Enter platform to validate against: ").strip().lower()

        if not platform:
            print("❌ No platform provided!")
            input("Press Enter to continue...")
            return

        # Perform validation
        results = self.validate(platform, source_file)

        print("\n" + "-"*40)
        print("📊 Validation Results")
        print("-"*40)

        if results["valid"]:
            print("✅ Validation PASSED - File is ready for compression!")
            print(f"📁 File: {source_file}")
            if "file_info" in results:
                print(f"📊 Size: {results['file_info'].get('size_readable', 'Unknown')}")
        else:
            print("❌ Validation FAILED:")
            for error in results["errors"]:
                print(f"  ❌ {error}")

        if results.get("warnings"):
            print("\n⚠️  Warnings:")
            for warning in results["warnings"]:
                print(f"  ⚠️  {warning}")

        if results.get("recommendations"):
            print("\n💡 Recommendations:")
            for rec in results["recommendations"]:
                print(f"  💡 {rec}")

        input("\nPress Enter to return to main menu...")

    def _menu_compress_context(self):
        """เมนูบีบอัด context"""
        print("\n" + "="*60)
        print("🗜️  Compress Context")
        print("="*60)

        # Get source file
        source_file = input("📁 Enter source file path: ").strip()
        if not source_file:
            print("❌ No file path provided!")
            input("Press Enter to continue...")
            return

        # Platform selection
        platforms = self.get_platform_list()
        platforms.append('all')  # Add 'all' option

        print(f"\n🌐 Available platforms: {', '.join(platforms)}")
        platform = input("🎯 Enter platform (or 'all'): ").strip().lower()

        if not platform:
            print("❌ No platform provided!")
            input("Press Enter to continue...")
            return

        # Get output directory
        output_dir = input("📂 Output directory (default: outputs): ").strip()
        if not output_dir:
            output_dir = None

        # Confirm operation
        print(f"\n🔍 Operation Summary:")
        print(f"📁 Source file: {source_file}")
        print(f"🎯 Platform: {platform}")
        print(f"📂 Output directory: {output_dir or 'outputs'}")

        confirm = input("\n✅ Proceed with compression? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled!")
            input("Press Enter to continue...")
            return

        # Perform compression
        print(f"\n🔄 Starting compression...")

        if platform == 'all':
            # Deploy to all platforms
            results = self.deploy_all(source_file, output_dir)
        else:
            # Deploy to specific platform
            success = self.compress(platform, source_file, output_dir)
            results = {'successful': 1 if success else 0, 'total': 1}

        # Show results
        print(f"\n📊 Compression completed!")
        print(f"✅ Successful: {results.get('successful', 0)}")
        print(f"❌ Failed: {results.get('failed', results.get('total', 0) - results.get('successful', 0))}")

        input("\nPress Enter to return to main menu...")

    def _menu_deploy_all(self):
        """เมนู deploy ไปทุก platforms"""
        print("\n" + "="*60)
        print("🚀 Deploy to All Platforms")
        print("="*60)

        # Get source file
        source_file = input("📁 Enter source file path: ").strip()
        if not source_file:
            print("❌ No file path provided!")
            input("Press Enter to continue...")
            return

        # Get output directory
        output_dir = input("📂 Output directory (default: outputs): ").strip()
        if not output_dir:
            output_dir = None

        # Confirm operation
        platforms = self.get_platform_list()
        print(f"\n🔍 Operation Summary:")
        print(f"📁 Source file: {source_file}")
        print(f"🎯 Platforms: All {len(platforms)} platforms")
        print(f"📂 Output directory: {output_dir or 'outputs'}")

        confirm = input("\n✅ Deploy to all platforms? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled!")
            input("Press Enter to continue...")
            return

        # Perform deployment
        print(f"\n🚀 Starting deployment to all platforms...")
        results = self.deploy_all(source_file, output_dir)

        input("\nPress Enter to return to main menu...")

    def _menu_system_info(self):
        """เมนูแสดงข้อมูลระบบ"""
        print("\n" + "="*60)
        print("📊 System Information")
        print("="*60)

        platforms = self.get_platform_list()

        print(f"🌐 Supported platforms: {len(platforms)}")
        print(f"📁 Config directory: {self.config_dir}")
        print(f"🔧 Manual installation: Yes")
        print(f"📄 Supported formats: .md, .txt")

        # Show platform summary
        print(f"\n📋 Platform Summary:")
        for platform in sorted(platforms):
            try:
                config = self.get_platform_config(platform)
                print(f"  🔹 {platform}: {config.get('name', 'Unknown')} → {config.get('target_file', 'Unknown')}")
            except Exception:
                print(f"  ❌ {platform}: Configuration error")

        input("\nPress Enter to return to main menu...")

    def _menu_settings(self):
        """เมนูตั้งค่า"""
        print("\n" + "="*60)
        print("⚙️  Settings")
        print("="*60)

        print(f"📁 Current config directory: {self.config_dir}")
        print("🔧 Available settings:")
        print("  1. Change config directory")
        print("  2. Show advanced help")
        print("  3. Back to main menu")

        choice = input("\nEnter setting to modify (1-3): ").strip()

        if choice == '1':
            new_dir = input("Enter new config directory path: ").strip()
            if new_dir and os.path.exists(new_dir):
                self.config_dir = new_dir
                self.config_loader = ConfigLoader(new_dir)
                print(f"✅ Config directory changed to: {new_dir}")
            else:
                print("❌ Invalid directory path!")
        elif choice == '2':
            self.show_help()
        elif choice == '3':
            return
        else:
            print("❌ Invalid choice!")

        input("\nPress Enter to return to main menu...")