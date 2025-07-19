#!/usr/bin/env python3
"""
F1 Tyre Degradation Analysis using FastF1 API
Simulates tyre wear based on track conditions, driving style, and compound types
"""

import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Enable FastF1 cache
import os
cache_dir = 'data/cache'
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

class TyreDegradationAnalyzer:
    def __init__(self):
        self.session_data = None
        self.tyre_data = None
        self.track_data = None
        
    def load_session_data(self, year, gp, session_type='R'):
        """
        Load F1 session data using FastF1 API
        
        Args:
            year (int): Year of the race
            gp (str): Grand Prix name (e.g., 'Monaco', 'Silverstone')
            session_type (str): Session type ('R' for race, 'Q' for qualifying, 'FP1', 'FP2', 'FP3')
        """
        try:
            print(f"Loading {year} {gp} {session_type} session data...")
            self.session_data = fastf1.get_session(year, gp, session_type)
            self.session_data.load()
            print("Session data loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading session data: {e}")
            return False
    
    def extract_tyre_data(self):
        """Extract tyre-related data from session"""
        if self.session_data is None:
            print("No session data loaded. Please load session data first.")
            return None
        
        try:
            # Get tyre data for all drivers
            tyre_data = []
            
            for driver in self.session_data.drivers:
                driver_data = self.session_data.get_driver(driver)
                if driver_data is not None:
                    # Get lap data with tyre information
                    laps = driver_data.laps
                    if laps is not None and len(laps) > 0:
                        for lap in laps:
                            if lap.has_telemetry:
                                telemetry = lap.get_telemetry()
                                if telemetry is not None and len(telemetry) > 0:
                                    # Add tyre compound info
                                    telemetry['Driver'] = driver
                                    telemetry['LapNumber'] = lap.LapNumber
                                    telemetry['Compound'] = lap.Compound
                                    telemetry['TyreLife'] = lap.TyreLife
                                    telemetry['TrackTemp'] = lap.TrackTemp
                                    telemetry['AirTemp'] = lap.AirTemp
                                    telemetry['LapTime'] = lap.LapTime.total_seconds()
                                    
                                    tyre_data.append(telemetry)
            
            if tyre_data:
                self.tyre_data = pd.concat(tyre_data, ignore_index=True)
                print(f"Extracted tyre data for {len(self.tyre_data)} data points")
                return self.tyre_data
            else:
                print("No tyre data found in session")
                return None
                
        except Exception as e:
            print(f"Error extracting tyre data: {e}")
            return None
    
    def calculate_tyre_degradation(self, compound_type=None, driver=None):
        """
        Calculate tyre degradation based on various factors
        
        Args:
            compound_type (str): Specific tyre compound to analyze
            driver (str): Specific driver to analyze
        """
        if self.tyre_data is None:
            print("No tyre data available. Please extract tyre data first.")
            return None
        
        # Filter data if specified
        data = self.tyre_data.copy()
        if compound_type:
            data = data[data['Compound'] == compound_type]
        if driver:
            data = data[data['Driver'] == driver]
        
        if len(data) == 0:
            print("No data available for specified filters")
            return None
        
        # Calculate degradation factors
        degradation_factors = {
            'track_temperature': self._calculate_temp_degradation(data),
            'speed_cornering': self._calculate_speed_degradation(data),
            'braking_force': self._calculate_braking_degradation(data),
            'acceleration': self._calculate_acceleration_degradation(data),
            'tyre_life': self._calculate_life_degradation(data)
        }
        
        return degradation_factors
    
    def _calculate_temp_degradation(self, data):
        """Calculate degradation based on track temperature"""
        if 'TrackTemp' not in data.columns:
            return 0
        
        # Higher temperature = faster degradation
        temp_factor = (data['TrackTemp'] - 20) / 30  # Normalize around 20°C
        return np.clip(temp_factor, 0, 2)  # Cap at 2x degradation
    
    def _calculate_speed_degradation(self, data):
        """Calculate degradation based on speed and cornering forces"""
        if 'Speed' not in data.columns:
            return 0
        
        # Higher speeds and lateral forces increase degradation
        speed_factor = data['Speed'] / 300  # Normalize to max F1 speed
        return np.clip(speed_factor, 0, 1)
    
    def _calculate_braking_degradation(self, data):
        """Calculate degradation based on braking forces"""
        if 'Brake' not in data.columns:
            return 0
        
        # Braking forces cause tyre wear
        brake_factor = data['Brake'] / 100  # Normalize brake pressure
        return np.clip(brake_factor, 0, 1)
    
    def _calculate_acceleration_degradation(self, data):
        """Calculate degradation based on acceleration forces"""
        if 'Throttle' not in data.columns:
            return 0
        
        # High throttle usage causes tyre wear
        throttle_factor = data['Throttle'] / 100  # Normalize throttle
        return np.clip(throttle_factor, 0, 1)
    
    def _calculate_life_degradation(self, data):
        """Calculate degradation based on tyre age"""
        if 'TyreLife' not in data.columns:
            return 0
        
        # Older tyres degrade faster
        life_factor = data['TyreLife'] / 50  # Normalize to typical tyre life
        return np.clip(life_factor, 0, 2)
    
    def simulate_tyre_performance(self, compound, track_temp, driver_style='normal'):
        """
        Simulate tyre performance over a race stint
        
        Args:
            compound (str): Tyre compound ('SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET')
            track_temp (float): Track temperature in Celsius
            driver_style (str): Driver style ('conservative', 'normal', 'aggressive')
        """
        # Base degradation rates (per lap)
        base_rates = {
            'SOFT': 0.15,
            'MEDIUM': 0.10,
            'HARD': 0.07,
            'INTERMEDIATE': 0.12,
            'WET': 0.14
        }
        
        # Driver style multipliers
        style_multipliers = {
            'conservative': 0.8,
            'normal': 1.0,
            'aggressive': 1.3
        }
        
        # Temperature effect
        temp_factor = 1 + (track_temp - 25) / 50  # 25°C as baseline
        
        # Calculate degradation rate
        base_rate = base_rates.get(compound, 0.10)
        style_mult = style_multipliers.get(driver_style, 1.0)
        degradation_rate = base_rate * style_mult * temp_factor
        
        # Simulate over 50 laps
        laps = np.arange(1, 51)
        tyre_performance = 100 * np.exp(-degradation_rate * laps)
        
        return pd.DataFrame({
            'Lap': laps,
            'Performance': tyre_performance,
            'Compound': compound,
            'TrackTemp': track_temp,
            'DriverStyle': driver_style
        })
    
    def plot_tyre_degradation(self, simulation_data):
        """Plot tyre degradation simulation"""
        plt.figure(figsize=(12, 8))
        
        # Plot performance over laps
        plt.subplot(2, 2, 1)
        for compound in simulation_data['Compound'].unique():
            data = simulation_data[simulation_data['Compound'] == compound]
            plt.plot(data['Lap'], data['Performance'], label=compound, linewidth=2)
        
        plt.xlabel('Lap Number')
        plt.ylabel('Tyre Performance (%)')
        plt.title('Tyre Performance Over Laps')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot temperature effect
        plt.subplot(2, 2, 2)
        temp_data = simulation_data[simulation_data['Compound'] == 'MEDIUM']
        for temp in temp_data['TrackTemp'].unique():
            data = temp_data[temp_data['TrackTemp'] == temp]
            plt.plot(data['Lap'], data['Performance'], 
                    label=f'{temp}°C', linewidth=2)
        
        plt.xlabel('Lap Number')
        plt.ylabel('Tyre Performance (%)')
        plt.title('Temperature Effect on Medium Tyres')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot driver style effect
        plt.subplot(2, 2, 3)
        style_data = simulation_data[simulation_data['Compound'] == 'SOFT']
        for style in style_data['DriverStyle'].unique():
            data = style_data[style_data['DriverStyle'] == style]
            plt.plot(data['Lap'], data['Performance'], 
                    label=style.title(), linewidth=2)
        
        plt.xlabel('Lap Number')
        plt.ylabel('Tyre Performance (%)')
        plt.title('Driver Style Effect on Soft Tyres')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Performance comparison at lap 20
        plt.subplot(2, 2, 4)
        lap_20_data = simulation_data[simulation_data['Lap'] == 20]
        compounds = lap_20_data['Compound'].unique()
        performances = [lap_20_data[lap_20_data['Compound'] == c]['Performance'].iloc[0] 
                       for c in compounds]
        
        plt.bar(compounds, performances, color=['red', 'yellow', 'white', 'green', 'blue'])
        plt.xlabel('Tyre Compound')
        plt.ylabel('Performance at Lap 20 (%)')
        plt.title('Performance Comparison at Lap 20')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def generate_race_strategy(self, track_length_km=5.0, fuel_load=100):
        """
        Generate optimal race strategy based on tyre degradation
        
        Args:
            track_length_km (float): Track length in kilometers
            fuel_load (float): Initial fuel load in kg
        """
        compounds = ['SOFT', 'MEDIUM', 'HARD']
        track_temp = 25  # Default temperature
        
        strategies = []
        
        for primary_compound in compounds:
            for secondary_compound in compounds:
                if primary_compound != secondary_compound:
                    # Simulate two-stint strategy
                    stint1 = self.simulate_tyre_performance(primary_compound, track_temp)
                    stint2 = self.simulate_tyre_performance(secondary_compound, track_temp)
                    
                    # Find optimal pit lap (when performance drops below 70%)
                    pit_lap = stint1[stint1['Performance'] < 70]['Lap'].iloc[0] if len(stint1[stint1['Performance'] < 70]) > 0 else 25
                    
                    total_time = (stint1['Performance'].iloc[:pit_lap].mean() + 
                                stint2['Performance'].iloc[:50-pit_lap].mean()) / 2
                    
                    strategies.append({
                        'Primary': primary_compound,
                        'Secondary': secondary_compound,
                        'PitLap': pit_lap,
                        'AvgPerformance': total_time,
                        'Strategy': f"{primary_compound} → {secondary_compound}"
                    })
        
        strategy_df = pd.DataFrame(strategies)
        strategy_df = strategy_df.sort_values('AvgPerformance', ascending=False)
        
        return strategy_df

def main():
    """Main function to demonstrate tyre analysis"""
    analyzer = TyreDegradationAnalyzer()
    
    print("=== F1 Tyre Degradation Analysis ===\n")
    
    # Example: Load recent race data (you can modify year and GP)
    print("1. Loading session data...")
    success = analyzer.load_session_data(2023, 'Monaco', 'R')
    
    if success:
        print("\n2. Extracting tyre data...")
        tyre_data = analyzer.extract_tyre_data()
        
        if tyre_data is not None:
            print("\n3. Calculating degradation factors...")
            degradation = analyzer.calculate_tyre_degradation()
            
            if degradation:
                print("Degradation factors calculated:")
                for factor, value in degradation.items():
                    print(f"  - {factor}: {np.mean(value):.3f}")
    
    print("\n4. Running tyre performance simulation...")
    
    # Create simulation data for different scenarios
    simulation_data = []
    
    # Different compounds
    for compound in ['SOFT', 'MEDIUM', 'HARD']:
        sim = analyzer.simulate_tyre_performance(compound, 25, 'normal')
        simulation_data.append(sim)
    
    # Different temperatures
    for temp in [15, 25, 35]:
        sim = analyzer.simulate_tyre_performance('MEDIUM', temp, 'normal')
        simulation_data.append(sim)
    
    # Different driver styles
    for style in ['conservative', 'normal', 'aggressive']:
        sim = analyzer.simulate_tyre_performance('SOFT', 25, style)
        simulation_data.append(sim)
    
    simulation_df = pd.concat(simulation_data, ignore_index=True)
    
    print("\n5. Plotting results...")
    analyzer.plot_tyre_degradation(simulation_df)
    
    print("\n6. Generating race strategies...")
    strategies = analyzer.generate_race_strategy()
    print("\nTop 5 Race Strategies:")
    print(strategies.head().to_string(index=False))
    
    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    main() 