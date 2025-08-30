import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List


class Visualizer:
    def __init__(self):
        # H2-themed color palette
        self.h2_color_palette = [
            '#2E8B57', '#228B22', '#32CD32', '#90EE90',
            '#4682B4', '#87CEEB', '#FFA500', '#FF69B4'
        ]

    def create_h2_capacity_chart(self, infrastructure_data: pd.DataFrame) -> go.Figure:
        """Create H2-specific capacity distribution chart"""

        # Group by H2 facility type
        capacity_by_type = infrastructure_data.groupby('type')['capacity'].sum().reset_index()

        # H2-specific type labels
        type_labels = {
            'existing_plant': 'Existing H2 Plants',
            'planned_plant': 'Planned H2 Megaplants',
            'storage': 'H2 Storage Hubs'
        }

        capacity_by_type['h2_type'] = capacity_by_type['type'].map(type_labels)
        capacity_by_type = capacity_by_type.dropna()

        fig = px.bar(
            capacity_by_type,
            x='h2_type',
            y='capacity',
            title='🌿 Hydrogen Infrastructure Capacity Distribution',
            labels={'capacity': 'H2 Capacity (MW)', 'h2_type': 'H2 Facility Type'},
            color='h2_type',
            color_discrete_sequence=['#2E8B57', '#228B22', '#4682B4']
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="H2 Infrastructure Type",
            yaxis_title="H2 Production Capacity (MW)",
            title_x=0.5
        )

        return fig

    def create_h2_demand_analysis(self, demand_data: pd.DataFrame) -> go.Figure:
        """Create H2-specific demand analysis chart"""

        demand_column = 'annual_h2_demand' if 'annual_h2_demand' in demand_data.columns else 'annual_demand'

        h2_demand_by_industry = demand_data.groupby('industry')[demand_column].sum().reset_index()
        h2_demand_by_industry = h2_demand_by_industry.sort_values(demand_column, ascending=True)

        fig = px.bar(
            h2_demand_by_industry,
            x=demand_column,
            y='industry',
            orientation='h',
            title='🏭 Annual Hydrogen Demand by Industry',
            labels={demand_column: 'Annual H2 Demand (tons/year)', 'industry': 'H2 Industry'},
            color=demand_column,
            color_continuous_scale='Viridis'
        )

        fig.update_layout(
            xaxis_title="Annual H2 Demand (tons/year)",
            yaxis_title="H2 Industry Sector",
            title_x=0.5
        )

        return fig

    def create_h2_production_methods_chart(self, infrastructure_data: pd.DataFrame) -> go.Figure:
        """Create chart showing H2 production methods"""

        if 'production_type' not in infrastructure_data.columns:
            # Create mock data if column doesn't exist
            mock_data = pd.DataFrame({
                'production_method': ['Green H2', 'Blue H2', 'Bio H2'],
                'count': [12, 6, 2]
            })

            fig = px.pie(
                mock_data,
                values='count',
                names='production_method',
                title='🌱 Hydrogen Production Methods Distribution',
                color='production_method',
                color_discrete_map={'Green H2': '#2E8B57', 'Blue H2': '#4682B4', 'Bio H2': '#DAA520'}
            )
        else:
            production_count = infrastructure_data['production_type'].value_counts().reset_index()
            production_count.columns = ['production_method', 'count']

            # H2 production method colors
            colors = {'Green': '#2E8B57', 'Blue': '#4682B4', 'Bio': '#DAA520', 'Grey': '#808080'}

            fig = px.pie(
                production_count,
                values='count',
                names='production_method',
                title='🌱 Hydrogen Production Methods Distribution',
                color='production_method',
                color_discrete_map=colors
            )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(title_x=0.5)

        return fig

    def create_renewable_h2_potential_chart(self, renewable_data: pd.DataFrame) -> go.Figure:
        """Create renewable H2 potential chart"""

        # Check for H2 potential columns
        h2_potential_col = None
        for col in ['annual_h2_potential', 'potential_h2_production']:
            if col in renewable_data.columns:
                h2_potential_col = col
                break

        if h2_potential_col is None:
            # Create mock data
            mock_data = pd.DataFrame({
                'renewable_type': ['Solar-to-H2', 'Wind-to-H2', 'Hydro-to-H2'],
                'h2_potential': [45000, 38000, 12000]
            })

            fig = px.bar(
                mock_data,
                x='renewable_type',
                y='h2_potential',
                title='⚡ Annual H2 Production Potential by Renewable Source',
                labels={'h2_potential': 'H2 Production Potential (tons/year)',
                        'renewable_type': 'Renewable-to-H2 Technology'},
                color='renewable_type',
                color_discrete_sequence=['#FFA500', '#87CEEB', '#4682B4']
            )
        else:
            h2_potential_by_type = renewable_data.groupby('type')[h2_potential_col].sum().reset_index()
            h2_potential_by_type['renewable_type'] = h2_potential_by_type['type'].str.title() + '-to-H2'

            fig = px.bar(
                h2_potential_by_type,
                x='renewable_type',
                y=h2_potential_col,
                title='⚡ Annual H2 Production Potential by Renewable Source',
                labels={h2_potential_col: 'H2 Production Potential (tons/year)',
                        'renewable_type': 'Renewable-to-H2 Technology'},
                color='renewable_type',
                color_discrete_sequence=['#FFA500', '#87CEEB', '#4682B4']
            )

        fig.update_layout(
            showlegend=False,
            xaxis_title="Renewable-to-H2 Technology",
            yaxis_title="H2 Production Potential (tons/year)",
            title_x=0.5
        )

        return fig

    def create_capacity_chart(self, infrastructure_data: pd.DataFrame) -> go.Figure:
        """Wrapper method for backward compatibility"""
        return self.create_h2_capacity_chart(infrastructure_data)

    def create_demand_analysis(self, demand_data: pd.DataFrame) -> go.Figure:
        """Wrapper method for backward compatibility"""
        return self.create_h2_demand_analysis(demand_data)

    def create_regional_distribution(self, infrastructure_data: pd.DataFrame) -> go.Figure:
        """Create H2 regional distribution pie chart"""

        regional_count = infrastructure_data['region'].value_counts().reset_index()
        regional_count.columns = ['region', 'count']

        fig = px.pie(
            regional_count,
            values='count',
            names='region',
            title='🗺️ H2 Infrastructure Distribution by Region',
            color_discrete_sequence=self.h2_color_palette
        )

        fig.update_layout(title_x=0.5)
        return fig

    def create_renewable_potential_chart(self, renewable_data: pd.DataFrame) -> go.Figure:
        """Wrapper method for backward compatibility"""
        return self.create_renewable_h2_potential_chart(renewable_data)

    def create_priority_ranking(self, optimization_results: List[Dict]) -> go.Figure:
        """Create H2 site priority ranking chart"""

        df = pd.DataFrame(optimization_results)
        df = df.sort_values('score', ascending=True)

        fig = px.bar(
            df,
            x='score',
            y='name',
            orientation='h',
            title='🏆 H2 Site Optimization Scores',
            labels={'score': 'Optimization Score', 'name': 'Recommended H2 Site'},
            color='score',
            color_continuous_scale='RdYlGn'
        )

        fig.update_layout(
            xaxis_title="H2 Site Optimization Score",
            yaxis_title="Recommended H2 Production Sites",
            title_x=0.5,
            height=max(400, len(optimization_results) * 40)
        )

        return fig

    def create_cost_breakdown_chart(self, cost_breakdown: Dict) -> go.Figure:
        """Create H2 investment cost breakdown chart"""

        categories = list(cost_breakdown.keys())
        values = list(cost_breakdown.values())

        fig = px.pie(
            values=values,
            names=categories,
            title='💰 H2 Infrastructure Investment Breakdown',
            color_discrete_sequence=self.h2_color_palette
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(title_x=0.5)

        return fig

    def create_roi_chart(self, roi_analysis: Dict) -> go.Figure:
        """Create H2 project ROI analysis chart"""

        fig = go.Figure()

        # Add annual H2 returns
        fig.add_trace(go.Scatter(
            x=roi_analysis['years'],
            y=[x / 1e6 for x in roi_analysis['annual_returns']],
            mode='lines+markers',
            name='Annual H2 Returns',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=6)
        ))

        # Add cumulative H2 returns
        fig.add_trace(go.Scatter(
            x=roi_analysis['years'],
            y=[x / 1e6 for x in roi_analysis['cumulative_returns']],
            mode='lines+markers',
            name='Cumulative H2 Returns',
            line=dict(color='#4682B4', width=3),
            marker=dict(size=6),
            yaxis='y2'
        ))

        # Add break-even line
        fig.add_hline(y=0, line_dash="dash", line_color="red",
                      annotation_text="H2 Break-even", annotation_position="bottom right")

        fig.update_layout(
            title='📈 H2 Project Return on Investment Analysis',
            xaxis_title='Years',
            yaxis=dict(title='Annual H2 Returns ($M)', side='left'),
            yaxis2=dict(title='Cumulative H2 Returns ($M)', side='right', overlaying='y'),
            title_x=0.5,
            hovermode='x unified',
            legend=dict(x=0.02, y=0.98)
        )

        return fig

    def create_timeline_chart(self, timeline_data: pd.DataFrame) -> go.Figure:
        """Create H2 investment timeline chart"""

        monthly_investment = timeline_data.groupby('Month')['Investment'].sum().reset_index()

        fig = px.area(
            monthly_investment,
            x='Month',
            y='Investment',
            title='📅 H2 Infrastructure Investment Timeline',
            labels={'Investment': 'Monthly H2 Investment ($M)', 'Month': 'Implementation Month'},
            color_discrete_sequence=['#2E8B57']
        )

        fig.update_layout(
            xaxis_title="Implementation Timeline (Months)",
            yaxis_title="Monthly H2 Investment ($M)",
            title_x=0.5,
            showlegend=False
        )

        return fig
