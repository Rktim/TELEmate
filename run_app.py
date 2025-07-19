#!/usr/bin/env python3
"""
F1 Tyre Degradation Simulator - Launcher
Simple script to run the Streamlit web application
"""

import subprocess
import sys
import os

def main():
    print("🏎️ TELEmate - F1 Tyre Degradation Simulator")
    print("=" * 50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
    
    # Check if FastF1 is installed
    try:
        import fastf1
        print("✅ FastF1 is installed")
    except ImportError:
        print("❌ FastF1 not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastf1"])
        print("✅ FastF1 installed")
    
    print("\n🚀 Starting Streamlit app...")
    print("📱 The app will open in your default web browser")
    print("🔄 To stop the app, press Ctrl+C in this terminal")
    print("-" * 40)
    
    # Run the Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main() 