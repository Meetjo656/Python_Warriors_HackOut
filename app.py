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


def display_folium_map(folium_map, width=700, height=500):
    """Display Folium map with fallback options"""
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


def create_plotly_map(infrastructure_data, renewable_data, demand_data, feasibility_data=None,
                      optimization_results=None):
    """Create interactive Plotly map"""
    fig = go.Figure()

    # Color mapping for trace categories
    colors = {
        'existing_plant': 'green',
        'planned_plant': 'darkgreen',
        'storage': 'blue',
        'renewable': 'orange',
        'demand': 'red',
        'recommended': 'lime',
        'feasible_site': 'purple'
    }

    # Add feasibility sites (from Hydro_74K.csv) with sampling for performance
    if feasibility_data is not None and not feasibility_data.empty:
        # Sample data for better performance (max 1000 points)
        if len(feasibility_data) > 1000:
            sample_data = feasibility_data.sample(n=1000, random_state=42)
        else:
            sample_data = feasibility_data

        fig.add_trace(go.Scattermapbox(
            lat=sample_data['latitude'],
            lon=sample_data['longitude'],
            mode='markers',
            marker=dict(
                size=6,
                color=sample_data['feasibility_score'],
                colorscale='Viridis',
                colorbar=dict(title="Feasibility Score"),
                cmin=sample_data['feasibility_score'].min(),
                cmax=sample_data['feasibility_score'].max(),
                opacity=0.8
            ),
            text=sample_data['name'],
            name='High Feasibility Sites',
            customdata=np.column_stack((
                sample_data['feasibility_score'],
                sample_data['h2_production_daily'],
                sample_data['capacity'],
                sample_data['system_efficiency']
            )),
            hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Feasibility Score: %{customdata[0]:.3f}<br>" +
                    "H2 Production: %{customdata[1]:.1f} kg/day<br>" +
                    "Total Capacity: %{customdata[2]:.1f} kW<br>" +
                    "System Efficiency: %{customdata[3]:.1f}%<br>" +
                    "<extra></extra>"
            )
        ))

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
                        "Type: " + type_labels.get(infra_type, infra_type) + "<br>" +
                        "<extra></extra>"
                )
            ))

    # Add renewable sources
    if not renewable_data.empty:
        fig.add_trace(go.Scattermapbox(
            lat=renewable_data['latitude'],
            lon=renewable_data['longitude'],
            mode='markers',
            marker=dict(size=8, color=colors['renewable']),
            text=renewable_data['name'],
            name='Renewable Sources',
            customdata=renewable_data['annual_h2_potential'],
            hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "H2 Potential: %{customdata:,.0f} tons/year<br>" +
                    "<extra></extra>"
            )
        ))

    # Add demand centers
    if not demand_data.empty:
        fig.add_trace(go.Scattermapbox(
            lat=demand_data['latitude'],
            lon=demand_data['longitude'],
            mode='markers',
            marker=dict(size=8, color=colors['demand']),
            text=demand_data['name'],
            name='H2 Demand Centers',
            customdata=demand_data['annual_h2_demand'],
            hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Annual Demand: %{customdata:,.0f} tons/year<br>" +
                    "<extra></extra>"
            )
        ))

    # Add optimization results
    if optimization_results:
        opt_df = pd.DataFrame(optimization_results)
        fig.add_trace(go.Scattermapbox(
            lat=opt_df['latitude'],
            lon=opt_df['longitude'],
            mode='markers',
            marker=dict(size=12, color=colors['recommended'],
                        symbol='star'),
            text=opt_df['name'],
            name='AI Recommended Sites',
            customdata=np.column_stack((opt_df['score'], opt_df['estimated_cost'])),
            hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Score: %{customdata[0]:.3f}<br>" +
                    "Investment: $%{customdata[1]:.1f} M<br>" +
                    "<extra></extra>"
            )
        ))

    # Update layout
    fig.update_layout(
        mapbox=dict(
            accesstoken=None,  # Using open street map
            style="open-street-map",
            center=dict(lat=20.5937, lon=78.9629),  # Center of India
            zoom=5
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )

    return fig


def load_real_feasibility_data():
    """Load the real feasibility dataset from Hydro_74K.csv"""
    try:
        # Load the Hydro_74K.csv file
        feasibility_data = pd.read_csv('Hydro_74K.csv')

        # Rename columns to match expected format
        feasibility_data = feasibility_data.rename(columns={
            'City': 'name',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Solar_Irradiance_kWh/m²/day': 'solar_irradiance',
            'Temperature_C': 'temperature',
            'Wind_Speed_m/s': 'wind_speed',
            'PV_Power_kW': 'pv_power',
            'Wind_Power_kW': 'wind_power',
            'Electrolyzer_Efficiency_%': 'electrolyzer_efficiency',
            'Hydrogen_Production_kg/day': 'h2_production_daily',
            'Desalination_Power_kW': 'desalination_power',
            'System_Efficiency_%': 'system_efficiency',
            'Feasibility_Score': 'feasibility_score'
        })

        # Add required columns for integration
        feasibility_data['type'] = 'feasible_site'
        feasibility_data['capacity'] = feasibility_data['pv_power'] + feasibility_data['wind_power']  # Total capacity
        feasibility_data['annual_h2_production'] = feasibility_data['h2_production_daily'] * 365  # Annual production
        feasibility_data['region'] = 'Atlantic'  # Based on coordinates

        return feasibility_data

    except Exception as e:
        st.error(f"Error loading Hydro_74K.csv: {e}")
        return pd.DataFrame()


def main():
    st.title("🌿 Green Hydrogen Infrastructure Mapper & Optimizer")
    st.markdown("""
    **Green hydrogen** is produced using renewable electricity to split water through electrolysis, 
    creating zero-emission hydrogen for industrial applications, transportation, and energy storage.

    **Load the H2 sample data** to explore real feasibility analysis of 74,000+ sites 
    and see AI-powered optimization recommendations.
    """)

    # Sidebar Configuration
    st.sidebar.header("🔬 Data Source Selection")
    use_real_data = st.sidebar.checkbox("Include Real Feasibility Data (74K sites)", value=True)

    # Map type selection
    st.sidebar.subheader("🗺️ Map Display Options")
    map_type = st.sidebar.radio(
        "Choose Map Type:",
        ["📊 Interactive Plotly Map", "🍃 Folium Map (detailed popups)"],
        index=0
    )

    # Show Folium availability status
    if FOLIUM_INTERACTIVE:
        st.sidebar.success("✅ Folium maps available")
    else:
        st.sidebar.warning("⚠️ Folium not available\n`pip install streamlit-folium folium`")

    feasibility_data = pd.DataFrame()
    if use_real_data:
        st.sidebar.info("📊 Using integrated real feasibility data from Hydro_74K.csv")
        feasibility_data = load_real_feasibility_data()

        if not feasibility_data.empty:
            st.sidebar.success(f"✅ Loaded {len(feasibility_data)} feasibility sites")

            # Add feasibility filter
            min_feasibility = st.sidebar.slider(
                "Minimum Feasibility Score",
                min_value=float(feasibility_data['feasibility_score'].min()),
                max_value=float(feasibility_data['feasibility_score'].max()),
                value=0.92,
                step=0.01
            )

            # Filter feasibility data
            feasibility_data = feasibility_data[feasibility_data['feasibility_score'] >= min_feasibility]
            st.sidebar.info(f"🎯 Showing {len(feasibility_data)} sites above {min_feasibility} feasibility score")
        else:
            st.sidebar.error("❌ Could not load Hydro_74K.csv")
            use_real_data = False

    # Initialize components
    data_loader = DataLoader()
    map_builder = MapBuilder()
    optimizer = SiteOptimizer()
    analyzer = CostAnalyzer()
    visualizer = Visualizer()

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Infrastructure Map", "📊 Data Analysis", "🎯 Site Optimization",
        "💰 Cost Analysis", "📈 Visualizations"
    ])

    # Load data
    with st.spinner("Loading hydrogen infrastructure data..."):
        try:
            infrastructure_data = data_loader.load_infrastructure_data()
            renewable_data = data_loader.load_renewable_sources()
            demand_data = data_loader.load_demand_centers()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()

    # TAB 1: Infrastructure Map
    with tab1:
        st.header("🗺️ Green Hydrogen Infrastructure Map")

        # Map options
        col1, col2 = st.columns([2, 1])

        with col2:
            st.subheader("Map Controls")
            show_infrastructure = st.checkbox("Show Infrastructure", value=True)
            show_renewable = st.checkbox("Show Renewable Sources", value=True)
            show_demand = st.checkbox("Show Demand Centers", value=True)
            show_feasibility = st.checkbox("Show Feasibility Sites", value=use_real_data)

            if st.button("🔄 Refresh Map"):
                st.rerun()

        with col1:
            # Display map based on selection
            try:
                if map_type == "📊 Interactive Plotly Map":
                    st.subheader("📍 Interactive Plotly Map")
                    fig = create_plotly_map(
                        infrastructure_data if show_infrastructure else pd.DataFrame(),
                        renewable_data if show_renewable else pd.DataFrame(),
                        demand_data if show_demand else pd.DataFrame(),
                        feasibility_data if show_feasibility else pd.DataFrame()
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif map_type == "🍃 Folium Map (detailed popups)":
                    if FOLIUM_INTERACTIVE:
                        st.subheader("🍃 Interactive Folium Map")
                        # Create Folium map
                        folium_map = map_builder.create_base_map()

                        # Add data layers to Folium map
                        if show_infrastructure and not infrastructure_data.empty:
                            map_builder.add_infrastructure(folium_map, infrastructure_data)

                        if show_renewable and not renewable_data.empty:
                            map_builder.add_renewable_sources(folium_map, renewable_data)

                        if show_demand and not demand_data.empty:
                            map_builder.add_demand_centers(folium_map, demand_data)

                        # Add feasibility sites if enabled
                        if show_feasibility and not feasibility_data.empty:
                            map_builder.add_feasibility_sites(folium_map, feasibility_data, max_sites=50)

                        # Add legend
                        map_builder.add_legend(folium_map)

                        # Display Folium map
                        display_folium_map(folium_map, width=700, height=500)

                    else:
                        st.warning("🍃 Folium not available. Install with: `pip install streamlit-folium folium`")
                        st.info("Falling back to Plotly map...")
                        fig = create_plotly_map(
                            infrastructure_data if show_infrastructure else pd.DataFrame(),
                            renewable_data if show_renewable else pd.DataFrame(),
                            demand_data if show_demand else pd.DataFrame(),
                            feasibility_data if show_feasibility else pd.DataFrame()
                        )
                        st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error creating map: {e}")
                st.info("Displaying basic information instead...")

                if show_infrastructure:
                    st.write("**Infrastructure Data Sample:**")
                    st.dataframe(infrastructure_data.head())

        # Map Statistics
        st.subheader("📊 Map Statistics")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

        with stat_col1:
            st.metric("Infrastructure Sites", len(infrastructure_data))
        with stat_col2:
            st.metric("Renewable Sources", len(renewable_data))
        with stat_col3:
            st.metric("Demand Centers", len(demand_data))
        with stat_col4:
            if use_real_data and not feasibility_data.empty:
                st.metric("High Feasibility Sites", len(feasibility_data))

    # TAB 2: Data Analysis
    with tab2:
        st.header("📊 Data Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Infrastructure Capacity")
            if not infrastructure_data.empty:
                fig = visualizer.create_capacity_chart(infrastructure_data)
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Regional Distribution")
            if not infrastructure_data.empty:
                fig = visualizer.create_regional_distribution(infrastructure_data)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("H2 Demand Analysis")
            if not demand_data.empty:
                fig = visualizer.create_demand_analysis(demand_data)
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Production Methods")
            if not infrastructure_data.empty:
                fig = visualizer.create_h2_production_methods_chart(infrastructure_data)
                st.plotly_chart(fig, use_container_width=True)

        # Feasibility Data Analysis
        if use_real_data and not feasibility_data.empty:
            st.subheader("🎯 Feasibility Analysis (Real Data from Hydro_74K)")

            feas_col1, feas_col2, feas_col3 = st.columns(3)

            with feas_col1:
                st.metric(
                    "Average Feasibility Score",
                    f"{feasibility_data['feasibility_score'].mean():.3f}",
                    f"{feasibility_data['feasibility_score'].std():.3f} std"
                )

            with feas_col2:
                st.metric(
                    "Total H2 Production Potential",
                    f"{feasibility_data['h2_production_daily'].sum():.0f} kg/day"
                )

            with feas_col3:
                st.metric(
                    "Average System Efficiency",
                    f"{feasibility_data['system_efficiency'].mean():.1f}%"
                )

            # Feasibility distribution chart
            fig = px.histogram(
                feasibility_data,
                x='feasibility_score',
                nbins=50,
                title='Distribution of Feasibility Scores',
                labels={'feasibility_score': 'Feasibility Score', 'count': 'Number of Sites'},
                color_discrete_sequence=['#2E8B57'],
                opacity=0.8
            )
            fig.update_layout(
                xaxis_title="Feasibility Score",
                yaxis_title="Number of Sites",
                title_x=0.5,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

    # TAB 3: Site Optimization
    with tab3:
        st.header("🎯 Site Optimization")

        # Optimization parameters
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Optimization Parameters")
            budget = st.slider("Budget (Million $)", 500, 5000, 2000, 100)
            max_projects = st.slider("Max Projects", 3, 20, 8)

            st.subheader("Priority Weights")
            weight_cost = st.slider("Cost Weight", 0.0, 1.0, 0.3, 0.1)
            weight_renewable = st.slider("Renewable Access Weight", 0.0, 1.0, 0.4, 0.1)
            weight_demand = st.slider("Demand Proximity Weight", 0.0, 1.0, 0.3, 0.1)

            optimize_button = st.button("🚀 Run Optimization", type="primary")

        with col2:
            if optimize_button:
                with st.spinner("Running AI optimization..."):
                    try:
                        params = {
                            'budget': budget,
                            'max_projects': max_projects,
                            'weights': {
                                'cost': weight_cost,
                                'renewable': weight_renewable,
                                'demand': weight_demand
                            }
                        }

                        optimization_results = optimizer.optimize_sites(
                            infrastructure_data, renewable_data, demand_data, params
                        )

                        if optimization_results:
                            st.success(f"✅ Optimization complete! Found {len(optimization_results)} optimal sites")

                            # Store results in session state
                            st.session_state.optimization_results = optimization_results

                            # Display results
                            st.subheader("🏆 Optimization Results")
                            results_df = pd.DataFrame(optimization_results)
                            st.dataframe(
                                results_df[['name', 'score', 'estimated_cost', 'capacity']].round(3),
                                use_container_width=True
                            )

                            # Show optimized map
                            st.subheader("🗺️ Optimized Sites Map")
                            fig = create_plotly_map(
                                infrastructure_data, renewable_data, demand_data,
                                feasibility_data if use_real_data else None,
                                optimization_results
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            # Priority ranking chart
                            fig = visualizer.create_priority_ranking(optimization_results)
                            st.plotly_chart(fig, use_container_width=True)

                        else:
                            st.warning("No optimal sites found with current parameters")

                    except Exception as e:
                        st.error(f"Optimization error: {e}")
                        st.info("Please check your parameters and try again")
            else:
                st.info("👈 Set parameters and click 'Run Optimization' to find optimal H2 sites")

    # TAB 4: Cost Analysis
    with tab4:
        st.header("💰 Cost Analysis")

        # Check if optimization results exist
        if hasattr(st.session_state, 'optimization_results') and st.session_state.optimization_results:
            optimization_results = st.session_state.optimization_results

            col1, col2 = st.columns(2)

            with col1:
                # Cost breakdown
                cost_breakdown = analyzer.calculate_cost_breakdown(optimization_results)
                fig = visualizer.create_cost_breakdown_chart(cost_breakdown)
                st.plotly_chart(fig, use_container_width=True)

                # Investment timeline
                timeline_data = analyzer.create_investment_timeline(optimization_results)
                fig = visualizer.create_timeline_chart(timeline_data)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # ROI analysis
                roi_analysis = analyzer.calculate_roi_analysis(optimization_results)
                fig = visualizer.create_roi_chart(roi_analysis)
                st.plotly_chart(fig, use_container_width=True)

                # Risk assessment
                st.subheader("⚠️ Risk Assessment")
                risks = analyzer.assess_risks(optimization_results)
                risks_df = pd.DataFrame(risks)
                st.dataframe(risks_df, use_container_width=True)

        else:
            st.info("📈 Run optimization first to see cost analysis")
            st.markdown("""
            The cost analysis will show:
            - **Investment breakdown** by category
            - **ROI analysis** over 20 years  
            - **Implementation timeline**
            - **Risk assessment** matrix
            """)

    # TAB 5: Visualizations
    with tab5:
        st.header("📈 Advanced Visualizations")

        viz_col1, viz_col2 = st.columns(2)

        with viz_col1:
            st.subheader("Renewable H2 Potential")
            fig = visualizer.create_renewable_potential_chart(renewable_data)
            st.plotly_chart(fig, use_container_width=True)

            # Additional feasibility correlation chart
            if use_real_data and not feasibility_data.empty:
                st.subheader("System Efficiency vs H2 Production")
                fig = px.scatter(
                    feasibility_data,
                    x='system_efficiency',
                    y='h2_production_daily',
                    size='capacity',
                    color='feasibility_score',
                    hover_data=['name'],
                    title='System Efficiency vs Daily H2 Production',
                    labels={
                        'system_efficiency': 'System Efficiency (%)',
                        'h2_production_daily': 'H2 Production (kg/day)',
                        'feasibility_score': 'Feasibility Score'
                    },
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)

        with viz_col2:
            if use_real_data and not feasibility_data.empty:
                st.subheader("Feasibility Score vs H2 Production")
                fig = px.scatter(
                    feasibility_data,
                    x='feasibility_score',
                    y='h2_production_daily',
                    size='capacity',
                    color='system_efficiency',
                    hover_data=['name'],
                    title='Feasibility Score vs H2 Production Potential',
                    labels={
                        'feasibility_score': 'Feasibility Score',
                        'h2_production_daily': 'H2 Production (kg/day)',
                        'system_efficiency': 'System Efficiency (%)'
                    },
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Solar vs Wind Power Distribution")
                # Create solar vs wind power scatter plot
                fig = px.scatter(
                    feasibility_data,
                    x='pv_power',
                    y='wind_power',
                    size='h2_production_daily',
                    color='feasibility_score',
                    hover_data=['name', 'temperature', 'wind_speed'],
                    title='Solar vs Wind Power Capacity Distribution',
                    labels={
                        'pv_power': 'Solar PV Power (kW)',
                        'wind_power': 'Wind Power (kW)',
                        'feasibility_score': 'Feasibility Score'
                    },
                    color_continuous_scale='Plasma'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Enable feasibility data to see additional visualizations")

    # Footer
    st.markdown("---")
    st.markdown("""
    **🌿 Green Hydrogen Infrastructure Mapper & Optimizer**  
    *Powered by real feasibility data from 74,000+ analyzed sites*

    📊 **Features:**
    - Interactive infrastructure mapping (Plotly + Folium)
    - AI-powered site optimization  
    - Real feasibility analysis integration
    - Cost and ROI modeling
    - Risk assessment
    """)


if __name__ == "__main__":
    main()
