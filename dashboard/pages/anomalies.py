"""
anomalies.py — Dashboard page: Anomaly Explorer.

Owner: Mayank Bajaj (1RV24CI066)
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from pipeline.storage import load_parquet

st.title("Anomaly Explorer")

uploaded = st.file_uploader("Upload a processed Parquet file", type=["parquet"])

if uploaded:
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    logs = load_parquet(tmp_path)
    os.unlink(tmp_path)
    df = pd.DataFrame(logs)

    anomalies = df[df["is_anomaly"] == True]
    normal = df[df["is_anomaly"] == False]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total entries", f"{len(df):,}")
    col2.metric("Anomalies", f"{len(anomalies):,}", delta=f"{len(anomalies)/len(df)*100:.1f}%")
    col3.metric("Normal entries", f"{len(normal):,}")

    fig = px.histogram(df, x="anomaly_score", color="is_anomaly",
                       nbins=50,
                       title="Anomaly Score Distribution",
                       labels={"anomaly_score": "Isolation Forest Score", "is_anomaly": "Anomaly"},
                       color_discrete_map={True: "#D85A30", False: "#3B8BD4"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Flagged anomalous entries")
    st.dataframe(
        anomalies[["raw", "template", "anomaly_score"]].sort_values("anomaly_score"),
        use_container_width=True,
    )
else:
    st.info("Run the pipeline first, then upload the Parquet output file here.")
