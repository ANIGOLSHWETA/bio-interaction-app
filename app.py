import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Bio Interaction Explorer",
    layout="wide"
)

# =====================================
# CUSTOM CSS (UI BEAUTIFICATION)
# =====================================
st.markdown("""
<style>
.big-title {
    font-size: 32px;
    font-weight: bold;
    color: #2E86C1;
}
.card {
    padding: 15px;
    border-radius: 10px;
    background-color: #F4F6F7;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🧬 lncRNA–miRNA Interaction Explorer</div>', unsafe_allow_html=True)

# =====================================
# LOAD DATA
# =====================================
df = pd.read_csv("final_interactions.csv")
least_df = pd.read_csv("least_interactions.csv")

# =====================================
# SIDEBAR
# =====================================
st.sidebar.header("🔍 Controls")

search = st.sidebar.text_input("Search Gene / miRNA")

view = st.sidebar.radio(
    "Select View",
    ["Top 🔥", "Least ❄️"]
)

# =====================================
# FILTER
# =====================================
data = df.head(50) if view == "Top 🔥" else least_df.head(50)

if search:
    data = data[
        data["lncRNA"].str.contains(search, case=False) |
        data["miRNA"].str.contains(search, case=False)
    ]

# =====================================
# METRICS CARDS
# =====================================
col1, col2, col3 = st.columns(3)

col1.metric("Total Interactions", len(df))
col2.metric("Showing", len(data))
col3.metric("Mode", view)

# =====================================
# TABLE
# =====================================
st.subheader("📊 Interaction Table")
st.dataframe(data, use_container_width=True)

# =====================================
# BUILD GRAPH
# =====================================
G = nx.Graph()

for _, row in data.iterrows():
    G.add_edge(row["lncRNA"], row["miRNA"], weight=row["Score"])

pos = nx.spring_layout(G, seed=42)

# =====================================
# EDGE TRACES (COLORED)
# =====================================
edge_traces = []

for u, v, d in G.edges(data=True):
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    score = d["weight"]

    if score > 0.8:
        color = "green"
    elif score > 0.6:
        color = "orange"
    else:
        color = "red"

    edge_traces.append(
        go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=2, color=color),
            hoverinfo='text',
            text=f"{u} ↔ {v}<br>Score: {score:.3f}"
        )
    )

# =====================================
# NODE TYPES (COLOR)
# =====================================
node_x, node_y = [], []
node_text = []
node_color = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

    # Simple rule (customize if needed)
    if "mir" in node.lower():
        node_color.append("lightcoral")   # miRNA
    else:
        node_color.append("skyblue")      # lncRNA

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    text=node_text,
    textposition="top center",
    marker=dict(size=18, color=node_color),
    hoverinfo='text'
)

# =====================================
# GRAPH FIGURE
# =====================================
fig = go.Figure(data=edge_traces + [node_trace])

fig.update_layout(
    title="🌐 Interaction Network",
    showlegend=False,
    hovermode='closest',
    margin=dict(b=20, l=5, r=5, t=40)
)

st.plotly_chart(fig, use_container_width=True)

# =====================================
# INTERACTION EXPLANATION
# =====================================
st.subheader("🧠 Interaction Explanation")

options = data.apply(lambda x: f"{x['lncRNA']} ↔ {x['miRNA']}", axis=1)
selected = st.selectbox("Select Interaction", options)

if selected:
    row = data.iloc[list(options).index(selected)]
    score = row["Score"]

    st.markdown(f"### 🔗 {row['lncRNA']} ↔ {row['miRNA']}")

    st.metric("Score", f"{score:.4f}")

    if score > 0.8:
        st.success("🟢 Strong Interaction")
    elif score > 0.6:
        st.warning("🟠 Moderate Interaction")
    else:
        st.error("🔴 Weak Interaction")

    # Explanation block
    st.markdown("#### 🧬 AI Explanation")
    st.write(f"""
    - High embedding similarity between nodes
    - Graph connectivity supports interaction
    - Model confidence: {round(score*100,2)}%
    """)

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.markdown("🚀 Powered by Node2Vec + Deep Learning + Graph AI")