import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import time

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="Bio Interaction AI", layout="wide")

# =====================================
# SIDEBAR (DASHBOARD NAVIGATION)
# =====================================
st.sidebar.title("🧬 Navigation")

page = st.sidebar.radio("Go to", [
    "🔍 Search",
    "🔥 Top Interactions",
    "❄️ Least Interactions"
])

theme = st.sidebar.toggle("🌗 Dark / Light Mode", value=True)

# =====================================
# THEME STYLES
# =====================================
if theme:
    bg = "linear-gradient(135deg, #1a0033, #3a0ca3, #7209b7)"
    text = "white"
else:
    bg = "linear-gradient(135deg, #f5f7fa, #c3cfe2)"
    text = "black"

st.markdown(f"""
<style>
body {{
    background: {bg};
    color: {text};
}}

.title {{
    font-size: 45px;
    font-weight: bold;
    text-align: center;
    color: #f72585;
}}

.card {{
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}}
</style>
""", unsafe_allow_html=True)

# =====================================
# LOADING ANIMATION
# =====================================
with st.spinner("🧠 AI is analyzing biological interactions..."):
    time.sleep(2)

# =====================================
# LOAD DATA
# =====================================
df = pd.read_csv("final_interactions.csv")

# =====================================
# HEADER
# =====================================
st.markdown('<div class="title">🧬 Bio Interaction AI System</div>', unsafe_allow_html=True)

# =====================================
# SEARCH PAGE
# =====================================
if page == "🔍 Search":

    st.subheader("🔍 Search lncRNA–miRNA Interaction")

    col1, col2 = st.columns(2)

    with col1:
        search_lnc = st.text_input("Enter lncRNA")

    with col2:
        search_mir = st.text_input("Enter miRNA")

    results = df.copy()

    if search_lnc:
        results = results[results["lncRNA"].str.contains(search_lnc, case=False)]

    if search_mir:
        results = results[results["miRNA"].str.contains(search_mir, case=False)]

    if len(results) > 0:

        st.dataframe(results.head(20), width='stretch')

        # =====================================
        # NEON GRAPH
        # =====================================
        st.subheader("🌐 Interaction Network")

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
            line=dict(width=2, color='#888')
        )

        node_x, node_y, node_color, node_text = [], [], [], []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)

            if node in df["lncRNA"].values:
                node_color.append("#00F5A0")  # neon green
            else:
                node_color.append("#FF00FF")  # neon pink

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=20,
                color=node_color,
                line=dict(width=3, color="white")
            )
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='white'
        )

        st.plotly_chart(fig, width='stretch')

        # =====================================
        # EXPLANATION PANEL
        # =====================================
        st.subheader("🧠 AI Explanation")

        selected = st.selectbox("Select interaction", results.index)

        row = results.loc[selected]
        score = row["Score"]

        if score > 0.8:
            strength = "Strong 🟢"
        elif score > 0.6:
            strength = "Moderate 🟠"
        else:
            strength = "Weak 🔴"

        st.markdown(f"""
        <div class="card">
        <h3>🔗 {row['lncRNA']} → {row['miRNA']}</h3>
        <p><b>Score:</b> {score:.4f}</p>
        <p><b>Strength:</b> {strength}</p>
        <p><b>Explanation:</b> Based on embedding similarity from Node2Vec + deep learning model.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("No results found")

# =====================================
# TOP INTERACTIONS
# =====================================
elif page == "🔥 Top Interactions":

    st.subheader("🔥 Top Interactions")

    top_df = df.sort_values(by="Score", ascending=False).head(20)
    st.dataframe(top_df, width='stretch')

# =====================================
# LEAST INTERACTIONS
# =====================================
elif page == "❄️ Least Interactions":

    st.subheader("❄️ Least Interactions")

    low_df = df.sort_values(by="Score", ascending=True).head(20)
    st.dataframe(low_df, width='stretch')
