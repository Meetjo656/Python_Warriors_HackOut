#!/usr/bin/env python3
"""
Quick data preview script to examine generated sample data
"""

import pandas as pd
import json
import os
from pathlib import Path


def preview_data(data_dir=None):
    """Preview all generated datasets"""

    if data_dir is None:
        project_root = Path(__file__).parent.parent
        data_dir = project_root / 'data' / 'generated'

    data_dir = Path(data_dir)

    print("=== Green Hydrogen Infrastructure Data Preview ===\n")
    print(f"Data directory: {data_dir}\n")

    # Infrastructure Data
    infra_file = data_dir / 'infrastructure_data.csv'
    if infra_file.exists():
        infra = pd.read_csv(infra_file)
        print("🏭 INFRASTRUCTURE DATA:")
        print(f"  Total facilities: {len(infra)}")
        print(f"  Types: {infra['type'].value_counts().to_dict()}")
        print(f"  States: {infra['state'].nunique()} states covered")
        print(f"  Total capacity: {infra['capacity'].sum():.1f} MW")
        print(f"  Total investment: ${infra['investment_cost'].sum():.1f}M")
        print(f"  Sample record: {infra.iloc[0]['name']} ({infra.iloc[0]['type']})")
        print()
    else:
        print("❌ Infrastructure data not found")

    # Renewable Data
    renewable_file = data_dir / 'renewable_data.csv'
    if renewable_file.exists():
        renewable = pd.read_csv(renewable_file)
        print("🌞 RENEWABLE ENERGY DATA:")
        print(f"  Total projects: {len(renewable)}")
        print(f"  Types: {renewable['type'].value_counts().to_dict()}")
        print(f"  Total capacity: {renewable['capacity'].sum():.1f} MW")
        print(f"  H2 potential: {renewable['potential_h2_production'].sum():.1f} tons/year")
        print()
    else:
        print("❌ Renewable data not found")

    # Demand Data
    demand_file = data_dir / 'demand_data.csv'
    if demand_file.exists():
        demand = pd.read_csv(demand_file)
        print("🏭 DEMAND CENTERS DATA:")
        print(f"  Total centers: {len(demand)}")
        print(f"  Industries: {list(demand['industry'].value_counts().head(3).index)}")
        print(f"  Priority levels: {demand['priority'].value_counts().to_dict()}")
        print(f"  Total demand: {demand['annual_demand'].sum():.1f} tons/year")
        print(f"  Supply gap: {demand['supply_gap'].sum():.1f} tons/year")
        print(f"  Avg willingness to pay: ${demand['willingness_to_pay'].mean():.2f}/kg")
        print()
    else:
        print("❌ Demand data not found")

    # Pipeline Data
    pipeline_file = data_dir / 'pipeline_data.csv'
    if pipeline_file.exists():
        pipelines = pd.read_csv(pipeline_file)
        print("🔗 PIPELINE DATA:")
        print(f"  Total pipelines: {len(pipelines)}")
        print(f"  Status: {pipelines['status'].value_counts().to_dict()}")
        print(f"  Total length: {pipelines['length'].sum():.1f} km")
        print(f"  Total capacity: {pipelines['capacity'].sum():.1f} tons/day")
        print()
    else:
        print("❌ Pipeline data not found")

    # Economic Data
    economic_file = data_dir / 'economic_data.json'
    if economic_file.exists():
        with open(economic_file, 'r') as f:
            economic = json.load(f)
        print("💰 ECONOMIC DATA:")
        print(f"  Green H2 price: ${economic['hydrogen_prices']['current_green_h2']}/kg")
        print(f"  PEM electrolyzer CAPEX: ${economic['capex_costs']['pem_electrolyzer']}/kW")
        print(f"  Pipeline cost: ${economic['capex_costs']['pipeline_construction']}M/km")
        print()
    else:
        print("❌ Economic data not found")


if __name__ == "__main__":
    preview_data()
