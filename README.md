<p align="center">
  <img src="assets/race.png" alt="TELEmate Logo" width="600"/>
</p>

<h1 align="center">TELEmate</h1>

<p align="center">

# TELEmate - F1 Tyre Degradation Simulator

A comprehensive tyre degradation simulation tool using FastF1 API to analyze tyre performance under different track and racing conditions.

## Features

- **Real F1 Data**: Uses FastF1 API to fetch actual Formula 1 telemetry data
- **Tyre Degradation Analysis**: Simulates tyre wear based on track conditions, driving style, and compound types
- **Multi-factor Analysis**: Considers track temperature, surface type, driver style, and racing conditions
- **Interactive Visualizations**: Dynamic charts and graphs for data analysis
- **Driver Comparison**: Optional driver-specific analysis and comparison

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Interactive Web App (Recommended)**:
```bash
streamlit run streamlit_app.py
```

2. **Basic Tyre Analysis**:
```python
python tyre_analysis.py
```

3. **Driver-Specific Analysis**:
```python
python driver_analysis.py --driver "HAM" --track "Monaco"
```

## Project Structure

- `streamlit_app.py` - TELEmate web application (main interface)
- `tyre_analysis.py` - Main tyre degradation analysis script
- `driver_analysis.py` - Driver-specific tyre performance analysis
- `utils/` - Utility functions and data processing
- `models/` - Tyre degradation models and algorithms
- `data/` - Cached F1 data and results

## Data Sources

- FastF1 API for real F1 telemetry data
- Track information and weather conditions
- Driver telemetry and lap times
- Tyre compound specifications

## Contributing

Feel free to contribute by adding new features, improving models, or enhancing visualizations. 
