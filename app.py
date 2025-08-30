import streamlit as st

# IMPORTANT: st.set_page_config() MUST be the very first Streamlit command
st.set_page_config(
    page_title="Green Hydrogen Infrastructure Mapper & Optimizer",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import plotly.graph_objects as go

# Import modules
from modules.data_loader import DataLoader
from modules.map_builder import MapBuilder
from modules.optimizer import SiteOptimizer
from modules.analyzer import CostAnalyzer
from modules.visualizer import Visualizer

# Try to import streamlit-folium
try:
    from streamlit_folium import st_folium

    FOLIUM_INTERACTIVE = True
except ImportError:
    FOLIUM_INTERACTIVE = False
    import streamlit.components.v1 as components


def display_map(folium_map, width=700, height=500):
    """Display map with fallback options"""
    if FOLIUM_INTERACTIVE:
        try:
            return st_folium(folium_map, width=width, height=height, returned_objects=["last_object_clicked"])
        except Exception as e:
            st.error(f"Interactive map error: {e}")
            return display_static_map(folium_map, width, height)
    else:
        return display_static_map(folium_map, width, height)


def display_static_map(folium_map, width, height):
    """Fallback: Static HTML display"""
    st.info("ℹ️ Displaying static map (streamlit-folium not available)")
    map_html = folium_map._repr_html_()
    components.html(map_html, width=width, height=height, scrolling=True)
    return {"last_object_clicked": None}


import plotly.graph_objects as go
import numpy as np
import pandas as pd


def create_plotly_map(infrastructure_data, renewable_data, demand_data, optimization_results=None):
    fig = go.Figure()

    # Color mapping for trace categories
    colors = {
        'existing_plant': 'green',
        'planned_plant': 'darkgreen',
        'storage': 'blue',
        'renewable': 'orange',
        'demand': 'red',
        'recommended': 'lime'
    }

    # Add infrastructure traces
    if not infrastructure_data.empty:
        for infra_type in infrastructure_data['type'].unique():
            subset = infrastructure_data[infrastructure_data['type'] == infra_type]
            type_labels = {
                'existing_plant': 'Existing H2 Plants',
                'planned_plant': 'Planned H2 Megaplants',
                'storage': 'H2 Storage Hubs'
            }
            fig.add_trace(go.Scattermapbox(
                lat=subset['latitude'],
                lon=subset['longitude'],
                mode='markers',
                marker=dict(size=12 if infra_type == 'planned_plant' else 10,
                            color=colors.get(infra_type, 'blue')),
                text=subset['name'],
                name=type_labels.get(infra_type, infra_type),
                customdata=subset['capacity'],
                hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Capacity: %{customdata:.1f} MW<br>" +
                        "Type: " + type_labels.get(infra_type, infra_type) +
                        "<extra></extra>"
                ),
            ))

    # Add renewable energy traces
    if not renewable_data.empty:
        renewable_potential_col = None
        if 'annual_h2_potential' in renewable_data.columns:
            renewable_potential_col = 'annual_h2_potential'
        elif 'potential_h2' in renewable_data.columns:
            renewable_potential_col = 'potential_h2'
        elif 'potential_h2_production' in renewable_data.columns:
            renewable_potential_col = 'potential_h2_production'

        potential_data = renewable_data[renewable_potential_col] if renewable_potential_col else [0] * len(
            renewable_data)

        fig.add_trace(go.Scattermapbox(
            lat=renewable_data['latitude'],
            lon=renewable_data['longitude'],
            mode='markers',
            marker=dict(size=10, color=colors['renewable'], symbol='circle'),
            text=renewable_data['name'],
            customdata=potential_data,
            name='Renewable to H2',
            hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "H2 Potential: %{customdata:,.0f} tons/year" +
                    "<extra></extra>"
            )
        ))

    # Add demand points
    if not demand_data.empty:
        demand_col = 'annual_h2_demand' if 'annual_h2_demand' in demand_data.columns else 'annual_demand'
        fig.add_trace(go.Scattermapbox(
            lat=demand_data['latitude'],
            lon=demand_data['longitude'],
            mode='markers',
            marker=dict(size=10, color=colors['demand'], symbol='square'),
            text=demand_data['name'],
            customdata=demand_data[demand_col],
            name='H2 Demand',
            hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Annual Demand: %{customdata:,.0f} tons/year" +
                    "<extra></extra>"
            )
        ))

    # Add optimization results
    if optimization_results:
        df_results = pd.DataFrame(optimization_results)
        # Provide both Score and Investment in a tuple for customdata
        combined_customdata = list(zip(df_results['score'], df_results['estimated_cost']))

        fig.add_trace(go.Scattermapbox(
            lat=df_results['latitude'],
            lon=df_results['longitude'],
            mode='markers',
            marker=dict(size=14, color=colors['recommended'], symbol='star'),
            text=df_results['name'],
            customdata=combined_customdata,
            name='Recommended H2 Sites',
            hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Score: %{customdata[0]:.3f}<br>" +
                    "Investment: $%{customdata[1]:.1f} M" +
                    "<extra></extra>"
            )
        ))

    # Map layout
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=20.5937, lon=78.962),
            zoom=4,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(255,255,255,0.8)'
        )
    )
    return fig


# Custom CSS with H2 theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .h2-metric-container {
        background: linear-gradient(135deg, #f0f8f0, #e8f5e8);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2E8B57;
    }
    .sidebar .sidebar-content {
        background-color: #f8fdf8;
    }
    .h2-info-box {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header with H2 focus
st.markdown('<h1 class="main-header">💚 Green Hydrogen Infrastructure Mapper & Optimizer</h1>', unsafe_allow_html=True)

# Add H2 focus subtitle
st.markdown("""
<div style="text-align: center; color: #666; margin-bottom: 30px; font-size: 1.2em;">
    <strong>AI-Powered Site Selection for Green Hydrogen Production • Renewable Integration • Supply Chain Optimization</strong>
</div>
""", unsafe_allow_html=True)

# Display streamlit-folium status
if FOLIUM_INTERACTIVE:
    st.success("✅ Interactive maps enabled")
else:
    st.warning("⚠️ Using static maps - streamlit-folium not available")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.optimization_run = False


def main():
    # Initialize components
    data_loader = DataLoader()
    map_builder = MapBuilder()
    optimizer = SiteOptimizer()
    analyzer = CostAnalyzer()
    visualizer = Visualizer()

    # Sidebar controls
    st.sidebar.title("🔧 H2 Infrastructure Analysis")
    st.sidebar.markdown("---")

    # Load data button
    if st.sidebar.button("🔄 Load H2 Sample Data"):
        with st.spinner("Loading hydrogen infrastructure data..."):
            st.session_state.infrastructure_data = data_loader.load_infrastructure_data()
            st.session_state.renewable_data = data_loader.load_renewable_sources()
            st.session_state.demand_data = data_loader.load_demand_centers()
            st.session_state.data_loaded = True
        st.sidebar.success("H2 data loaded successfully!")

    if not st.session_state.data_loaded:
        # H2-focused information
        st.markdown("""
        <div class="h2-info-box">
            <h3 style="color:blue;">🌿 About Green Hydrogen Infrastructure Mapping</h3>
            <p style="color:blue"><strong>Green hydrogen</strong> is produced using renewable electricity to split water through electrolysis, 
            creating zero-emission hydrogen for industrial applications, transportation, and energy storage.</p>

            <h4>🎯 Key H2 Applications Covered:</h4>
            <ul>
                <li><strong>🏭 Green Steel Production</strong> - Decarbonizing steel manufacturing with H2</li>
                <li><strong>🚛 Hydrogen Mobility</strong> - Fuel cell vehicles and H2 refueling stations</li>
                <li><strong>🌱 Green Ammonia</strong> - Clean fertilizer production and shipping fuel</li>
                <li><strong>⚡ H2 Power Generation</strong> - Grid-scale hydrogen fuel cells</li>
                <li><strong>🔋 Energy Storage</strong> - Long-duration renewable energy storage via H2</li>
                <li><strong>🚢 H2 Export Markets</strong> - International green hydrogen trade</li>
            </ul>

            <p>👈 <strong>Load the H2 sample data</strong> to explore India's hydrogen infrastructure potential 
            and see AI-powered optimization recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # H2 Optimization parameters
    st.sidebar.subheader("💰 H2 Investment Parameters")
    investment_budget = st.sidebar.slider("H2 Investment Budget ($M)", 100, 2000, 500, step=50)
    max_projects = st.sidebar.slider("Maximum New H2 Projects", 3, 15, 8)

    st.sidebar.subheader("📍 H2 Location Criteria")
    max_distance_renewable = st.sidebar.slider("Max Distance to Renewable Source (km)", 20, 200, 75, step=5)
    min_demand_proximity = st.sidebar.slider("Min H2 Demand Proximity Score", 0.1, 1.0, 0.6, step=0.1)

    st.sidebar.subheader("🎯 H2 Priority Weights")
    weight_cost = st.sidebar.slider("Cost Optimization", 0.0, 1.0, 0.3, step=0.1)
    weight_renewable = st.sidebar.slider("Renewable Access", 0.0, 1.0, 0.4, step=0.1)
    weight_demand = st.sidebar.slider("H2 Market Access", 0.0, 1.0, 0.3, step=0.1)

    # Normalize weights
    total_weight = weight_cost + weight_renewable + weight_demand
    if total_weight > 0:
        weight_cost /= total_weight
        weight_renewable /= total_weight
        weight_demand /= total_weight

    # Run H2 optimization
    if st.sidebar.button("🚀 Optimize H2 Sites"):
        with st.spinner("Optimizing green hydrogen site locations..."):
            optimization_params = {
                'budget': investment_budget,
                'max_projects': max_projects,
                'max_distance_renewable': max_distance_renewable,
                'min_demand_proximity': min_demand_proximity,
                'weights': {'cost': weight_cost, 'renewable': weight_renewable, 'demand': weight_demand}
            }

            st.session_state.optimization_results = optimizer.optimize_sites(
                st.session_state.infrastructure_data,
                st.session_state.renewable_data,
                st.session_state.demand_data,
                optimization_params
            )
            st.session_state.optimization_run = True
        st.sidebar.success("H2 optimization completed!")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🗺️ H2 Infrastructure Map", "📊 H2 Analytics", "💡 H2 Recommendations", "💰 H2 Economics"])

    with tab1:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("🌿 Green Hydrogen Infrastructure Mapping")

            # Choose map type
            map_type = st.radio("Select Map Visualization:", ["Interactive H2 Map (Folium)", "Static H2 Map (Plotly)"],
                                horizontal=True)

            if map_type == "Interactive H2 Map (Folium)" and FOLIUM_INTERACTIVE:
                # Create Folium map
                m = map_builder.create_base_map()
                m = map_builder.add_infrastructure_layer(m, st.session_state.infrastructure_data)
                m = map_builder.add_renewable_layer(m, st.session_state.renewable_data)
                m = map_builder.add_demand_layer(m, st.session_state.demand_data)

                if st.session_state.optimization_run:
                    m = map_builder.add_optimization_results(m, st.session_state.optimization_results)

                map_data = display_map(m, width=700, height=600)

            else:
                # Use Plotly map
                optimization_results = st.session_state.optimization_results if st.session_state.optimization_run else None
                plotly_fig = create_plotly_map(
                    st.session_state.infrastructure_data,
                    st.session_state.renewable_data,
                    st.session_state.demand_data,
                    optimization_results
                )
                st.plotly_chart(plotly_fig, use_container_width=True)

        with col2:
            st.subheader("H2 Map Legend")
            legend_html = """
            <div style="background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd;">
            <h4 style="color: #2E8B57; margin-bottom: 15px;">🌿 Hydrogen Infrastructure</h4>

            <div style="margin-bottom: 12px;">
                <span style="color: green; font-size: 18px;">●</span> 
                <strong style="color:black;">Existing H2 Plants</strong><br>
                <small style="margin-left: 20px; color: #666;">Operational hydrogen production facilities</small>
            </div>

            <div style="margin-bottom: 12px;">
                <span style="color: darkgreen; font-size: 18px;">●</span> 
                <strong style="color:black;">Planned H2 Megaplants</strong><br>
                <small style="margin-left: 20px; color: #666;">Future large-scale green H2 facilities</small>
            </div>

            <div style="margin-bottom: 12px;">
                <span style="color: blue; font-size: 18px;">●</span> 
                <strong style="color:black;">H2 Storage Hubs</strong><br>
                <small style="margin-left: 20px; color: #666;">Hydrogen storage and distribution centers</small>
            </div>

            <div style="margin-bottom: 12px;">
                <span style="color: orange; font-size: 18px;">●</span> 
                <strong style="color:black;">Renewable-to-H2 Sources</strong><br>
                <small style="margin-left: 20px; color: #666;">Solar/Wind farms for hydrogen production</small>
            </div>

            <div style="margin-bottom: 12px;">
                <span style="color: red; font-size: 18px;">●</span> 
                <strong style="color:black;">H2 Demand Centers</strong><br>
                <small style="margin-left: 20px; color: #666;">Industries requiring hydrogen supply</small>
            </div>

            <div style="margin-bottom: 12px;">
                <span style="color: lightgreen; font-size: 18px;">★</span> 
                <strong style="color:black;">AI-Recommended H2 Sites</strong><br>
                <small style="margin-left: 20px; color: #666;">Optimized locations for new H2 plants</small>
            </div>

            <hr style="margin: 15px 0;">
            <h5 style="color: #2E8B57; margin-bottom: 10px;">🎯 H2 Industry Focus:</h5>
            <div style="font-size: 12px; color: #555;">
                • 🏭 Green Steel Production<br>
                • 🚛 Hydrogen Mobility & Transport<br>
                • 🌱 Green Ammonia Production<br>
                • ⚡ H2 Fuel Cells & Power<br>
                • 🚢 Green H2 Export<br>
                • 🏭 Industrial H2 Applications
            </div>
            </div>
            """
            st.markdown(legend_html, unsafe_allow_html=True)

            # H2-SPECIFIC STATISTICS
            st.subheader("Current H2 Infrastructure")
            if st.session_state.data_loaded:
                existing_h2_plants = len(st.session_state.infrastructure_data[
                                             st.session_state.infrastructure_data['type'] == 'existing_plant'])
                planned_h2_plants = len(st.session_state.infrastructure_data[
                                            st.session_state.infrastructure_data['type'] == 'planned_plant'])
                h2_storage_hubs = len(st.session_state.infrastructure_data[
                                          st.session_state.infrastructure_data['type'] == 'storage'])

                # H2-focused metrics
                total_h2_capacity = st.session_state.infrastructure_data['capacity'].sum()
                green_h2_sources = len(st.session_state.renewable_data[
                                           st.session_state.renewable_data.get('dedicated_h2_production',
                                                                               False) == True])
                h2_demand_centers = len(st.session_state.demand_data)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("H2 Plants (Existing)", existing_h2_plants, delta="Operational")
                    st.metric("H2 Megaplants (Planned)", planned_h2_plants, delta="Future")
                    st.metric("H2 Storage Hubs", h2_storage_hubs)

                with col2:
                    st.metric("Total H2 Capacity", f"{total_h2_capacity:,.0f} MW")
                    st.metric("Renewable-H2 Projects", green_h2_sources, delta="Dedicated")
                    st.metric("H2 Demand Centers", h2_demand_centers)

                # Additional H2 metrics
                if not st.session_state.infrastructure_data.empty:
                    green_capacity = st.session_state.infrastructure_data[
                        st.session_state.infrastructure_data.get('production_type', '') == 'Green']['capacity'].sum()
                    green_percentage = (green_capacity / total_h2_capacity * 100) if total_h2_capacity > 0 else 0

                    st.metric("Green H2 Share", f"{green_percentage:.1f}%",
                              delta="of total capacity", delta_color="normal")

    with tab2:
        st.subheader("📊 H2 Infrastructure Analytics Dashboard")

        col1, col2 = st.columns(2)

        with col1:
            # H2 capacity chart
            fig = visualizer.create_h2_capacity_chart(st.session_state.infrastructure_data)
            st.plotly_chart(fig, use_container_width=True)

            # H2 production methods
            fig = visualizer.create_h2_production_methods_chart(st.session_state.infrastructure_data)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # H2 demand analysis
            fig = visualizer.create_h2_demand_analysis(st.session_state.demand_data)
            st.plotly_chart(fig, use_container_width=True)

            # Renewable H2 potential
            fig = visualizer.create_renewable_h2_potential_chart(st.session_state.renewable_data)
            st.plotly_chart(fig, use_container_width=True)

        # H2-specific KPIs
        st.subheader("🎯 Key H2 Infrastructure Metrics")

        if st.session_state.data_loaded:
            col1, col2, col3, col4 = st.columns(4)

            # Calculate H2-specific metrics
            total_h2_production = st.session_state.infrastructure_data.get('annual_h2_production', pd.Series([0])).sum()
            total_h2_demand = st.session_state.demand_data.get('annual_h2_demand', pd.Series([0])).sum()
            h2_supply_gap = st.session_state.demand_data.get('h2_supply_gap', pd.Series([0])).sum()
            green_h2_plants = len(st.session_state.infrastructure_data[
                                      st.session_state.infrastructure_data.get('production_type', '') == 'Green'])

            with col1:
                st.metric(
                    "Total H2 Production",
                    f"{total_h2_production:,.0f} tons/year",
                    delta="Current capacity"
                )

            with col2:
                st.metric(
                    "Total H2 Demand",
                    f"{total_h2_demand:,.0f} tons/year",
                    delta="Market requirement"
                )

            with col3:
                st.metric(
                    "H2 Supply Gap",
                    f"{h2_supply_gap:,.0f} tons/year",
                    delta="Investment opportunity",
                    delta_color="inverse"
                )

            with col4:
                st.metric(
                    "Green H2 Plants",
                    f"{green_h2_plants}",
                    delta="Zero-emission facilities",
                    delta_color="normal"
                )

    with tab3:
        if st.session_state.optimization_run:
            st.subheader("🎯 H2 Site Optimization Results")

            results = st.session_state.optimization_results

            # Key H2 metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Recommended H2 Sites", len(results))
            with col2:
                total_investment = sum([site['estimated_cost'] for site in results])
                st.metric("Total H2 Investment", f"${total_investment:.1f}M")
            with col3:
                total_capacity = sum([site['capacity'] for site in results])
                st.metric("Total H2 Capacity", f"{total_capacity:.1f} MW")
            with col4:
                avg_score = np.mean([site['score'] for site in results])
                st.metric("Avg. Optimization Score", f"{avg_score:.3f}")

            # Detailed H2 recommendations
            st.subheader("📋 H2 Site Recommendations")

            recommendations_df = pd.DataFrame(results)
            recommendations_df = recommendations_df.round(3)

            # Format the dataframe for display
            display_df = recommendations_df[
                ['name', 'latitude', 'longitude', 'capacity', 'estimated_cost', 'score']].copy()
            display_df.columns = ['H2 Site Name', 'Latitude', 'Longitude', 'H2 Capacity (MW)', 'Investment ($M)',
                                  'Optimization Score']

            st.dataframe(display_df, use_container_width=True)

            # H2 Priority ranking
            st.subheader("🏆 H2 Implementation Priority")
            priority_chart = visualizer.create_priority_ranking(results)
            st.plotly_chart(priority_chart, use_container_width=True)

        else:
            st.info("Run H2 optimization to view recommendations.")

    with tab4:
        if st.session_state.optimization_run:
            st.subheader("💰 H2 Economic Analysis")

            results = st.session_state.optimization_results

            # H2 cost breakdown
            col1, col2 = st.columns(2)

            with col1:
                cost_breakdown = analyzer.calculate_cost_breakdown(results)
                fig_cost = visualizer.create_cost_breakdown_chart(cost_breakdown)
                st.plotly_chart(fig_cost, use_container_width=True)

            with col2:
                roi_analysis = analyzer.calculate_roi_analysis(results)
                fig_roi = visualizer.create_roi_chart(roi_analysis)
                st.plotly_chart(fig_roi, use_container_width=True)

            # H2 investment timeline
            st.subheader("📅 H2 Investment Timeline")
            timeline_data = analyzer.create_investment_timeline(results)
            fig_timeline = visualizer.create_timeline_chart(timeline_data)
            st.plotly_chart(fig_timeline, use_container_width=True)

            # H2 risk assessment
            st.subheader("⚠️ H2 Project Risk Assessment")
            risk_data = analyzer.assess_risks(results)
            risk_df = pd.DataFrame(risk_data)
            st.dataframe(risk_df, use_container_width=True)

        else:
            st.info("Run H2 optimization to view economic analysis.")


if __name__ == "__main__":
    main()
