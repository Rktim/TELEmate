#!/usr/bin/env python3
"""
Driver-Specific Tyre Analysis using FastF1 API
Analyzes individual driver tyre performance and driving styles
"""

import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Enable FastF1 cache
import os
cache_dir = 'data/cache'
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

class DriverTyreAnalyzer:
    def __init__(self):
        self.session_data = None
        self.driver_data = {}
        self.comparison_data = None
        
    def load_session_data(self, year, gp, session_type='R'):
        """Load F1 session data"""
        try:
            print(f"Loading {year} {gp} {session_type} session data...")
            self.session_data = fastf1.get_session(year, gp, session_type)
            self.session_data.load()
            print("Session data loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading session data: {e}")
            return False
    
    def analyze_driver(self, driver_code):
        """
        Analyze tyre performance for a specific driver
        
        Args:
            driver_code (str): Driver code (e.g., 'HAM', 'VER', 'LEC')
        """
        if self.session_data is None:
            print("No session data loaded. Please load session data first.")
            return None
        
        try:
            print(f"Analyzing driver: {driver_code}")
            driver_data = self.session_data.get_driver(driver_code)
            
            if driver_data is None:
                print(f"Driver {driver_code} not found in session")
                return None
            
            # Get all laps for the driver
            laps = driver_data.laps
            
            if laps is None or len(laps) == 0:
                print(f"No lap data found for driver {driver_code}")
                return None
            
            # Extract tyre and performance data
            tyre_info = []
            
            for lap in laps:
                if lap.has_telemetry:
                    telemetry = lap.get_telemetry()
                    if telemetry is not None and len(telemetry) > 0:
                        # Calculate driving style metrics
                        avg_speed = telemetry['Speed'].mean()
                        max_speed = telemetry['Speed'].max()
                        avg_throttle = telemetry['Throttle'].mean()
                        avg_brake = telemetry['Brake'].mean()
                        
                        # Calculate cornering forces (simplified)
                        lateral_forces = np.abs(telemetry['Speed'].diff()).mean()
                        
                        tyre_info.append({
                            'LapNumber': lap.LapNumber,
                            'Compound': lap.Compound,
                            'TyreLife': lap.TyreLife,
                            'LapTime': lap.LapTime.total_seconds(),
                            'TrackTemp': lap.TrackTemp,
                            'AirTemp': lap.AirTemp,
                            'AvgSpeed': avg_speed,
                            'MaxSpeed': max_speed,
                            'AvgThrottle': avg_throttle,
                            'AvgBrake': avg_brake,
                            'LateralForces': lateral_forces,
                            'Driver': driver_code
                        })
            
            if tyre_info:
                driver_df = pd.DataFrame(tyre_info)
                self.driver_data[driver_code] = driver_df
                print(f"Analyzed {len(driver_df)} laps for {driver_code}")
                return driver_df
            else:
                print(f"No tyre data found for driver {driver_code}")
                return None
                
        except Exception as e:
            print(f"Error analyzing driver {driver_code}: {e}")
            return None
    
    def calculate_driving_style(self, driver_code):
        """
        Calculate driving style characteristics for a driver
        
        Args:
            driver_code (str): Driver code
        """
        if driver_code not in self.driver_data:
            print(f"No data available for driver {driver_code}")
            return None
        
        data = self.driver_data[driver_code]
        
        # Calculate driving style metrics
        style_metrics = {
            'driver': driver_code,
            'avg_throttle': data['AvgThrottle'].mean(),
            'avg_brake': data['AvgBrake'].mean(),
            'avg_speed': data['AvgSpeed'].mean(),
            'max_speed': data['MaxSpeed'].max(),
            'lateral_forces': data['LateralForces'].mean(),
            'tyre_aggression': (data['AvgThrottle'].mean() + data['AvgBrake'].mean()) / 2,
            'speed_consistency': data['AvgSpeed'].std(),
            'lap_time_consistency': data['LapTime'].std()
        }
        
        # Classify driving style
        throttle_score = style_metrics['avg_throttle'] / 100
        brake_score = style_metrics['avg_brake'] / 100
        aggression_score = (throttle_score + brake_score) / 2
        
        if aggression_score < 0.4:
            style = 'Conservative'
        elif aggression_score < 0.6:
            style = 'Balanced'
        else:
            style = 'Aggressive'
        
        style_metrics['driving_style'] = style
        style_metrics['aggression_score'] = aggression_score
        
        return style_metrics
    
    def analyze_tyre_usage_patterns(self, driver_code):
        """
        Analyze how a driver uses different tyre compounds
        
        Args:
            driver_code (str): Driver code
        """
        if driver_code not in self.driver_data:
            print(f"No data available for driver {driver_code}")
            return None
        
        data = self.driver_data[driver_code]
        
        # Group by compound
        compound_analysis = data.groupby('Compound').agg({
            'LapTime': ['mean', 'std', 'count'],
            'AvgSpeed': 'mean',
            'AvgThrottle': 'mean',
            'AvgBrake': 'mean',
            'TyreLife': 'mean'
        }).round(3)
        
        # Flatten column names
        compound_analysis.columns = ['_'.join(col).strip() for col in compound_analysis.columns]
        
        return compound_analysis
    
    def compare_drivers(self, driver_codes):
        """
        Compare tyre performance between multiple drivers
        
        Args:
            driver_codes (list): List of driver codes to compare
        """
        comparison_data = []
        
        for driver in driver_codes:
            if driver in self.driver_data:
                data = self.driver_data[driver]
                style = self.calculate_driving_style(driver)
                
                # Add driver data to comparison
                for _, row in data.iterrows():
                    comparison_data.append({
                        'Driver': driver,
                        'Compound': row['Compound'],
                        'LapTime': row['LapTime'],
                        'AvgSpeed': row['AvgSpeed'],
                        'AvgThrottle': row['AvgThrottle'],
                        'AvgBrake': row['AvgBrake'],
                        'TyreLife': row['TyreLife'],
                        'DrivingStyle': style['driving_style'] if style else 'Unknown',
                        'AggressionScore': style['aggression_score'] if style else 0
                    })
        
        if comparison_data:
            self.comparison_data = pd.DataFrame(comparison_data)
            return self.comparison_data
        else:
            print("No comparison data available")
            return None
    
    def plot_driver_comparison(self, driver_codes):
        """Plot comparison between drivers"""
        if self.comparison_data is None:
            print("No comparison data available. Run compare_drivers() first.")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Driver Tyre Performance Comparison', fontsize=16)
        
        # Filter data for specified drivers
        data = self.comparison_data[self.comparison_data['Driver'].isin(driver_codes)]
        
        # 1. Lap times by compound
        for compound in data['Compound'].unique():
            compound_data = data[data['Compound'] == compound]
            for driver in driver_codes:
                driver_data = compound_data[compound_data['Driver'] == driver]
                if len(driver_data) > 0:
                    axes[0, 0].scatter(driver_data['TyreLife'], driver_data['LapTime'], 
                                     label=f'{driver} ({compound})', alpha=0.7)
        
        axes[0, 0].set_xlabel('Tyre Life')
        axes[0, 0].set_ylabel('Lap Time (s)')
        axes[0, 0].set_title('Lap Times vs Tyre Life')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Average speed by compound
        speed_data = data.groupby(['Driver', 'Compound'])['AvgSpeed'].mean().unstack()
        speed_data.plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_xlabel('Driver')
        axes[0, 1].set_ylabel('Average Speed (km/h)')
        axes[0, 1].set_title('Average Speed by Compound')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Driving style comparison
        style_data = data.groupby('Driver').agg({
            'AvgThrottle': 'mean',
            'AvgBrake': 'mean',
            'AggressionScore': 'mean'
        })
        
        style_data[['AvgThrottle', 'AvgBrake']].plot(kind='bar', ax=axes[0, 2])
        axes[0, 2].set_xlabel('Driver')
        axes[0, 2].set_ylabel('Average Input (%)')
        axes[0, 2].set_title('Driving Input Comparison')
        axes[0, 2].tick_params(axis='x', rotation=45)
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Tyre life distribution
        for driver in driver_codes:
            driver_data = data[data['Driver'] == driver]
            axes[1, 0].hist(driver_data['TyreLife'], alpha=0.7, label=driver, bins=10)
        
        axes[1, 0].set_xlabel('Tyre Life')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Tyre Life Distribution')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 5. Lap time consistency
        consistency_data = data.groupby('Driver')['LapTime'].std().sort_values()
        consistency_data.plot(kind='bar', ax=axes[1, 1], color='orange')
        axes[1, 1].set_xlabel('Driver')
        axes[1, 1].set_ylabel('Lap Time Std Dev (s)')
        axes[1, 1].set_title('Lap Time Consistency (Lower is Better)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Compound preference heatmap
        compound_pref = data.groupby(['Driver', 'Compound']).size().unstack(fill_value=0)
        sns.heatmap(compound_pref, annot=True, fmt='d', cmap='YlOrRd', ax=axes[1, 2])
        axes[1, 2].set_title('Compound Usage Heatmap')
        axes[1, 2].set_xlabel('Compound')
        axes[1, 2].set_ylabel('Driver')
        
        plt.tight_layout()
        plt.show()
    
    def generate_driver_report(self, driver_code):
        """Generate a comprehensive report for a driver"""
        if driver_code not in self.driver_data:
            print(f"No data available for driver {driver_code}")
            return
        
        data = self.driver_data[driver_code]
        style = self.calculate_driving_style(driver_code)
        compound_analysis = self.analyze_tyre_usage_patterns(driver_code)
        
        print(f"\n=== DRIVER REPORT: {driver_code} ===")
        print(f"Total Laps Analyzed: {len(data)}")
        print(f"Driving Style: {style['driving_style']}")
        print(f"Aggression Score: {style['aggression_score']:.3f}")
        print(f"Average Speed: {style['avg_speed']:.1f} km/h")
        print(f"Speed Consistency: {style['speed_consistency']:.1f} km/h")
        print(f"Lap Time Consistency: {style['lap_time_consistency']:.3f} seconds")
        
        print(f"\n--- Tyre Usage Analysis ---")
        if compound_analysis is not None:
            print(compound_analysis.to_string())
        
        print(f"\n--- Performance Summary ---")
        print(f"Best Lap Time: {data['LapTime'].min():.3f} seconds")
        print(f"Average Lap Time: {data['LapTime'].mean():.3f} seconds")
        print(f"Worst Lap Time: {data['LapTime'].max():.3f} seconds")
        print(f"Average Tyre Life: {data['TyreLife'].mean():.1f} laps")
        
        # Compound recommendations
        print(f"\n--- Tyre Strategy Recommendations ---")
        best_compound = compound_analysis['LapTime_mean'].idxmin() if compound_analysis is not None else 'Unknown'
        print(f"Best Performing Compound: {best_compound}")
        
        if style['aggression_score'] > 0.6:
            print("Recommendation: Consider more conservative tyre management")
        elif style['aggression_score'] < 0.4:
            print("Recommendation: Can push harder on tyres")
        else:
            print("Recommendation: Current driving style is well-balanced")

def main():
    parser = argparse.ArgumentParser(description='Analyze driver-specific tyre performance')
    parser.add_argument('--year', type=int, default=2023, help='Year of the race')
    parser.add_argument('--gp', type=str, default='Monaco', help='Grand Prix name')
    parser.add_argument('--session', type=str, default='R', help='Session type (R/Q/FP1/FP2/FP3)')
    parser.add_argument('--driver', type=str, help='Specific driver to analyze')
    parser.add_argument('--compare', nargs='+', help='Drivers to compare')
    
    args = parser.parse_args()
    
    analyzer = DriverTyreAnalyzer()
    
    print("=== Driver Tyre Analysis ===\n")
    
    # Load session data
    success = analyzer.load_session_data(args.year, args.gp, args.session)
    
    if not success:
        print("Failed to load session data. Exiting.")
        return
    
    # Analyze specific driver if provided
    if args.driver:
        print(f"\nAnalyzing driver: {args.driver}")
        driver_data = analyzer.analyze_driver(args.driver)
        
        if driver_data is not None:
            analyzer.generate_driver_report(args.driver)
    
    # Compare drivers if provided
    if args.compare:
        print(f"\nComparing drivers: {', '.join(args.compare)}")
        
        # Analyze all specified drivers
        for driver in args.compare:
            analyzer.analyze_driver(driver)
        
        # Generate comparison
        comparison_data = analyzer.compare_drivers(args.compare)
        
        if comparison_data is not None:
            print(f"\nComparison data generated for {len(comparison_data)} data points")
            analyzer.plot_driver_comparison(args.compare)
    
    # If no specific analysis requested, analyze top drivers
    if not args.driver and not args.compare:
        print("\nAnalyzing top drivers from session...")
        top_drivers = ['HAM', 'VER', 'LEC', 'PER', 'SAI']  # Example drivers
        
        for driver in top_drivers:
            analyzer.analyze_driver(driver)
        
        # Generate comparison
        comparison_data = analyzer.compare_drivers(top_drivers)
        
        if comparison_data is not None:
            analyzer.plot_driver_comparison(top_drivers)
    
    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    main() 