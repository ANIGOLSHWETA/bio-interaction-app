import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Bio Interaction Explorer",
    layout="wide",
    page_icon="🧬"
)

# =====================================
# CUSTOM CSS (BEAUTIFUL UI)
# =====================================
st.markdown("""
<style>
.main {
    background-color: #0e1117;
    color: white;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background: linear-gradient(135deg, #1f4037, #99f2c8);
    color: black;
    margin-bottom: 15px;
}
.metric {
    font-size: 20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# TITLE
# =====================================
st.title("🧬 Bio-Interaction Intelligence System")
st.markdown("Explore predicted biological relationships with explainable AI")

# =====================================
# LOAD DATA
# =====================================
@st.cache_data
def load_data():
    df = pd.read_csv("final_predictions.csv")
    exp_df = pd.read_csv("explanations.csv")
    via_df = pd.read_csv("via_related_predictions.csv")
    return df, exp_df, via_df

df, exp_df, via_df = load_data()

# =====================================
# SIDEBAR FILTERS
# =====================================
st.sidebar.header("🔍 Filters")

threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.6)

node_search = st.sidebar.text_input("Search Node")

filtered_df = df[df["Score"] > threshold]

if node_search:
    filtered_df = filtered_df[
        (filtered_df["Node1"] == node_search) |
        (filtered_df["Node2"] == node_search)
    ]

# =====================================
# TOP METRICS
# =====================================
col1, col2, col3 = st.columns(3)

col1.markdown(f"<div class='card'><div class='metric'>Total Predictions</div>{len(df)}</div>", unsafe_allow_html=True)
col2.markdown(f"<div class='card'><div class='metric'>High Confidence</div>{len(df[df['Score']>0.8])}</div>", unsafe_allow_html=True)
col3.markdown(f"<div class='card'><div class='metric'>Filtered Results</div>{len(filtered_df)}</div>", unsafe_allow_html=True)

# =====================================
# TABLE VIEW
# =====================================
st.subheader("📊 Predicted Interactions")
st.dataframe(filtered_df.head(50), use_container_width=True)

# =====================================
# SELECT INTERACTION
# =====================================
st.subheader("🔬 Interaction Explorer")

if len(filtered_df) > 0:
    selected_index = st.selectbox(
        "Select Interaction",
        filtered_df.index
    )

    row = filtered_df.loc[selected_index]

    st.markdown(f"""
    <div class='card'>
    <h3>{row['Node1']} ↔ {row['Node2']}</h3>
    <p>Score: <b>{row['Score']:.3f}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # =====================================
    # EXPLANATION
    # =====================================
    exp_row = exp_df[
        (exp_df["Node1"] == row["Node1"]) &
        (exp_df["Node2"] == row["Node2"])
    ]

    if not exp_row.empty:
        exp_row = exp_row.iloc[0]

        st.subheader("🧠 Why this interaction?")

        col1, col2 = st.columns(2)

        col1.metric("Cosine Similarity", round(exp_row["Cosine_Similarity"], 3))
        col2.metric("Common Neighbors", int(exp_row["Common_Neighbors"]))

        if row["Score"] > 0.8:
            st.success("🔥 Strong Biological Interaction")
        elif row["Score"] > 0.6:
            st.warning("⚠️ Moderate Interaction")
        else:
            st.error("❄️ Weak Interaction")

# =====================================
# GRAPH VISUALIZATION (INTERACTIVE)
# =====================================
st.subheader("🌐 Network Visualization")

G = nx.Graph()

for _, r in filtered_df.head(30).iterrows():
    G.add_edge(r["Node1"], r["Node2"], weight=r["Score"])

pos = nx.spring_layout(G, seed=42)

edge_x = []
edge_y = []

for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1),
    hoverinfo='none',
    mode='lines'
)

node_x = []
node_y = []
node_text = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=node_text,
    textposition="top center",
    marker=dict(size=10)
)

fig = go.Figure(data=[edge_trace, node_trace])

fig.update_layout(
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# =====================================
# VIA RELATIONSHIPS
# =====================================
st.subheader("🔗 Indirect (Via) Relationships")

st.dataframe(via_df.head(20), use_container_width=True)

# =====================================
# DOWNLOAD BUTTONS
# =====================================
st.subheader("⬇️ Download Results")

st.download_button("Download Predictions", df.to_csv(index=False), "predictions.csv")
st.download_button("Download Via Relations", via_df.to_csv(index=False), "via_relations.csv")
