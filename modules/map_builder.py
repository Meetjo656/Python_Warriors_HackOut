import folium
import pandas as pd
from typing import List, Dict
import numpy as np


class MapBuilder:
    def __init__(self):
        self.center_lat = 20.5937
        self.center_lon = 78.9629  # Center of India

    def create_base_map(self):
        """Create base map for H2 infrastructure with custom styling"""
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=5,
            tiles='OpenStreetMap',
            width='100%',
            height='100%'
        )

        # Add custom title to map
        title_html = '''
        <h3 align="center" style="font-size:20px"><b>🌿 Green Hydrogen Infrastructure Map</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        return m

    def add_infrastructure(self, folium_map, infrastructure_data: pd.DataFrame):
        """Add H2 infrastructure facilities to the map"""
        if infrastructure_data.empty:
            return

        # Color mapping for different facility types
        colors = {
            'existing_plant': 'green',
            'planned_plant': 'darkgreen',
            'storage': 'blue'
        }

        # Icons for different facility types
        icons = {
            'existing_plant': 'leaf',
            'planned_plant': 'cog',
            'storage': 'tint'
        }

        for idx, facility in infrastructure_data.iterrows():
            facility_type = facility.get('type', 'existing_plant')
            color = colors.get(facility_type, 'green')
            icon = icons.get(facility_type, 'leaf')

            # Create detailed popup
            popup_html = f"""
            <div style="width: 300px;">
                <h4>🏭 {facility['name']}</h4>
                <hr>
                <b>🔋 H2 Capacity:</b> {facility['capacity']:.1f} MW<br>
                <b>⚙️ Technology:</b> {facility.get('technology', 'N/A')}<br>
                <b>🏭 Production Type:</b> {facility.get('production_type', 'N/A')}<br>
                <b>🧪 H2 Purity:</b> {facility.get('h2_purity', 'N/A'):.2f}%<br>
                <b>📊 Annual H2 Production:</b> {facility.get('annual_h2_production', 'N/A'):,.0f} tons/year<br>
                <b>🌱 Carbon Intensity:</b> {facility.get('carbon_intensity', 'N/A')} kg CO2/kg H2<br>
                <b>♻️ Renewable Powered:</b> {'✅ Yes' if facility.get('renewable_powered', False) else '❌ No'}<br>
                <b>💰 Investment:</b> ${facility['investment_cost']:.1f}M<br>
                <b>📍 Status:</b> {facility['status'].replace('_', ' ').title()}
            </div>
            """

            # Add marker to map
            folium.Marker(
                location=[facility['latitude'], facility['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"{facility['name']} ({facility['capacity']:.0f} MW)",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(folium_map)

    def add_renewable_sources(self, folium_map, renewable_data: pd.DataFrame):
        """Add renewable energy sources to the map"""
        if renewable_data.empty:
            return

        # Color mapping for renewable types
        colors = {
            'solar': 'orange',
            'wind': 'lightblue',
            'hydro': 'blue'
        }

        icons = {
            'solar': 'sun-o',
            'wind': 'leaf',
            'hydro': 'tint'
        }

        for idx, source in renewable_data.iterrows():
            source_type = source.get('type', 'solar')
            color = colors.get(source_type, 'orange')
            icon = icons.get(source_type, 'sun-o')

            # Create detailed popup
            popup_html = f"""
            <div style="width: 300px;">
                <h4>⚡ {source['name']}</h4>
                <hr>
                <b>⚡ Energy Type:</b> {source['type'].title()}-to-H2<br>
                <b>🔋 Capacity:</b> {source['capacity']:.1f} MW<br>
                <b>🎯 Dedicated H2 Production:</b> {'✅ Yes' if source.get('dedicated_h2_production', False) else '❌ No'}<br>
                <b>🌿 H2 Electrolyzer Capacity:</b> {source.get('h2_electrolyzer_capacity', 0):.1f} MW<br>
                <b>📊 Annual H2 Potential:</b> {source.get('annual_h2_potential', source.get('potential_h2_production', 0)):,.0f} tons/year<br>
                <b>🔌 Grid Connected:</b> {'✅ Yes' if source.get('grid_connection', True) else '❌ No'}<br>
                <b>💧 Water Access:</b> {source.get('water_access_rating', source.get('water_access', 'N/A'))}<br>
                <b>🚢 Distance to Port:</b> {source.get('distance_to_port', 'N/A'):.0f} km
            </div>
            """

            # Add marker to map
            folium.Marker(
                location=[source['latitude'], source['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"{source['name']} ({source['capacity']:.0f} MW)",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(folium_map)

    def add_demand_centers(self, folium_map, demand_data: pd.DataFrame):
        """Add H2 demand centers to the map"""
        if demand_data.empty:
            return

        # Determine correct column names
        demand_col = 'annual_h2_demand' if 'annual_h2_demand' in demand_data.columns else 'annual_demand'
        supply_gap_col = 'h2_supply_gap' if 'h2_supply_gap' in demand_data.columns else 'supply_gap'
        wtp_col = 'willingness_to_pay_h2' if 'willingness_to_pay_h2' in demand_data.columns else 'willingness_to_pay'

        for idx, center in demand_data.iterrows():
            # Create detailed popup
            popup_html = f"""
            <div style="width: 300px;">
                <h4>🏭 {center['name']}</h4>
                <hr>
                <b>🏭 H2 Industry:</b> {center['industry']}<br>
                <b>📊 Annual H2 Demand:</b> {center.get(demand_col, 0):,.0f} tons/year<br>
                <b>📈 H2 Supply Gap:</b> {center.get(supply_gap_col, 0):,.0f} tons/year<br>
                <b>🌿 Green H2 Preference:</b> {'✅ Yes' if center.get('green_h2_preference', False) else '❌ No'}<br>
                <b>💰 Willing to Pay:</b> ${center.get(wtp_col, 0):.2f}/kg H2<br>
                <b>🧪 H2 Purity Required:</b> {center.get('h2_purity_requirement', center.get('quality_requirement', 99)):.1f}%<br>
                <b>🌱 CO2 Reduction Target:</b> {center.get('carbon_reduction_target', center.get('co2_reduction_target', 0)):,.0f} tons/year<br>
                <b>📋 Contract Length:</b> {center.get('contract_length_years', center.get('contract_duration', 0))} years<br>
                <b>🚢 Port Proximity:</b> {center.get('port_proximity', 'N/A'):.0f} km
            </div>
            """

            # Color based on priority
            color = 'red' if center.get('priority', 'Medium') == 'High' else 'lightred'

            # Add marker to map
            folium.Marker(
                location=[center['latitude'], center['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"{center['name']} ({center.get(demand_col, 0):,.0f} tons/year)",
                icon=folium.Icon(color=color, icon='industry', prefix='fa')
            ).add_to(folium_map)

    def add_optimization_results(self, folium_map, optimization_results: List[Dict]):
        """Add AI-recommended sites to the map"""
        if not optimization_results:
            return

        for i, site in enumerate(optimization_results):
            # Create detailed popup
            popup_html = f"""
            <div style="width: 300px;">
                <h4>⭐ {site['name']}</h4>
                <hr>
                <b>🏆 Optimization Rank:</b> #{i + 1}<br>
                <b>🔋 H2 Production Capacity:</b> {site['capacity']:.1f} MW<br>
                <b>💰 Estimated Investment:</b> ${site['estimated_cost']:.1f}M<br>
                <b>📊 Optimization Score:</b> {site['score']:.3f}<br>
                <b>🌿 Expected H2 Production:</b> {site.get('annual_h2_production', site['capacity'] * 0.5 * 8760 * 0.05):,.0f} tons/year<br>
                <b>⚡ Distance to Renewable:</b> {site.get('distance_to_renewable', 0):.1f} km<br>
                <b>🏭 H2 Demand Accessibility:</b> {site.get('demand_score', 0):.3f}<br>
                <b>♻️ Renewable Energy Access:</b> {site.get('renewable_score', 0):.3f}<br>
                <b>🌱 CO2 Reduction Potential:</b> {site.get('co2_reduction', site['capacity'] * 8760 * 0.5 * 0.05 * 9):,.0f} tons/year<br>
                <b>⏱️ Implementation Time:</b> {site.get('implementation_time', 36)} months
            </div>
            """

            # Add star marker for recommended sites
            folium.Marker(
                location=[site['latitude'], site['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"⭐ {site['name']} (Score: {site['score']:.3f})",
                icon=folium.Icon(color='purple', icon='star', prefix='fa')
            ).add_to(folium_map)

    def add_feasibility_sites(self, folium_map, feasibility_data: pd.DataFrame, max_sites: int = 100):
        """Add high feasibility sites to the map (sampled for performance)"""
        if feasibility_data.empty:
            return

        # Sample data for performance (show only top sites)
        if len(feasibility_data) > max_sites:
            # Show top feasibility sites
            sample_data = feasibility_data.nlargest(max_sites, 'feasibility_score')
        else:
            sample_data = feasibility_data

        # Create feature group for feasibility sites
        fg = folium.FeatureGroup(name="High Feasibility Sites")

        for idx, site in sample_data.iterrows():
            # Create detailed popup
            popup_html = f"""
            <div style="width: 300px;">
                <h4>🎯 {site['name']}</h4>
                <hr>
                <b>📊 Feasibility Score:</b> {site['feasibility_score']:.3f}<br>
                <b>🌿 H2 Production:</b> {site['h2_production_daily']:.1f} kg/day<br>
                <b>⚡ Total Capacity:</b> {site['capacity']:.1f} kW<br>
                <b>🔋 Solar Power:</b> {site['pv_power']:.1f} kW<br>
                <b>💨 Wind Power:</b> {site['wind_power']:.1f} kW<br>
                <b>🌡️ Temperature:</b> {site['temperature']:.1f}°C<br>
                <b>💨 Wind Speed:</b> {site['wind_speed']:.1f} m/s<br>
                <b>⚙️ System Efficiency:</b> {site['system_efficiency']:.1f}%<br>
                <b>💧 Desalination Power:</b> {site['desalination_power']:.1f} kW
            </div>
            """

            # Color based on feasibility score
            if site['feasibility_score'] >= 0.95:
                color = 'darkgreen'
            elif site['feasibility_score'] >= 0.90:
                color = 'green'
            else:
                color = 'lightgreen'

            # Add circle marker (smaller footprint)
            folium.CircleMarker(
                location=[site['latitude'], site['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"{site['name']} (Score: {site['feasibility_score']:.3f})",
                radius=max(3, min(8, site['feasibility_score'] * 8)),  # Size based on score
                color=color,
                fillColor=color,
                weight=2,
                fillOpacity=0.7
            ).add_to(fg)

        fg.add_to(folium_map)

    def add_legend(self, folium_map):
        """Add legend to the map"""
        legend_html = """
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 200px; height: 180px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>🗺️ Map Legend</h4>
        <i class="fa fa-leaf" style="color:green"></i> Existing H2 Plants<br>
        <i class="fa fa-cog" style="color:darkgreen"></i> Planned H2 Megaplants<br>
        <i class="fa fa-tint" style="color:blue"></i> H2 Storage Hubs<br>
        <i class="fa fa-sun-o" style="color:orange"></i> Renewable-to-H2<br>
        <i class="fa fa-industry" style="color:red"></i> H2 Demand Centers<br>
        <i class="fa fa-star" style="color:purple"></i> AI Recommended Sites
        </div>
        """
        folium_map.get_root().html.add_child(folium.Element(legend_html))
