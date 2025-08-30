import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from pulp import LpProblem, LpMaximize, LpVariable, PULP_CBC_CMD

class SiteOptimizer:
    def __init__(self):
        self.candidate_sites = self._generate_candidate_sites()

    def _generate_candidate_sites(self):
        np.random.seed(45)
        candidates = []
        for i in range(50):  # Generate 50 candidate sites with random attributes
            candidates.append({
                'id': f'candidate_{i}',
                'name': f'Candidate Site {i+1}',
                'latitude': 20 + np.random.uniform(-15, 15),
                'longitude': 77 + np.random.uniform(-20, 20),
                'land_cost': np.random.uniform(5, 50),  # $/sq meter
                'grid_access': np.random.choice([True, False]),
                'transport_score': np.random.uniform(0.3, 1.0),
                'regulatory_score': np.random.uniform(0.4, 1.0),
                'environmental_score': np.random.uniform(0.5, 1.0)
            })
        return candidates

    def optimize_sites(self, infrastructure_data: pd.DataFrame, renewable_data: pd.DataFrame,
                       demand_data: pd.DataFrame, params: dict):
        # Determine correct demand column to use
        demand_cols = ['annual_hydrogen_demand', 'annual_hydrogen', 'annual_h2_demand', 'annual_demand']
        demand_col = None
        for c in demand_cols:
            if c in demand_data.columns:
                demand_col = c
                break
        if not demand_col:
            raise KeyError(f"Demand DataFrame missing required demand column (checked {demand_cols})")

        demand_coords = demand_data[['latitude', 'longitude']].values
        demand_weights = demand_data[demand_col].values

        renewable_coords = renewable_data[['latitude', 'longitude']].values

        infra_coords = infrastructure_data[['latitude', 'longitude']].values if not infrastructure_data.empty else np.array([])

        scored_candidates = []

        for site in self.candidate_sites:
            site_coords = np.array([[site['latitude'], site['longitude']]])

            # Distance to renewables (km)
            renewable_dists = cdist(site_coords, renewable_coords) * 111
            min_renew_dist = renewable_dists.min() if len(renewable_dists) > 0 else 1000
            renewable_score = max(0, 1 - min_renew_dist / params.get('max_distance_renewable', 100))

            # Weighted proximity to demand centers
            demand_dists = cdist(site_coords, demand_coords) * 111
            weighted_demand = np.sum(demand_weights / (1 + demand_dists))
            demand_score = weighted_demand / demand_weights.sum() if demand_weights.sum() > 0 else 0

            # Estimated cost proxy
            base_cost = 200  # M$
            grid_cost = 0 if site['grid_access'] else 50
            transport_cost = (1 - site['transport_score']) * 100
            connection_cost = min_renew_dist * 2  # $2M/km approx
            land_cost = site['land_cost'] * 10

            total_estimated_cost = base_cost + grid_cost + transport_cost + connection_cost + land_cost
            cost_score = max(0, 1 - total_estimated_cost / 1000)  # Normalize assuming 1000M max

            # Infrastructure synergy score
            if infra_coords.size > 0:
                infra_dists = cdist(site_coords, infra_coords) * 111
                min_infra_dist = infra_dists.min()
            else:
                min_infra_dist = 1000
            synergy_score = max(0, 1 - min_infra_dist / 100)

            # Combine scores with weights
            weights = params.get('weights', {'cost': 0.3, 'renewable': 0.4, 'demand': 0.3})
            total_score = (
                weights['cost'] * cost_score +
                weights['renewable'] * renewable_score +
                weights['demand'] * demand_score +
                0.1 * synergy_score +
                0.05 * site['regulatory_score'] +
                0.05 * site['environmental_score']
            )

            if total_score > 0.2:  # Minimum viable score threshold
                scored_candidates.append({
                    'id': site['id'],
                    'name': site['name'],
                    'latitude': site['latitude'],
                    'longitude': site['longitude'],
                    'score': total_score,
                    'cost_score': cost_score,
                    'renewable_score': renewable_score,
                    'demand_score': demand_score,
                    'synergy_score': synergy_score,
                    'regulatory_score': site['regulatory_score'],
                    'environmental_score': site['environmental_score'],
                    'estimated_cost': total_estimated_cost,
                    'distance_to_renewable': min_renew_dist,
                    'transport_score': site['transport_score'],
                    'capacity': np.random.uniform(100, 500),  # MW, mock capacity
                    'implementation_time': np.random.randint(24, 48),  # months mock
                    'roi': 5 + total_score * 20,  # % ROI mockup
                    'supply_radius': 75000  # meters, 75 km coverage mock
                })

        # Sort candidates by descending score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)

        # Optimization problem to select best sites under budget and max_projects constraints
        prob = LpProblem("H2_Site_Selection", LpMaximize)
        x = [LpVariable(f"x_{i}", cat='Binary') for i in range(len(scored_candidates))]

        prob += sum(x[i] * scored_candidates[i]['score'] for i in range(len(scored_candidates))), "Maximize_Total_Score"
        prob += sum(x[i] * scored_candidates[i]['estimated_cost'] for i in range(len(scored_candidates))) <= params.get('budget', 1000), "BudgetConstraint"
        prob += sum(x) <= params.get('max_projects', 10), "MaxProjectsConstraint"

        prob.solve(PULP_CBC_CMD(msg=0))

        selected_sites = []
        rank = 1
        for i, decision_var in enumerate(x):
            if decision_var.varValue == 1:
                candidate = scored_candidates[i]
                candidate['rank'] = rank
                selected_sites.append(candidate)
                rank += 1

        return selected_sites
