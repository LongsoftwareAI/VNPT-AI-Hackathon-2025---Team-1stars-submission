#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-run script: Complete KB build after embedding
Runs BM25 + Package automatically
"""

import subprocess
import sys
import os

def run_script(script_name):
    """Run a preprocessing script"""
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, f"preprocessing/{script_name}"],
        cwd=os.path.dirname(__file__)
    )
    
    if result.returncode != 0:
        print(f"[ERROR] {script_name} failed!")
        return False
    
    print(f"[OK] {script_name} completed")
    return True

if __name__ == "__main__":
    print("[*] Auto-completing knowledge base build...")
    
    # Step 1: BM25
    if not run_script("4_build_bm25.py"):
        sys.exit(1)
    
    # Step 2: Package
    if not run_script("5_package_kb.py"):
        sys.exit(1)
    
    print("\n" + "="*60)
    print("[OK] KNOWLEDGE BASE BUILD COMPLETE!")
    print("="*60)
    print("\nNext: Test with main_optimized.py")
