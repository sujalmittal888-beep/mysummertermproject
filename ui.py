"""TASKFLOW — MAXIMUM CYBERPUNK UI."""
import base64
from pathlib import Path
import requests
import streamlit as st
import streamlit.components.v1 as components

API = "http://localhost:8000"
_ASSETS = Path(__file__).parent

def _b64(p): return base64.b64encode(Path(p).read_bytes()).decode()

@st.cache_resource
def _load_assets():
    sound_path = _ASSETS / "artifacts" / "Fahh-sound-effect.mp3"
    sound = _b64(str(sound_path)) if sound_path.exists() else ""
    return (
        _b64(str(_ASSETS/"Technology Gif Background.gif")),
        _b64(str(_ASSETS/"sadat-alam-protik-BEa-gD_If1s-unsplash.png")),
        sound,
    )

_GIF, _SUNSET, _ERROR_SOUND = _load_assets()

def _play_error():
    """Play the fail sound by rendering a self-destructing autoplay audio element."""
    if _ERROR_SOUND:
        components.html(
            f'<audio autoplay style="display:none"><source src="data:audio/mpeg;base64,{_ERROR_SOUND}" type="audio/mpeg"></audio>',
            height=0,
        )

st.set_page_config(page_title="TASKFLOW", page_icon="⚡", layout="wide",
                   initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════
#  INJECT JS ANIMATIONS INTO PARENT FRAME (same-origin hack)
# ═══════════════════════════════════════════════════════════
components.html(f"""
<script>
(function(){{
  const D = window.parent.document;

  /* ── 1. EXTRA CSS: glitch, pulse, float, ripple, matrix ── */
  const S = D.createElement('style');
  S.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {{
      --c:#00f5ff; --m:#bf00ff; --o:#ff6b00; --g:#00ff88; --r:#ff2d55;
      --bg:#020814; --s1:rgba(0,245,255,0.06); --b1:rgba(0,245,255,0.18);
      --tx:#e8f4ff; --mu:rgba(232,244,255,0.45);
    }}

    /* GIF BG */
    .stApp {{
      background: url("data:image/gif;base64,{_GIF}") center/cover fixed no-repeat !important;
      font-family:'Inter',sans-serif;
    }}
    .stApp::before {{
      content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
      background:linear-gradient(135deg,rgba(2,8,20,0.93),rgba(4,12,35,0.88),rgba(8,4,22,0.93));
    }}
    .main .block-container {{ position:relative; z-index:1; padding:1.8rem 2.5rem; }}

    /* SCAN LINES */
    .stApp::after {{
      content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
      background:repeating-linear-gradient(0deg,transparent 0,transparent 2px,rgba(0,245,255,0.012) 2px,rgba(0,245,255,0.012) 4px);
      animation: scanmove 8s linear infinite;
    }}
    @keyframes scanmove {{ 0%{{background-position:0 0}} 100%{{background-position:0 100px}} }}

    /* GLITCH TITLE */
    .glitch {{
      position:relative;
      font-family:'Orbitron',sans-serif !important;
      font-weight:900 !important;
      font-size:3.2rem !important;
      letter-spacing:6px;
      background:linear-gradient(90deg,#00f5ff,#bf00ff,#ff6b00,#00f5ff);
      background-size:300%;
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
      animation: gshift 4s ease infinite, glitch-skew 6s ease infinite;
      display:inline-block;
    }}
    .glitch::before, .glitch::after {{
      content:attr(data-text);
      position:absolute; top:0; left:0;
      background:linear-gradient(90deg,#00f5ff,#bf00ff,#ff6b00);
      background-size:300%;
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
      animation: gshift 4s ease infinite;
    }}
    .glitch::before {{
      clip:rect(0,900px,0,0);
      text-shadow:-2px 0 #ff2d55;
      animation: gshift 4s ease infinite, glitch1 3s infinite linear alternate-reverse;
    }}
    .glitch::after {{
      clip:rect(0,900px,0,0);
      text-shadow:2px 0 #00f5ff;
      animation: gshift 4s ease infinite, glitch2 2.5s infinite linear alternate-reverse;
    }}
    @keyframes gshift {{ 0%{{background-position:0%}} 50%{{background-position:100%}} 100%{{background-position:0%}} }}
    @keyframes glitch-skew {{ 0%,90%{{transform:skewX(0deg)}} 91%{{transform:skewX(-1.5deg)}} 93%{{transform:skewX(1deg)}} 95%{{transform:skewX(0deg)}} }}
    @keyframes glitch1 {{
      0%{{clip:rect(42px,9999px,44px,0);transform:translate(-2px)}}
      20%{{clip:rect(12px,9999px,89px,0);transform:translate(2px)}}
      40%{{clip:rect(65px,9999px,67px,0);transform:translate(-2px)}}
      60%{{clip:rect(1px,9999px,32px,0);transform:translate(2px)}}
      80%{{clip:rect(75px,9999px,77px,0);transform:translate(-2px)}}
      100%{{clip:rect(30px,9999px,50px,0);transform:translate(2px)}}
    }}
    @keyframes glitch2 {{
      0%{{clip:rect(65px,9999px,119px,0);transform:translate(2px)}}
      20%{{clip:rect(5px,9999px,39px,0);transform:translate(-2px)}}
      40%{{clip:rect(80px,9999px,82px,0);transform:translate(2px)}}
      60%{{clip:rect(25px,9999px,27px,0);transform:translate(-2px)}}
      80%{{clip:rect(50px,9999px,100px,0);transform:translate(2px)}}
      100%{{clip:rect(10px,9999px,59px,0);transform:translate(-2px)}}
    }}

    /* NEON PULSE ON BORDERS */
    @keyframes neon-pulse {{
      0%,100%{{ box-shadow:0 0 8px rgba(0,245,255,0.3),0 0 25px rgba(0,245,255,0.1); border-color:rgba(0,245,255,0.25); }}
      50%{{ box-shadow:0 0 20px rgba(0,245,255,0.6),0 0 60px rgba(0,245,255,0.2),0 0 100px rgba(191,0,255,0.1); border-color:rgba(0,245,255,0.55); }}
    }}
    @keyframes float {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-6px)}} }}
    @keyframes fade-up {{ from{{opacity:0;transform:translateY(18px)}} to{{opacity:1;transform:translateY(0)}} }}
    @keyframes border-spin {{
      0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}}
    }}

    /* HERO CARD */
    .hero-card {{
      background:linear-gradient(135deg,rgba(0,245,255,0.055),rgba(191,0,255,0.055));
      border:1px solid rgba(0,245,255,0.22);
      border-radius:18px; padding:2.2rem 3rem; margin-bottom:2rem;
      backdrop-filter:blur(20px);
      animation:neon-pulse 3s ease-in-out infinite, fade-up .6s ease;
      display:flex; align-items:center; gap:2.5rem;
    }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
      background:rgba(2,5,16,0.96) !important;
      border-right:1px solid var(--b1) !important;
      backdrop-filter:blur(28px);
    }}
    section[data-testid="stSidebar"] * {{ color:var(--tx) !important; }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
      font-family:'Orbitron',sans-serif !important;
      color:var(--c) !important; font-size:0.6rem !important;
      letter-spacing:0.22em !important; text-transform:uppercase !important;
      text-shadow:0 0 12px rgba(0,245,255,0.5);
    }}

    /* ALL HEADINGS */
    h1 {{ font-family:'Orbitron',sans-serif !important; font-weight:900 !important; font-size:1.4rem !important;
          background:linear-gradient(90deg,var(--c),var(--m)); -webkit-background-clip:text;
          -webkit-text-fill-color:transparent; background-clip:text; }}
    h2,h3 {{ font-family:'Orbitron',sans-serif !important; color:var(--c) !important; font-weight:700 !important;
             letter-spacing:1px; text-shadow:0 0 18px rgba(0,245,255,0.4); }}
    p,label,div[data-testid="stMarkdownContainer"],.stMarkdown {{ color:var(--tx) !important; font-family:'Inter',sans-serif !important; }}
    .stCaption,small {{ color:var(--mu) !important; }}
    code {{ font-family:'JetBrains Mono',monospace !important; color:var(--c) !important; }}

    /* INPUTS */
    .stTextArea textarea,.stTextInput input {{
      background:rgba(0,245,255,0.035) !important;
      border:1px solid var(--b1) !important; border-radius:10px !important;
      color:var(--tx) !important; font-family:'Inter',sans-serif !important; font-size:0.9rem !important;
      transition:border-color .25s,box-shadow .25s;
    }}
    .stTextArea textarea:focus,.stTextInput input:focus {{
      border-color:var(--c) !important;
      box-shadow:0 0 0 3px rgba(0,245,255,0.14),0 0 30px rgba(0,245,255,0.12) !important;
    }}
    .stSelectbox>div>div {{
      background:rgba(0,245,255,0.035) !important; border:1px solid var(--b1) !important;
      border-radius:10px !important; color:var(--tx) !important;
    }}

    /* PRIMARY BUTTON */
    .stButton>button[kind="primary"] {{
      background:linear-gradient(135deg,#00f5ff,#bf00ff) !important;
      color:#020814 !important; font-family:'Orbitron',sans-serif !important;
      font-weight:700 !important; font-size:0.72rem !important;
      letter-spacing:3px !important; text-transform:uppercase !important;
      border:none !important; border-radius:10px !important; padding:0.65rem 2.2rem !important;
      box-shadow:0 0 22px rgba(0,245,255,0.4),0 0 55px rgba(191,0,255,0.2) !important;
      transition:all .25s !important; position:relative; overflow:hidden;
      animation:btn-glow 2.5s ease-in-out infinite;
    }}
    @keyframes btn-glow {{
      0%,100%{{box-shadow:0 0 22px rgba(0,245,255,0.4),0 0 55px rgba(191,0,255,0.2)}}
      50%{{box-shadow:0 0 35px rgba(0,245,255,0.7),0 0 90px rgba(191,0,255,0.4),0 0 120px rgba(0,245,255,0.15)}}
    }}
    .stButton>button[kind="primary"]:hover {{
      transform:translateY(-2px) scale(1.03) !important;
      box-shadow:0 0 45px rgba(0,245,255,0.75),0 0 100px rgba(191,0,255,0.45) !important;
    }}
    .stButton>button[kind="primary"]:disabled {{ opacity:.3 !important; transform:none !important; animation:none !important; }}

    /* OTHER BUTTONS */
    .stButton>button,.stDownloadButton>button {{
      background:var(--s1) !important; border:1px solid var(--b1) !important;
      color:var(--c) !important; border-radius:8px !important;
      font-family:'Inter',sans-serif !important; font-size:0.8rem !important;
      transition:all .22s !important; position:relative; overflow:hidden;
    }}
    .stButton>button:hover,.stDownloadButton>button:hover {{
      background:rgba(0,245,255,0.11) !important; border-color:var(--c) !important;
      box-shadow:0 0 16px rgba(0,245,255,0.32) !important; transform:translateY(-1px) !important;
    }}

    /* RIPPLE */
    .ripple {{
      position:absolute; border-radius:50%;
      background:rgba(0,245,255,0.35);
      transform:scale(0); animation:ripple .55s linear;
      pointer-events:none;
    }}
    @keyframes ripple {{ to{{transform:scale(4);opacity:0}} }}

    /* EXPANDERS */
    .streamlit-expanderHeader {{
      background:var(--s1) !important; border:1px solid var(--b1) !important;
      border-radius:10px !important; color:var(--tx) !important;
      font-family:'Inter',sans-serif !important;
      transition:background .2s,box-shadow .2s !important;
    }}
    .streamlit-expanderHeader:hover {{
      background:rgba(0,245,255,0.1) !important;
      box-shadow:0 0 14px rgba(0,245,255,0.2) !important;
    }}
    .streamlit-expanderContent {{
      background:rgba(2,8,20,0.65) !important; border:1px solid var(--b1) !important;
      border-top:none !important; border-radius:0 0 10px 10px !important;
      backdrop-filter:blur(10px);
    }}

    /* STATUS */
    .stSuccess{{background:rgba(0,255,136,0.07)!important;border:1px solid rgba(0,255,136,0.35)!important;border-radius:10px!important;color:var(--g)!important;}}
    .stError{{background:rgba(255,45,85,0.08)!important;border:1px solid rgba(255,45,85,0.4)!important;border-radius:10px!important;}}
    .stWarning{{background:rgba(255,107,0,0.08)!important;border:1px solid rgba(255,107,0,0.4)!important;border-radius:10px!important;}}
    .stSpinner>div{{border-top-color:var(--c)!important;}}

    img {{ border-radius:12px; border:1px solid var(--b1); box-shadow:0 0 25px rgba(0,245,255,0.08); }}
    hr {{ border-color:var(--b1)!important; }}
    .stJson{{background:rgba(0,0,0,0.55)!important;border:1px solid var(--b1)!important;border-radius:10px!important;}}
    ::-webkit-scrollbar{{width:5px;height:5px;}}
    ::-webkit-scrollbar-track{{background:rgba(0,0,0,0.4);}}
    ::-webkit-scrollbar-thumb{{background:var(--c);border-radius:3px;}}
    ::-webkit-scrollbar-thumb:hover{{background:var(--m);}}

    /* TOP PROGRESS LINE */
    .top-bar{{position:fixed;top:0;left:0;height:2px;width:100%;z-index:9999;
      background:linear-gradient(90deg,#00f5ff,#bf00ff,#ff6b00,#00f5ff);
      background-size:300%;
      animation:border-spin 3s linear infinite;
    }}

    /* CORNER BRACKETS on cards */
    .cx-card {{
      position:relative; border:1px solid rgba(0,245,255,0.15);
      border-radius:12px; padding:1.4rem 1.6rem; margin:0.5rem 0;
      background:rgba(0,245,255,0.03); backdrop-filter:blur(10px);
      animation:fade-up .5s ease, neon-pulse 4s ease-in-out infinite;
      transition:transform .25s,box-shadow .25s;
    }}
    .cx-card:hover {{ transform:translateY(-3px); box-shadow:0 0 40px rgba(0,245,255,0.12); }}
    .cx-card::before,.cx-card::after {{
      content:''; position:absolute; width:14px; height:14px;
    }}
    .cx-card::before {{ top:-1px; left:-1px; border-top:2px solid var(--c); border-left:2px solid var(--c); border-radius:2px 0 0 0; }}
    .cx-card::after  {{ bottom:-1px; right:-1px; border-bottom:2px solid var(--m); border-right:2px solid var(--m); border-radius:0 0 2px 0; }}
  `;
  D.head.appendChild(S);

  /* ── 2. TOP PROGRESS BAR ── */
  const bar = D.createElement('div');
  bar.className='top-bar'; D.body.prepend(bar);

  /* ── 3. PARTICLE CANVAS ── */
  const canvas = D.createElement('canvas');
  Object.assign(canvas.style,{{
    position:'fixed',top:'0',left:'0',width:'100%',height:'100%',
    zIndex:'0',pointerEvents:'none',opacity:'0.55'
  }});
  D.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let W,H,particles=[];

  function resize(){{ W=canvas.width=D.body.offsetWidth; H=canvas.height=D.body.offsetHeight; }}
  resize();
  new ResizeObserver(resize).observe(D.body);

  const COLORS=['#00f5ff','#bf00ff','#00ff88','#ff6b00'];
  function mkParticle(){{
    return {{
      x:Math.random()*W, y:Math.random()*H,
      vx:(Math.random()-.5)*0.45, vy:(Math.random()-.5)*0.45,
      r:Math.random()*1.8+0.4,
      c:COLORS[Math.floor(Math.random()*COLORS.length)],
      a:Math.random()*0.6+0.2,
      life:Math.random()*200+100, age:0,
    }};
  }}
  for(let i=0;i<130;i++) particles.push(mkParticle());

  function drawParticles(){{
    ctx.clearRect(0,0,W,H);
    particles.forEach((p,i)=>{{
      p.x+=p.vx; p.y+=p.vy; p.age++;
      if(p.x<0||p.x>W||p.y<0||p.y>H||p.age>p.life) particles[i]=mkParticle();
      // draw connections
      particles.forEach((q,j)=>{{
        if(j<=i) return;
        const dx=p.x-q.x, dy=p.y-q.y, dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<100){{
          ctx.save();
          ctx.globalAlpha=(1-dist/100)*0.18;
          ctx.strokeStyle=p.c; ctx.lineWidth=0.6;
          ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y); ctx.stroke();
          ctx.restore();
        }}
      }});
      ctx.save();
      ctx.globalAlpha=p.a*(1-p.age/p.life);
      ctx.shadowBlur=8; ctx.shadowColor=p.c; ctx.fillStyle=p.c;
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();
      ctx.restore();
    }});
    requestAnimationFrame(drawParticles);
  }}
  drawParticles();

  /* ── 4. MATRIX RAIN ── */
  const rain = D.createElement('canvas');
  Object.assign(rain.style,{{
    position:'fixed',top:'0',left:'0',width:'100%',height:'100%',
    zIndex:'0',pointerEvents:'none',opacity:'0.07'
  }});
  D.body.appendChild(rain);

  const rc=rain.getContext('2d');
  rain.width=D.body.offsetWidth; rain.height=D.body.offsetHeight;
  const cols=Math.floor(rain.width/20);
  const drops=Array(cols).fill(1);
  const chars='アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789ABCDEF⚡◆▲';

  function matrixRain(){{
    rc.fillStyle='rgba(2,8,20,0.05)';
    rc.fillRect(0,0,rain.width,rain.height);
    rc.fillStyle='#00f5ff'; rc.font='14px JetBrains Mono,monospace';
    drops.forEach((y,i)=>{{
      const ch=chars[Math.floor(Math.random()*chars.length)];
      rc.fillText(ch,i*20,y*20);
      if(y*20>rain.height&&Math.random()>.975) drops[i]=0;
      drops[i]++;
    }});
  }}
  setInterval(matrixRain,55);

  /* ── 5. RIPPLE on buttons ── */
  D.addEventListener('click',e=>{{
    const btn=e.target.closest('button');
    if(!btn) return;
    const r=D.createElement('span'); r.className='ripple';
    const rect=btn.getBoundingClientRect();
    const size=Math.max(rect.width,rect.height);
    Object.assign(r.style,{{
      width:size+'px',height:size+'px',
      left:(e.clientX-rect.left-size/2)+'px',
      top:(e.clientY-rect.top-size/2)+'px',
    }});
    btn.style.position='relative'; btn.style.overflow='hidden';
    btn.appendChild(r);
    setTimeout(()=>r.remove(),600);
  }});

  /* ── 6. CURSOR GLOW ── */
  const cursor = D.createElement('div');
  Object.assign(cursor.style,{{
    position:'fixed', width:'20px', height:'20px', borderRadius:'50%',
    border:'1.5px solid rgba(0,245,255,0.7)',
    pointerEvents:'none', zIndex:'99999',
    transform:'translate(-50%,-50%)',
    transition:'width .15s,height .15s,opacity .2s',
    boxShadow:'0 0 12px rgba(0,245,255,0.5)',
    display:'block',
  }});
  D.body.appendChild(cursor);

  const dot = D.createElement('div');
  Object.assign(dot.style,{{
    position:'fixed', width:'4px', height:'4px', borderRadius:'50%',
    background:'#00f5ff', pointerEvents:'none', zIndex:'99999',
    transform:'translate(-50%,-50%)',
    boxShadow:'0 0 8px #00f5ff',
  }});
  D.body.appendChild(dot);

  D.addEventListener('mousemove',e=>{{
    cursor.style.left=e.clientX+'px'; cursor.style.top=e.clientY+'px';
    dot.style.left=e.clientX+'px';   dot.style.top=e.clientY+'px';
  }});
  D.addEventListener('mousedown',()=>{{
    cursor.style.width='35px'; cursor.style.height='35px';
    cursor.style.borderColor='rgba(191,0,255,0.9)';
    cursor.style.boxShadow='0 0 22px rgba(191,0,255,0.7)';
  }});
  D.addEventListener('mouseup',()=>{{
    cursor.style.width='20px'; cursor.style.height='20px';
    cursor.style.borderColor='rgba(0,245,255,0.7)';
    cursor.style.boxShadow='0 0 12px rgba(0,245,255,0.5)';
  }});

}})();
</script>
""", height=0)

# ═══════════════════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════════════════
try:
    _h = requests.get(f"{API}/health", timeout=2).json()
    _prov = _h.get("provider", "")
    _status = f'<span style="background:rgba(0,255,136,0.12);border:1px solid rgba(0,255,136,0.4);color:#00ff88;padding:3px 12px;border-radius:20px;font-size:0.68rem;letter-spacing:2px;">● ONLINE</span><span style="color:rgba(232,244,255,0.35);font-size:0.7rem;margin-left:10px;font-family:monospace;">{_prov}</span>'
except Exception:
    _status = '<span style="color:#ff2d55;font-size:0.75rem;">● OFFLINE</span>'

st.markdown(f"""
<div class="hero-card">
  <div style="flex:1;min-width:0;">
    <div style="font-family:Orbitron,sans-serif;font-size:0.6rem;color:rgba(0,245,255,0.65);letter-spacing:5px;text-transform:uppercase;margin-bottom:0.5rem;">⚡ Industrial AI Pipeline v1.0</div>
    <div class="glitch" data-text="TASKFLOW" style="font-family:Orbitron,sans-serif;font-size:3rem;font-weight:900;letter-spacing:5px;background:linear-gradient(90deg,#00f5ff,#bf00ff,#ff6b00,#00f5ff);background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:gshift 4s ease infinite;">TASKFLOW</div>
    <div style="color:rgba(232,244,255,0.55);font-size:0.9rem;margin-top:0.5rem;max-width:460px;line-height:1.6;">Transform natural language into validated Task Flow DAGs — swap providers in the sidebar.</div>
    <div style="margin-top:0.9rem;">{_status}</div>
  </div>
  <div style="flex-shrink:0;position:relative;">
    <img src="data:image/png;base64,{_SUNSET}" style="width:230px;height:138px;object-fit:cover;border-radius:14px;border:1px solid rgba(0,245,255,0.25);box-shadow:0 0 40px rgba(0,245,255,0.12),0 0 80px rgba(191,0,255,0.08);animation:float 4s ease-in-out infinite;"/>
    <div style="position:absolute;inset:0;border-radius:14px;background:linear-gradient(135deg,transparent 60%,rgba(0,245,255,0.06));pointer-events:none;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
EXAMPLES = [
    "Pick the red box from Shelf A, inspect it, and place it on Conveyor Belt 3.",
    "Navigate to Station 2, scan barcode on the package, then move it to the output tray.",
    "Retrieve the blue cylinder from storage, verify weight, assemble with component B, and seal.",
    "Pick item from room 1, drop at room 3, while dropping three products at room 2.",
]

_PROVIDER_META = {
    "gemini": {"label": "☁  Gemini (Google)", "color": "#4285F4", "needs_key": True,  "needs_url": False, "default_model": "gemini-2.5-flash"},
    "ollama": {"label": "🖥  Ollama (Local)",  "color": "#00ff88", "needs_key": False, "needs_url": True,  "default_model": "llama3.2"},
    "openai": {"label": "☁  OpenAI",           "color": "#bf00ff", "needs_key": True,  "needs_url": False, "default_model": "gpt-4o"},
    "mock":   {"label": "🧪  Mock (offline)",  "color": "#ff6b00", "needs_key": False, "needs_url": False, "default_model": "mock-deterministic-v1"},
}

with st.sidebar:
    st.markdown("### LLM PROVIDER")

    # fetch current provider from backend
    try:
        _cur = requests.get(f"{API}/health", timeout=2).json().get("provider", "")
        _cur_name = _cur.split(":")[0] if ":" in _cur else _cur
    except Exception:
        _cur_name = ""

    selected_provider = st.selectbox(
        "Provider", options=list(_PROVIDER_META.keys()),
        format_func=lambda k: _PROVIDER_META[k]["label"],
        index=list(_PROVIDER_META.keys()).index(_cur_name) if _cur_name in _PROVIDER_META else 0,
        label_visibility="collapsed",
    )

    meta = _PROVIDER_META[selected_provider]

    # for Ollama: show a dropdown of installed models, fall back to text input if none
    if selected_provider == "ollama":
        try:
            _om = requests.get(f"{API}/ollama/models", timeout=3).json()
            _installed = [m["name"] for m in _om.get("models", [])]
        except Exception:
            _installed = []

        if _installed:
            model_val = st.selectbox("Model", options=_installed, label_visibility="visible")
        else:
            st.caption("No models installed yet — pull one below first.")
            model_val = st.text_input("Model", value=meta["default_model"], placeholder="model name")
    else:
        model_val = st.text_input("Model", value=meta["default_model"], placeholder="model name")

    api_key_val = ""
    if meta["needs_key"]:
        api_key_val = st.text_input("API Key", type="password", placeholder="paste your key…")

    base_url_val = "http://localhost:11434"
    if meta["needs_url"]:
        base_url_val = st.text_input("Ollama URL", value="http://localhost:11434")

    if st.button("⚡  CONNECT", type="primary", use_container_width=True):
        payload = {"provider": selected_provider, "model": model_val,
                   "api_key": api_key_val, "base_url": base_url_val}
        try:
            r = requests.patch(f"{API}/provider", json=payload, timeout=10)
            if r.ok:
                d = r.json()
                st.success(f"Switched → {d['provider']}:{d['model']}")
            else:
                _play_error(); st.error(r.json().get("detail", r.text))
        except Exception as e:
            _play_error(); st.error(f"Cannot reach backend: {e}")

    # current provider badge
    if _cur_name in _PROVIDER_META:
        c = _PROVIDER_META[_cur_name]["color"]
        st.markdown(f'<div style="margin-top:6px;padding:6px 12px;border-radius:8px;border:1px solid {c}44;background:{c}11;color:{c};font-size:0.7rem;font-family:Orbitron,sans-serif;letter-spacing:1px;text-align:center;">ACTIVE: {_cur}</div>', unsafe_allow_html=True)

    # ── Ollama model manager (only shown when Ollama is selected) ──
    if selected_provider == "ollama":
        st.divider()
        st.markdown("### OLLAMA MODELS")

        # list installed models
        try:
            mdata = requests.get(f"{API}/ollama/models", timeout=5).json()
            if mdata.get("error"):
                st.warning(mdata["error"])
            else:
                installed = mdata.get("models", [])
                if installed:
                    for m in installed:
                        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(0,245,255,0.08);"><span style="color:#00ff88;font-size:0.75rem;font-family:monospace;">{m["name"]}</span><span style="color:rgba(232,244,255,0.35);font-size:0.7rem;">{m["size"]}</span></div>', unsafe_allow_html=True)
                else:
                    st.caption("No models installed yet.")
        except Exception:
            st.caption("Backend offline.")

        st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
        pull_model_name = st.text_input("Pull a model", placeholder="e.g. llama3.2, qwen2.5:7b", label_visibility="visible")
        pull_btn = st.button("⬇  PULL MODEL", use_container_width=True, disabled=not pull_model_name.strip())

        if pull_btn and pull_model_name.strip():
            st.session_state["_pull_job"] = None
            try:
                r = requests.post(f"{API}/ollama/pull", json={"model": pull_model_name.strip()}, timeout=5)
                if r.ok:
                    st.session_state["_pull_job"] = r.json()["job_id"]
                else:
                    _play_error(); st.error(r.text)
            except Exception as e:
                _play_error(); st.error(str(e))

        # poll and show progress
        if st.session_state.get("_pull_job"):
            job_id = st.session_state["_pull_job"]
            progress_box = st.empty()
            try:
                job = requests.get(f"{API}/ollama/pull/{job_id}", timeout=5).json()
                last_line = job["lines"][-1] if job["lines"] else job["status"]
                if job["error"]:
                    progress_box.error(job["error"])
                    st.session_state["_pull_job"] = None
                elif job["done"]:
                    progress_box.success(f"✓ {pull_model_name} ready!")
                    st.session_state["_pull_job"] = None
                else:
                    progress_box.markdown(f'<div style="color:#00f5ff;font-size:0.72rem;font-family:monospace;padding:6px;background:rgba(0,245,255,0.05);border-radius:6px;border:1px solid rgba(0,245,255,0.15);">⬇ {last_line}</div>', unsafe_allow_html=True)
                    import time; time.sleep(1); st.rerun()
            except Exception:
                pass

    st.divider()
    st.markdown("### EXAMPLES")
    for ex in EXAMPLES:
        if st.button((ex[:50]+"…") if len(ex)>50 else ex, key=f"ex_{hash(ex)}", use_container_width=True):
            st.session_state["_instr"] = ex
    st.divider()
    st.markdown('<div style="color:rgba(0,245,255,0.2);font-size:0.6rem;text-align:center;font-family:Orbitron,sans-serif;letter-spacing:3px;">TASKFLOW v1.0.0</div>', unsafe_allow_html=True)

api_url = API

# ═══════════════════════════════════════════════════════════
#  INPUT
# ═══════════════════════════════════════════════════════════
if "_instr" not in st.session_state:
    st.session_state["_instr"] = ""
if "_pull_job" not in st.session_state:
    st.session_state["_pull_job"] = None

st.markdown("### INSTRUCTION INPUT")
instruction = st.text_area(
    "instr", value=st.session_state["_instr"], height=95,
    placeholder="Describe the industrial task in plain English…",
    label_visibility="collapsed", key="instr_box",
)
run = st.button("⚡  EXECUTE PIPELINE", type="primary", disabled=not instruction.strip())

# ═══════════════════════════════════════════════════════════
#  PIPELINE
# ═══════════════════════════════════════════════════════════
ACTION_COLORS = {
    "navigate":"#2563EB","locate":"#0891B2","pick":"#16A34A","place":"#DC2626",
    "inspect":"#9333EA","scan":"#D97706","sort":"#0D9488","transfer":"#7C3AED",
    "move":"#DB2777","assemble":"#EA580C","verify":"#059669","deliver":"#B45309",
}

if run and instruction.strip():
    with st.spinner("Firing up model…"):
        try:
            resp = requests.post(f"{api_url}/instructions",
                                 json={"instruction": instruction.strip()}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as e:
            _play_error(); st.error(f"API {e.response.status_code}: {e.response.text}"); st.stop()
        except Exception as e:
            _play_error(); st.error(f"Request failed: {e}"); st.stop()

    pid = data["pipeline_id"]
    tasks = data["plan"]["tasks"]
    v = data["validation"]
    artifacts = data.get("artifacts", {})

    st.markdown(f'<div style="background:rgba(0,245,255,0.05);border:1px solid rgba(0,245,255,0.22);border-radius:10px;padding:0.75rem 1.4rem;margin:0.8rem 0 1.6rem;animation:fade-up .4s ease;display:flex;align-items:center;gap:1rem;"><span style="font-size:1.2rem;">⚡</span><div><div style="font-family:Orbitron,sans-serif;font-size:0.65rem;color:#00f5ff;letter-spacing:3px;text-transform:uppercase;">Pipeline Complete</div><div style="color:rgba(232,244,255,0.45);font-size:0.75rem;margin-top:2px;font-family:monospace;">ID: <span style="color:#bf00ff;">{pid}</span></div></div></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    # ── TASK PLAN ──────────────────────────────────────────
    with col_l:
        st.markdown(f'### TASK PLAN <span style="font-size:0.72rem;color:rgba(0,245,255,0.45);font-family:Inter,sans-serif;">{len(tasks)} tasks</span>', unsafe_allow_html=True)
        for t in tasks:
            c = ACTION_COLORS.get(t["action"], "#475569")
            deps = " → ".join(t["depends_on"]) if t["depends_on"] else "START"
            with st.expander(f"{t['id']}  ·  {t['description']}", expanded=False):
                cond_badge = f'<span style="color:#ff6b00;font-size:0.68rem;font-family:Orbitron,sans-serif;letter-spacing:1px;">◆ CONDITIONAL</span>' if t.get("condition") else ""
                st.markdown(f'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px;"><span style="background:{c}22;border:1px solid {c}66;color:{c};padding:2px 12px;border-radius:20px;font-size:0.7rem;font-family:Orbitron,sans-serif;letter-spacing:1px;font-weight:600;">{t["action"].upper()}</span><span style="color:rgba(232,244,255,0.38);font-size:0.76rem;">after: <strong style="color:rgba(232,244,255,0.65);">{deps}</strong></span>{cond_badge}</div>', unsafe_allow_html=True)
                if t.get("condition"): st.caption(f"Condition: `{t['condition']}`")
                if t.get("metadata"): st.json(t["metadata"], expanded=False)

    # ── VALIDATION ─────────────────────────────────────────
    with col_r:
        passed = v.get("valid", False)
        sc = "#00ff88" if passed else "#ff2d55"
        st.markdown(f'### VALIDATION <span style="font-size:0.72rem;color:{sc};">{"✓ PASSED" if passed else "✗ FAILED"}</span>', unsafe_allow_html=True)
        CHECK_KEYS = ["cycle_check","dependency_check","reachability_check",
                      "action_check","conditional_check","structural_check","consistency_check"]
        rows = "".join(
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(0,245,255,0.07);"><span style="color:rgba(232,244,255,0.55);font-size:0.78rem;">{k.replace("_check","").replace("_"," ").title()}</span><span style="color:{"#00f5ff" if v.get(k)=="passed" else "#ff2d55"};font-size:0.72rem;font-family:Orbitron,sans-serif;letter-spacing:1px;">{"✓" if v.get(k)=="passed" else "✗"} {(v.get(k) or "—").upper()}</span></div>'
            for k in CHECK_KEYS if v.get(k) is not None
        )
        st.markdown(f'<div class="cx-card"><div style="display:flex;justify-content:space-between;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid rgba(0,245,255,0.1);"><span style="color:rgba(0,245,255,0.55);font-size:0.65rem;font-family:Orbitron,sans-serif;letter-spacing:2px;">GRAPH STATS</span><span style="color:rgba(232,244,255,0.55);font-size:0.75rem;font-family:monospace;">{v.get("node_count",0)} nodes · {v.get("edge_count",0)} edges</span></div>{rows}</div>', unsafe_allow_html=True)
        if v.get("issues"): st.warning("Issues: " + " · ".join(i if isinstance(i, str) else i.get("message", str(i)) for i in v["issues"]))

    # ── GRAPH ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### TASK GRAPH")
    if "task_graph.png" in artifacts:
        img = requests.get(f"{api_url}/downloads/{pid}/task_graph.png", timeout=15)
        if img.ok: st.image(img.content, use_container_width=True)
    if "task_graph.html" in artifacts:
        html = requests.get(f"{api_url}/downloads/{pid}/task_graph.html", timeout=10)
        if html.ok:
            with st.expander("⬡  Interactive Graph", expanded=False):
                st.components.v1.html(html.text, height=520, scrolling=True)

    # ── DOWNLOADS ──────────────────────────────────────────
    st.markdown("### EXPORT")
    dl_cols = st.columns(min(len(artifacts), 6))
    for i, name in enumerate(artifacts):
        r2 = requests.get(f"{api_url}/downloads/{pid}/{name}", timeout=10)
        if r2.ok: dl_cols[i%len(dl_cols)].download_button(name, data=r2.content, file_name=name, key=f"dl_{name}")

    with st.expander("⬡  Raw API Response", expanded=False):
        st.json(data)
