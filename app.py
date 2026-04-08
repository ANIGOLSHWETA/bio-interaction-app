# =====================================
# 1. IMPORTS
# =====================================
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="Bio Interaction Explorer", layout="wide")

# =====================================
# 2. LOAD DATA
# =====================================
@st.cache_data
def load_data():
    return pd.read_csv("final_interactions.csv")

df = load_data()

# =====================================
# 3. TITLE
# =====================================
st.title("🧬 lncRNA–miRNA Interaction Explorer")
st.markdown("Explore predicted biological interactions using AI")

# =====================================
# 4. TOP INTERACTIONS 🔥
# =====================================
st.subheader("🔥 Top Interactions")
top_df = df.sort_values(by="Score", ascending=False).head(10)
st.dataframe(top_df, width='stretch')

# =====================================
# 5. LEAST INTERACTIONS ❄️
# =====================================
st.subheader("❄️ Least Interactions")
least_df = df.sort_values(by="Score", ascending=True).head(10)
st.dataframe(least_df, width='stretch')

# =====================================
# 6. SEARCH (FULL DATASET)
# =====================================
st.subheader("🔍 Search Any lncRNA / miRNA")

search = st.text_input("Enter gene or miRNA name")

# ALWAYS start from FULL dataset
results = df.copy()

# Filter if user types
if search:
    results = results[
        (results["lncRNA"].str.contains(search, case=False, na=False)) |
        (results["miRNA"].str.contains(search, case=False, na=False))
    ]

# =====================================
# 7. OPTIONAL SCORE FILTER
# =====================================
min_score = st.slider("Minimum Interaction Score", 0.0, 1.0, 0.0)
results = results[results["Score"] >= min_score]

# =====================================
# 8. DISPLAY RESULTS
# =====================================
if len(results) > 0:
    st.success(f"✅ Found {len(results)} interactions")

    st.subheader("📊 Matching Interactions")
    st.dataframe(results.head(20), width='stretch')

    # =====================================
    # 9. NETWORK GRAPH 🌐
    # =====================================
    st.subheader("🌐 Interaction Network")

    G = nx.Graph()

    for _, row in results.head(20).iterrows():
        G.add_edge(row["lncRNA"], row["miRNA"], weight=row["Score"])

    pos = nx.spring_layout(G, seed=42)

    # EDGES
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
        line=dict(width=2, color='gray'),
        hoverinfo='none'
    )

    # NODES
    node_x, node_y, node_text, node_color = [], [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        # Color logic
        if "mir" in node.lower():
            node_color.append("red")   # miRNA
        else:
            node_color.append("blue")  # lncRNA

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(
            size=20,
            color=node_color,
            line=dict(width=2, color='black')
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig, width='stretch')

else:
    st.warning("❌ No interactions found")

# =====================================
# 10. EXPLANATION PANEL 🧠
# =====================================
st.subheader("🧠 How to Interpret")

st.markdown("""
- 🔴 **Red nodes** → miRNA  
- 🔵 **Blue nodes** → lncRNA  
- 📈 **Score** → Probability of interaction  
- 🔥 High score → Strong interaction  
- ❄️ Low score → Weak interaction  

💡 Search explores FULL dataset → helps find novel interactions
""")
