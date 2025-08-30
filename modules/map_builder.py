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
                     <h3 align="center" style="font-size:20px; color:#2E8B57;">
                     <b>🌿 Green Hydrogen Infrastructure Map of India</b></h3>
                     '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Add different tile layers
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='OpenStreetMap',
            name='🗺️ Street Map'
        ).add_to(m)

        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='🛰️ Satellite View',
            overlay=False,
            control=True
        ).add_to(m)

        return m

    def add_infrastructure_layer(self, m, infrastructure_data: pd.DataFrame):
        """Add H2 infrastructure to map with detailed popups"""

        # H2-SPECIFIC STYLING
        type_config = {
            'existing_plant': {'color': 'green', 'icon': 'flash', 'prefix': 'fa'},
            'planned_plant': {'color': 'darkgreen', 'icon': 'plus', 'prefix': 'fa'},
            'storage': {'color': 'blue', 'icon': 'database', 'prefix': 'fa'}
        }

        # Create H2-focused feature groups with emojis
        existing_h2_fg = folium.FeatureGroup(name='🏭 Existing H2 Plants')
        planned_h2_fg = folium.FeatureGroup(name='🚀 Planned H2 Megaplants')
        h2_storage_fg = folium.FeatureGroup(name='🏗️ H2 Storage Hubs')

        for _, facility in infrastructure_data.iterrows():
            config = type_config.get(facility['type'], type_config['existing_plant'])

            # H2-SPECIFIC DETAILED POPUP CONTENT
            if facility['type'] in ['existing_plant', 'planned_plant']:
                popup_content = f"""
                <div style="width: 300px; font-family: Arial, sans-serif;">
                    <h4 style="color: #2E8B57; margin-bottom: 10px;">
                        🌿 {facility['name']}
                    </h4>
                    <hr style="margin: 8px 0;">
                    <p><strong>🔋 H2 Capacity:</strong> {facility['capacity']:.1f} MW</p>
                    <p><strong>⚙️ Technology:</strong> {facility.get('technology', 'N/A')}</p>
                    <p><strong>🏭 Production Type:</strong> {facility.get('production_type', 'N/A')}</p>
                    <p><strong>🧪 H2 Purity:</strong> {facility.get('h2_purity', 'N/A'):.2f}%</p>
                    <p><strong>📊 Annual H2 Production:</strong> {facility.get('annual_h2_production', 'N/A'):,.0f} tons/year</p>
                    <p><strong>🌱 Carbon Intensity:</strong> {facility.get('carbon_intensity', 'N/A')} kg CO2/kg H2</p>
                    <p><strong>♻️ Renewable Powered:</strong> {'✅ Yes' if facility.get('renewable_powered', False) else '❌ No'}</p>
                    <p><strong>💰 Investment:</strong> ${facility['investment_cost']:.1f}M</p>
                    <p><strong>📍 Status:</strong> {facility['status'].replace('_', ' ').title()}</p>
                </div>
                """
            else:  # H2 Storage
                popup_content = f"""
                <div style="width: 300px; font-family: Arial, sans-serif;">
                    <h4 style="color: #4682B4; margin-bottom: 10px;">
                        🏗️ {facility['name']}
                    </h4>
                    <hr style="margin: 8px 0;">
                    <p><strong>🛢️ H2 Storage Capacity:</strong> {facility['capacity']:,.0f} tons</p>
                    <p><strong>⚙️ Storage Technology:</strong> {facility.get('technology', 'N/A')}</p>
                    <p><strong>📊 Storage Pressure:</strong> {facility.get('storage_pressure', 'N/A')} bar</p>
                    <p><strong>💰 Investment:</strong> ${facility['investment_cost']:.1f}M</p>
                    <p><strong>🎯 Strategic Reserve:</strong> {'✅ Yes' if facility.get('strategic_reserve', False) else '❌ No'}</p>
                    <p><strong>📍 Status:</strong> {facility['status'].replace('_', ' ').title()}</p>
                </div>
                """

            marker = folium.Marker(
                location=[facility['latitude'], facility['longitude']],
                popup=folium.Popup(popup_content, max_width=350),
                tooltip=f"🌿 {facility['name']} - Click for details",
                icon=folium.Icon(
                    color=config['color'],
                    icon=config['icon'],
                    prefix=config['prefix']
                )
            )

            # Add to appropriate feature group
            if facility['type'] == 'existing_plant':
                marker.add_to(existing_h2_fg)
            elif facility['type'] == 'planned_plant':
                marker.add_to(planned_h2_fg)
            else:
                marker.add_to(h2_storage_fg)

        # Add feature groups to map
        existing_h2_fg.add_to(m)
        planned_h2_fg.add_to(m)
        h2_storage_fg.add_to(m)

        return m

    def add_renewable_layer(self, m, renewable_data: pd.DataFrame):
        """Add renewable sources optimized for H2 production"""

        renewable_h2_fg = folium.FeatureGroup(name='⚡ Renewable-to-H2 Sources')

        type_colors = {
            'solar': 'orange',
            'wind': 'lightblue',
            'hydro': 'darkblue'
        }

        type_icons = {
            'solar': '☀️',
            'wind': '💨',
            'hydro': '💧'
        }

        for _, source in renewable_data.iterrows():
            color = type_colors.get(source['type'], 'orange')
            icon_emoji = type_icons.get(source['type'], '⚡')

            # H2-FOCUSED RENEWABLE POPUP
            popup_content = f"""
            <div style="width: 320px; font-family: Arial, sans-serif;">
                <h4 style="color: #FF8C00; margin-bottom: 10px;">
                    {icon_emoji} {source['name']}
                </h4>
                <hr style="margin: 8px 0;">
                <p><strong>⚡ Energy Type:</strong> {source['type'].title()}-to-H2</p>
                <p><strong>🔋 Capacity:</strong> {source['capacity']:.1f} MW</p>
                <p><strong>🎯 Dedicated H2 Production:</strong> {'✅ Yes' if source.get('dedicated_h2_production', False) else '❌ No'}</p>
                <p><strong>🌿 H2 Electrolyzer Capacity:</strong> {source.get('h2_electrolyzer_capacity', 0):.1f} MW</p>
                <p><strong>📊 Annual H2 Potential:</strong> {source.get('annual_h2_potential', source.get('potential_h2_production', 0)):,.0f} tons/year</p>
                <p><strong>🔌 Grid Connected:</strong> {'✅ Yes' if source.get('grid_connection', True) else '❌ No'}</p>
                <p><strong>💧 Water Access:</strong> {source.get('water_access_rating', source.get('water_access', 'N/A'))}</p>
                <p><strong>🚢 Distance to Port:</strong> {source.get('distance_to_port', 'N/A'):.0f} km</p>
            </div>
            """

            # Different marker size for dedicated H2 facilities
            radius = 15 if source.get('dedicated_h2_production', False) else 10

            folium.CircleMarker(
                location=[source['latitude'], source['longitude']],
                radius=radius,
                popup=folium.Popup(popup_content, max_width=350),
                tooltip=f"{icon_emoji} {source['name']} - H2 Potential: {source.get('annual_h2_potential', source.get('potential_h2_production', 0)):,.0f} tons/year",
                color='black',
                weight=2,
                fill=True,
                fillColor=color,
                fillOpacity=0.8
            ).add_to(renewable_h2_fg)

        renewable_h2_fg.add_to(m)
        return m

    def add_demand_layer(self, m, demand_data: pd.DataFrame):
        """Add H2 demand centers with industry-specific styling"""

        h2_demand_fg = folium.FeatureGroup(name='🏭 H2 Demand Centers')

        # H2 industry colors and icons
        industry_config = {
            'Green Steel Production': {'color': 'red', 'icon': '🏭'},
            'Hydrogen Mobility/Transportation': {'color': 'purple', 'icon': '🚛'},
            'H2 Mobility & Transport': {'color': 'purple', 'icon': '🚛'},
            'Green Ammonia Production': {'color': 'darkred', 'icon': '🌱'},
            'Hydrogen Fuel Cells': {'color': 'pink', 'icon': '🔋'},
            'H2 Fuel Cells': {'color': 'pink', 'icon': '🔋'},
            'Green Hydrogen Export': {'color': 'cadetblue', 'icon': '🚢'},
            'Green H2 Export': {'color': 'cadetblue', 'icon': '🚢'},
            'Hydrogen Power Generation': {'color': 'orange', 'icon': '⚡'},
            'H2 Power Generation': {'color': 'orange', 'icon': '⚡'},
            'Industrial Heating (H2)': {'color': 'gray', 'icon': '🔥'},
            'Industrial H2 Applications': {'color': 'gray', 'icon': '🔥'},
            'Hydrogen Refining': {'color': 'lightred', 'icon': '⚗️'},
            'H2 Refining': {'color': 'lightred', 'icon': '⚗️'}
        }

        for _, center in demand_data.iterrows():
            industry_info = industry_config.get(center['industry'], {'color': 'red', 'icon': '🏭'})
            color = industry_info['color']
            icon_emoji = industry_info['icon']

            # H2-SPECIFIC DEMAND POPUP
            demand_col = 'annual_h2_demand' if 'annual_h2_demand' in center else 'annual_demand'
            supply_gap_col = 'h2_supply_gap' if 'h2_supply_gap' in center else 'supply_gap'
            wtp_col = 'willingness_to_pay_h2' if 'willingness_to_pay_h2' in center else 'willingness_to_pay'

            popup_content = f"""
            <div style="width: 340px; font-family: Arial, sans-serif;">
                <h4 style="color: #DC143C; margin-bottom: 10px;">
                    {icon_emoji} {center['name']}
                </h4>
                <hr style="margin: 8px 0;">
                <p><strong>🏭 H2 Industry:</strong> {center['industry']}</p>
                <p><strong>📊 Annual H2 Demand:</strong> {center.get(demand_col, 0):,.0f} tons/year</p>
                <p><strong>📈 H2 Supply Gap:</strong> {center.get(supply_gap_col, 0):,.0f} tons/year</p>
                <p><strong>🌿 Green H2 Preference:</strong> {'✅ Yes' if center.get('green_h2_preference', False) else '❌ No'}</p>
                <p><strong>💰 Willing to Pay:</strong> ${center.get(wtp_col, 0):.2f}/kg H2</p>
                <p><strong>🧪 H2 Purity Required:</strong> {center.get('h2_purity_requirement', center.get('quality_requirement', 99)):.1f}%</p>
                <p><strong>🌱 CO2 Reduction Target:</strong> {center.get('carbon_reduction_target', center.get('co2_reduction_target', 0)):,.0f} tons/year</p>
                <p><strong>📋 Contract Length:</strong> {center.get('contract_length_years', center.get('contract_duration', 0))} years</p>
                <p><strong>🚢 Port Proximity:</strong> {center.get('port_proximity', 'N/A'):.0f} km</p>
            </div>
            """

            # Different marker shapes for export vs domestic
            icon_type = 'ship' if 'Export' in center['industry'] else 'industry'

            folium.Marker(
                location=[center['latitude'], center['longitude']],
                popup=folium.Popup(popup_content, max_width=370),
                tooltip=f"{icon_emoji} {center['name']} - {center['industry']}",
                icon=folium.Icon(
                    color=color,
                    icon=icon_type,
                    prefix='fa'
                )
            ).add_to(h2_demand_fg)

        h2_demand_fg.add_to(m)
        return m

    def add_optimization_results(self, m, optimization_results: List[Dict]):
        """Add H2-optimized site recommendations"""

        if not optimization_results:
            return m

        h2_recommendations_fg = folium.FeatureGroup(name='🌟 AI-Recommended H2 Sites')

        for i, site in enumerate(optimization_results):
            # H2-SPECIFIC RECOMMENDATION POPUP
            popup_content = f"""
            <div style="width: 360px; font-family: Arial, sans-serif;">
                <h4 style="color: #32CD32; margin-bottom: 10px;">
                    🌟 {site['name']}
                </h4>
                <hr style="margin: 8px 0;">
                <p><strong>🏆 Optimization Rank:</strong> #{i + 1}</p>
                <p><strong>🔋 H2 Production Capacity:</strong> {site['capacity']:.1f} MW</p>
                <p><strong>💰 Estimated Investment:</strong> ${site['estimated_cost']:.1f}M</p>
                <p><strong>📊 Optimization Score:</strong> {site['score']:.3f}</p>
                <p><strong>🌿 Expected H2 Production:</strong> {site.get('annual_h2_production', site['capacity'] * 0.5 * 8760 * 0.05):,.0f} tons/year</p>
                <p><strong>⚡ Distance to Renewable:</strong> {site.get('distance_to_renewable', 0):.1f} km</p>
                <p><strong>🏭 H2 Demand Accessibility:</strong> {site.get('demand_score', 0):.3f}</p>
                <p><strong>♻️ Renewable Energy Access:</strong> {site.get('renewable_score', 0):.3f}</p>
                <p><strong>🌱 CO2 Reduction Potential:</strong> {site.get('co2_reduction', site['capacity'] * 8760 * 0.5 * 0.05 * 9):,.0f} tons/year</p>
                <p><strong>⏱️ Implementation Time:</strong> {site.get('implementation_time', 36)} months</p>
            </div>
            """

            # Create star marker for recommendations
            folium.Marker(
                location=[site['latitude'], site['longitude']],
                popup=folium.Popup(popup_content, max_width=400),
                tooltip=f"🌟 H2 Recommendation #{i + 1}: {site['name']} (Score: {site['score']:.3f})",
                icon=folium.Icon(
                    color='lightgreen',
                    icon='star',
                    prefix='fa'
                )
            ).add_to(h2_recommendations_fg)

            # H2 supply radius circle
            folium.Circle(
                location=[site['latitude'], site['longitude']],
                radius=site.get('h2_supply_radius', 75000),  # 75km H2 supply radius
                popup=f"H2 Supply Coverage Area - {site['name']}",
                color='lightgreen',
                weight=2,
                fill=True,
                fillOpacity=0.1,
                tooltip=f"H2 Supply Area: {site.get('h2_supply_radius', 75):.0f}km radius"
            ).add_to(h2_recommendations_fg)

        h2_recommendations_fg.add_to(m)

        # Add comprehensive layer control
        folium.LayerControl(collapsed=False, position='topright').add_to(m)

        # Add custom legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 160px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    border-radius: 10px;
                    ">
        <h4 style="margin-bottom: 10px; color: #2E8B57;">🌿 H2 Infrastructure Legend</h4>
        <p><span style="color: green;">●</span> Existing H2 Plants</p>
        <p><span style="color: darkgreen;">●</span> Planned H2 Megaplants</p>
        <p><span style="color: blue;">●</span> H2 Storage Hubs</p>
        <p><span style="color: orange;">●</span> Renewable-to-H2</p>
        <p><span style="color: red;">●</span> H2 Demand Centers</p>
        <p><span style="color: lightgreen;">★</span> AI Recommended Sites</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        return m
