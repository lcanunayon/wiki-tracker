@@ -1,26 +1,16 @@
import streamlit as st
import json
import os
from anytree import Node, RenderTree
import plotly.graph_objects as go
from datetime import datetime
import webbrowser

DATA_FILE = "wiki_history.json"
# --- Session Setup ---
if "data" not in st.session_state:
    st.session_state["data"] = {"pages": {}}  # unique for each user session

# ---- Data Management ----
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"pages": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
data = st.session_state["data"]

# --- Helper functions (local only) ---
def add_page(title, parent=None, url=None):
    data = load_data()
    pages = data["pages"]

    if title not in pages:
@@ -34,9 +24,6 @@ def add_page(title, parent=None, url=None):
        if title not in pages[parent]["children"]:
            pages[parent]["children"].append(title)

    save_data(data)

# ---- Build Tree ----
def build_tree(data):
    nodes = {}
    for title in data["pages"]:
@@ -46,18 +33,12 @@ def build_tree(data):
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
@@ -78,8 +59,7 @@ def plot_tree(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#aaa")))
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        x=x, y=y,
        mode="markers+text",
        text=labels,
        textposition="top center",
@@ -95,10 +75,8 @@ def plot_tree(data):
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- Streamlit App ----
st.title("🐇 Wikipedia Rabbit Hole Tracker")

data = load_data()
# --- App UI ---
st.title("🐇 Wikipedia Rabbit Hole Tracker (Your Personal Session)")

st.subheader("➕ Add a Page")
with st.form("add_page_form"):
@@ -109,16 +87,13 @@ def plot_tree(data):
    if submitted and title:
        add_page(title, parent, url)
        st.success(f"Added: {title}")
        st.rerun()

st.subheader("🌳 Your Exploration Tree")
st.subheader("🌳 Your Personal Exploration Tree")
plot_tree(data)

st.subheader("📖 Page Details")
if data["pages"]:
    selected = st.selectbox("Select a page", list(data["pages"].keys()))
    page = data["pages"][selected]
    st.markdown(f"**URL:** [{page['url']}]({page['url']})")
    st.write(f"Visited: {page['timestamp']}")
    if st.button("Open in browser"):
        webbrowser.open(page["url"])
    st.write(f"Visited: {page['timestamp']}")
