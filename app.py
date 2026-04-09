# =====================================
# 1. IMPORTS
# =====================================
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="Bio Interaction Explorer", layout="wide")

# =====================================
# 2. CUSTOM CSS 🎨
# =====================================
st.markdown("""
<style>
.main {
    background: linear-gradient(to right, #eef2f3, #ffffff);
}

.big-title {
    font-size: 40px;
    font-weight: bold;
    color: #2c3e50;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}

.badge-strong {
    background-color: #2ecc71;
    color: white;
    padding: 5px 10px;
    border-radius: 10px;
}

.badge-medium {
    background-color: #f39c12;
    color: white;
    padding: 5px 10px;
    border-radius: 10px;
}

.badge-weak {
    background-color: #e74c3c;
    color: white;
    padding: 5px 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# 3. LOAD DATA
# =====================================
@st.cache_data
def load_data():
    return pd.read_csv("final_interactions.csv")

df = load_data()

# =====================================
# 4. HEADER
# =====================================
st.markdown('<div class="big-title">🧬 lncRNA–miRNA Interaction Explorer</div>', unsafe_allow_html=True)
st.markdown("### 🔬 Explainable AI for Biological Interaction Discovery")

# =====================================
# 5. SEARCH BAR
# =====================================
search = st.text_input("🔍 Search any lncRNA or miRNA")

results = df.copy()

if search:
    results = results[
        (results["lncRNA"].str.contains(search, case=False, na=False)) |
        (results["miRNA"].str.contains(search, case=False, na=False))
    ]

# =====================================
# 6. METRICS CARDS
# =====================================
col1, col2, col3 = st.columns(3)

col1.metric("Total Interactions", len(df))
col2.metric("Matching Results", len(results))
col3.metric("Max Score", round(df["Score"].max(), 2))

# =====================================
# 7. RESULTS TABLE
# =====================================
if len(results) > 0:

    st.markdown("## 📊 Results")

    display_df = results.head(20)
    st.dataframe(display_df, width='stretch')

    # =====================================
    # 8. SELECT INTERACTION
    # =====================================
    st.markdown("## 🧠 Explain Interaction")

    selected = st.selectbox("Choose interaction", display_df.index)
    row = display_df.loc[selected]

    lnc = row["lncRNA"]
    mir = row["miRNA"]
    score = row["Score"]

    # =====================================
    # 9. BADGE LOGIC
    # =====================================
    if score > 0.8:
        badge = '<span class="badge-strong">Strong</span>'
        use = "High confidence → Drug discovery & disease research"
    elif score > 0.6:
        badge = '<span class="badge-medium">Moderate</span>'
        use = "Potential interaction → Needs validation"
    else:
        badge = '<span class="badge-weak">Weak</span>'
        use = "Low confidence → Less biological relevance"

    # =====================================
    # 10. EXPLANATION CARD
    # =====================================
    st.markdown(f"""
    <div class="card">
    <h3>🧬 {lnc} ↔ {mir}</h3>
    <p><b>Interaction Strength:</b> {badge} ({score:.2f})</p>

    <p><b>🧠 WHY?</b><br>
    Similar embedding patterns suggest biological co-functionality.</p>

    <p><b>⚙️ HOW?</b><br>
    Node2Vec converts nodes into vectors → similarity = interaction probability.</p>

    <p><b>💊 USE?</b><br>
    {use}</p>
    </div>
    """, unsafe_allow_html=True)

    # =====================================
    # 11. NETWORK GRAPH
    # =====================================
    st.markdown("## 🌐 Interaction Network")

    G = nx.Graph()

    for _, r in display_df.iterrows():
        G.add_edge(r["lncRNA"], r["miRNA"], weight=r["Score"])

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines')

    node_x, node_y, node_text, node_color = [], [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        if "mir" in node.lower():
            node_color.append("red")
        else:
            node_color.append("blue")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        marker=dict(size=22, color=node_color)
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))

    st.plotly_chart(fig, width='stretch')

else:
    st.warning("❌ No interactions found")
