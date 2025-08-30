import pandas as pd
import numpy as np
from typing import Dict, List


class CostAnalyzer:
    def __init__(self):
        self.cost_categories = [
            'Construction', 'Equipment', 'Grid Connection',
            'Transport Infrastructure', 'Land Acquisition',
            'Permits & Licensing', 'Contingency'
        ]

    def calculate_cost_breakdown(self, optimization_results: List[Dict]) -> Dict:
        """Calculate detailed cost breakdown for optimized sites"""

        total_investment = sum([site['estimated_cost'] for site in optimization_results])

        # Cost breakdown percentages (typical for hydrogen projects)
        breakdown = {
            'Construction': 0.35,
            'Equipment': 0.25,
            'Grid Connection': 0.15,
            'Transport Infrastructure': 0.10,
            'Land Acquisition': 0.05,
            'Permits & Licensing': 0.05,
            'Contingency': 0.05
        }

        cost_breakdown = {}
        for category, percentage in breakdown.items():
            cost_breakdown[category] = total_investment * percentage

        return cost_breakdown

    def calculate_roi_analysis(self, optimization_results: List[Dict]) -> Dict:
        """Calculate ROI analysis for the portfolio"""

        total_investment = sum([site['estimated_cost'] for site in optimization_results])
        weighted_roi = sum([site['roi'] * site['estimated_cost'] for site in optimization_results]) / total_investment

        # Generate ROI timeline (simplified)
        years = list(range(1, 21))  # 20-year analysis
        cumulative_returns = []
        annual_returns = []

        for year in years:
            if year <= 3:  # Construction phase
                annual_return = -total_investment / 3
            else:
                annual_return = total_investment * (weighted_roi / 100)

            annual_returns.append(annual_return)

            if year == 1:
                cumulative_returns.append(annual_return)
            else:
                cumulative_returns.append(cumulative_returns[-1] + annual_return)

        return {
            'years': years,
            'annual_returns': annual_returns,
            'cumulative_returns': cumulative_returns,
            'total_investment': total_investment,
            'weighted_roi': weighted_roi
        }

    def create_investment_timeline(self, optimization_results: List[Dict]) -> pd.DataFrame:
        """Create investment timeline for implementation"""

        timeline_data = []

        for site in optimization_results:
            # Spread investment over implementation time
            monthly_investment = site['estimated_cost'] / site['implementation_time']

            for month in range(1, site['implementation_time'] + 1):
                timeline_data.append({
                    'Month': month,
                    'Site': site['name'],
                    'Investment': monthly_investment,
                    'Cumulative': monthly_investment * month,
                    'Phase': 'Construction' if month <= site['implementation_time'] * 0.8 else 'Commissioning'
                })

        return pd.DataFrame(timeline_data)

    def assess_risks(self, optimization_results: List[Dict]) -> List[Dict]:
        """Assess risks for the project portfolio"""

        risks = []

        # Portfolio-level risks
        total_investment = sum([site['estimated_cost'] for site in optimization_results])
        avg_regulatory_score = np.mean([site['regulatory_score'] for site in optimization_results])
        avg_environmental_score = np.mean([site['environmental_score'] for site in optimization_results])

        risks.append({
            'Risk Category': 'Regulatory Risk',
            'Risk Level': 'Low' if avg_regulatory_score > 0.8 else 'Medium' if avg_regulatory_score > 0.6 else 'High',
            'Impact': f'${total_investment * 0.1:.1f}M potential delay cost',
            'Mitigation': 'Early stakeholder engagement, regulatory pre-approval'
        })

        risks.append({
            'Risk Category': 'Environmental Risk',
            'Risk Level': 'Low' if avg_environmental_score > 0.8 else 'Medium' if avg_environmental_score > 0.6 else 'High',
            'Impact': f'${total_investment * 0.05:.1f}M additional compliance cost',
            'Mitigation': 'Comprehensive EIA, community engagement'
        })

        risks.append({
            'Risk Category': 'Market Risk',
            'Risk Level': 'Medium',
            'Impact': '±20% demand variation',
            'Mitigation': 'Long-term offtake agreements, diversified customer base'
        })

        risks.append({
            'Risk Category': 'Technology Risk',
            'Risk Level': 'Low',
            'Impact': '5-10% efficiency variation',
            'Mitigation': 'Proven technology, performance guarantees'
        })

        risks.append({
            'Risk Category': 'Financial Risk',
            'Risk Level': 'Medium',
            'Impact': f'${total_investment * 0.15:.1f}M cost overrun potential',
            'Mitigation': 'Fixed-price contracts, contingency reserves'
        })

        return risks
