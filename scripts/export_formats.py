#!/usr/bin/env python3
"""
Export sample data to various formats (JSON, Excel, GeoJSON)
"""

import pandas as pd
import json
import os
from pathlib import Path


def export_to_formats(input_dir=None, output_dir=None):
    """Export data to multiple formats"""

    if input_dir is None:
        project_root = Path(__file__).parent.parent
        input_dir = project_root / 'data' / 'generated'

    if output_dir is None:
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'data' / 'exports'

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting data from: {input_dir}")
    print(f"Exporting data to: {output_dir}\n")

    # Load data
    try:
        infra = pd.read_csv(input_dir / 'infrastructure_data.csv')
        renewable = pd.read_csv(input_dir / 'renewable_data.csv')
        demand = pd.read_csv(input_dir / 'demand_data.csv')
        pipelines = pd.read_csv(input_dir / 'pipeline_data.csv')
    except FileNotFoundError as e:
        print(f"❌ Error: Required data file not found - {e}")
        print("Run 'python scripts/generate_data.py' first to generate data")
        return 1

    # Export to Excel
    excel_file = output_dir / 'hydrogen_infrastructure_data.xlsx'
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        infra.to_excel(writer, sheet_name='Infrastructure', index=False)
        renewable.to_excel(writer, sheet_name='Renewable', index=False)
        demand.to_excel(writer, sheet_name='Demand', index=False)
        pipelines.to_excel(writer, sheet_name='Pipelines', index=False)

    print(f"✅ Excel file exported: {excel_file}")

    # Export to GeoJSON (requires geopandas - optional)
    try:
        import geopandas as gpd
        from shapely.geometry import Point

        def create_geojson(df, filename):
            if 'latitude' in df.columns and 'longitude' in df.columns:
                geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
                gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
                output_file = output_dir / filename
                gdf.to_file(output_file, driver='GeoJSON')
                return output_file
            return None

        # Create GeoJSON files
        infra_geo = create_geojson(infra, 'infrastructure.geojson')
        renewable_geo = create_geojson(renewable, 'renewable.geojson')
        demand_geo = create_geojson(demand, 'demand_centers.geojson')

        print(f"✅ GeoJSON files exported:")
        if infra_geo: print(f"   - {infra_geo}")
        if renewable_geo: print(f"   - {renewable_geo}")
        if demand_geo: print(f"   - {demand_geo}")

    except ImportError:
        print("⚠️  GeoPandas not available - skipping GeoJSON export")
        print("   Install with: pip install geopandas")

    # Export summaries to JSON
    summary_data = {
        'metadata': {
            'generated_date': pd.Timestamp.now().isoformat(),
            'total_records': len(infra) + len(renewable) + len(demand),
            'geographic_coverage': 'India',
            'coordinate_system': 'WGS84 (EPSG:4326)'
        },
        'infrastructure_summary': {
            'facilities_by_type': infra['type'].value_counts().to_dict(),
            'facilities_by_state': infra['state'].value_counts().to_dict(),
            'total_capacity_mw': float(infra['capacity'].sum()),
            'total_investment_million_usd': float(infra['investment_cost'].sum())
        },
        'renewable_summary': {
            'projects_by_type': renewable['type'].value_counts().to_dict(),
            'projects_by_state': renewable['state'].value_counts().to_dict(),
            'total_capacity_mw': float(renewable['capacity'].sum()),
            'total_h2_potential_tons_year': float(renewable['potential_h2_production'].sum())
        },
        'demand_summary': {
            'centers_by_industry': demand['industry'].value_counts().to_dict(),
            'centers_by_priority': demand['priority'].value_counts().to_dict(),
            'total_demand_tons_year': float(demand['annual_demand'].sum()),
            'total_supply_gap_tons_year': float(demand['supply_gap'].sum()),
            'avg_willingness_to_pay_usd_kg': float(demand['willingness_to_pay'].mean())
        }
    }

    summary_file = output_dir / 'data_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"✅ Summary JSON exported: {summary_file}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(export_to_formats())
