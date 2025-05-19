import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(page_title="AgenticSTLC", layout="wide")

# Disable Streamlit's file watcher for PyTorch to prevent introspection issues
st.query_params["disableWatchdog"] = "true"

from src.test_pilot.ui.streamlit_ui.streamlit_app import load_app

if __name__ == "__main__":
    load_app()