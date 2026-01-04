#!/usr/bin/env python3
"""
Cross-platform BudgetTrak MCP server launcher

This script works on Windows, macOS, and Linux.
It handles PYTHONPATH setup automatically.
"""
import os
import sys
from pathlib import Path

# Get absolute path to project root
project_root = Path(__file__).parent.resolve()

# Add project to Python path
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

# Import and run the server
from budgetrak.server import main

if __name__ == "__main__":
    main()
