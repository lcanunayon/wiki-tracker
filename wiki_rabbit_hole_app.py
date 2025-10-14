import streamlit as st
from anytree import Node, RenderTree
import plotly.graph_objects as go
from datetime import datetime

# --- Session Setup ---
if "data" not in st.session_state:
    st.session_state["data"] = {"pages": {}}  # unique for each user session

data = st.session_state["data"]

# --- Helper functions (local only) ---
def add_page(title, parent=None, url=None):
    pages = data["pages"]

    if title not in pages:
        pages[title] = {
            "url": url or f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
            "children": [],
            "timestamp": datetime.now().isoformat()
        }

    if parent and parent in pages:
        if title not in pages[parent]["children"]:
            pages[parent]["children"].append(title)

def build_tree(data):
    nodes = {}
    for title in data["pages"]:
        nodes[title] = Node(title)
    for title, info in data["pages"].items():
        for child in info["children"]:
            nodes[child].parent = nodes[title]
    return nodes

def plot_tree(data):
    if not data["pages"]:
        st.info("No pages added yet.")
        return

    nodes = build_tree(data)
    edges = []
    for title, info in data["pages"].items():
        for child in info["children"]:
            edges.append((title, child))

    labels = list(data["pages"].keys())
    label_to_idx = {label: i for i, label in enumerate(labels)}
    x, y = [], []
    for i, label in enumerate(labels):
        x.append(i)
        y.append(-i % 5)

    edge_x, edge_y = [], []
    for parent, child in edges:
        edge_x += [label_to_idx[parent], label_to_idx[child], None]
        edge_y += [y[label_to_idx[parent]], y[label_to_idx[child]], None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#aaa")))
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(size=10, color="#00cc96")
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- App UI ---
st.title("🐇 Wikipedia Rabbit Hole Tracker (Your Personal Session)")

st.subheader("➕ Add a Page")
with st.form("add_page_form"):
    title = st.text_input("Wikipedia Page Title")
    parent = st.selectbox("Parent Page (optional)", [None] + list(data["pages"].keys()))
    url = st.text_input("Custom URL (optional)")
    submitted = st.form_submit_button("Add Page")
    if submitted and title:
        add_page(title, parent, url)
        st.success(f"Added: {title}")

st.subheader("🌳 Your Personal Exploration Tree")
plot_tree(data)

st.subheader("📖 Page Details")
if data["pages"]:
    selected = st.selectbox("Select a page", list(data["pages"].keys()))
    page = data["pages"][selected]
    st.markdown(f"**URL:** [{page['url']}]({page['url']})")
    st.write(f"Visited: {page['timestamp']}")