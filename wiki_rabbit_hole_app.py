import streamlit as st
import json
from anytree import Node, RenderTree
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Wikipedia Rabbit Hole Tracker", layout="wide")

# ---- Session Setup ----
if "data" not in st.session_state:
    st.session_state["data"] = {"pages": {}}

data = st.session_state["data"]

# ---- Helper Functions ----
def add_page(title, parent=None, url=None):
    pages = data["pages"]
    if title not in pages:
        pages[title] = {
            "url": url or "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "children": []
        }
    if parent and parent in pages:
        if title not in pages[parent]["children"]:
            pages[parent]["children"].append(title)

def build_tree(data):
    nodes = {t: Node(t) for t in data["pages"]}
    for title, info in data["pages"].items():
        for child in info["children"]:
            nodes[child].parent = nodes[title]
    return nodes

def plot_tree(data):
    if not data["pages"]:
        st.info("No pages added yet.")
        return

    nodes = build_tree(data)
    all_children = {c for v in data["pages"].values() for c in v["children"]}
    roots = [t for t in data["pages"] if t not in all_children]

    # Build simple coordinate layout
    labels = list(data["pages"].keys())
    x = list(range(len(labels)))
    y = [-i for i in range(len(labels))]
    edge_x, edge_y = [], []

    for title, info in data["pages"].items():
        for child in info["children"]:
            edge_x += [x[labels.index(title)], x[labels.index(child)], None]
            edge_y += [y[labels.index(title)], y[labels.index(child)], None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#aaa")))
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(size=10, color="#4CAF50")
    ))
    fig.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True)

# ---- Streamlit UI ----
st.title("🐇 Wikipedia Rabbit Hole Tracker")

st.subheader("➕ Add a Page")
with st.form("add_page_form"):
    title = st.text_input("Page Title")
    parent = st.selectbox("Parent Page (optional)", [""] + list(data["pages"].keys()))
    url = st.text_input("Wikipedia URL (optional)")
    submitted = st.form_submit_button("Add Page")
    if submitted and title:
        add_page(title, parent if parent else None, url)
        st.success(f"Added: {title}")
        st.rerun()

st.subheader("🌳 Your Personal Exploration Tree")
plot_tree(data)

if data["pages"]:
    st.subheader("📖 Page Details")
    selected = st.selectbox("Select a page", list(data["pages"].keys()))
    page = data["pages"][selected]
    if page["url"]:
        st.markdown(f"**URL:** [{page['url']}]({page['url']})")
    st.write(f"Visited: {page['timestamp']}")
