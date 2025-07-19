#!/usr/bin/env python3
"""
F1 Tyre Degradation Simulator - Streamlit Web App
Interactive tyre degradation analysis with FastF1 data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import base64
warnings.filterwarnings('ignore')

def get_image_base64(image_path):
    """Convert image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return ""

def display_logo(width=200, location="main"):
    """Display logo with fallback"""
    try:
        if location == "sidebar":
            st.image("race.png", width=width)
        else:
            st.markdown("""
            <div class="logo-container">
                <img src="data:image/png;base64,""" + get_image_base64("race.png") + """" width=""" + str(width) + """ alt="TELEmate Logo">
            </div>
            """, unsafe_allow_html=True)
    except:
        # Fallback to text if image fails
        if location == "sidebar":
            st.markdown("### TELEmate")
        else:
            st.title("TELEmate")

# Import our custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.driver_data import F1_DRIVERS, get_driver_number, get_driver_by_number, get_all_driver_initials
from models.tyre_model import TyreDegradationModel



# Page configuration
st.set_page_config(
    page_title="TELEmate - F1 Tyre Analysis",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for race-themed color scheme
st.markdown("""
<style>
    /* Dark theme with race colors */
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    .stApp {
        background-color: #0a0a0a;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1a1a;
        border-right: 2px solid #00ff00;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00ff00;
        font-weight: 600;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #0000ff;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2a2a2a;
        border-radius: 6px;
        color: #ffffff;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0000ff;
        color: #ffffff;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #ff0000;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #cc0000;
    }
    
    /* Selectboxes */
    .stSelectbox > div > div {
        background-color: #1a1a1a;
        border: 1px solid #00ff00;
        border-radius: 6px;
        color: #ffffff;
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background-color: #00ff00;
    }
    
    .stSlider > div > div > div > div > div {
        background-color: #ffffff;
    }
    
    /* Dataframes */
    .dataframe {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        background-color: #1a1a1a;
    }
    
    /* Custom panels */
    .panel {
        background-color: #1a1a1a;
        border: 1px solid #00ff00;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    
    .metric-card {
        background-color: #1a1a1a;
        border: 1px solid #00ff00;
        border-radius: 6px;
        padding: 12px;
        margin: 4px 0;
        color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 255, 0, 0.1);
    }
    
    .driver-card {
        background-color: #1a1a1a;
        border: 1px solid #ff0000;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 4px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #ffffff;
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .logo-container img {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 255, 0, 0.3);
    }
    
    /* Strong text */
    strong {
        color: #00ff00;
    }
</style>
""", unsafe_allow_html=True)

# Initialize tyre model
@st.cache_resource
def load_tyre_model():
    return TyreDegradationModel()

tyre_model = load_tyre_model()

def main():
    # Header with title and status
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Display the logo
        display_logo(width=200, location="main")
        st.markdown("**F1 Tyre Degradation Analysis**")
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <strong>Status:</strong> Connected<br>
            <strong>Mode:</strong> Simulation<br>
            <strong>Session:</strong> Active
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <strong>Date:</strong> """ + pd.Timestamp.now().strftime("%d/%m/%Y") + """<br>
            <strong>Time:</strong> """ + pd.Timestamp.now().strftime("%H:%M") + """<br>
            <strong>TELEmate:</strong> v1.0
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar - Left Panel
    with st.sidebar:
        # Logo in sidebar
        display_logo(width=150, location="sidebar")
        st.markdown("### TELEmate CONTROL")
        
        # Track and conditions
        st.markdown("**TRACK SETUP**")
        tracks = ['Monaco', 'Silverstone', 'Monza', 'Spa', 'Suzuka']
        selected_track = st.selectbox("Circuit", tracks, index=0)
        
        track_temp = st.slider("Track Temp (°C)", 15, 45, 25)
        track_conditions = st.selectbox("Conditions", ['dry', 'intermediate', 'wet'])
        
        st.markdown("---")
        
        # Driver selection
        st.markdown("**DRIVER SELECTION**")
        all_drivers = get_all_driver_initials()
        
        selected_drivers = st.multiselect(
            "Select Drivers",
            all_drivers,
            default=['HAM', 'VER', 'LEC'],
            help="Choose drivers to analyze"
        )
        
        # Selected drivers display
        if selected_drivers:
            st.markdown("**ACTIVE DRIVERS**")
            for driver in selected_drivers:
                driver_number = get_driver_number(driver)
                st.markdown(f"""
                <div class="driver-card">
                    <span><strong>{driver}</strong></span>
                    <span>#{driver_number}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Tyre Analysis", "Race Strategy", "Driver Comparison"])
    
    with tab1:
        show_tyre_analysis(track_temp, selected_track, track_conditions)
    
    with tab2:
        show_race_strategy(track_temp, selected_track, track_conditions)
    
    with tab3:
        show_driver_comparison(track_temp, selected_track, track_conditions, selected_drivers)

def show_tyre_analysis(track_temp, track_name, track_conditions):
    st.markdown("### TYRE PERFORMANCE ANALYSIS")
    
    # Main telemetry area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Compound comparison
        compounds = ['SOFT', 'MEDIUM', 'HARD']
        if track_conditions in ['wet', 'intermediate']:
            compounds.extend(['INTERMEDIATE', 'WET'])
        
        # Simulate all compounds
        comparison_data = []
        for compound in compounds:
            stint_data = tyre_model.simulate_stint(
                compound, track_temp, track_name, 'normal', 50, track_conditions
            )
            comparison_data.append(stint_data)
        
        comparison_df = pd.concat(comparison_data, ignore_index=True)
        
        # Create performance plot with race theme
        fig = px.line(comparison_df, x='Lap', y='Performance', color='Compound',
                     title=f"Tyre Performance Telemetry - {track_name}",
                     labels={'Performance': 'Performance (%)', 'Lap': 'Lap Number'},
                     color_discrete_map={
                         'SOFT': '#00ff00',
                         'MEDIUM': '#ff0000', 
                         'HARD': '#0000ff',
                         'INTERMEDIATE': '#ffffff',
                         'WET': '#ffff00'
                     })
        
        # Update layout for race theme
        fig.update_layout(
            height=400,
            showlegend=True,
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            xaxis=dict(gridcolor='#1a1a1a'),
            yaxis=dict(gridcolor='#1a1a1a')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional telemetry graphs
        col1a, col1b = st.columns(2)
        
        with col1a:
            # Lap time comparison
            fig_lap = px.line(comparison_df, x='Lap', y='LapTime', color='Compound',
                             title="Lap Time Evolution",
                             labels={'LapTime': 'Lap Time (s)', 'Lap': 'Lap Number'})
            
            fig_lap.update_layout(
                height=300,
                plot_bgcolor='#0a0a0a',
                paper_bgcolor='#0a0a0a',
                font=dict(color='#ffffff'),
                xaxis=dict(gridcolor='#1a1a1a'),
                yaxis=dict(gridcolor='#1a1a1a')
            )
            st.plotly_chart(fig_lap, use_container_width=True)
        
        with col1b:
            # Temperature effect
            temp_range = range(15, 46, 5)
            temp_data = []
            
            for temp in temp_range:
                performance = tyre_model.calculate_tyre_performance(
                    'MEDIUM', temp, track_name, 'normal', 10, track_conditions
                )
                temp_data.append({'Temperature': temp, 'Performance': performance * 100})
            
            temp_df = pd.DataFrame(temp_data)
            fig_temp = px.line(temp_df, x='Temperature', y='Performance',
                              title="Temperature Sensitivity",
                              labels={'Performance': 'Performance (%)', 'Temperature': 'Track Temp (°C)'})
            
            fig_temp.update_layout(
                height=300,
                plot_bgcolor='#0a0a0a',
                paper_bgcolor='#0a0a0a',
                font=dict(color='#ffffff'),
                xaxis=dict(gridcolor='#1a1a1a'),
                yaxis=dict(gridcolor='#1a1a1a')
            )
            st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Right panel - Compound data
        st.markdown("**COMPOUND DATA**")
        
        # Calculate summary statistics
        summary_data = []
        for compound in compounds:
            compound_data = comparison_df[comparison_df['Compound'] == compound]
            if len(compound_data) > 0:
                peak_performance = compound_data['Performance'].max()
                peak_lap = compound_data.loc[compound_data['Performance'].idxmax(), 'Lap']
                avg_performance = compound_data['Performance'].mean()
                optimal_laps = len(compound_data[compound_data['Performance'] > 80])
                
                # Color coding for compounds
                color_map = {
                    'SOFT': '#00ff00',
                    'MEDIUM': '#ff0000',
                    'HARD': '#0000ff',
                    'INTERMEDIATE': '#ffffff',
                    'WET': '#ffff00'
                }
                
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {color_map.get(compound, '#4CAF50')}">
                    <strong>{compound}</strong><br>
                    Peak: {peak_performance:.1f}% (Lap {int(peak_lap)})<br>
                    Avg: {avg_performance:.1f}%<br>
                    Optimal: {optimal_laps} laps
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Track conditions
        st.markdown("**TRACK CONDITIONS**")
        st.markdown(f"""
        <div class="metric-card">
            <strong>Circuit:</strong> {track_name}<br>
            <strong>Temperature:</strong> {track_temp}°C<br>
            <strong>Conditions:</strong> {track_conditions.title()}<br>
            <strong>Surface:</strong> Asphalt
        </div>
        """, unsafe_allow_html=True)
        
        # Performance metrics
        st.markdown("**PERFORMANCE METRICS**")
        best_compound = comparison_df.groupby('Compound')['Performance'].mean().idxmax()
        best_avg = comparison_df.groupby('Compound')['Performance'].mean().max()
        
        st.markdown(f"""
        <div class="metric-card">
            <strong>Best Compound:</strong> {best_compound}<br>
            <strong>Avg Performance:</strong> {best_avg:.1f}%<br>
            <strong>Analysis Time:</strong> {pd.Timestamp.now().strftime("%H:%M:%S")}
        </div>
        """, unsafe_allow_html=True)

def show_race_strategy(track_temp, track_name, track_conditions):
    st.markdown("### RACE STRATEGY ANALYSIS")
    
    # Main strategy area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Strategy parameters panel
        st.markdown("**STRATEGY PARAMETERS**")
        
        col1a, col1b = st.columns(2)
        
        with col1a:
            race_laps = st.slider("Race Laps", 30, 80, 50)
            min_performance = st.slider("Min Performance (%)", 50, 90, 70)
        
        with col1b:
            available_compounds = st.multiselect(
                "Available Compounds",
                ['SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET'],
                default=['SOFT', 'MEDIUM', 'HARD']
            )
        
        if st.button("Generate Strategies", key="gen_strat"):
            with st.spinner("Calculating optimal strategies..."):
                strategies = tyre_model.generate_race_strategy(
                    track_name, track_temp, track_conditions, 
                    available_compounds, race_laps
                )
                
                if len(strategies) > 0:
                    st.session_state.strategies = strategies
                    st.success("Strategies generated!")
                else:
                    st.error("No valid strategies found")
        
        # Strategy visualization
        if 'strategies' in st.session_state:
            strategies = st.session_state.strategies
            
            # Create strategy comparison chart
            fig = go.Figure()
            
            colors = ['#00ff00', '#ff0000', '#0000ff', '#ffffff', '#ffff00']
            
            for i, strategy in strategies.head(8).iterrows():
                fig.add_trace(go.Bar(
                    name=strategy['Strategy'],
                    x=[strategy['Strategy']],
                    y=[strategy['TotalTime']],
                    text=f"{strategy['TotalTime']:.1f}s",
                    textposition='auto',
                    marker_color=colors[i % len(colors)]
                ))
            
            fig.update_layout(
                title="Race Strategy Comparison",
                xaxis_title="Strategy",
                yaxis_title="Total Race Time (seconds)",
                height=400,
                plot_bgcolor='#0a0a0a',
                paper_bgcolor='#0a0a0a',
                font=dict(color='#ffffff'),
                xaxis=dict(gridcolor='#1a1a1a'),
                yaxis=dict(gridcolor='#1a1a1a')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Strategy timeline
            if len(strategies) > 0:
                best_strategy = strategies.iloc[0]
                
                # Create timeline visualization
                fig_timeline = go.Figure()
                
                # First stint
                fig_timeline.add_trace(go.Scatter(
                    x=[0, best_strategy['PitLap']],
                    y=[best_strategy['AvgPerformance'], best_strategy['AvgPerformance']],
                    mode='lines+markers',
                    name=f"Stint 1: {best_strategy['Primary']}",
                    line=dict(color='#00ff00', width=3)
                ))
                
                # Second stint
                fig_timeline.add_trace(go.Scatter(
                    x=[best_strategy['PitLap'], race_laps],
                    y=[best_strategy['AvgPerformance'], best_strategy['AvgPerformance']],
                    mode='lines+markers',
                    name=f"Stint 2: {best_strategy['Secondary']}",
                    line=dict(color='#ff0000', width=3)
                ))
                
                fig_timeline.update_layout(
                    title="Optimal Strategy Timeline",
                    xaxis_title="Lap",
                    yaxis_title="Performance (%)",
                    height=300,
                    plot_bgcolor='#0a0a0a',
                    paper_bgcolor='#0a0a0a',
                    font=dict(color='#ffffff'),
                    xaxis=dict(gridcolor='#1a1a1a'),
                    yaxis=dict(gridcolor='#1a1a1a')
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
    
    with col2:
        # Right panel - Strategy data
        st.markdown("**STRATEGY DATA**")
        
        if 'strategies' in st.session_state:
            strategies = st.session_state.strategies
            
            # Display top strategies
            st.markdown("**TOP STRATEGIES**")
            for i, strategy in strategies.head(5).iterrows():
                st.markdown(f"""
                <div class="metric-card">
                    <strong>{i+1}. {strategy['Strategy']}</strong><br>
                    Pit Lap: {strategy['PitLap']}<br>
                    Total Time: {strategy['TotalTime']:.1f}s<br>
                    Avg Performance: {strategy['AvgPerformance']:.1f}%
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Race parameters
        st.markdown("**RACE PARAMETERS**")
        st.markdown(f"""
        <div class="metric-card">
            <strong>Circuit:</strong> {track_name}<br>
            <strong>Race Laps:</strong> {race_laps if 'race_laps' in locals() else 50}<br>
            <strong>Conditions:</strong> {track_conditions.title()}<br>
            <strong>Temperature:</strong> {track_temp}°C
        </div>
        """, unsafe_allow_html=True)
        
        # Strategy metrics
        if 'strategies' in st.session_state:
            strategies = st.session_state.strategies
            if len(strategies) > 0:
                best_time = strategies.iloc[0]['TotalTime']
                worst_time = strategies.iloc[-1]['TotalTime']
                time_diff = worst_time - best_time
                
                st.markdown("**STRATEGY METRICS**")
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Best Time:</strong> {best_time:.1f}s<br>
                    <strong>Worst Time:</strong> {worst_time:.1f}s<br>
                    <strong>Time Spread:</strong> {time_diff:.1f}s<br>
                    <strong>Strategies:</strong> {len(strategies)}
                </div>
                """, unsafe_allow_html=True)

def show_driver_comparison(track_temp, track_name, track_conditions, selected_drivers):
    st.markdown("### Driver Comparison")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Analysis Parameters**")
        
        # Driver style selection
        driver_styles = ['conservative', 'normal', 'aggressive']
        selected_style = st.selectbox(
            "Driver Style",
            driver_styles,
            index=1,  # Default to 'normal'
            help="Select the driving style to simulate"
        )
        
        # Compound selection
        compound = st.selectbox("Tyre Compound", ['SOFT', 'MEDIUM', 'HARD'])
        
        if st.button("Compare Selected Drivers"):
            with st.spinner("Analyzing drivers..."):
                # Simulate each selected driver
                driver_comparison_data = []
                
                for driver in selected_drivers:
                    # Simulate driver performance
                    stint_data = tyre_model.simulate_stint(
                        compound, track_temp, track_name, selected_style, 50, track_conditions
                    )
                    stint_data['Driver'] = driver
                    stint_data['DriverNumber'] = get_driver_number(driver)
                    driver_comparison_data.append(stint_data)
                
                if driver_comparison_data:
                    comparison_df = pd.concat(driver_comparison_data, ignore_index=True)
                    st.session_state.driver_comparison = comparison_df
                    st.success(f"Analysis complete for {len(selected_drivers)} drivers!")
                else:
                    st.error("No drivers selected for comparison")
    
    with col2:
        st.markdown("**Driver Summary**")
        
        if 'driver_comparison' in st.session_state:
            driver_comparison = st.session_state.driver_comparison
            
            # Calculate summary for each driver
            driver_summary = []
            for driver in selected_drivers:
                driver_data = driver_comparison[driver_comparison['Driver'] == driver]
                if len(driver_data) > 0:
                    avg_performance = driver_data['Performance'].mean()
                    avg_lap_time = driver_data['LapTime'].mean()
                    consistency = driver_data['LapTime'].std()
                    peak_performance = driver_data['Performance'].max()
                    
                    driver_summary.append({
                        'Driver': f"{driver} (#{get_driver_number(driver)})",
                        'Avg Performance': f"{avg_performance:.1f}%",
                        'Peak Performance': f"{peak_performance:.1f}%",
                        'Avg Lap Time': f"{avg_lap_time:.2f}s",
                        'Consistency': f"{consistency:.3f}s"
                    })
            
            if driver_summary:
                summary_df = pd.DataFrame(driver_summary)
                st.dataframe(summary_df, use_container_width=True)
    
    # Driver comparison visualization
    if 'driver_comparison' in st.session_state:
        st.markdown("### Driver Performance Comparison")
        
        driver_comparison = st.session_state.driver_comparison
        
        # Create subplot for performance and lap times
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Performance Over Laps', 'Lap Time Distribution'),
            specs=[[{"type": "scatter"}, {"type": "box"}]]
        )
        
        # Performance plot
        for driver in selected_drivers:
            driver_data = driver_comparison[driver_comparison['Driver'] == driver]
            if len(driver_data) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=driver_data['Lap'],
                        y=driver_data['Performance'],
                        mode='lines',
                        name=f"{driver} (#{get_driver_number(driver)})",
                        showlegend=True
                    ),
                    row=1, col=1
                )
        
        # Lap time distribution
        for driver in selected_drivers:
            driver_data = driver_comparison[driver_comparison['Driver'] == driver]
            if len(driver_data) > 0:
                fig.add_trace(
                    go.Box(
                        y=driver_data['LapTime'],
                        name=f"{driver} (#{get_driver_number(driver)})",
                        showlegend=False
                    ),
                    row=1, col=2
                )
        
        fig.update_layout(
            height=500, 
            title_text="Driver Performance Comparison",
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional analysis
        st.markdown("### Performance Rankings")
        
        # Best average performance
        best_performance = driver_comparison.groupby('Driver')['Performance'].mean().sort_values(ascending=False)
        st.write("**Best Average Performance:**")
        for i, (driver, perf) in enumerate(best_performance.items(), 1):
            st.write(f"{i}. {driver} (#{get_driver_number(driver)}): {perf:.1f}%")
        
        # Most consistent
        most_consistent = driver_comparison.groupby('Driver')['LapTime'].std().sort_values()
        st.write("**Most Consistent (Lowest Lap Time Variance):**")
        for i, (driver, consistency) in enumerate(most_consistent.items(), 1):
            st.write(f"{i}. {driver} (#{get_driver_number(driver)}): {consistency:.3f}s")



if __name__ == "__main__":
    main() 