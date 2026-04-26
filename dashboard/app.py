"""
app.py — Streamlit dashboard entry point.

Run with: streamlit run dashboard/app.py

"""

import streamlit as st

st.set_page_config(
    page_title="Log Analyzer Dashboard",
    page_icon="🔍",
    layout="wide",
)

st.title("Memory Efficient Log File Analyzer")
st.caption("RV College of Engineering · Experiential Learning 2024-25 · Team 57")

st.info("Use the sidebar to navigate between pages: Overview, Anomalies, and Performance.")

st.markdown("""
### Quick Start
1. Run the pipeline first: `python main.py --input data/samples/sample.log`
2. Come back here to explore the results.
""")
