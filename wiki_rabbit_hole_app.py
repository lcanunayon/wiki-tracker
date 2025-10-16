import streamlit as st
from anytree import Node
import plotly.graph_objects as go
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import json
import sys

st.write("Python version:", sys.version)

# -------------------------------
# 🔥 Firebase Configuration (Admin SDK)
# -------------------------------
# Load credentials from Streamlit Secrets
firebase_config = st.secrets["FIREBASE"]
default_app = firebase_admin.initialize_app()

# Convert to a dict for Firebase Admin SDK
cred = credentials.Certificate(json.loads(json.dumps(firebase_config)))

# Initialize Firebase app only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://wiki-rabbit-hole-default-rtdb.firebaseio.com'
    })

# Reference to your database
ref = db.reference("/")

# Example helper functions
def save_page(user_id, page_title, parent=None, url=None):
    data = {
        "url": url or f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
        "parent": parent,
        "timestamp": datetime.now().isoformat()
    }
    ref.child("users").child(user_id).child("pages").child(page_title).set(data)

def get_pages(user_id):
    pages = ref.child("users").child(user_id).child("pages").get()
    return pages or {}

# Example usage (temporary testing)
user_id = "demo_user"
save_page(user_id, "Quantum Mechanics")
st.write("Pages:", get_pages(user_id))

# -------------------------------
# 🌐 User Session Setup
# -------------------------------
st.set_page_config(page_title="Wikipedia Rabbit Hole Tracker", layout="wide")
st.title("🐇 Wikipedia Rabbit Hole Tracker")
st.caption("Your personal Wikipedia exploration tree — automatically saved online!")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "pages" not in st.session_state:
    st.session_state.pages = {}

# -------------------------------
# 🔐 Simple User Login / Signup
# -------------------------------
st.sidebar.header("Login or Create Session")
user_name = st.sidebar.text_input("Enter a username to start", placeholder="e.g. angelo123")
if st.sidebar.button("Start Session"):
    if user_name:
        st.session_state.user_id = user_name
        # Load data if exists, else start fresh
        data = db.child("users").child(user_name).get().val()
        st.session_state.pages = data or {}
        st.sidebar.success(f"Welcome {user_name}!")
    else:
        st.sidebar.error("Please enter a username")

if not st.session_state.user_id:
    st.stop()

# -------------------------------
# 🌱 Core Functions
# -------------------------------
def save_data():
    db.child("users").child(st.session_state.user_id).set(st.session_state.pages)

def add_page(title, parent=None, url=None):
    pages = st.session_state.pages
    if title not in pages:
        pages[title] = {
            "url": url or f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
            "children": [],
            "timestamp": datetime.now().isoformat()
        }
    if parent and parent in pages and title not in pages[parent]["children"]:
        pages[parent]["children"].append(title)
    save_data()

def build_tree():
    pages = st.session_state.pages
    nodes = {t: Node(t) for t in pages}
    for title, info in pages.items():
        for child in info["children"]:
            if child in nodes:
                nodes[child].parent = nodes[title]
    return nodes

def plot_tree():
    pages = st.session_state.pages
    if not pages:
        st.info("No pages yet — start by adding one!")
        return

    nodes = build_tree()
    all_children = {c for v in pages.values() for c in v["children"]}
    roots = [t for t in pages if t not in all_children]

    # Recursive layout (tree)
    positions = {}
    def layout(node, x=0, y=0, dx=2):
        positions[node.name] = (x, y)
        children = list(node.children)
        n = len(children)
        for i, child in enumerate(children):
            layout(child, x + (i - n / 2) * dx, y - 1, dx / 1.8)

    for root in roots:
        layout(nodes[root])

    edge_x, edge_y = [], []
    for t, info in pages.items():
        for child in info["children"]:
            if child in positions:
                x0, y0 = positions[t]
                x1, y1 = positions[child]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#aaa")))
    x_vals, y_vals = zip(*positions.values())
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode="markers+text",
        text=list(positions.keys()),
        textposition="bottom center",
        marker=dict(size=12, color="#00cc96"),
        hovertext=[pages[n]["url"] for n in positions.keys()],
        hoverinfo="text"
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white",
        height=600,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 🧩 Streamlit Interface
# -------------------------------
st.sidebar.header("Add a Wikipedia Page")
title = st.sidebar.text_input("Page title")
parent = st.sidebar.selectbox("Parent (optional)", [None] + list(st.session_state.pages.keys()))
url = st.sidebar.text_input("Custom URL (optional)")
if st.sidebar.button("Add Page"):
    if title:
        add_page(title, parent, url)
        st.sidebar.success(f"Added {title}")
    else:
        st.sidebar.error("Please enter a title")

st.subheader("🌳 Your Wikipedia Tree")
plot_tree()