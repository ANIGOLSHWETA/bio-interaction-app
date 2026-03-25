
import streamlit as st
import pandas as pd
from pyvis.network import Network

st.set_page_config(layout="wide")

st.title("🧬 Biological Interaction Prediction System")

df = pd.read_csv("final_predictions.csv")
least_df = pd.read_csv("least_related_predictions.csv")
via_df = pd.read_csv("via_related_predictions.csv")

threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.6)

tab1, tab2, tab3 = st.tabs(["Top", "Least", "Via"])

with tab1:
    filtered_df = df[df["Score"] >= threshold]

    net = Network(height="600px", width="100%", bgcolor="#111", font_color="white")

    for _, row in filtered_df.head(100).iterrows():
        net.add_node(row["Node1"])
        net.add_node(row["Node2"])
        net.add_edge(row["Node1"], row["Node2"], title=str(row["Score"]))

    net.save_graph("graph.html")

    with open("graph.html", "r") as f:
        st.components.v1.html(f.read(), height=600)

    st.dataframe(filtered_df.head(20))

with tab2:
    st.dataframe(least_df)

with tab3:
    st.dataframe(via_df)
