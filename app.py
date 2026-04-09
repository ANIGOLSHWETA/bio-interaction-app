import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Bio Interaction Explorer", layout="wide")

# ==============================
# CLEAN BEAUTIFUL UI
# ==============================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f3e8ff, #e0c3fc);
    color: #2b2b2b;
}

.title {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
    color: #6a0dad;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.highlight {
    color: #6a0dad;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv("final_interactions.csv")

# ==============================
# TITLE
# ==============================
st.markdown('<div class="title">🧬 lncRNA–miRNA Interaction Explorer</div>', unsafe_allow_html=True)

# ==============================
# INPUT
# ==============================
st.subheader("🔍 Search Interaction")

col1, col2 = st.columns(2)

with col1:
    lnc_input = st.text_input("Enter lncRNA")

with col2:
    mir_input = st.text_input("Enter miRNA")

# ==============================
# SEARCH LOGIC
# ==============================
results = df.copy()

if lnc_input:
    results = results[results["lncRNA"].str.contains(lnc_input, case=False)]

if mir_input:
    results = results[results["miRNA"].str.contains(mir_input, case=False)]

# ==============================
# OUTPUT
# ==============================
if len(results) > 0:

    st.subheader("📊 Matching Interactions")

    st.dataframe(results.head(10), width='stretch')

    # ==============================
    # SELECT ONE INTERACTION
    # ==============================
    selected = st.selectbox("Select interaction", results.index)
    row = results.loc[selected]

    score = row["Score"]
    prediction = "Interaction Exists ✅" if score > 0.5 else "No Strong Interaction ❌"

    # ==============================
    # EXPLANATION CARD
    # ==============================
    st.markdown(f"""
    <div class="card">
    <h3>🔗 {row['lncRNA']} → {row['miRNA']}</h3>

    <p><b>📊 Confidence Score:</b> {score:.4f}</p>
    <p><b>🧠 Prediction:</b> {prediction}</p>

    <p><b>💡 Why this interaction is useful?</b><br>
    This interaction suggests that the lncRNA may regulate the miRNA,
    influencing gene expression pathways. Such interactions are important in:
    <ul>
        <li>Disease prediction</li>
        <li>Drug target discovery</li>
        <li>Understanding gene regulation</li>
    </ul>
    </p>

    <p><b>🔍 How model predicted?</b><br>
    Based on Node2Vec embeddings + similarity patterns + deep learning classification.
    </p>
    </div>
    """, unsafe_allow_html=True)

    # ==============================
    # GRAPH VISUALIZATION
    # ==============================
    st.subheader("🌐 Interaction Graph")

    G = nx.Graph()
    G.add_edge(row["lncRNA"], row["miRNA"], weight=score)

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines')

    node_x, node_y, node_text = [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        marker=dict(size=25, color=["purple", "orange"])
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    st.plotly_chart(fig, width='stretch')

    # ==============================
    # GLOBAL INSIGHTS
    # ==============================
    st.subheader("📈 Global Interaction Insights")

    col1, col2 = st.columns(2)

    # Top
    with col1:
        st.markdown("### 🔥 Top Predictions")
        top_df = df.sort_values(by="Score", ascending=False).head(5)
        st.dataframe(top_df, width='stretch')

    # Least
    with col2:
        st.markdown("### ❄️ Least Predictions")
        low_df = df.sort_values(by="Score", ascending=True).head(5)
        st.dataframe(low_df, width='stretch')

    # ==============================
    # UNIQUE VISUALIZATION (DISTRIBUTION)
    # ==============================
    st.subheader("📊 Score Distribution")

    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(x=df["Score"], nbinsx=20))

    st.plotly_chart(fig2, width='stretch')

else:
    st.warning("❌ No matching interactions found")
