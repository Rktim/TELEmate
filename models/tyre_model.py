"""
Tyre Degradation Model
Advanced tyre wear simulation based on multiple factors
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import warnings
warnings.filterwarnings('ignore')

class TyreDegradationModel:
    def __init__(self):
        # Tyre compound characteristics
        self.compound_properties = {
            'SOFT': {
                'base_grip': 1.0,
                'degradation_rate': 0.15,
                'peak_laps': 3,
                'optimal_temp': 25,
                'temp_sensitivity': 0.02,
                'wear_factor': 1.2,
                'color': 'red'
            },
            'MEDIUM': {
                'base_grip': 0.95,
                'degradation_rate': 0.10,
                'peak_laps': 5,
                'optimal_temp': 30,
                'temp_sensitivity': 0.015,
                'wear_factor': 1.0,
                'color': 'yellow'
            },
            'HARD': {
                'base_grip': 0.90,
                'degradation_rate': 0.07,
                'peak_laps': 8,
                'optimal_temp': 35,
                'temp_sensitivity': 0.01,
                'wear_factor': 0.8,
                'color': 'white'
            },
            'INTERMEDIATE': {
                'base_grip': 0.85,
                'degradation_rate': 0.12,
                'optimal_temp': 20,
                'temp_sensitivity': 0.025,
                'wear_factor': 1.1,
                'color': 'green'
            },
            'WET': {
                'base_grip': 0.80,
                'degradation_rate': 0.14,
                'optimal_temp': 15,
                'temp_sensitivity': 0.03,
                'wear_factor': 1.3,
                'color': 'blue'
            }
        }
        
        # Track characteristics
        self.track_properties = {
            'Monaco': {
                'abrasion': 0.8,
                'cornering_intensity': 0.9,
                'braking_zones': 0.7,
                'acceleration_zones': 0.6,
                'surface_grip': 0.85
            },
            'Silverstone': {
                'abrasion': 0.6,
                'cornering_intensity': 0.8,
                'braking_zones': 0.5,
                'acceleration_zones': 0.8,
                'surface_grip': 0.9
            },
            'Monza': {
                'abrasion': 0.4,
                'cornering_intensity': 0.5,
                'braking_zones': 0.8,
                'acceleration_zones': 0.9,
                'surface_grip': 0.95
            },
            'Spa': {
                'abrasion': 0.7,
                'cornering_intensity': 0.8,
                'braking_zones': 0.6,
                'acceleration_zones': 0.7,
                'surface_grip': 0.88
            },
            'Suzuka': {
                'abrasion': 0.8,
                'cornering_intensity': 0.9,
                'braking_zones': 0.6,
                'acceleration_zones': 0.7,
                'surface_grip': 0.87
            }
        }
        
        # Driver style characteristics
        self.driver_styles = {
            'conservative': {
                'throttle_aggression': 0.7,
                'braking_aggression': 0.6,
                'cornering_aggression': 0.5,
                'tyre_management': 1.2
            },
            'normal': {
                'throttle_aggression': 1.0,
                'braking_aggression': 1.0,
                'cornering_aggression': 1.0,
                'tyre_management': 1.0
            },
            'aggressive': {
                'throttle_aggression': 1.3,
                'braking_aggression': 1.4,
                'cornering_aggression': 1.5,
                'tyre_management': 0.8
            }
        }
    
    def calculate_tyre_performance(self, compound, track_temp, track_name, 
                                 driver_style='normal', tyre_age=0, 
                                 track_conditions='dry'):
        """
        Calculate tyre performance over a lap
        
        Args:
            compound (str): Tyre compound
            track_temp (float): Track temperature in Celsius
            track_name (str): Track name
            driver_style (str): Driver style
            tyre_age (int): Tyre age in laps
            track_conditions (str): Track conditions (dry/wet/intermediate)
        """
        if compound not in self.compound_properties:
            raise ValueError(f"Unknown compound: {compound}")
        
        props = self.compound_properties[compound]
        track_props = self.track_properties.get(track_name, self.track_properties['Silverstone'])
        style_props = self.driver_styles[driver_style]
        
        # Base performance calculation
        base_performance = props['base_grip']
        
        # Temperature effect
        temp_diff = abs(track_temp - props['optimal_temp'])
        temp_factor = 1 - (temp_diff * props['temp_sensitivity'])
        temp_factor = np.clip(temp_factor, 0.5, 1.2)
        
        # Tyre age degradation
        if tyre_age <= props.get('peak_laps', 5):
            # Peak performance period
            age_factor = 1.0
        else:
            # Degradation period
            degradation_laps = tyre_age - props.get('peak_laps', 5)
            age_factor = np.exp(-props['degradation_rate'] * degradation_laps)
        
        # Track abrasion effect
        abrasion_factor = 1 - (track_props['abrasion'] * 0.1)
        
        # Driver style effect
        style_factor = (style_props['throttle_aggression'] + 
                       style_props['braking_aggression'] + 
                       style_props['cornering_aggression']) / 3
        
        # Track conditions effect
        if track_conditions == 'wet' and compound not in ['WET', 'INTERMEDIATE']:
            condition_factor = 0.3
        elif track_conditions == 'intermediate' and compound not in ['WET', 'INTERMEDIATE']:
            condition_factor = 0.6
        else:
            condition_factor = 1.0
        
        # Calculate final performance
        performance = (base_performance * temp_factor * age_factor * 
                      abrasion_factor * style_factor * condition_factor)
        
        return np.clip(performance, 0.1, 1.0)
    
    def simulate_stint(self, compound, track_temp, track_name, 
                      driver_style='normal', max_laps=50, 
                      track_conditions='dry'):
        """
        Simulate a complete tyre stint
        
        Args:
            compound (str): Tyre compound
            track_temp (float): Track temperature
            track_name (str): Track name
            driver_style (str): Driver style
            max_laps (int): Maximum number of laps
            track_conditions (str): Track conditions
        """
        performance_data = []
        
        for lap in range(1, max_laps + 1):
            performance = self.calculate_tyre_performance(
                compound, track_temp, track_name, driver_style, 
                lap - 1, track_conditions
            )
            
            # Calculate lap time based on performance
            base_lap_time = 90.0  # Base lap time in seconds
            lap_time = base_lap_time / performance
            
            performance_data.append({
                'Lap': lap,
                'Performance': performance * 100,  # Convert to percentage
                'LapTime': lap_time,
                'Compound': compound,
                'TrackTemp': track_temp,
                'DriverStyle': driver_style,
                'TrackConditions': track_conditions
            })
            
            # Stop if performance drops too low
            if performance < 0.3:
                break
        
        return pd.DataFrame(performance_data)
    
    def find_optimal_pit_window(self, stint_data, min_performance=70):
        """
        Find optimal pit stop window based on performance threshold
        
        Args:
            stint_data (DataFrame): Stint simulation data
            min_performance (float): Minimum acceptable performance percentage
        """
        # Find first lap where performance drops below threshold
        below_threshold = stint_data[stint_data['Performance'] < min_performance]
        
        if len(below_threshold) > 0:
            optimal_pit_lap = below_threshold['Lap'].iloc[0]
        else:
            # If performance never drops below threshold, use last lap
            optimal_pit_lap = stint_data['Lap'].iloc[-1]
        
        return optimal_pit_lap
    
    def calculate_tyre_wear_rate(self, compound, track_name, driver_style, track_temp):
        """
        Calculate tyre wear rate based on conditions
        
        Args:
            compound (str): Tyre compound
            track_name (str): Track name
            driver_style (str): Driver style
            track_temp (float): Track temperature
        """
        props = self.compound_properties[compound]
        track_props = self.track_properties.get(track_name, self.track_properties['Silverstone'])
        style_props = self.driver_styles[driver_style]
        
        # Base wear rate
        base_wear = props['wear_factor']
        
        # Track abrasion effect
        track_wear = track_props['abrasion']
        
        # Driver style effect
        driver_wear = (style_props['throttle_aggression'] + 
                      style_props['braking_aggression'] + 
                      style_props['cornering_aggression']) / 3
        
        # Temperature effect
        temp_wear = 1 + (track_temp - 25) / 50  # 25°C as baseline
        
        # Calculate total wear rate
        total_wear_rate = base_wear * track_wear * driver_wear * temp_wear
        
        return total_wear_rate
    
    def generate_race_strategy(self, track_name, track_temp, track_conditions='dry',
                             available_compounds=None, race_laps=50):
        """
        Generate optimal race strategy
        
        Args:
            track_name (str): Track name
            track_temp (float): Track temperature
            track_conditions (str): Track conditions
            available_compounds (list): Available compounds
            race_laps (int): Total race laps
        """
        if available_compounds is None:
            available_compounds = ['SOFT', 'MEDIUM', 'HARD']
        
        strategies = []
        
        # Generate different strategy combinations
        for primary_compound in available_compounds:
            for secondary_compound in available_compounds:
                if primary_compound != secondary_compound:
                    # Simulate first stint
                    stint1 = self.simulate_stint(
                        primary_compound, track_temp, track_name, 
                        'normal', race_laps, track_conditions
                    )
                    
                    # Find optimal pit lap
                    pit_lap = self.find_optimal_pit_window(stint1)
                    
                    if pit_lap < race_laps:
                        # Simulate second stint
                        remaining_laps = race_laps - pit_lap
                        stint2 = self.simulate_stint(
                            secondary_compound, track_temp, track_name,
                            'normal', remaining_laps, track_conditions
                        )
                        
                        # Calculate total race time
                        total_time = (stint1['LapTime'].iloc[:pit_lap].sum() + 
                                     stint2['LapTime'].sum())
                        
                        # Calculate average performance
                        avg_performance = (stint1['Performance'].iloc[:pit_lap].mean() + 
                                         stint2['Performance'].mean()) / 2
                        
                        strategies.append({
                            'Primary': primary_compound,
                            'Secondary': secondary_compound,
                            'PitLap': pit_lap,
                            'TotalTime': total_time,
                            'AvgPerformance': avg_performance,
                            'Strategy': f"{primary_compound} → {secondary_compound}"
                        })
        
        # Sort by total time (faster is better)
        strategy_df = pd.DataFrame(strategies)
        if len(strategy_df) > 0:
            strategy_df = strategy_df.sort_values('TotalTime')
        
        return strategy_df
    
    def analyze_driver_impact(self, compound, track_name, track_temp, 
                            driver_styles=None):
        """
        Analyze how different driver styles affect tyre performance
        
        Args:
            compound (str): Tyre compound
            track_name (str): Track name
            track_temp (float): Track temperature
            driver_styles (list): List of driver styles to compare
        """
        if driver_styles is None:
            driver_styles = ['conservative', 'normal', 'aggressive']
        
        comparison_data = []
        
        for style in driver_styles:
            stint_data = self.simulate_stint(
                compound, track_temp, track_name, style, 50
            )
            
            # Add driver style info
            stint_data['DriverStyle'] = style
            comparison_data.append(stint_data)
        
        return pd.concat(comparison_data, ignore_index=True)
    
    def calculate_compound_comparison(self, track_name, track_temp, 
                                    compounds=None, driver_style='normal'):
        """
        Compare different compounds on the same track
        
        Args:
            track_name (str): Track name
            track_temp (float): Track temperature
            compounds (list): Compounds to compare
            driver_style (str): Driver style
        """
        if compounds is None:
            compounds = ['SOFT', 'MEDIUM', 'HARD']
        
        comparison_data = []
        
        for compound in compounds:
            stint_data = self.simulate_stint(
                compound, track_temp, track_name, driver_style, 50
            )
            comparison_data.append(stint_data)
        
        return pd.concat(comparison_data, ignore_index=True)

def main():
    """Example usage of the tyre degradation model"""
    model = TyreDegradationModel()
    
    print("=== Tyre Degradation Model Demo ===\n")
    
    # Example 1: Compare compounds on Monaco
    print("1. Compound comparison on Monaco (25°C):")
    comparison = model.calculate_compound_comparison('Monaco', 25)
    
    for compound in ['SOFT', 'MEDIUM', 'HARD']:
        compound_data = comparison[comparison['Compound'] == compound]
        peak_performance = compound_data['Performance'].max()
        optimal_lap = compound_data.loc[compound_data['Performance'].idxmax(), 'Lap']
        print(f"  {compound}: Peak {peak_performance:.1f}% at lap {optimal_lap}")
    
    # Example 2: Driver style impact
    print("\n2. Driver style impact on Soft tyres (Monaco, 25°C):")
    driver_impact = model.analyze_driver_impact('SOFT', 'Monaco', 25)
    
    for style in ['conservative', 'normal', 'aggressive']:
        style_data = driver_impact[driver_impact['DriverStyle'] == style]
        avg_performance = style_data['Performance'].mean()
        print(f"  {style.title()}: Average {avg_performance:.1f}% performance")
    
    # Example 3: Race strategy
    print("\n3. Optimal race strategies for Monaco (25°C):")
    strategies = model.generate_race_strategy('Monaco', 25)
    
    print("Top 3 strategies:")
    for i, strategy in strategies.head(3).iterrows():
        print(f"  {i+1}. {strategy['Strategy']}: Pit lap {strategy['PitLap']}, "
              f"Total time {strategy['TotalTime']:.1f}s")

if __name__ == "__main__":
    main() 