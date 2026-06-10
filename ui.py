"""Streamlit UI for the TaskFlow pipeline."""
import json

import requests
import streamlit as st

API = "http://localhost:8000"

st.set_page_config(page_title="TaskFlow", page_icon="🤖", layout="wide")
st.title("🤖 TaskFlow — Language to Task Graph")
st.caption("Convert natural language industrial instructions into a validated Task Flow DAG.")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API base URL", value=API)
    try:
        r = requests.get(f"{api_url}/health", timeout=3)
        info = r.json()
        st.success(f"API online  ·  v{info['version']}")
        st.caption(f"Provider: `{info['provider']}`")
    except Exception:
        st.error("API unreachable — start the server first.")

    st.divider()
    st.markdown(
        "**Endpoints used**\n"
        "- `POST /instructions` – full pipeline\n"
        "- `GET /downloads/{id}/{file}` – artifacts\n"
    )

# ── Main input ────────────────────────────────────────────────────────────────
EXAMPLES = [
    "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3.",
    "Navigate to Station 2, scan barcode on the package, then move it to the output tray.",
    "Retrieve the blue cylinder from storage, verify weight, assemble with component B, and seal.",
]

st.subheader("Instruction")
example = st.selectbox("Load an example", ["— type your own —"] + EXAMPLES, index=0)
default_text = "" if example.startswith("—") else example
instruction = st.text_area(
    "Natural language instruction",
    value=default_text,
    height=90,
    placeholder="e.g. Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3.",
    label_visibility="collapsed",
)

run = st.button("▶  Run Pipeline", type="primary", disabled=not instruction.strip())

# ── Pipeline execution ────────────────────────────────────────────────────────
if run and instruction.strip():
    with st.spinner("Running pipeline…"):
        try:
            resp = requests.post(
                f"{api_url}/instructions",
                json={"instruction": instruction.strip()},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as e:
            st.error(f"API error {e.response.status_code}: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    st.success(f"Pipeline `{data['pipeline_id']}` completed.")

    col_left, col_right = st.columns([1, 1])

    # ── Task plan ──────────────────────────────────────────────────────────
    with col_left:
        st.subheader("Task Plan")
        tasks = data["plan"]["tasks"]
        st.caption(f"{len(tasks)} tasks")
        for t in tasks:
            deps = ", ".join(t["depends_on"]) or "—"
            with st.expander(f"**{t['id']}** · {t['action']}  —  {t['description']}", expanded=False):
                cols = st.columns(2)
                cols[0].markdown(f"**Depends on:** {deps}")
                if t.get("condition"):
                    cols[1].markdown(f"**Condition:** {t['condition']}")
                if t.get("metadata"):
                    st.json(t["metadata"], expanded=False)

    # ── Validation ────────────────────────────────────────────────────────
    with col_right:
        st.subheader("Validation")
        v = data["validation"]
        passed = v.get("passed", False)
        st.markdown(f"**Result:** {'✅ Passed' if passed else '❌ Failed'}")

        checks = v.get("checks", [])
        if checks:
            st.caption(f"{sum(c.get('passed', False) for c in checks)}/{len(checks)} checks passed")
            for c in checks:
                icon = "✅" if c.get("passed") else "❌"
                st.markdown(f"{icon} `{c.get('name', '?')}` — {c.get('message', '')}")

        errors = v.get("errors", [])
        if errors:
            st.warning("Errors:\n" + "\n".join(f"- {e}" for e in errors))

    # ── Graph image ───────────────────────────────────────────────────────
    st.subheader("Task Graph")
    pid = data["pipeline_id"]
    artifacts = data.get("artifacts", {})

    if "task_graph.png" in artifacts:
        img_resp = requests.get(f"{api_url}/downloads/{pid}/task_graph.png", timeout=10)
        if img_resp.ok:
            st.image(img_resp.content, use_container_width=True)

    if "task_graph.html" in artifacts:
        html_resp = requests.get(f"{api_url}/downloads/{pid}/task_graph.html", timeout=10)
        if html_resp.ok:
            with st.expander("Interactive graph (HTML)", expanded=False):
                st.components.v1.html(html_resp.text, height=500, scrolling=True)

    # ── Downloads ─────────────────────────────────────────────────────────
    st.subheader("Downloads")
    dl_cols = st.columns(len(artifacts) if artifacts else 1)
    for i, name in enumerate(artifacts):
        url = f"{api_url}/downloads/{pid}/{name}"
        r2 = requests.get(url, timeout=10)
        if r2.ok:
            dl_cols[i % len(dl_cols)].download_button(
                label=f"⬇ {name}",
                data=r2.content,
                file_name=name,
                key=f"dl_{name}",
            )

    # ── Raw JSON ──────────────────────────────────────────────────────────
    with st.expander("Raw API response", expanded=False):
        st.json(data)
