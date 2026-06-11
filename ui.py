"""Streamlit UI for the TaskFlow pipeline — dark cyberpunk theme."""
import base64
from pathlib import Path

import requests
import streamlit as st

API = "http://localhost:8000"

# ── Asset loading ─────────────────────────────────────────────────────────────
def _b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()

_ASSETS = Path(__file__).parent
_GIF_B64    = _b64(str(_ASSETS / "Technology Gif Background.gif"))
_SUNSET_B64 = _b64(str(_ASSETS / "sadat-alam-protik-BEa-gD_If1s-unsplash.png"))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="TaskFlow", page_icon="⚡", layout="wide",
                   initial_sidebar_state="expanded")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');

/* ── Root palette ── */
:root {{
  --neon:    #00f5ff;
  --neon2:   #bf00ff;
  --accent:  #ff6b00;
  --bg:      #020814;
  --glass:   rgba(0,245,255,0.04);
  --border:  rgba(0,245,255,0.18);
  --text:    #e8f4ff;
  --muted:   rgba(232,244,255,0.55);
}}

/* ── Animated GIF background ── */
.stApp {{
  background: url("data:image/gif;base64,{_GIF_B64}") center/cover fixed no-repeat;
  font-family: 'Inter', sans-serif;
}}

/* dark overlay so content is readable */
.stApp::before {{
  content: '';
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg,
    rgba(2,8,20,0.91) 0%,
    rgba(5,15,40,0.85) 50%,
    rgba(10,5,25,0.91) 100%);
  z-index: 0;
  pointer-events: none;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: rgba(2,8,20,0.92) !important;
  border-right: 1px solid var(--border) !important;
  backdrop-filter: blur(20px);
}}
section[data-testid="stSidebar"] * {{
  color: var(--text) !important;
}}

/* ── Main content area ── */
.main .block-container {{
  padding-top: 2rem;
  position: relative;
  z-index: 1;
}}

/* ── Hero title ── */
h1 {{
  font-family: 'Orbitron', sans-serif !important;
  font-weight: 900 !important;
  font-size: 3rem !important;
  background: linear-gradient(90deg, var(--neon), var(--neon2), var(--accent), var(--neon));
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientShift 4s ease infinite;
  text-shadow: none;
  letter-spacing: 2px;
}}

@keyframes gradientShift {{
  0%   {{ background-position: 0% 50%; }}
  50%  {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}

/* ── All headings ── */
h2, h3 {{
  font-family: 'Orbitron', sans-serif !important;
  color: var(--neon) !important;
  font-weight: 700 !important;
  letter-spacing: 1px;
  text-shadow: 0 0 20px rgba(0,245,255,0.4);
}}

/* ── Body text ── */
p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] {{
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}}

/* ── Caption / muted ── */
.stCaption, small {{
  color: var(--muted) !important;
}}

/* ── Input fields ── */
.stTextArea textarea, .stTextInput input {{
  background: rgba(0,245,255,0.05) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  transition: border-color .3s, box-shadow .3s;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
  border-color: var(--neon) !important;
  box-shadow: 0 0 20px rgba(0,245,255,0.25), inset 0 0 10px rgba(0,245,255,0.05) !important;
  outline: none !important;
}}

/* ── Selectbox ── */
.stSelectbox > div > div {{
  background: rgba(0,245,255,0.05) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
}}

/* ── Primary button ── */
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, var(--neon), var(--neon2)) !important;
  color: #020814 !important;
  font-family: 'Orbitron', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  letter-spacing: 2px !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 0.7rem 2rem !important;
  box-shadow: 0 0 25px rgba(0,245,255,0.4), 0 0 60px rgba(191,0,255,0.2) !important;
  transition: all .3s !important;
  text-transform: uppercase;
}}
.stButton > button[kind="primary"]:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 0 40px rgba(0,245,255,0.7), 0 0 80px rgba(191,0,255,0.4) !important;
}}
.stButton > button[kind="primary"]:disabled {{
  opacity: 0.35 !important;
  transform: none !important;
}}

/* ── Secondary / download buttons ── */
.stButton > button, .stDownloadButton > button {{
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  color: var(--neon) !important;
  font-family: 'Inter', sans-serif !important;
  border-radius: 8px !important;
  transition: all .25s !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  background: rgba(0,245,255,0.12) !important;
  border-color: var(--neon) !important;
  box-shadow: 0 0 15px rgba(0,245,255,0.3) !important;
}}

/* ── Expander ── */
.streamlit-expanderHeader {{
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--neon) !important;
  font-family: 'Inter', sans-serif !important;
}}
.streamlit-expanderContent {{
  background: rgba(0,245,255,0.02) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 8px 8px !important;
}}

/* ── Success / error / warning ── */
.stSuccess {{
  background: rgba(0,245,255,0.08) !important;
  border: 1px solid var(--neon) !important;
  border-radius: 8px !important;
  color: var(--neon) !important;
}}
.stError {{
  background: rgba(255,50,50,0.1) !important;
  border: 1px solid rgba(255,80,80,0.5) !important;
  border-radius: 8px !important;
}}
.stWarning {{
  background: rgba(255,107,0,0.1) !important;
  border: 1px solid rgba(255,107,0,0.5) !important;
  border-radius: 8px !important;
  color: var(--accent) !important;
}}

/* ── Info box ── */
.stInfo {{
  background: rgba(191,0,255,0.08) !important;
  border: 1px solid rgba(191,0,255,0.4) !important;
  border-radius: 8px !important;
}}

/* ── Spinner ── */
.stSpinner > div {{
  border-top-color: var(--neon) !important;
}}

/* ── Divider ── */
hr {{
  border-color: var(--border) !important;
}}

/* ── Images ── */
img {{
  border-radius: 10px;
  border: 1px solid var(--border);
  box-shadow: 0 0 30px rgba(0,245,255,0.1);
}}

/* ── JSON viewer ── */
.stJson {{
  background: rgba(0,0,0,0.5) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.3); }}
::-webkit-scrollbar-thumb {{ background: var(--neon); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--neon2); }}

/* ── Sidebar header text ── */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
  font-family: 'Orbitron', sans-serif !important;
  color: var(--neon) !important;
}}

/* ── Metric / stat boxes ── */
div[data-testid="metric-container"] {{
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 1rem !important;
}}

</style>
""", unsafe_allow_html=True)

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
  background: linear-gradient(90deg, rgba(0,245,255,0.07), rgba(191,0,255,0.07));
  border: 1px solid rgba(0,245,255,0.2);
  border-radius: 16px;
  padding: 2.5rem 3rem;
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 2rem;
">
  <div style="flex:1">
    <div style="font-family:'Orbitron',sans-serif; font-size:0.75rem; color:#00f5ff; letter-spacing:4px; text-transform:uppercase; margin-bottom:0.5rem; opacity:0.8;">
      ⚡ Industrial AI Pipeline
    </div>
    <h1 style="margin:0; font-family:'Orbitron',sans-serif; font-size:2.8rem; font-weight:900;
               background:linear-gradient(90deg,#00f5ff,#bf00ff,#ff6b00);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
      TASKFLOW
    </h1>
    <p style="color:rgba(232,244,255,0.7); font-size:1.05rem; margin-top:0.5rem; max-width:520px;">
      Transform natural language into validated Task Flow DAGs — powered by Gemini AI.
    </p>
  </div>
  <div>
    <img src="data:image/png;base64,{_SUNSET_B64}"
         style="width:220px; height:130px; object-fit:cover; border-radius:12px;
                border:1px solid rgba(0,245,255,0.3);
                box-shadow: 0 0 30px rgba(0,245,255,0.15), 0 0 60px rgba(191,0,255,0.1);" />
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### SYSTEM STATUS")
    try:
        r = requests.get(f"{API}/health", timeout=3)
        info = r.json()
        st.success(f"ONLINE  ·  v{info['version']}")
        st.caption(f"Provider: `{info['provider']}`")
    except Exception:
        st.error("API OFFLINE")
        st.caption("Start the backend server first.")

    st.divider()
    st.markdown("### CONFIGURATION")
    api_url = st.text_input("API Base URL", value=API)

    st.divider()
    st.markdown("### ENDPOINTS")
    st.markdown("""
- `POST /instructions`
- `GET /downloads/{id}/{file}`
- `GET /health`
    """)

    st.divider()
    st.markdown(
        "<div style='color:rgba(0,245,255,0.4); font-size:0.7rem; text-align:center; letter-spacing:2px;'>TASKFLOW v1.0.0</div>",
        unsafe_allow_html=True,
    )

# ── Input section ─────────────────────────────────────────────────────────────
EXAMPLES = [
    "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3.",
    "Navigate to Station 2, scan barcode on the package, then move it to the output tray.",
    "Retrieve the blue cylinder from storage, verify weight, assemble with component B, and seal.",
]

st.markdown("### INSTRUCTION INPUT")
example = st.selectbox("Load example", ["— type your own —"] + EXAMPLES, index=0,
                       label_visibility="collapsed")
default_text = "" if example.startswith("—") else example
instruction = st.text_area(
    "instruction",
    value=default_text,
    height=100,
    placeholder="e.g.  Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3.",
    label_visibility="collapsed",
)

run = st.button("EXECUTE PIPELINE", type="primary", disabled=not instruction.strip())

# ── Pipeline execution ────────────────────────────────────────────────────────
if run and instruction.strip():
    with st.spinner("Processing through Gemini AI..."):
        try:
            resp = requests.post(
                f"{api_url}/instructions",
                json={"instruction": instruction.strip()},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as e:
            st.error(f"API error {e.response.status_code}: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    st.markdown(f"""
    <div style="background:rgba(0,245,255,0.06); border:1px solid rgba(0,245,255,0.3);
                border-radius:10px; padding:1rem 1.5rem; margin:1rem 0;
                display:flex; align-items:center; gap:1rem;">
      <span style="font-size:1.5rem;">⚡</span>
      <div>
        <div style="color:#00f5ff; font-family:'Orbitron',sans-serif; font-size:0.8rem; letter-spacing:2px;">
          PIPELINE COMPLETE
        </div>
        <div style="color:rgba(232,244,255,0.6); font-size:0.8rem; margin-top:2px;">
          ID: <code style="color:#bf00ff;">{data['pipeline_id']}</code>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    # ── Task plan ─────────────────────────────────────────────────────────
    with col_left:
        st.markdown("### TASK PLAN")
        tasks = data["plan"]["tasks"]

        ACTION_COLORS = {
            "navigate": "#00f5ff", "locate": "#00d4aa", "pick": "#00ff88",
            "place": "#ff6b00",    "inspect": "#bf00ff", "scan": "#ffcc00",
            "assemble": "#ff00aa", "verify": "#ff4488",
        }

        st.caption(f"{len(tasks)} tasks generated")
        for t in tasks:
            color = ACTION_COLORS.get(t["action"], "#ffffff")
            deps = ", ".join(t["depends_on"]) if t["depends_on"] else "START"
            with st.expander(
                f"{t['id']} · {t['action'].upper()}  —  {t['description']}", expanded=False
            ):
                st.markdown(f"""
                <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:0.5rem;">
                  <span style="background:rgba(0,0,0,0.3); border:1px solid {color}33;
                               color:{color}; padding:2px 10px; border-radius:20px; font-size:0.75rem;
                               font-family:'Orbitron',sans-serif; letter-spacing:1px;">
                    {t['action'].upper()}
                  </span>
                  <span style="color:rgba(232,244,255,0.5); font-size:0.8rem; padding-top:3px;">
                    depends on: <strong style="color:{color}">{deps}</strong>
                  </span>
                </div>
                """, unsafe_allow_html=True)
                if t.get("condition"):
                    st.markdown(f"**Condition:** `{t['condition']}`")
                if t.get("metadata"):
                    st.json(t["metadata"], expanded=False)

    # ── Validation ────────────────────────────────────────────────────────
    with col_right:
        st.markdown("### VALIDATION REPORT")
        v = data["validation"]
        passed = v.get("valid", False)

        status_color = "#00f5ff" if passed else "#ff4444"
        status_text  = "ALL CHECKS PASSED" if passed else "VALIDATION FAILED"

        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.3); border:1px solid {status_color}44;
                    border-radius:10px; padding:1rem 1.5rem; margin-bottom:1rem;">
          <div style="color:{status_color}; font-family:'Orbitron',sans-serif;
                      font-size:0.85rem; letter-spacing:2px; font-weight:700;">
            {'✓' if passed else '✗'} {status_text}
          </div>
          <div style="color:rgba(232,244,255,0.5); font-size:0.8rem; margin-top:4px;">
            {v.get('node_count', 0)} nodes  ·  {v.get('edge_count', 0)} edges
          </div>
        </div>
        """, unsafe_allow_html=True)

        CHECK_KEYS = [
            "cycle_check", "dependency_check", "reachability_check",
            "action_check", "conditional_check", "structural_check", "consistency_check",
        ]
        rows = ""
        for key in CHECK_KEYS:
            val = v.get(key)
            if val is not None:
                ok = val == "passed"
                c  = "#00f5ff" if ok else "#ff4444"
                icon = "✓" if ok else "✗"
                label = key.replace("_check", "").replace("_", " ").title()
                rows += f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:6px 0; border-bottom:1px solid rgba(0,245,255,0.06);">
                  <span style="color:rgba(232,244,255,0.7); font-size:0.82rem;">{label}</span>
                  <span style="color:{c}; font-size:0.85rem; font-weight:600;
                               font-family:'Orbitron',sans-serif; letter-spacing:1px;">
                    {icon} {val.upper()}
                  </span>
                </div>"""
        st.markdown(
            f'<div style="background:rgba(0,0,0,0.2); border:1px solid rgba(0,245,255,0.1); border-radius:8px; padding:0.5rem 1rem;">{rows}</div>',
            unsafe_allow_html=True,
        )

        issues = v.get("issues", [])
        if issues:
            st.warning("Issues:\n" + "\n".join(f"- {i}" for i in issues))

    # ── Graph ─────────────────────────────────────────────────────────────
    st.markdown("### TASK GRAPH")
    pid = data["pipeline_id"]
    artifacts = data.get("artifacts", {})

    if "task_graph.png" in artifacts:
        img_resp = requests.get(f"{api_url}/downloads/{pid}/task_graph.png", timeout=10)
        if img_resp.ok:
            st.image(img_resp.content, use_container_width=True)

    if "task_graph.html" in artifacts:
        html_resp = requests.get(f"{api_url}/downloads/{pid}/task_graph.html", timeout=10)
        if html_resp.ok:
            with st.expander("Interactive Graph", expanded=False):
                st.components.v1.html(html_resp.text, height=520, scrolling=True)

    # ── Downloads ─────────────────────────────────────────────────────────
    st.markdown("### EXPORT ARTIFACTS")
    dl_cols = st.columns(min(len(artifacts), 6))
    for i, name in enumerate(artifacts):
        r2 = requests.get(f"{api_url}/downloads/{pid}/{name}", timeout=10)
        if r2.ok:
            dl_cols[i % len(dl_cols)].download_button(
                label=name,
                data=r2.content,
                file_name=name,
                key=f"dl_{name}",
            )

    with st.expander("Raw API Response", expanded=False):
        st.json(data)
