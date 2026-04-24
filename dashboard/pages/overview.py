"""
overview.py — Dashboard page: Log Volume and Level Distribution.

Owner: Mayank Bajaj (1RV24CI066)
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from pipeline.storage import load_parquet

st.title("Log Overview")

uploaded = st.file_uploader("Upload a processed Parquet file", type=["parquet"])

if uploaded:
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    logs = load_parquet(tmp_path)
    os.unlink(tmp_path)
    df = pd.DataFrame(logs)

    st.metric("Total log entries", f"{len(df):,}")
    st.metric("Unique templates", f"{df['template'].nunique():,}")
    st.metric("Anomalies detected", f"{df['is_anomaly'].sum():,}")

    level_map = {0: "DEBUG", 1: "INFO", 2: "WARN", 3: "ERROR", 4: "CRITICAL"}
    df["level_name"] = df["log_level"].map(level_map).fillna("INFO")
    fig = px.histogram(df, x="log_level", color="level_name",
                       labels={"log_level": "Log Level"},
                       title="Log Level Distribution",
                       color_discrete_map={
                           "DEBUG": "#888", "INFO": "#3B8BD4",
                           "WARN": "#EF9F27", "ERROR": "#D85A30", "CRITICAL": "#A32D2D"
                       })
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 most frequent templates")
    top = df["template"].value_counts().head(10).reset_index()
    top.columns = ["template", "count"]
    st.dataframe(top, use_container_width=True)
else:
    st.info("Run the pipeline first, then upload the Parquet output file here.")
