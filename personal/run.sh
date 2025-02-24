#!/bin/bash

# Navigate to the project directory
cd ~/Documents/GitHub/MyUdemyProgress/personal/

# Activate the virtual environment
source .venv/bin/activate

# Run the Streamlit app
streamlit run main.py --server.headless=true --server.port 8598
