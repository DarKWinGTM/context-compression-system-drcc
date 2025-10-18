#!/usr/bin/env python3
"""
Context Compression System - Package Entry Point
Main entry point for python -m src command
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Import and run the main CLI
from cli import main

if __name__ == '__main__':
    sys.exit(main())