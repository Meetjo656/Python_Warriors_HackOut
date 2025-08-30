#!/usr/bin/env python3
"""
Script to generate all sample data for the Green Hydrogen Infrastructure Mapper
Run this script to create comprehensive sample datasets
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data.sample_data import SampleDataGenerator
from datetime import datetime


def main():
    print("=== Green Hydrogen Infrastructure Data Generator ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Create data directories
    data_dir = project_root / 'data' / 'generated'
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create generator instance
    generator = SampleDataGenerator()

    # Generate all datasets
    try:
        data = generator.save_all_data(str(data_dir) + '/')

        print("\n=== Generation Summary ===")
        for dataset_name, dataset in data.items():
            if hasattr(dataset, '__len__') and hasattr(dataset, 'columns'):
                print(f"{dataset_name.title()}: {len(dataset)} records")
                print(f"  - Columns: {list(dataset.columns[:5])}{'...' if len(dataset.columns) > 5 else ''}")

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"All data files saved to '{data_dir}' directory")

    except Exception as e:
        print(f"Error generating data: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
