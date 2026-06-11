"""Streamlit UI — FULL CYBERPUNK MODE."""
import base64
from pathlib import Path

import requests
import streamlit as st

API = "http://localhost:8000"
_ASSETS = Path(__file__).parent


def _b64(p: str) -> str:
    return base64.b64encode(Path(p).read_bytes()).decode()


@st.cache_resource
def _load_assets():
    gif    = _b64(str(_ASSETS / "Technology Gif Background.gif"))
    sunset = _b64(str(_ASSETS / "sadat-alam-protik-BEa-gD_If1s-unsplash.png"))
    return gif, sunset


_GIF_B64, _SUNSET_B64 = _load_assets()

st.set_page_config(page_title="TASKFLOW", page_icon="⚡", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ─── VARIABLES ─────────────────────────────────────── */
:root {{
  --c:   #00f5ff;
  --m:   #bf00ff;
  --o:   #ff6b00;
  --g:   #00ff88;
  --r:   #ff2d55;
  --bg:  #020814;
  --s1:  rgba(0,245,255,0.06);
  --b1:  rgba(0,245,255,0.18);
  --b2:  rgba(0,245,255,0.08);
  --tx:  #e8f4ff;
  --mu:  rgba(232,244,255,0.45);
}}

/* ─── ANIMATED GIF BACKGROUND ──────────────────────── */
.stApp {{
  background: url("data:image/gif;base64,{_GIF_B64}") center/cover fixed no-repeat !important;
  font-family: 'Inter', sans-serif;
}}
.stApp::before {{
  content:'';
  position:fixed; inset:0; z-index:0; pointer-events:none;
  background: linear-gradient(135deg,
    rgba(2,8,20,0.93) 0%,
    rgba(4,12,35,0.88) 40%,
    rgba(8,4,22,0.93) 100%);
}}
.main .block-container {{ position:relative; z-index:1; padding:2rem 2.5rem; }}

/* ─── SIDEBAR ───────────────────────────────────────── */
section[data-testid="stSidebar"] {{
  background: rgba(2,6,18,0.95) !important;
  border-right: 1px solid var(--b1) !important;
  backdrop-filter: blur(24px);
}}
section[data-testid="stSidebar"] * {{ color: var(--tx) !important; }}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
  font-family:'Orbitron',sans-serif !important;
  color: var(--c) !important;
  font-size:0.65rem !important;
  letter-spacing:0.2em !important;
  text-transform:uppercase !important;
  text-shadow: 0 0 12px rgba(0,245,255,0.5);
}}

/* ─── HEADINGS ──────────────────────────────────────── */
h1 {{
  font-family:'Orbitron',sans-serif !important;
  font-weight:900 !important;
  font-size:2.6rem !important;
  background: linear-gradient(90deg, var(--c), var(--m), var(--o), var(--c));
  background-size:300%;
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  animation: gshift 5s ease infinite;
  letter-spacing:3px !important;
}}
@keyframes gshift {{
  0%   {{ background-position:0% 50%; }}
  50%  {{ background-position:100% 50%; }}
  100% {{ background-position:0% 50%; }}
}}
h2, h3 {{
  font-family:'Orbitron',sans-serif !important;
  color: var(--c) !important;
  font-weight:700 !important;
  letter-spacing:1px;
  text-shadow: 0 0 18px rgba(0,245,255,0.45);
}}

/* ─── BODY TEXT ─────────────────────────────────────── */
p, label, div[data-testid="stMarkdownContainer"],
.stMarkdown {{ color:var(--tx) !important; font-family:'Inter',sans-serif !important; }}
.stCaption, small {{ color:var(--mu) !important; }}
code {{ font-family:'JetBrains Mono',monospace !important; color:var(--c) !important; }}

/* ─── INPUTS ────────────────────────────────────────── */
.stTextArea textarea, .stTextInput input {{
  background: rgba(0,245,255,0.04) !important;
  border: 1px solid var(--b1) !important;
  border-radius:10px !important;
  color: var(--tx) !important;
  font-family:'Inter',sans-serif !important;
  font-size:0.9rem !important;
  backdrop-filter:blur(8px);
  transition: border-color .25s, box-shadow .25s;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
  border-color: var(--c) !important;
  box-shadow: 0 0 0 3px rgba(0,245,255,0.15), 0 0 25px rgba(0,245,255,0.1) !important;
  outline:none !important;
}}
.stSelectbox > div > div {{
  background: rgba(0,245,255,0.04) !important;
  border: 1px solid var(--b1) !important;
  border-radius:10px !important;
  color: var(--tx) !important;
}}

/* ─── PRIMARY BUTTON ────────────────────────────────── */
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, var(--c), var(--m)) !important;
  color: #020814 !important;
  font-family:'Orbitron',sans-serif !important;
  font-weight:700 !important;
  font-size:0.78rem !important;
  letter-spacing:3px !important;
  text-transform:uppercase !important;
  border:none !important;
  border-radius:10px !important;
  padding:0.65rem 2.2rem !important;
  box-shadow: 0 0 20px rgba(0,245,255,0.35), 0 0 50px rgba(191,0,255,0.2) !important;
  transition: all .25s !important;
  position:relative;
}}
.stButton > button[kind="primary"]:hover {{
  transform:translateY(-2px) scale(1.02) !important;
  box-shadow: 0 0 35px rgba(0,245,255,0.6), 0 0 80px rgba(191,0,255,0.35) !important;
}}
.stButton > button[kind="primary"]:disabled {{ opacity:.3 !important; transform:none !important; }}

/* ─── OTHER BUTTONS ─────────────────────────────────── */
.stButton > button, .stDownloadButton > button {{
  background: var(--s1) !important;
  border: 1px solid var(--b1) !important;
  color: var(--c) !important;
  border-radius:8px !important;
  font-family:'Inter',sans-serif !important;
  font-size:0.8rem !important;
  transition:all .2s !important;
  backdrop-filter:blur(6px);
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  background: rgba(0,245,255,0.12) !important;
  border-color: var(--c) !important;
  box-shadow: 0 0 14px rgba(0,245,255,0.3) !important;
  transform: translateY(-1px) !important;
}}

/* ─── EXPANDERS ─────────────────────────────────────── */
.streamlit-expanderHeader {{
  background: var(--s1) !important;
  border: 1px solid var(--b1) !important;
  border-radius:10px !important;
  color: var(--tx) !important;
  font-family:'Inter',sans-serif !important;
  backdrop-filter:blur(8px);
  transition: background .2s !important;
}}
.streamlit-expanderHeader:hover {{ background: rgba(0,245,255,0.1) !important; }}
.streamlit-expanderContent {{
  background: rgba(2,8,20,0.6) !important;
  border:1px solid var(--b1) !important;
  border-top:none !important;
  border-radius:0 0 10px 10px !important;
  backdrop-filter:blur(8px);
}}

/* ─── STATUS BOXES ──────────────────────────────────── */
.stSuccess {{ background:rgba(0,255,136,0.07) !important; border:1px solid rgba(0,255,136,0.35) !important; border-radius:10px !important; color:var(--g) !important; }}
.stError   {{ background:rgba(255,45,85,0.08) !important;  border:1px solid rgba(255,45,85,0.4) !important;  border-radius:10px !important; }}
.stWarning {{ background:rgba(255,107,0,0.08) !important;  border:1px solid rgba(255,107,0,0.4) !important;  border-radius:10px !important; }}
.stInfo    {{ background:rgba(191,0,255,0.07) !important;  border:1px solid rgba(191,0,255,0.35) !important; border-radius:10px !important; }}
.stSpinner > div {{ border-top-color: var(--c) !important; }}

/* ─── MISC ──────────────────────────────────────────── */
img {{ border-radius:12px; border:1px solid var(--b1); box-shadow:0 0 25px rgba(0,245,255,0.08); }}
hr  {{ border-color: var(--b1) !important; }}
.stJson {{ background:rgba(0,0,0,0.55) !important; border:1px solid var(--b1) !important; border-radius:10px !important; }}
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:rgba(0,0,0,0.4); }}
::-webkit-scrollbar-thumb {{ background:var(--c); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:var(--m); }}

/* ─── SCAN LINE OVERLAY ─────────────────────────────── */
.stApp::after {{
  content:'';
  position:fixed; inset:0; z-index:0; pointer-events:none;
  background: repeating-linear-gradient(
    0deg,
    rgba(0,0,0,0) 0px,
    rgba(0,0,0,0) 2px,
    rgba(0,245,255,0.015) 2px,
    rgba(0,245,255,0.015) 4px
  );
}}
</style>
""", unsafe_allow_html=True)

# ─── HERO BANNER ─────────────────────────────────────────────────────────────
try:
    health = requests.get(f"{API}/health", timeout=2).json()
    status_html = f"""
      <span style="background:rgba(0,255,136,0.12); border:1px solid rgba(0,255,136,0.4);
                   color:#00ff88; padding:3px 12px; border-radius:20px; font-size:0.7rem;
                   font-family:'Orbitron',sans-serif; letter-spacing:2px;">
        ● ONLINE
      </span>
      <span style="color:rgba(232,244,255,0.35); font-size:0.7rem;
                   font-family:'JetBrains Mono',monospace; margin-left:10px;">
        {health.get('provider','')}
      </span>"""
except Exception:
    status_html = """<span style="color:#ff2d55; font-size:0.75rem;
                                  font-family:'Orbitron',sans-serif;">● OFFLINE</span>"""

st.markdown(f"""
<div style="
  background: linear-gradient(135deg, rgba(0,245,255,0.06) 0%, rgba(191,0,255,0.06) 100%);
  border: 1px solid rgba(0,245,255,0.2);
  border-radius:18px;
  padding:2.2rem 3rem;
  margin-bottom:2rem;
  backdrop-filter:blur(16px);
  display:flex; align-items:center; gap:2.5rem;
  box-shadow: 0 0 60px rgba(0,245,255,0.05), inset 0 1px 0 rgba(255,255,255,0.04);
">
  <div style="flex:1; min-width:0;">
    <div style="font-family:'Orbitron',sans-serif; font-size:0.65rem; color:rgba(0,245,255,0.7);
                letter-spacing:5px; text-transform:uppercase; margin-bottom:0.6rem;">
      ⚡ Industrial AI Pipeline v1.0
    </div>
    <div style="
      font-family:'Orbitron',sans-serif; font-size:2.8rem; font-weight:900;
      background: linear-gradient(90deg,#00f5ff,#bf00ff,#ff6b00,#00f5ff);
      background-size:300%; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      background-clip:text; animation:gshift 5s ease infinite; letter-spacing:4px;
      line-height:1.1; margin-bottom:0.6rem;">
      TASKFLOW
    </div>
    <div style="color:rgba(232,244,255,0.6); font-size:0.95rem; max-width:480px; line-height:1.6;">
      Transform natural language into validated Task Flow DAGs — powered by Gemini AI.
    </div>
    <div style="margin-top:1rem;">
      {status_html}
    </div>
  </div>
  <div style="flex-shrink:0;">
    <div style="position:relative;">
      <img src="data:image/png;base64,{_SUNSET_B64}"
           style="width:240px; height:145px; object-fit:cover; border-radius:14px;
                  border:1px solid rgba(0,245,255,0.25);
                  box-shadow:0 0 40px rgba(0,245,255,0.12), 0 0 80px rgba(191,0,255,0.08);" />
      <div style="position:absolute; inset:0; border-radius:14px;
                  background:linear-gradient(135deg, transparent 50%, rgba(0,245,255,0.08));
                  pointer-events:none;"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
EXAMPLES = [
    "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3.",
    "Navigate to Station 2, scan barcode on the package, then move it to the output tray.",
    "Retrieve the blue cylinder from storage, verify weight, assemble with component B, and seal.",
    "Pick item from room 1, drop at room 3, while dropping three products at room 2.",
]

with st.sidebar:
    st.markdown("### SYSTEM")
    api_url = st.text_input("API URL", value=API, label_visibility="collapsed")
    st.divider()
    st.markdown("### EXAMPLES")
    for ex in EXAMPLES:
        label = (ex[:50] + "…") if len(ex) > 50 else ex
        if st.button(label, key=f"ex_{hash(ex)}", use_container_width=True):
            st.session_state["_instr"] = ex
    st.divider()
    st.markdown("""
<div style="color:rgba(0,245,255,0.25); font-size:0.65rem; text-align:center;
            font-family:'Orbitron',sans-serif; letter-spacing:3px;">
TASKFLOW v1.0.0
</div>""", unsafe_allow_html=True)

# ─── INPUT ───────────────────────────────────────────────────────────────────
if "_instr" not in st.session_state:
    st.session_state["_instr"] = ""

st.markdown("### INSTRUCTION INPUT")

instruction = st.text_area(
    "instruction",
    value=st.session_state["_instr"],
    height=95,
    placeholder="Describe the industrial task in plain English…",
    label_visibility="collapsed",
    key="instr_box",
)

run = st.button("⚡  EXECUTE PIPELINE", type="primary",
                disabled=not instruction.strip())

# ─── PIPELINE ────────────────────────────────────────────────────────────────
ACTION_COLORS = {
    "navigate": "#2563EB", "locate": "#0891B2", "pick":     "#16A34A",
    "place":    "#DC2626", "inspect":"#9333EA", "scan":     "#D97706",
    "sort":     "#0D9488", "transfer":"#7C3AED","move":     "#DB2777",
    "assemble": "#EA580C", "verify": "#059669", "deliver":  "#B45309",
}

if run and instruction.strip():
    with st.spinner("Processing through Gemini AI…"):
        try:
            resp = requests.post(f"{api_url}/instructions",
                                 json={"instruction": instruction.strip()},
                                 timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as e:
            st.error(f"API {e.response.status_code}: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    pid       = data["pipeline_id"]
    tasks     = data["plan"]["tasks"]
    v         = data["validation"]
    artifacts = data.get("artifacts", {})

    # pipeline complete banner
    st.markdown(f"""
    <div style="
      background:rgba(0,245,255,0.05); border:1px solid rgba(0,245,255,0.25);
      border-radius:10px; padding:0.8rem 1.4rem; margin:1rem 0 1.8rem;
      display:flex; align-items:center; gap:1rem;
      box-shadow:0 0 20px rgba(0,245,255,0.05);
    ">
      <span style="font-size:1.3rem;">⚡</span>
      <div>
        <div style="font-family:'Orbitron',sans-serif; font-size:0.7rem;
                    color:#00f5ff; letter-spacing:3px; text-transform:uppercase;">
          Pipeline Complete
        </div>
        <div style="color:rgba(232,244,255,0.5); font-size:0.78rem; margin-top:2px;
                    font-family:'JetBrains Mono',monospace;">
          ID: <span style="color:#bf00ff;">{pid}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    # ── TASK PLAN ─────────────────────────────────────────────────────────
    with col_l:
        st.markdown(f"### TASK PLAN  <span style='font-size:0.75rem; color:rgba(0,245,255,0.5); font-family:Inter,sans-serif;'>{len(tasks)} tasks</span>", unsafe_allow_html=True)
        for t in tasks:
            c    = ACTION_COLORS.get(t["action"], "#475569")
            deps = " → ".join(t["depends_on"]) if t["depends_on"] else "START"
            with st.expander(f"{t['id']}  ·  {t['description']}", expanded=False):
                st.markdown(f"""
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
                  <span style="background:{c}22; border:1px solid {c}66; color:{c};
                               padding:2px 12px; border-radius:20px; font-size:0.72rem;
                               font-family:'Orbitron',sans-serif; letter-spacing:1px; font-weight:600;">
                    {t['action'].upper()}
                  </span>
                  <span style="color:rgba(232,244,255,0.4); font-size:0.78rem;">
                    after: <strong style="color:rgba(232,244,255,0.7);">{deps}</strong>
                  </span>
                  {'<span style="color:#ff6b00; font-size:0.72rem; font-family:Orbitron,sans-serif; letter-spacing:1px;">◆ CONDITIONAL</span>' if t.get('condition') else ''}
                </div>
                """, unsafe_allow_html=True)
                if t.get("condition"):
                    st.caption(f"Condition: `{t['condition']}`")
                if t.get("metadata"):
                    st.json(t["metadata"], expanded=False)

    # ── VALIDATION ────────────────────────────────────────────────────────
    with col_r:
        passed = v.get("valid", False)
        sc = "#00ff88" if passed else "#ff2d55"
        st.markdown(f"### VALIDATION  <span style='font-size:0.75rem; color:{sc};'>{'✓ PASSED' if passed else '✗ FAILED'}</span>", unsafe_allow_html=True)

        CHECK_KEYS = [
            "cycle_check", "dependency_check", "reachability_check",
            "action_check", "conditional_check", "structural_check", "consistency_check",
        ]
        rows = ""
        for k in CHECK_KEYS:
            val = v.get(k)
            if val is None:
                continue
            ok  = val == "passed"
            kc  = "#00f5ff" if ok else "#ff2d55"
            rows += f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:7px 0; border-bottom:1px solid rgba(0,245,255,0.07);">
              <span style="color:rgba(232,244,255,0.6); font-size:0.8rem;">
                {k.replace('_check','').replace('_',' ').title()}
              </span>
              <span style="color:{kc}; font-size:0.75rem; font-family:'Orbitron',sans-serif;
                           letter-spacing:1px;">
                {'✓' if ok else '✗'} {val.upper()}
              </span>
            </div>"""

        st.markdown(f"""
        <div style="
          background:rgba(0,0,0,0.35); border:1px solid rgba(0,245,255,0.12);
          border-radius:12px; padding:0.8rem 1.2rem;
          backdrop-filter:blur(8px);
        ">
          <div style="display:flex; justify-content:space-between; margin-bottom:10px;
                      padding-bottom:8px; border-bottom:1px solid rgba(0,245,255,0.12);">
            <span style="color:rgba(0,245,255,0.6); font-size:0.7rem;
                         font-family:'Orbitron',sans-serif; letter-spacing:2px;">GRAPH STATS</span>
            <span style="color:rgba(232,244,255,0.6); font-size:0.78rem;
                         font-family:'JetBrains Mono',monospace;">
              {v.get('node_count',0)} nodes · {v.get('edge_count',0)} edges
            </span>
          </div>
          {rows}
        </div>
        """, unsafe_allow_html=True)

        if v.get("issues"):
            st.warning("Issues: " + " · ".join(v["issues"]))

    # ── GRAPH ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### TASK GRAPH")

    if "task_graph.png" in artifacts:
        img = requests.get(f"{api_url}/downloads/{pid}/task_graph.png", timeout=15)
        if img.ok:
            st.image(img.content, use_container_width=True)

    if "task_graph.html" in artifacts:
        html = requests.get(f"{api_url}/downloads/{pid}/task_graph.html", timeout=10)
        if html.ok:
            with st.expander("⬡  Interactive Graph", expanded=False):
                st.components.v1.html(html.text, height=520, scrolling=True)

    # ── DOWNLOADS ─────────────────────────────────────────────────────────
    st.markdown("### EXPORT")
    dl_cols = st.columns(min(len(artifacts), 6))
    for i, name in enumerate(artifacts):
        r2 = requests.get(f"{api_url}/downloads/{pid}/{name}", timeout=10)
        if r2.ok:
            dl_cols[i % len(dl_cols)].download_button(
                name, data=r2.content, file_name=name, key=f"dl_{name}")

    with st.expander("⬡  Raw API Response", expanded=False):
        st.json(data)
