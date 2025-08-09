#!/usr/bin/env python3
"""
Test script to verify the SystemC LLDB formatter package structure.

This script tests the basic functionality of the formatter module
without requiring LLDB to be present.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Test basic imports
    import sysc_lldb_formatter
    print("✓ Successfully imported sysc_lldb_formatter")
    
    # Test package metadata
    print(f"✓ Package version: {sysc_lldb_formatter.__version__}")
    print(f"✓ Package author: {sysc_lldb_formatter.__author__}")
    print(f"✓ Package license: {sysc_lldb_formatter.__license__}")
    
    # Test module docstring
    if sysc_lldb_formatter.__doc__:
        print("✓ Package has documentation")
    else:
        print("⚠ Package documentation missing")
    
    print("⚠ Note: Formatter classes require LLDB environment to test fully")
    print("\n🎉 Basic package structure tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
