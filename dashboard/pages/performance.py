"""
performance.py — Dashboard page: Pipeline Performance Metrics.

Reads from evaluation/reports/benchmark_results.csv and visualises
RAM usage, processing time, and compression ratio.

Owner: Mayank Bajaj (1RV24CI066)
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

st.title("Pipeline Performance")

REPORT_PATH = "evaluation/reports/benchmark_results.csv"

if os.path.exists(REPORT_PATH):
    df = pd.read_csv(REPORT_PATH)

    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Peak RAM — pipeline", f"{latest['pipeline_peak_ram_mb']} MB",
                delta=f"-{latest['ram_saved_mb']} MB vs baseline", delta_color="inverse")
    col2.metric("Processing time", f"{latest['pipeline_time_s']} s",
                delta=f"{latest['speedup']}x faster")
    col3.metric("Lines processed", f"{int(latest['line_count']):,}")

    fig = go.Figure()
    fig.add_bar(name="Baseline", x=df["dataset"], y=df["baseline_peak_ram_mb"],
                marker_color="#D85A30")
    fig.add_bar(name="Pipeline", x=df["dataset"], y=df["pipeline_peak_ram_mb"],
                marker_color="#3B8BD4")
    fig.update_layout(barmode="group", title="Peak RAM: Baseline vs Pipeline (MB)",
                      yaxis_title="MB")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("All benchmark runs")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No benchmark data found yet.")
    st.code("python evaluation/benchmark.py --dataset data/samples/sample.log")
    st.info("Run the command above to generate performance data, then refresh this page.")
