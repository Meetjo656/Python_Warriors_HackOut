import pandas as pd
import numpy as np
from typing import Dict, List
import random
from datetime import datetime, timedelta
import json


class SampleDataGenerator:
    def __init__(self):
        # Indian geographic bounds
        self.lat_bounds = (8.4, 37.6)  # India's latitude range
        self.lon_bounds = (68.7, 97.25)  # India's longitude range

        # Major Indian cities for realistic placement
        self.major_cities = {
            'Mumbai': (19.0760, 72.8777),
            'Delhi': (28.7041, 77.1025),
            'Bangalore': (12.9716, 77.5946),
            'Chennai': (13.0827, 80.2707),
            'Kolkata': (22.5726, 88.3639),
            'Hyderabad': (17.3850, 78.4867),
            'Pune': (18.5204, 73.8567),
            'Ahmedabad': (23.0225, 72.5714),
            'Surat': (21.1702, 72.8311),
            'Jaipur': (26.9124, 75.7873),
            'Lucknow': (26.8467, 80.9462),
            'Kanpur': (26.4499, 80.3319),
            'Nagpur': (21.1458, 79.0882),
            'Indore': (22.7196, 75.8577),
            'Bhopal': (23.2599, 77.4126),
            'Visakhapatnam': (17.6868, 83.2185),
            'Kochi': (9.9312, 76.2673),
            'Coimbatore': (11.0168, 76.9558),
            'Vadodara': (22.3072, 73.1812),
            'Rajkot': (22.3039, 70.8022)
        }

        self.states = [
            'Maharashtra', 'Gujarat', 'Rajasthan', 'Karnataka', 'Tamil Nadu',
            'Andhra Pradesh', 'Telangana', 'Kerala', 'West Bengal', 'Uttar Pradesh',
            'Madhya Pradesh', 'Punjab', 'Haryana', 'Odisha', 'Jharkhand',
            'Bihar', 'Assam', 'Chhattisgarh', 'Uttarakhand', 'Himachal Pradesh'
        ]

        # H2-ONLY INDUSTRIES
        self.industries = {
            'Green Steel Production': {'demand_range': (15000, 80000), 'priority': 'High',
                                       'locations': ['Mumbai', 'Chennai', 'Visakhapatnam', 'Kolkata']},
            'Hydrogen Mobility/Transportation': {'demand_range': (5000, 30000), 'priority': 'High',
                                                 'locations': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai']},
            'Green Ammonia Production': {'demand_range': (20000, 100000), 'priority': 'High',
                                         'locations': ['Gujarat', 'Andhra Pradesh', 'Tamil Nadu']},
            'Hydrogen Fuel Cells': {'demand_range': (3000, 20000), 'priority': 'Medium',
                                    'locations': ['Pune', 'Hyderabad', 'Bangalore']},
            'Green Hydrogen Export': {'demand_range': (50000, 200000), 'priority': 'High',
                                      'locations': ['Gujarat', 'Andhra Pradesh', 'Odisha']},
            'Hydrogen Power Generation': {'demand_range': (10000, 60000), 'priority': 'Medium',
                                          'locations': ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Andhra Pradesh']},
            'Hydrogen Refining': {'demand_range': (8000, 40000), 'priority': 'Medium',
                                  'locations': ['Gujarat', 'Maharashtra', 'Uttar Pradesh']},
            'Industrial Heating (H2)': {'demand_range': (5000, 25000), 'priority': 'Medium',
                                        'locations': ['Gujarat', 'Maharashtra', 'Tamil Nadu']}
        }

        self.renewable_potential = {
            'Rajasthan': {'solar': 'Excellent', 'wind': 'Good', 'hydro': 'Poor'},
            'Gujarat': {'solar': 'Excellent', 'wind': 'Excellent', 'hydro': 'Poor'},
            'Karnataka': {'solar': 'Good', 'wind': 'Excellent', 'hydro': 'Good'},
            'Tamil Nadu': {'solar': 'Good', 'wind': 'Excellent', 'hydro': 'Good'},
            'Maharashtra': {'solar': 'Good', 'wind': 'Good', 'hydro': 'Good'},
            'Andhra Pradesh': {'solar': 'Excellent', 'wind': 'Good', 'hydro': 'Good'},
            'Telangana': {'solar': 'Good', 'wind': 'Good', 'hydro': 'Poor'},
            'Madhya Pradesh': {'solar': 'Good', 'wind': 'Poor', 'hydro': 'Good'},
            'Uttarakhand': {'solar': 'Fair', 'wind': 'Poor', 'hydro': 'Excellent'},
            'Himachal Pradesh': {'solar': 'Fair', 'wind': 'Poor', 'hydro': 'Excellent'}
        }

    def generate_infrastructure_data(self, num_existing=20, num_planned=15, num_storage=10) -> pd.DataFrame:
        """Generate comprehensive hydrogen infrastructure data"""
        np.random.seed(42)
        random.seed(42)

        data = []

        # H2-FOCUSED EXISTING PLANTS
        existing_technologies = ['PEM Electrolysis', 'Alkaline Electrolysis', 'Steam Methane Reforming (Blue H2)',
                                 'Biomass Gasification']

        for i in range(num_existing):
            city = random.choice(list(self.major_cities.keys()))
            lat, lon = self.major_cities[city]
            lat += np.random.uniform(-0.5, 0.5)
            lon += np.random.uniform(-0.5, 0.5)

            technology = np.random.choice(existing_technologies, p=[0.35, 0.25, 0.25, 0.15])

            # H2-specific capacity ranges
            if technology in ['PEM Electrolysis', 'Alkaline Electrolysis']:
                capacity = np.random.uniform(50, 400)  # Green H2 plants
            else:
                capacity = np.random.uniform(100, 600)  # Traditional H2 plants

            production_method = 'Green' if 'Electrolysis' in technology else 'Blue' if 'Steam' in technology else 'Bio'

            data.append({
                'id': f'existing_h2_{i + 1}',
                'name': f'{city} Green Hydrogen Plant {i + 1}',
                'type': 'existing_plant',
                'latitude': lat,
                'longitude': lon,
                'capacity': round(capacity, 1),
                'status': 'Operational',
                'city': city,
                'state': self._get_state_for_city(city),
                'commissioning_year': np.random.randint(2018, 2024),
                'technology': technology,
                'feedstock': self._get_feedstock(technology),
                'investment_cost': round(capacity * np.random.uniform(2.0, 4.0), 1),  # Higher for H2
                'annual_h2_production': round(capacity * 8760 * np.random.uniform(0.6, 0.85) * 0.05, 1),  # tons H2/year
                'h2_purity': np.random.uniform(99.5, 99.99),
                'production_method': production_method,
                'grid_connected': np.random.choice([True, False], p=[0.8, 0.2]),
                'renewable_powered': production_method == 'Green',
                'operator': f'H2 Energy Corp {chr(65 + i % 10)}',
                'environmental_rating': 'A+' if production_method == 'Green' else 'B',
                'h2_storage_onsite': round(np.random.uniform(100, 1000), 1),  # tons
                'export_capability': np.random.choice([True, False], p=[0.4, 0.6])
            })

        # PLANNED GREEN H2 PLANTS
        for i in range(num_planned):
            city = random.choice(list(self.major_cities.keys()))
            lat, lon = self.major_cities[city]
            lat += np.random.uniform(-0.8, 0.8)
            lon += np.random.uniform(-0.8, 0.8)

            capacity = np.random.uniform(300, 1500)  # Larger future green H2 plants

            data.append({
                'id': f'planned_h2_{i + 1}',
                'name': f'{city} Green Hydrogen Megaplant {i + 1}',
                'type': 'planned_plant',
                'latitude': lat,
                'longitude': lon,
                'capacity': round(capacity, 1),
                'status': np.random.choice(['Planning', 'Under Construction', 'Financial Close'], p=[0.4, 0.3, 0.3]),
                'city': city,
                'state': self._get_state_for_city(city),
                'commissioning_year': np.random.randint(2025, 2030),
                'technology': 'PEM Electrolysis',
                'feedstock': 'Renewable Electricity + Water',
                'investment_cost': round(capacity * np.random.uniform(3.0, 5.0), 1),
                'annual_h2_production': round(capacity * 8760 * 0.75 * 0.05, 1),
                'h2_purity': np.random.uniform(99.9, 99.999),
                'production_method': 'Green',
                'grid_connected': True,
                'renewable_powered': True,
                'dedicated_renewable': np.random.choice([True, False], p=[0.7, 0.3]),
                'renewable_source': np.random.choice(['Solar', 'Wind', 'Solar+Wind'], p=[0.4, 0.3, 0.3]),
                'operator': f'Green H2 Corp {chr(65 + i % 8)}',
                'environmental_rating': 'A+',
                'h2_storage_onsite': round(capacity * np.random.uniform(0.5, 2.0), 1),
                'export_capability': True,
                'carbon_capture': np.random.choice([True, False], p=[0.3, 0.7])
            })

        # H2 STORAGE FACILITIES
        storage_types = ['Underground H2 Cavern', 'High Pressure H2 Tanks', 'Liquid H2 Storage',
                         'Metal Hydride Storage']

        for i in range(num_storage):
            city = random.choice(list(self.major_cities.keys()))
            lat, lon = self.major_cities[city]
            lat += np.random.uniform(-0.3, 0.3)
            lon += np.random.uniform(-0.3, 0.3)

            storage_type = np.random.choice(storage_types, p=[0.3, 0.4, 0.2, 0.1])
            capacity = np.random.uniform(1000, 10000)  # tons H2

            data.append({
                'id': f'h2_storage_{i + 1}',
                'name': f'{city} H2 Storage Hub {i + 1}',
                'type': 'storage',
                'latitude': lat,
                'longitude': lon,
                'capacity': round(capacity, 1),
                'storage_type': storage_type,
                'status': np.random.choice(['Operational', 'Under Construction'], p=[0.7, 0.3]),
                'city': city,
                'state': self._get_state_for_city(city),
                'commissioning_year': np.random.randint(2020, 2026),
                'technology': storage_type,
                'investment_cost': round(capacity * np.random.uniform(0.3, 0.8), 1),
                'max_pressure': np.random.uniform(300, 900),  # bar for H2
                'h2_purity_maintained': np.random.uniform(99.5, 99.95),
                'storage_duration': np.random.choice(['Short-term', 'Seasonal', 'Long-term'], p=[0.4, 0.4, 0.2]),
                'safety_rating': np.random.choice(['AAA', 'AA', 'A'], p=[0.3, 0.5, 0.2]),
                'operator': f'H2 Storage Solutions {chr(65 + i % 6)}',
                'transport_connectivity': np.random.uniform(0.7, 1.0),
                'leak_detection_system': 'Advanced H2 Sensors',
                'filling_rate': round(capacity * np.random.uniform(0.05, 0.15), 1)  # tons/hour
            })

        return pd.DataFrame(data)

    def generate_renewable_data(self, num_solar=30, num_wind=25, num_hydro=15) -> pd.DataFrame:
        """Generate renewable energy sources data with H2 focus"""
        np.random.seed(43)

        data = []

        # SOLAR FARMS FOR H2
        high_solar_states = ['Rajasthan', 'Gujarat', 'Andhra Pradesh', 'Karnataka', 'Maharashtra']

        for i in range(num_solar):
            state = np.random.choice(high_solar_states, p=[0.3, 0.25, 0.2, 0.15, 0.1])
            lat = np.random.uniform(*self.lat_bounds)
            lon = np.random.uniform(*self.lon_bounds)

            if state == 'Rajasthan':
                lat = np.random.uniform(24, 30)
                lon = np.random.uniform(69, 78)
            elif state == 'Gujarat':
                lat = np.random.uniform(20, 25)
                lon = np.random.uniform(68, 75)

            capacity = np.random.uniform(100, 2000)  # Larger for H2 production
            irradiance = np.random.uniform(4.5, 6.5)

            data.append({
                'id': f'solar_h2_{i + 1}',
                'name': f'{state} Solar-to-H2 Farm {i + 1}',
                'type': 'solar',
                'latitude': lat,
                'longitude': lon,
                'state': state,
                'capacity': round(capacity, 1),
                'technology': np.random.choice(['c-Si', 'Bifacial', 'Perovskite-Si'], p=[0.5, 0.4, 0.1]),
                'efficiency': np.random.uniform(20, 26),  # Higher efficiency for H2
                'capacity_factor': np.random.uniform(22, 32),
                'solar_irradiance': round(irradiance, 2),
                'land_area': round(capacity * np.random.uniform(3, 6), 1),
                'grid_connection': np.random.choice([True, False], p=[0.7, 0.3]),
                'dedicated_h2_production': np.random.choice([True, False], p=[0.4, 0.6]),
                'h2_electrolyzer_capacity': capacity * np.random.uniform(0.2, 0.6) if np.random.random() < 0.4 else 0,
                'commissioning_year': np.random.randint(2020, 2025),
                'ppa_signed': np.random.choice([True, False], p=[0.8, 0.2]),
                'developer': f'Solar-H2 Dev {chr(65 + i % 12)}',
                'annual_generation': round(capacity * irradiance * 365 * 0.9 / 4, 1),
                'potential_h2_production': round(capacity * irradiance * 365 * 0.9 * 0.025, 1),  # Higher H2 potential
                'distance_to_grid': np.random.uniform(0.5, 20),
                'green_h2_certification': np.random.choice(['GO', 'I-REC', 'Green-e', 'None'], p=[0.3, 0.3, 0.2, 0.2]),
                'water_access': np.random.choice(['Abundant', 'Moderate', 'Limited'], p=[0.4, 0.4, 0.2])
            })

        # WIND FARMS FOR H2
        high_wind_states = ['Tamil Nadu', 'Gujarat', 'Karnataka', 'Rajasthan', 'Maharashtra']

        for i in range(num_wind):
            state = np.random.choice(high_wind_states, p=[0.3, 0.25, 0.2, 0.15, 0.1])
            lat = np.random.uniform(*self.lat_bounds)
            lon = np.random.uniform(*self.lon_bounds)

            capacity = np.random.uniform(200, 2500)  # Larger wind farms for H2
            wind_speed = np.random.uniform(7, 13)

            data.append({
                'id': f'wind_h2_{i + 1}',
                'name': f'{state} Wind-to-H2 Farm {i + 1}',
                'type': 'wind',
                'latitude': lat,
                'longitude': lon,
                'state': state,
                'capacity': round(capacity, 1),
                'turbine_type': np.random.choice(['Onshore', 'Offshore'], p=[0.85, 0.15]),
                'hub_height': np.random.randint(100, 180),
                'rotor_diameter': np.random.randint(120, 200),
                'capacity_factor': np.random.uniform(28, 50),  # Higher CF for H2-focused
                'avg_wind_speed': round(wind_speed, 1),
                'num_turbines': np.random.randint(30, 250),
                'grid_connection': np.random.choice([True, False], p=[0.8, 0.2]),
                'dedicated_h2_production': np.random.choice([True, False], p=[0.35, 0.65]),
                'h2_electrolyzer_capacity': capacity * np.random.uniform(0.15, 0.5) if np.random.random() < 0.35 else 0,
                'commissioning_year': np.random.randint(2018, 2025),
                'ppa_signed': np.random.choice([True, False], p=[0.85, 0.15]),
                'developer': f'Wind-H2 Power {chr(65 + i % 10)}',
                'annual_generation': round(capacity * 8760 * np.random.uniform(0.3, 0.5), 1),
                'potential_h2_production': round(capacity * 8760 * np.random.uniform(0.3, 0.5) * 0.02, 1),
                'transmission_distance': np.random.uniform(5, 60),
                'green_h2_certification': np.random.choice(['GO', 'I-REC', 'Green-e', 'None'],
                                                           p=[0.35, 0.3, 0.2, 0.15]),
                'water_access': np.random.choice(['Abundant', 'Moderate', 'Limited'], p=[0.3, 0.5, 0.2])
            })

        # HYDRO FOR H2
        hydro_states = ['Uttarakhand', 'Himachal Pradesh', 'Kerala', 'Karnataka', 'Andhra Pradesh']

        for i in range(num_hydro):
            state = np.random.choice(hydro_states, p=[0.25, 0.25, 0.2, 0.15, 0.15])
            lat = np.random.uniform(*self.lat_bounds)
            lon = np.random.uniform(*self.lon_bounds)

            capacity = np.random.uniform(50, 1500)

            data.append({
                'id': f'hydro_h2_{i + 1}',
                'name': f'{state} Hydro-to-H2 Plant {i + 1}',
                'type': 'hydro',
                'latitude': lat,
                'longitude': lon,
                'state': state,
                'capacity': round(capacity, 1),
                'plant_type': np.random.choice(['Run-of-river', 'Storage', 'Pumped Storage'], p=[0.5, 0.3, 0.2]),
                'head': np.random.uniform(30, 800),
                'capacity_factor': np.random.uniform(45, 95),
                'reservoir_capacity': np.random.uniform(20, 3000) if np.random.random() > 0.4 else None,
                'grid_connection': True,
                'dedicated_h2_production': np.random.choice([True, False], p=[0.25, 0.75]),
                'h2_electrolyzer_capacity': capacity * np.random.uniform(0.1, 0.3) if np.random.random() < 0.25 else 0,
                'commissioning_year': np.random.randint(2015, 2024),
                'environmental_flow': np.random.uniform(15, 35),
                'developer': f'Hydro-H2 Power {chr(65 + i % 8)}',
                'annual_generation': round(capacity * 8760 * np.random.uniform(0.45, 0.95), 1),
                'potential_h2_production': round(capacity * 8760 * np.random.uniform(0.45, 0.95) * 0.018, 1),
                'water_availability': np.random.choice(['Abundant', 'Seasonal', 'Regulated'], p=[0.4, 0.4, 0.2]),
                'green_h2_certification': np.random.choice(['GO', 'I-REC', 'None'], p=[0.4, 0.3, 0.3])
            })

        return pd.DataFrame(data)

    def generate_demand_data(self, num_centers=40) -> pd.DataFrame:
        """Generate H2-specific demand centers data"""
        np.random.seed(44)

        data = []

        for i in range(num_centers):
            # H2-FOCUSED INDUSTRY SELECTION
            industry = np.random.choice(list(self.industries.keys()),
                                        p=[0.18, 0.15, 0.20, 0.12, 0.15, 0.10, 0.08, 0.02])

            industry_info = self.industries[industry]
            demand_range = industry_info['demand_range']
            priority = industry_info['priority']

            # Location selection
            if 'locations' in industry_info:
                location = np.random.choice(industry_info['locations'])
                if location in self.major_cities:
                    lat, lon = self.major_cities[location]
                    lat += np.random.uniform(-1, 1)
                    lon += np.random.uniform(-1, 1)
                    city = location
                    state = self._get_state_for_city(location)
                else:
                    lat = np.random.uniform(*self.lat_bounds)
                    lon = np.random.uniform(*self.lon_bounds)
                    city = f"{location} Industrial Area"
                    state = location
            else:
                city = random.choice(list(self.major_cities.keys()))
                lat, lon = self.major_cities[city]
                lat += np.random.uniform(-1, 1)
                lon += np.random.uniform(-1, 1)
                state = self._get_state_for_city(city)

            annual_demand = np.random.uniform(*demand_range)
            current_h2_supply = annual_demand * np.random.uniform(0.05, 0.3)  # Low current H2 supply

            # H2-SPECIFIC WILLINGNESS TO PAY
            wtp_base = {
                'Green Steel Production': 4.2,
                'Hydrogen Mobility/Transportation': 7.5,
                'Green Ammonia Production': 3.8,
                'Hydrogen Fuel Cells': 6.0,
                'Green Hydrogen Export': 2.5,
                'Hydrogen Power Generation': 4.5,
                'Hydrogen Refining': 3.5,
                'Industrial Heating (H2)': 4.8
            }

            willingness_to_pay = wtp_base.get(industry, 4.5) + np.random.uniform(-0.3, 0.3)

            data.append({
                'id': f'h2_demand_{i + 1}',
                'name': f'{city} {industry} Plant {i + 1}',
                'industry': industry,
                'latitude': lat,
                'longitude': lon,
                'city': city,
                'state': state,
                'annual_h2_demand': round(annual_demand, 1),
                'current_h2_supply': round(current_h2_supply, 1),
                'h2_supply_gap': round(annual_demand - current_h2_supply, 1),
                'priority': priority,
                'urgency_score': np.random.uniform(0.4, 1.0),
                'transport_accessibility': np.random.uniform(0.5, 1.0),
                'h2_storage_capacity': round(annual_demand * np.random.uniform(0.08, 0.25), 1),
                'h2_purity_requirement': np.random.uniform(99.0, 99.99),
                'contract_duration': np.random.randint(7, 25),
                'willingness_to_pay_h2': round(willingness_to_pay, 2),
                'seasonal_variation': np.random.uniform(0.1, 0.35),
                'backup_h2_requirement': np.random.choice([True, False], p=[0.8, 0.2]),
                'green_h2_preference': np.random.choice([True, False], p=[0.7, 0.3]),
                'carbon_neutrality_target': np.random.randint(2025, 2050),
                'expansion_planned': np.random.choice([True, False], p=[0.4, 0.6]),
                'current_h2_source': np.random.choice(['Grey H2', 'Blue H2', 'Green H2', 'None'],
                                                      p=[0.4, 0.2, 0.1, 0.3]),
                'preferred_delivery': np.random.choice(['Pipeline', 'Truck', 'Rail', 'On-site'],
                                                       p=[0.5, 0.3, 0.1, 0.1]),
                'h2_applications': self._get_h2_applications(industry),
                'co2_reduction_target': round(annual_demand * np.random.uniform(8, 12), 1),  # tons CO2/year
                'renewable_energy_integration': np.random.choice([True, False], p=[0.6, 0.4])
            })

        return pd.DataFrame(data)

    def generate_pipeline_data(self, infrastructure_data: pd.DataFrame, num_pipelines=15) -> pd.DataFrame:
        """Generate H2-specific pipeline data"""
        np.random.seed(45)

        plants = infrastructure_data[infrastructure_data['type'].isin(['existing_plant', 'planned_plant'])]
        storage = infrastructure_data[infrastructure_data['type'] == 'storage']

        data = []

        for i in range(num_pipelines):
            if len(plants) > 1 and len(storage) > 0:
                if np.random.random() < 0.6:
                    start = plants.iloc[np.random.randint(0, len(plants))]
                    end = storage.iloc[np.random.randint(0, len(storage))]
                else:
                    indices = np.random.choice(len(plants), 2, replace=False)
                    start = plants.iloc[indices[0]]
                    end = plants.iloc[indices[1]]

                distance = np.sqrt((start['latitude'] - end['latitude']) ** 2 +
                                   (start['longitude'] - end['longitude']) ** 2) * 111

                # H2-SPECIFIC PIPELINE SPECS
                diameter = np.random.choice([300, 400, 500, 600, 800], p=[0.1, 0.2, 0.3, 0.3, 0.1])  # mm
                pressure = np.random.uniform(50, 100)  # bar for H2
                h2_capacity = diameter * pressure * 0.008  # H2-specific capacity

                data.append({
                    'id': f'h2_pipeline_{i + 1}',
                    'name': f'H2 Pipeline {start["city"]} - {end["city"]}',
                    'type': 'pipeline',
                    'start_lat': start['latitude'],
                    'start_lon': start['longitude'],
                    'end_lat': end['latitude'],
                    'end_lon': end['longitude'],
                    'start_facility': start['name'],
                    'end_facility': end['name'],
                    'length': round(distance, 1),
                    'diameter': diameter,
                    'pressure': round(pressure, 1),
                    'h2_capacity': round(h2_capacity, 1),  # tons H2/day
                    'material': 'H2-Compatible Steel',
                    'coating': 'H2-Barrier Coating',
                    'status': np.random.choice(['Operational', 'Under Construction', 'Planned'], p=[0.5, 0.3, 0.2]),
                    'commissioning_year': np.random.randint(2022, 2028),
                    'investment_cost': round(distance * np.random.uniform(3, 6), 1),  # Higher for H2
                    'operator': f'H2 Pipeline Corp {chr(65 + i % 6)}',
                    'leak_detection': 'Advanced H2 Sensors',
                    'h2_purity_maintained': np.random.uniform(99.5, 99.9),
                    'compressor_stations': max(1, int(distance / 150)),  # Every 150km
                    'safety_systems': ['Emergency Shutdown', 'H2 Leak Detection', 'Pressure Relief'],
                    'environmental_clearance': np.random.choice([True, False], p=[0.9, 0.1]),
                    'right_of_way_secured': np.random.choice([True, False], p=[0.8, 0.2])
                })

        return pd.DataFrame(data)

    def generate_economic_data(self) -> Dict:
        """Generate H2-specific economic assumptions"""
        return {
            'hydrogen_prices': {
                'current_grey_h2': 2.1,  # $/kg
                'current_blue_h2': 2.8,  # $/kg
                'current_green_h2': 5.4,  # $/kg
                'projected_green_h2_2030': 2.5,  # $/kg
                'h2_transport_cost_pipeline': 0.1,  # $/kg/100km
                'h2_transport_cost_truck': 1.2,  # $/kg/100km
                'h2_storage_cost': 0.5,  # $/kg/month
                'h2_export_price': 3.5,  # $/kg FOB
                'green_ammonia_price': 800,  # $/ton
                'green_steel_premium': 150  # $/ton premium
            },
            'h2_capex_costs': {
                'pem_electrolyzer': 1200,  # $/kW
                'alkaline_electrolyzer': 800,  # $/kW
                'h2_storage_underground': 500,  # $/kg capacity
                'h2_storage_pressure': 1500,  # $/kg capacity
                'h2_pipeline_construction': 2.5,  # M$/km
                'h2_compressor_station': 8.0,  # M$ per station
                'h2_purification_system': 300,  # $/kg/day
                'h2_fuel_cell_system': 500,  # $/kW
                'h2_truck_loading_station': 2.0,  # M$ per station
                'h2_quality_control': 0.5  # M$ per facility
            },
            'h2_opex_factors': {
                'electrolyzer_maintenance': 0.03,  # % of capex annually
                'renewable_electricity_cost': 0.03,  # $/kWh
                'water_cost': 0.002,  # $/m³
                'h2_plant_labor_cost': 75000,  # $/year per operator
                'h2_safety_systems': 0.008,  # % of capex annually
                'h2_quality_control': 0.005,  # % of capex annually
                'h2_transportation_cost': 0.15,  # $/kg/100km
                'insurance_premium': 0.012,  # % of capex annually
                'regulatory_compliance': 0.003  # % of capex annually
            }
        }

    def _get_state_for_city(self, city: str) -> str:
        """Map cities to states"""
        city_state_map = {
            'Mumbai': 'Maharashtra', 'Delhi': 'Delhi', 'Bangalore': 'Karnataka',
            'Chennai': 'Tamil Nadu', 'Kolkata': 'West Bengal', 'Hyderabad': 'Telangana',
            'Pune': 'Maharashtra', 'Ahmedabad': 'Gujarat', 'Surat': 'Gujarat',
            'Jaipur': 'Rajasthan', 'Lucknow': 'Uttar Pradesh', 'Kanpur': 'Uttar Pradesh',
            'Nagpur': 'Maharashtra', 'Indore': 'Madhya Pradesh', 'Bhopal': 'Madhya Pradesh',
            'Visakhapatnam': 'Andhra Pradesh', 'Kochi': 'Kerala', 'Coimbatore': 'Tamil Nadu',
            'Vadodara': 'Gujarat', 'Rajkot': 'Gujarat'
        }
        return city_state_map.get(city, np.random.choice(self.states))

    def _get_feedstock(self, technology: str) -> str:
        """Get H2-specific feedstock based on technology"""
        feedstock_map = {
            'Steam Methane Reforming (Blue H2)': 'Natural Gas + Steam + CCS',
            'PEM Electrolysis': 'Renewable Electricity + Water',
            'Alkaline Electrolysis': 'Renewable Electricity + Water',
            'Biomass Gasification': 'Biomass + Steam',
            'Coal Gasification': 'Coal + Steam + Oxygen'
        }
        return feedstock_map.get(technology, 'Renewable Electricity + Water')

    def _get_h2_applications(self, industry: str) -> List[str]:
        """Get specific H2 applications by industry"""
        applications_map = {
            'Green Steel Production': ['Direct Reduction', 'Blast Furnace Injection'],
            'Hydrogen Mobility/Transportation': ['Fuel Cell Vehicles', 'H2 Refueling Stations'],
            'Green Ammonia Production': ['Haber-Bosch Process', 'Fertilizer Production'],
            'Hydrogen Fuel Cells': ['Stationary Power', 'Backup Power'],
            'Green Hydrogen Export': ['Liquefaction', 'LOHC Transport'],
            'Hydrogen Power Generation': ['Gas Turbines', 'Fuel Cells'],
            'Hydrogen Refining': ['Hydrocracking', 'Desulfurization'],
            'Industrial Heating (H2)': ['High-temp Furnaces', 'Process Heat']
        }
        return applications_map.get(industry, ['General H2 Use'])

    def save_all_data(self, output_dir: str = 'data/generated/'):
        """Generate and save all H2-focused datasets"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        print("Generating H2 infrastructure data...")
        infrastructure = self.generate_infrastructure_data()
        infrastructure.to_csv(f'{output_dir}infrastructure_data.csv', index=False)

        print("Generating renewable energy data for H2...")
        renewable = self.generate_renewable_data()
        renewable.to_csv(f'{output_dir}renewable_data.csv', index=False)

        print("Generating H2 demand centers data...")
        demand = self.generate_demand_data()
        demand.to_csv(f'{output_dir}demand_data.csv', index=False)

        print("Generating H2 pipeline data...")
        pipelines = self.generate_pipeline_data(infrastructure)
        pipelines.to_csv(f'{output_dir}pipeline_data.csv', index=False)

        print("Generating H2 economic data...")
        economic = self.generate_economic_data()
        with open(f'{output_dir}economic_data.json', 'w') as f:
            json.dump(economic, f, indent=2)

        print(f"All H2-focused data saved to {output_dir}")

        self._generate_summary_stats(infrastructure, renewable, demand, pipelines, output_dir)

        return {
            'infrastructure': infrastructure,
            'renewable': renewable,
            'demand': demand,
            'pipelines': pipelines,
            'economic': economic
        }

    def _generate_summary_stats(self, infrastructure, renewable, demand, pipelines, output_dir):
        """Generate H2-specific summary statistics"""
        stats = {
            'h2_infrastructure_summary': {
                'total_h2_facilities': len(infrastructure),
                'green_h2_plants': len(infrastructure[infrastructure.get('production_method', '') == 'Green']),
                'blue_h2_plants': len(infrastructure[infrastructure.get('production_method', '') == 'Blue']),
                'h2_storage_facilities': len(infrastructure[infrastructure['type'] == 'storage']),
                'total_h2_capacity_mw': infrastructure['capacity'].sum(),
                'total_h2_investment_million': infrastructure['investment_cost'].sum(),
                'annual_h2_production_tons': infrastructure.get('annual_h2_production', pd.Series([0])).sum()
            },
            'h2_renewable_summary': {
                'total_renewable_projects': len(renewable),
                'dedicated_h2_projects': len(renewable[renewable.get('dedicated_h2_production', False) == True]),
                'solar_h2_projects': len(renewable[renewable['type'] == 'solar']),
                'wind_h2_projects': len(renewable[renewable['type'] == 'wind']),
                'hydro_h2_projects': len(renewable[renewable['type'] == 'hydro']),
                'total_renewable_capacity_mw': renewable['capacity'].sum(),
                'total_h2_potential_tons': renewable['potential_h2_production'].sum()
            },
            'h2_demand_summary': {
                'total_h2_demand_centers': len(demand),
                'high_priority_h2': len(demand[demand['priority'] == 'High']),
                'green_h2_preference': len(demand[demand.get('green_h2_preference', False) == True]),
                'total_h2_demand_tons': demand['annual_h2_demand'].sum(),
                'h2_supply_gap_tons': demand['h2_supply_gap'].sum(),
                'avg_h2_price_usd_kg': demand['willingness_to_pay_h2'].mean()
            },
            'h2_pipeline_summary': {
                'total_h2_pipelines': len(pipelines),
                'operational_h2_pipelines': len(pipelines[pipelines['status'] == 'Operational']),
                'planned_h2_pipelines': len(pipelines[pipelines['status'] == 'Planned']),
                'total_h2_pipeline_length_km': pipelines['length'].sum(),
                'total_h2_capacity_tons_day': pipelines['h2_capacity'].sum()
            }
        }

        with open(f'{output_dir}h2_summary_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)


if __name__ == "__main__":
    generator = SampleDataGenerator()
    data = generator.save_all_data()

    print("\n=== H2-Focused Data Generation Complete ===")
    print(f"H2 Infrastructure facilities: {len(data['infrastructure'])}")
    print(f"Renewable projects for H2: {len(data['renewable'])}")
    print(f"H2 demand centers: {len(data['demand'])}")
    print(f"H2 pipelines: {len(data['pipelines'])}")
