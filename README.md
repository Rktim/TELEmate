<p align="center">
  <img src="race.png" alt="TELEmate Logo" width="600"/>
</p>

<h1 align="center">TELEmate</h1>

<p align="center">

# TELEmate - F1 Tyre Degradation Simulator

A comprehensive tyre degradation simulation tool using FastF1 API to analyze tyre performance under different track and racing conditions.
---

## Demo
<p align="center">
  <a href="https://telemate.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/Launch%20App-Streamlit%20🚀-brightgreen?style=for-the-badge&logo=streamlit&logoColor=white" alt="Launch App">
  </a>
</p>


## Features

- **Real F1 Data**: Uses FastF1 API to fetch actual Formula 1 telemetry data
- **Tyre Degradation Analysis**: Simulates tyre wear based on track conditions, driving style, and compound types
- **Multi-factor Analysis**: Considers track temperature, surface type, driver style, and racing conditions
- **Interactive Visualizations**: Dynamic charts and graphs for data analysis
- **Driver Comparison**: Optional driver-specific analysis and comparison


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

## License

This project is licensed under the . See the LICENSE file for details.

