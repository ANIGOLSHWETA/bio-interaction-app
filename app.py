import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# ==============================
# PAGE CONFIG (PRO LEVEL UI)
# ==============================
st.set_page_config(
    page_title="Bio Interaction Intelligence",
    layout="wide"
)

# ==============================
# CUSTOM CSS (INDUSTRY UI)
# ==============================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}
.title {
    font-size: 40px;
    font-weight: bold;
    color: #00F5A0;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
.highlight {
    color: #00F5A0;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv("final_interactions.csv")

# ==============================
# HEADER
# ==============================
st.markdown('<div class="title">🧬 Bio Interaction Intelligence System</div>', unsafe_allow_html=True)

st.markdown("Explore **lncRNA–miRNA interactions** using AI-powered predictions.")

# ==============================
# SEARCH PANEL
# ==============================
st.markdown("### 🔍 Search Interaction")

col1, col2 = st.columns(2)

with col1:
    search_lnc = st.text_input("Enter lncRNA")

with col2:
    search_mir = st.text_input("Enter miRNA")

# ==============================
# SEARCH LOGIC (IMPORTANT)
# ==============================
results = df.copy()

if search_lnc:
    results = results[results["lncRNA"].str.contains(search_lnc, case=False, na=False)]

if search_mir:
    results = results[results["miRNA"].str.contains(search_mir, case=False, na=False)]

# ==============================
# RESULTS DISPLAY
# ==============================
st.markdown("### 📊 Interaction Results")

if len(results) > 0:

    st.dataframe(results.head(20), width='stretch')

    # ==============================
    # INTERACTION GRAPH
    # ==============================
    st.markdown("### 🌐 Interaction Network")

    G = nx.Graph()

    for _, row in results.head(20).iterrows():
        G.add_edge(row["lncRNA"], row["miRNA"], weight=row["Score"])

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=2, color='#888'),
        hoverinfo='none'
    )

    node_x, node_y, node_text, node_color = [], [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        if node in df["lncRNA"].values:
            node_color.append("cyan")
        else:
            node_color.append("orange")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(
            size=20,
            color=node_color,
            line=dict(width=2, color='white')
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='#0f2027'
    )

    st.plotly_chart(fig, width='stretch')

    # ==============================
    # CLICK EXPLANATION PANEL
    # ==============================
    st.markdown("### 🧠 Interaction Explanation")

    selected = st.selectbox(
        "Select interaction to explain",
        results.head(20).index
    )

    row = results.loc[selected]

    score = row["Score"]

    if score > 0.8:
        strength = "Strong Interaction 🟢"
        reason = "Highly similar embedding patterns → likely biological regulation"
    elif score > 0.6:
        strength = "Moderate Interaction 🟠"
        reason = "Partial similarity → possible indirect regulation"
    else:
        strength = "Weak Interaction 🔴"
        reason = "Low similarity → unlikely functional relationship"

    st.markdown(f"""
    <div class="card">
    <h4>🔗 Interaction</h4>
    <p><span class="highlight">{row['lncRNA']}</span> → <span class="highlight">{row['miRNA']}</span></p>

    <h4>📊 Confidence Score</h4>
    <p>{score:.4f}</p>

    <h4>📌 Interpretation</h4>
    <p>{strength}</p>

    <h4>🧬 Why this interaction exists?</h4>
    <p>{reason}</p>

    <h4>💡 Biological Meaning</h4>
    <p>
    lncRNA may regulate miRNA activity, influencing gene expression pathways.
    This helps in disease understanding, drug targeting, and biomarker discovery.
    </p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("❌ No interactions found. Try different search.")
