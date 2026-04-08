import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# =====================================
# CONFIG
# =====================================
st.set_page_config(page_title="lncRNA–miRNA Interaction Explorer", layout="wide")

st.title("🧬 lncRNA–miRNA Interaction Explorer")
st.markdown("Explore predicted interactions with Explainable AI insights")

# =====================================
# LOAD DATA
# =====================================
df = pd.read_csv("final_predictions.csv")

# 👉 FILTER ONLY lncRNA-miRNA
df = df[
    (df["Node1"].str.contains("lnc", case=False)) &
    (df["Node2"].str.contains("mir", case=False))
]

# =====================================
# SEARCH BAR
# =====================================
search = st.text_input("🔍 Search lncRNA or miRNA")

if search:
    df = df[
        df["Node1"].str.contains(search, case=False) |
        df["Node2"].str.contains(search, case=False)
    ]

# =====================================
# BUILD GRAPH
# =====================================
G = nx.Graph()

for _, row in df.head(50).iterrows():
    G.add_edge(row["Node1"], row["Node2"], weight=row["Score"])

pos = nx.spring_layout(G, seed=42)

# =====================================
# NODE COLORS
# =====================================
node_colors = []
for node in G.nodes():
    if "lnc" in node.lower():
        node_colors.append("blue")
    else:
        node_colors.append("red")

# =====================================
# EDGE COLORS
# =====================================
edge_colors = []
for u, v, d in G.edges(data=True):
    score = d["weight"]
    if score > 0.8:
        edge_colors.append("green")
    elif score > 0.6:
        edge_colors.append("orange")
    else:
        edge_colors.append("red")

# =====================================
# PLOTLY GRAPH
# =====================================
edge_x = []
edge_y = []

for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

node_x = []
node_y = []
texts = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    texts.append(node)

fig = go.Figure()

# edges
fig.add_trace(go.Scatter(
    x=edge_x, y=edge_y,
    mode='lines',
    line=dict(width=2, color='gray'),
    hoverinfo='none'
))

# nodes
fig.add_trace(go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=texts,
    textposition="top center",
    marker=dict(
        size=20,
        color=node_colors
    )
))

fig.update_layout(
    title="🌐 Interaction Network",
    showlegend=False,
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# =====================================
# EXPLANATION PANEL
# =====================================
st.subheader("📊 Interaction Explanation")

selected = st.selectbox(
    "Select Interaction",
    df.apply(lambda x: f"{x['Node1']} ↔ {x['Node2']}", axis=1)
)

row = df[df.apply(lambda x: f"{x['Node1']} ↔ {x['Node2']}", axis=1) == selected].iloc[0]

score = row["Score"]

st.markdown(f"""
### 🔬 Interaction Details

- **lncRNA:** {row['Node1']}
- **miRNA:** {row['Node2']}
- **Prediction Score:** `{score:.4f}`

---

### 🧠 Explainable AI Insight

- High embedding similarity → strong biological relation  
- Graph proximity → nodes share neighbors  
- Model confidence → {("HIGH" if score > 0.8 else "MEDIUM" if score > 0.6 else "LOW")}

---

### 📌 Biological Meaning

- lncRNA may regulate miRNA activity  
- Could impact gene expression pathways  
- Potential biomarker or therapeutic target
""")

# =====================================
# TOP INTERACTIONS TABLE
# =====================================
st.subheader("🔥 Top Interactions")
st.dataframe(df.head(20))
