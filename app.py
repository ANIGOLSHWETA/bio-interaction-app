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
st.markdown("Understand WHY interactions happen using AI")

# =====================================
# 4. SEARCH
# =====================================
search = st.text_input("🔍 Search lncRNA or miRNA")

results = df.copy()

if search:
    results = results[
        (results["lncRNA"].str.contains(search, case=False, na=False)) |
        (results["miRNA"].str.contains(search, case=False, na=False))
    ]

# =====================================
# 5. SHOW RESULTS
# =====================================
if len(results) > 0:
    st.success(f"Found {len(results)} interactions")

    display_df = results.head(20)

    st.dataframe(display_df, width='stretch')

    # =====================================
    # SELECT INTERACTION
    # =====================================
    st.subheader("🧠 Select Interaction to Explain")

    selected = st.selectbox(
        "Choose interaction",
        display_df.index
    )

    row = display_df.loc[selected]

    lnc = row["lncRNA"]
    mir = row["miRNA"]
    score = row["Score"]

    # =====================================
    # EXPLANATION PANEL
    # =====================================
    st.subheader("🔬 Interaction Explanation")

    if score > 0.8:
        strength = "Strong"
        meaning = "Very high similarity in biological patterns"
        use = "Highly useful for disease prediction and drug discovery"
    elif score > 0.6:
        strength = "Moderate"
        meaning = "Possible regulatory interaction"
        use = "Useful for further biological validation"
    else:
        strength = "Weak"
        meaning = "Low similarity, less likely interaction"
        use = "May not be biologically significant"

    st.markdown(f"""
    ### 🧬 {lnc} ↔ {mir}

    **📈 Interaction Strength:** {strength} ({score:.2f})

    **🧠 WHY this interaction?**  
    The model found strong similarity between their embeddings, meaning they appear in similar biological contexts.

    **⚙️ HOW was it predicted?**  
    Using Node2Vec, both nodes were converted into vectors.  
    Their similarity (cosine + dot product) indicates interaction likelihood.

    **💊 WHAT is it useful for?**  
    {use}

    **🔬 Biological Meaning:**  
    {lnc} may regulate or influence {mir}, impacting gene expression pathways.
    """)

    # =====================================
    # NETWORK GRAPH
    # =====================================
    st.subheader("🌐 Interaction Network")

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
        marker=dict(size=20, color=node_color)
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    st.plotly_chart(fig, width='stretch')

else:
    st.warning("No interactions found")
