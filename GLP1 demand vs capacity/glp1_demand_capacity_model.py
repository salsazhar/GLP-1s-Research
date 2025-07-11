import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class GLP1DemandCapacityModel:
    """
    GLP-1 Demand vs Peptide Manufacturing Capacity Gap Analysis Model
    
    This model analyzes the growing gap between GLP-1 drug demand and peptide 
    manufacturing capacity, projecting supply-demand imbalances through 2030.
    """
    
    def __init__(self, input_data_path):
        """Initialize model with input data"""
        self.input_data = pd.read_csv(input_data_path)
        self.load_parameters()
        
    def load_parameters(self):
        """Load and organize model parameters from input data"""
        # Historical demand data
        historical_demand = self.input_data[self.input_data['data_type'] == 'historical_demand']
        self.historical_demand = dict(zip(historical_demand['parameter'], historical_demand['value']))
        
        # Capacity data
        capacity_actual = self.input_data[self.input_data['data_type'] == 'capacity_actual']
        capacity_target = self.input_data[self.input_data['data_type'] == 'capacity_target']
        self.capacity_2024 = capacity_actual['value'].iloc[0]
        self.capacity_2030_target = capacity_target['value'].iloc[0]
        
        # Model configuration - handle empty parameter values
        baseline_year_data = self.input_data[self.input_data['parameter'] == 'baseline_year']
        projection_end_data = self.input_data[self.input_data['parameter'] == 'projection_end_year']
        
        if not baseline_year_data.empty:
            self.baseline_year = int(baseline_year_data['value'].iloc[0])
        else:
            self.baseline_year = 2024
            
        if not projection_end_data.empty:
            self.projection_end_year = int(projection_end_data['value'].iloc[0])
        else:
            self.projection_end_year = 2030
        
        # Baseline values - handle empty parameter values
        demand_baseline_data = self.input_data[self.input_data['parameter'] == 'demand_baseline_pct']
        capacity_baseline_data = self.input_data[self.input_data['parameter'] == 'capacity_baseline_billions']
        max_penetration_data = self.input_data[self.input_data['parameter'] == 'max_penetration_pct']
        
        if not demand_baseline_data.empty:
            self.demand_baseline_pct = demand_baseline_data['value'].iloc[0]
        else:
            self.demand_baseline_pct = 4.0
            
        if not capacity_baseline_data.empty:
            self.capacity_baseline_billions = capacity_baseline_data['value'].iloc[0]
        else:
            self.capacity_baseline_billions = 117.26
            
        if not max_penetration_data.empty:
            self.max_penetration_pct = max_penetration_data['value'].iloc[0]
        else:
            self.max_penetration_pct = 25.0
        
        # Scenario CAGR parameters
        demand_cagrs = self.input_data[self.input_data['data_type'].str.contains('demand_cagr', na=False)]
        capacity_cagrs = self.input_data[self.input_data['data_type'].str.contains('capacity_cagr', na=False)]
        
        self.scenarios = {}
        for _, row in demand_cagrs.iterrows():
            scenario = row['data_type'].split('_')[-1]
            capacity_cagr_data = capacity_cagrs[capacity_cagrs['data_type'] == f'capacity_cagr_{scenario}']
            
            if not capacity_cagr_data.empty:
                capacity_cagr_value = capacity_cagr_data['value'].iloc[0]
            else:
                # Default capacity CAGR if not found
                capacity_cagr_value = 0.14
                
            self.scenarios[scenario] = {
                'demand_cagr': row['value'],
                'capacity_cagr': capacity_cagr_value
            }
    
    def calculate_future_value(self, baseline_value, cagr, years_elapsed):
        """Calculate future value using compound annual growth rate"""
        return baseline_value * ((1 + cagr) ** years_elapsed)
    
    def calculate_index(self, future_value, baseline_value):
        """Calculate index relative to baseline (baseline = 100)"""
        return (future_value / baseline_value) * 100
    
    def apply_market_constraints(self, projected_demand_pct, year):
        """Apply market saturation constraints"""
        years_from_baseline = year - self.baseline_year
        max_demand = self.max_penetration_pct
        
        # Apply saturation ceiling if projected demand exceeds biological/market limits
        if projected_demand_pct > max_demand:
            return max_demand
        return projected_demand_pct
    
    def generate_projections(self):
        """Generate projections for all scenarios and years"""
        results = []
        
        for scenario_name, scenario_params in self.scenarios.items():
            demand_cagr = scenario_params['demand_cagr']
            capacity_cagr = scenario_params['capacity_cagr']
            
            for year in range(self.baseline_year, self.projection_end_year + 1):
                years_elapsed = year - self.baseline_year
                
                # Calculate projected demand (percentage of adults)
                projected_demand_pct = self.calculate_future_value(
                    self.demand_baseline_pct, demand_cagr, years_elapsed
                )
                
                # Apply market constraints
                constrained_demand_pct = self.apply_market_constraints(projected_demand_pct, year)
                
                # Calculate demand index (2024 = 100)
                demand_index = self.calculate_index(constrained_demand_pct, self.demand_baseline_pct)
                
                # Calculate projected capacity (billions USD)
                projected_capacity_billions = self.calculate_future_value(
                    self.capacity_baseline_billions, capacity_cagr, years_elapsed
                )
                
                # Calculate capacity index (2024 = 100)
                capacity_index = self.calculate_index(projected_capacity_billions, self.capacity_baseline_billions)
                
                # Calculate gap ratio
                gap_ratio = demand_index / capacity_index if capacity_index > 0 else float('inf')
                
                # Determine gap severity
                gap_severity = self.classify_gap_severity(gap_ratio)
                
                results.append({
                    'scenario': scenario_name,
                    'year': year,
                    'years_elapsed': years_elapsed,
                    'demand_cagr': demand_cagr,
                    'capacity_cagr': capacity_cagr,
                    'projected_demand_pct': projected_demand_pct,
                    'constrained_demand_pct': constrained_demand_pct,
                    'demand_index': demand_index,
                    'projected_capacity_billions': projected_capacity_billions,
                    'capacity_index': capacity_index,
                    'gap_ratio': gap_ratio,
                    'gap_severity': gap_severity,
                    'cagr_differential': demand_cagr - capacity_cagr
                })
        
        return pd.DataFrame(results)
    
    def classify_gap_severity(self, gap_ratio):
        """Classify the severity of the demand-capacity gap"""
        if gap_ratio >= 10:
            return 'Critical (10x+)'
        elif gap_ratio >= 5:
            return 'Severe (5x-10x)'
        elif gap_ratio >= 3:
            return 'Moderate (3x-5x)'
        elif gap_ratio >= 2:
            return 'Concerning (2x-3x)'
        elif gap_ratio >= 1.5:
            return 'Watch (1.5x-2x)'
        else:
            return 'Balanced (<1.5x)'
    
    def generate_summary_statistics(self, projections_df):
        """Generate summary statistics for key metrics"""
        summary_stats = []
        
        for scenario in self.scenarios.keys():
            scenario_data = projections_df[projections_df['scenario'] == scenario]
            
            # Key years to track
            key_years = [2025, 2027, 2030]
            
            for year in key_years:
                year_data = scenario_data[scenario_data['year'] == year]
                if not year_data.empty:
                    summary_stats.append({
                        'scenario': scenario,
                        'year': year,
                        'gap_ratio': year_data['gap_ratio'].iloc[0],
                        'gap_severity': year_data['gap_severity'].iloc[0],
                        'demand_index': year_data['demand_index'].iloc[0],
                        'capacity_index': year_data['capacity_index'].iloc[0],
                        'cagr_differential': year_data['cagr_differential'].iloc[0]
                    })
        
        return pd.DataFrame(summary_stats)
    
    def run_model(self):
        """Run the complete model and return results"""
        print("Running GLP-1 Demand vs Capacity Gap Analysis Model...")
        print(f"Baseline Year: {self.baseline_year}")
        print(f"Projection End Year: {self.projection_end_year}")
        print(f"Scenarios: {list(self.scenarios.keys())}")
        print()
        
        # Generate projections
        projections = self.generate_projections()
        
        # Generate summary statistics
        summary = self.generate_summary_statistics(projections)
        
        return projections, summary
    
    def save_results(self, projections_df, summary_df, output_dir):
        """Save results to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed projections
        projections_file = f"{output_dir}/glp1_projections_{timestamp}.csv"
        projections_df.to_csv(projections_file, index=False)
        print(f"Detailed projections saved to: {projections_file}")
        
        # Save summary statistics
        summary_file = f"{output_dir}/glp1_summary_{timestamp}.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"Summary statistics saved to: {summary_file}")
        
        return projections_file, summary_file

def main():
    """Main function to run the model"""
    # File paths
    input_file = "GLP1s_ Demand vs Capacity  - model_input_data.csv"
    output_dir = "."
    
    # Initialize and run model
    model = GLP1DemandCapacityModel(input_file)
    projections, summary = model.run_model()
    
    # Save results
    projections_file, summary_file = model.save_results(projections, summary, output_dir)
    
    # Print key insights
    print("\n" + "="*60)
    print("KEY MODEL INSIGHTS")
    print("="*60)
    
    for scenario in model.scenarios.keys():
        scenario_data = projections[projections['scenario'] == scenario]
        final_year_data = scenario_data[scenario_data['year'] == 2030].iloc[0]
        
        print(f"\n{scenario.upper()} SCENARIO (2030):")
        print(f"  Gap Ratio: {final_year_data['gap_ratio']:.1f}x")
        print(f"  Gap Severity: {final_year_data['gap_severity']}")
        print(f"  Demand Index: {final_year_data['demand_index']:.0f}")
        print(f"  Capacity Index: {final_year_data['capacity_index']:.0f}")
        print(f"  CAGR Differential: {final_year_data['cagr_differential']:.1%}")
    
    print(f"\nResults saved to:")
    print(f"  - Detailed projections: {projections_file}")
    print(f"  - Summary statistics: {summary_file}")

if __name__ == "__main__":
    main() 