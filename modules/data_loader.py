import pandas as pd
import numpy as np
from typing import Dict, List
import random


class DataLoader:
    def __init__(self):
        # H2-FOCUSED REGIONS AND INDUSTRIES
        self.regions = ['North', 'South', 'East', 'West', 'Central']
        self.h2_renewable_types = ['Solar', 'Wind', 'Hydro']

    def load_feasibility_data(self, csv_file_path: str = 'Hydro_74K.csv') -> pd.DataFrame:
        """Load real-world H2 feasibility data from CSV"""
        try:
            df = pd.read_csv(csv_file_path)

            # Rename columns to match the project structure
            df_processed = df.copy()
            df_processed = df_processed.rename(columns={
                'City': 'site_id',
                'Latitude': 'latitude',
                'Longitude': 'longitude',
                'Solar_Irradiance_kWh/m²/day': 'solar_irradiance',
                'Temperature_C': 'temperature',
                'Wind_Speed_m/s': 'wind_speed',
                'PV_Power_kW': 'pv_capacity',
                'Wind_Power_kW': 'wind_capacity',
                'Electrolyzer_Efficiency_%': 'electrolyzer_efficiency',
                'Hydrogen_Production_kg/day': 'h2_production_daily',
                'Desalination_Power_kW': 'desalination_power',
                'System_Efficiency_%': 'system_efficiency',
                'Feasibility_Score': 'feasibility_score'
            })

            # Add derived columns for integration
            df_processed['name'] = 'H2 Site ' + df_processed['site_id'].astype(str)
            df_processed['type'] = 'feasible_site'
            df_processed['capacity'] = df_processed['pv_capacity'] + df_processed['wind_capacity']  # Total MW
            df_processed['annual_h2_production'] = df_processed['h2_production_daily'] * 365 / 1000  # tons/year
            df_processed['status'] = 'feasible'
            df_processed['technology'] = 'PEM Electrolysis'
            df_processed['production_type'] = 'Green'
            df_processed['renewable_powered'] = True
            df_processed['carbon_intensity'] = 0.0  # kg CO2/kg H2 for green H2

            # Estimate investment cost based on capacity
            np.random.seed(42)
            df_processed['investment_cost'] = df_processed['capacity'] * np.random.uniform(2.5, 4.0, len(df_processed))

            # Add region classification based on coordinates
            df_processed['region'] = df_processed.apply(self._classify_region, axis=1)

            print(f"✅ Loaded {len(df_processed)} feasibility sites from {csv_file_path}")
            return df_processed

        except FileNotFoundError:
            print(f"❌ Error: {csv_file_path} not found")
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error loading feasibility data: {e}")
            return pd.DataFrame()

    def _classify_region(self, row):
        """Classify sites into regions based on coordinates"""
        lat, lon = row['latitude'], row['longitude']

        if lat > 25 and lon < -10:
            return 'North Atlantic'
        elif lat > 25 and lon >= -10:
            return 'Northeast'
        elif 20 <= lat <= 25 and lon < -10:
            return 'West Atlantic'
        elif 20 <= lat <= 25 and lon >= -10:
            return 'Central'
        else:
            return 'South'

    def load_infrastructure_data(self) -> pd.DataFrame:
        """Load H2-focused infrastructure data"""
        np.random.seed(42)
        random.seed(42)
        data = []

        # H2 PRODUCTION FACILITIES
        for i in range(20):
            h2_tech = np.random.choice(['PEM Electrolysis', 'Alkaline Electrolysis', 'Blue H2 + CCS'],
                                       p=[0.4, 0.3, 0.3])
            production_type = 'Green' if 'Electrolysis' in h2_tech else 'Blue'

            data.append({
                'id': f'h2_plant_{i}',
                'name': f'Green H2 Production Hub {i + 1}',
                'type': 'existing_plant',
                'latitude': 20 + np.random.uniform(-15, 15),
                'longitude': 77 + np.random.uniform(-20, 20),
                'capacity': np.random.uniform(100, 800),
                'status': 'operational',
                'region': np.random.choice(self.regions),
                'commissioning_year': np.random.randint(2020, 2024),
                'technology': h2_tech,
                'production_type': production_type,
                'h2_purity': np.random.uniform(99.5, 99.99),
                'annual_h2_production': np.random.uniform(5000, 50000),  # tons/year
                'investment_cost': np.random.uniform(200, 1000),
                'renewable_powered': production_type == 'Green',
                'carbon_intensity': 0.5 if production_type == 'Green' else 4.2  # kg CO2/kg H2
            })

        # PLANNED GREEN H2 MEGAPLANTS
        for i in range(15):
            data.append({
                'id': f'planned_h2_{i}',
                'name': f'Green H2 Megaplant {i + 1}',
                'type': 'planned_plant',
                'latitude': 20 + np.random.uniform(-15, 15),
                'longitude': 77 + np.random.uniform(-20, 20),
                'capacity': np.random.uniform(500, 2000),  # Larger future plants
                'status': 'planned',
                'region': np.random.choice(self.regions),
                'commissioning_year': np.random.randint(2025, 2030),
                'technology': 'Advanced PEM Electrolysis',
                'production_type': 'Green',
                'h2_purity': 99.99,
                'annual_h2_production': np.random.uniform(25000, 150000),
                'investment_cost': np.random.uniform(800, 3000),
                'renewable_powered': True,
                'carbon_intensity': 0.3,  # Future improved efficiency
                'export_oriented': np.random.choice([True, False], p=[0.6, 0.4])
            })

        # H2 STORAGE HUBS
        for i in range(12):
            data.append({
                'id': f'h2_storage_{i}',
                'name': f'H2 Storage Hub {i + 1}',
                'type': 'storage',
                'latitude': 20 + np.random.uniform(-15, 15),
                'longitude': 77 + np.random.uniform(-20, 20),
                'capacity': np.random.uniform(2000, 15000),  # tons H2
                'status': np.random.choice(['operational', 'under_construction'], p=[0.7, 0.3]),
                'region': np.random.choice(self.regions),
                'commissioning_year': np.random.randint(2021, 2026),
                'technology': np.random.choice(['Underground Cavern', 'High Pressure Tanks', 'Liquid H2'],
                                               p=[0.4, 0.5, 0.1]),
                'storage_pressure': np.random.uniform(350, 900),  # bar
                'investment_cost': np.random.uniform(100, 500),
                'strategic_reserve': np.random.choice([True, False], p=[0.3, 0.7])
            })

        return pd.DataFrame(data)

    def load_renewable_sources(self) -> pd.DataFrame:
        """Load renewable sources optimized for H2 production"""
        np.random.seed(43)
        data = []

        # SOLAR FARMS FOR H2
        for i in range(30):
            dedicated_h2 = np.random.choice([True, False], p=[0.4, 0.6])
            data.append({
                'id': f'solar_h2_{i}',
                'name': f'Solar-to-H2 Farm {i + 1}',
                'type': 'solar',
                'latitude': 20 + np.random.uniform(-15, 15),
                'longitude': 77 + np.random.uniform(-20, 20),
                'capacity': np.random.uniform(200, 2500),  # Larger for H2
                'efficiency': np.random.uniform(22, 28),  # Higher efficiency
                'region': np.random.choice(self.regions),
                'dedicated_h2_production': dedicated_h2,
                'h2_electrolyzer_capacity': np.random.uniform(50, 800) if dedicated_h2 else 0,
                'annual_h2_potential': np.random.uniform(2000, 25000),  # tons H2/year
                'grid_connection': not dedicated_h2,  # Dedicated plants are off-grid
                'water_access_rating': np.random.choice(['Excellent', 'Good', 'Moderate'], p=[0.3, 0.5, 0.2]),
                'land_cost': np.random.uniform(5, 25),  # $/sq meter
                'distance_to_port': np.random.uniform(50, 500)  # For H2 export
            })

        # WIND FARMS FOR H2
        for i in range(25):
            dedicated_h2 = np.random.choice([True, False], p=[0.35, 0.65])
            data.append({
                'id': f'wind_h2_{i}',
                'name': f'Wind-to-H2 Farm {i + 1}',
                'type': 'wind',
                'latitude': 20 + np.random.uniform(-15, 15),
                'longitude': 77 + np.random.uniform(-20, 20),
                'capacity': np.random.uniform(300, 3000),
                'capacity_factor': np.random.uniform(35, 55),  # Higher CF for H2
                'region': np.random.choice(self.regions),
                'dedicated_h2_production': dedicated_h2,
                'h2_electrolyzer_capacity': np.random.uniform(80, 1200) if dedicated_h2 else 0,
                'annual_h2_potential': np.random.uniform(3000, 40000),
                'grid_connection': not dedicated_h2,
                'offshore_potential': np.random.choice([True, False], p=[0.2, 0.8]),
                'wind_quality': np.random.choice(['Excellent', 'Good'], p=[0.6, 0.4]),
                'distance_to_port': np.random.uniform(30, 400)
            })

        return pd.DataFrame(data)

    def load_demand_centers(self) -> pd.DataFrame:
        """Load H2-specific demand centers"""
        np.random.seed(44)

        # H2-ONLY INDUSTRIES
        h2_industries = [
            'Green Steel Production', 'H2 Mobility & Transport', 'Green Ammonia Production',
            'H2 Fuel Cells', 'Green H2 Export', 'H2 Power Generation',
            'Industrial H2 Applications', 'H2 Refining'
        ]

        data = []

        for i in range(35):
            industry = np.random.choice(h2_industries,
                                        p=[0.20, 0.15, 0.18, 0.12, 0.15, 0.10, 0.08, 0.02])

            # H2 demand ranges by industry (tons/year)
            demand_ranges = {
                'Green Steel Production': (20000, 100000),
                'H2 Mobility & Transport': (3000, 25000),
                'Green Ammonia Production': (30000, 150000),
                'H2 Fuel Cells': (2000, 15000),
                'Green H2 Export': (50000, 300000),
                'H2 Power Generation': (15000, 80000),
                'Industrial H2 Applications': (8000, 40000),
                'H2 Refining': (12000, 60000)
            }

            annual_h2_demand = np.random.uniform(*demand_ranges[industry])
            current_h2_supply = annual_h2_demand * np.random.uniform(0.05, 0.25)  # Low current green H2

            # H2-specific pricing
            h2_prices = {
                'Green Steel Production': 4.0,
                'H2 Mobility & Transport': 8.0,
                'Green Ammonia Production': 3.5,
                'H2 Fuel Cells': 6.5,
                'Green H2 Export': 2.8,
                'H2 Power Generation': 4.5,
                'Industrial H2 Applications': 5.0,
                'H2 Refining': 3.8
            }

            data.append({
                'id': f'h2_demand_{i}',
                'name': f'{industry} Facility {i + 1}',
                'industry': industry,
                'latitude': 20 + np.random.uniform(-15, 15),
                'longitude': 77 + np.random.uniform(-20, 20),
                'annual_h2_demand': round(annual_h2_demand, 1),
                'current_h2_supply': round(current_h2_supply, 1),
                'h2_supply_gap': round(annual_h2_demand - current_h2_supply, 1),
                'priority': np.random.choice(['High', 'Medium'], p=[0.7, 0.3]),
                'region': np.random.choice(self.regions),
                'willingness_to_pay_h2': h2_prices[industry] + np.random.uniform(-0.5, 0.5),
                'green_h2_preference': np.random.choice([True, False], p=[0.8, 0.2]),
                'carbon_reduction_target': round(annual_h2_demand * np.random.uniform(8, 12), 1),  # tons CO2
                'h2_purity_requirement': np.random.uniform(99.0, 99.9),
                'storage_capacity_onsite': round(annual_h2_demand * 0.1, 1),  # 10% of annual demand
                'transport_accessibility': np.random.uniform(0.6, 1.0),
                'contract_length_years': np.random.randint(10, 25),
                'renewable_energy_access': np.random.choice([True, False], p=[0.7, 0.3]),
                'port_proximity': np.random.uniform(20, 300)  # km to nearest port
            })

        return pd.DataFrame(data)
