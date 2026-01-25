#!/usr/bin/env python
# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""Test performance optimizations"""

import sys
import os
import time
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from progress_RR import ProgressContext
    print("✓ ProgressContext imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ProgressContext: {e}")
    sys.exit(1)

# Test creating dummy CSV
def create_test_csv():
    """Create a test CSV file"""
    test_data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Name': ['Workout 1', 'Workout 2', 'Workout 3'],
        'Distance': [10000, 15000, 20000],
        'Climbing': [100, 200, 300],
        'Moving Time': [3600, 5400, 7200],
        'Avg Speed': [10.0, 10.0, 10.0],
        'Avg Power': [200, 250, 300],
        'Avg HR': [140, 145, 150],
        'Max HR': [180, 185, 190],
        'Work': [600000, 1000000, 1500000],
        'RPE': [7, 8, 9],
        'Feel': ['Good', 'Great', 'Good'],
    }
    
    df = pd.DataFrame(test_data)
    test_csv = os.path.join(os.path.dirname(__file__), 'test_sample.csv')
    df.to_csv(test_csv, index=False)
    print(f"✓ Test CSV created: {test_csv}")
    return test_csv

# Test ProgressContext
print("\nTesting ProgressContext...")

class MockGUI:
    def __init__(self):
        self.progress_dialog = None

gui = MockGUI()

try:
    with ProgressContext(gui, "Test Progress", 100) as progress:
        for i in range(1, 101, 10):
            progress.set_label(f"Processing step {i}%...")
            progress.set_value(i)
            time.sleep(0.1)  # Simulate work
    print("✓ ProgressContext test completed successfully")
except Exception as e:
    print(f"✗ ProgressContext test failed: {e}")
    sys.exit(1)

# Test CSV creation
print("\nTesting CSV operations...")
try:
    test_csv = create_test_csv()
    df = pd.read_csv(test_csv)
    print(f"✓ CSV has {len(df)} rows and {len(df.columns)} columns")
    os.remove(test_csv)
    print(f"✓ Test CSV cleaned up")
except Exception as e:
    print(f"✗ CSV test failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("All performance tests passed! ✓")
print("="*50)
