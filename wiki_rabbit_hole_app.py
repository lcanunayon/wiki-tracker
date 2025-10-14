import streamlit as st
import json
import os
from anytree import Node, RenderTree
import plotly.graph_objects as go
from datetime import datetime
import webbrowser

DATA_FILE = "wiki_history.json"

# ---- Data Management ----
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"pages": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_page(title, parent=None, url=None):
    data = load_data()
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

    save_data(data)

# ---- Build Tree ----
def build_tree(data):
    nodes = {}
    for title in data["pages"]:
        nodes[title] = Node(title)
    for title, info in data["pages"].items():
        for child in info["children"]:
            nodes[child].parent = nodes[title]
    return nodes

# ---- Plotly Tree ----
def plot_tree(data):
    if not data["pages"]:
        st.info("No pages added yet.")
        return

    nodes = build_tree(data)

    # Find root nodes
    all_children = {c for v in data["pages"].values() for c in v["children"]}
    roots = [t for t in data["pages"] if t not in all_children]

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
        x=x,
        y=y,
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

# ---- Streamlit App ----
st.title("🐇 Wikipedia Rabbit Hole Tracker")

data = load_data()

st.subheader("➕ Add a Page")
with st.form("add_page_form"):
    title = st.text_input("Wikipedia Page Title")
    parent = st.selectbox("Parent Page (optional)", [None] + list(data["pages"].keys()))
    url = st.text_input("Custom URL (optional)")
    submitted = st.form_submit_button("Add Page")
    if submitted and title:
        add_page(title, parent, url)
        st.success(f"Added: {title}")
        st.rerun()

st.subheader("🌳 Your Exploration Tree")
plot_tree(data)

st.subheader("📖 Page Details")
if data["pages"]:
    selected = st.selectbox("Select a page", list(data["pages"].keys()))
    page = data["pages"][selected]
    st.markdown(f"**URL:** [{page['url']}]({page['url']})")
    st.write(f"Visited: {page['timestamp']}")
    if st.button("Open in browser"):
        webbrowser.open(page["url"])
