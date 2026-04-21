import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db import init_db, get_db
from ai_engine.predictor import predict
from datetime import datetime

st.set_page_config(page_title="HoneypotX", page_icon="🕷️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');
* { font-family: 'Share Tech Mono', monospace; }
html, body, [data-testid="stAppViewContainer"] { background-color: #020810 !important; color: #00ff88 !important; }
h1,h2,h3 { font-family: 'Orbitron', monospace !important; }

.metric-card { background: linear-gradient(135deg, rgba(0,255,136,0.05), rgba(0,0,0,0.8)); border: 1px solid rgba(0,255,136,0.3); border-radius: 4px; padding: 20px; text-align: center; position: relative; overflow: hidden; }
.metric-card::before { content:''; position:absolute; top:0;left:0;right:0; height:1px; background: linear-gradient(90deg, transparent, #00ff88, transparent); }
.metric-value { font-family:'Orbitron',monospace; font-size:2.5rem; font-weight:900; color:#00ff88; text-shadow:0 0 20px rgba(0,255,136,0.5); line-height:1; }
.metric-label { font-size:0.7rem; color:rgba(0,255,136,0.5); text-transform:uppercase; letter-spacing:3px; margin-top:8px; }

.metric-card.danger { border-color:rgba(255,50,50,0.4); background:linear-gradient(135deg,rgba(255,50,50,0.05),rgba(0,0,0,0.8)); }
.metric-card.danger::before { background:linear-gradient(90deg,transparent,#ff3232,transparent); }
.metric-card.danger .metric-value { color:#ff3232; text-shadow:0 0 20px rgba(255,50,50,0.5); }
.metric-card.danger .metric-label { color:rgba(255,50,50,0.5); }

.metric-card.warning { border-color:rgba(255,200,0,0.4); background:linear-gradient(135deg,rgba(255,200,0,0.05),rgba(0,0,0,0.8)); }
.metric-card.warning::before { background:linear-gradient(90deg,transparent,#ffc800,transparent); }
.metric-card.warning .metric-value { color:#ffc800; text-shadow:0 0 20px rgba(255,200,0,0.5); }
.metric-card.warning .metric-label { color:rgba(255,200,0,0.5); }

.metric-card.info { border-color:rgba(0,200,255,0.4); background:linear-gradient(135deg,rgba(0,200,255,0.05),rgba(0,0,0,0.8)); }
.metric-card.info::before { background:linear-gradient(90deg,transparent,#00c8ff,transparent); }
.metric-card.info .metric-value { color:#00c8ff; text-shadow:0 0 20px rgba(0,200,255,0.5); }
.metric-card.info .metric-label { color:rgba(0,200,255,0.5); }

.section-header { font-family:'Orbitron',monospace; font-size:0.65rem; color:rgba(0,255,136,0.4); text-transform:uppercase; letter-spacing:5px; border-bottom:1px solid rgba(0,255,136,0.1); padding-bottom:8px; margin-bottom:16px; }

.result-box { border:1px solid rgba(0,255,136,0.2); border-radius:4px; padding:20px; background:rgba(0,255,136,0.02); margin-top:12px; }
.input-panel { border:1px solid rgba(0,255,136,0.2); border-radius:4px; padding:20px; background:rgba(0,255,136,0.02); margin-bottom:24px; position:relative; }
.input-panel::before { content:''; position:absolute; top:0;left:0;right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(0,255,136,0.4),transparent); }

[data-testid="stTextArea"] textarea { background:#020810 !important; color:#00ff88 !important; border:1px solid rgba(0,255,136,0.3) !important; border-radius:4px !important; font-family:'Share Tech Mono',monospace !important; }
[data-testid="stSelectbox"] > div > div { background:#020810 !important; color:#00ff88 !important; border-color:rgba(0,255,136,0.3) !important; }
[data-testid="stButton"] button { background:transparent !important; border:1px solid rgba(0,255,136,0.4) !important; color:#00ff88 !important; font-family:'Share Tech Mono',monospace !important; letter-spacing:2px !important; border-radius:2px !important; width:100%; }
[data-testid="stButton"] button:hover { border-color:#00ff88 !important; box-shadow:0 0 15px rgba(0,255,136,0.2) !important; }
.stDataFrame td, .stDataFrame th { color:#00ff88 !important; background:rgba(0,255,136,0.02) !important; border-color:rgba(0,255,136,0.1) !important; }
.block-container { padding:1.5rem 2rem !important; }
.title-main { font-family:'Orbitron',monospace; font-size:3rem; font-weight:900; color:#00ff88; text-shadow:0 0 40px rgba(0,255,136,0.4); letter-spacing:8px; text-align:center; }
.title-sub { font-size:0.65rem; color:rgba(0,255,136,0.35); letter-spacing:10px; text-transform:uppercase; margin-top:4px; text-align:center; }
.status-dot { display:inline-block; width:8px; height:8px; background:#00ff88; border-radius:50%; box-shadow:0 0 10px #00ff88; animation:pulse 2s infinite; margin-right:8px; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
</style>
""", unsafe_allow_html=True)

init_db()
db = get_db()

ATTACK_COLORS = {
    "sql":        "#ff3232",
    "bruteforce": "#ffc800",
    "xss":        "#ff6b35",
    "cmdinject":  "#ff0080",
    "traversal":  "#aa44ff",
    "normal":     "#00ff88",
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Share Tech Mono", color="#00ff88", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
)

QUICK_PAYLOADS = {
    "SQL Injection":     "' OR 1=1-- select * from users",
    "Brute Force":       "login admin password 123456",
    "XSS":               "<script>alert(document.cookie)</script>",
    "Command Injection": "; cat /etc/passwd && whoami",
    "Path Traversal":    "../../etc/passwd",
    "Normal Request":    "GET /home user dashboard load",
}

def fetch_logs():
    logs = list(db.logs.find({}, {"_id": 0}))
    return pd.DataFrame(logs) if logs else pd.DataFrame(columns=["ip","endpoint","payload","attack_type","risk"])

# ── HEADER ──
st.markdown("""
<div style="padding:20px 0 24px">
    <div class="title-main">HONEYPOTX</div>
    <div class="title-sub"><span class="status-dot"></span>AI Threat Intelligence System · Live</div>
</div>
""", unsafe_allow_html=True)

col_r, col_f = st.columns([6,1])
with col_r:
    auto = st.checkbox("Auto-refresh (5s)", value=False)
with col_f:
    if st.button("⟳ REFRESH"):
        st.rerun()

# ── INPUT PANEL ──
st.markdown('<div class="section-header">Payload Analyzer — Test Any Input</div>', unsafe_allow_html=True)
st.markdown('<div class="input-panel">', unsafe_allow_html=True)

quick_col, input_col = st.columns([1, 2])

with quick_col:
    st.markdown('<div style="font-size:0.65rem;color:rgba(0,255,136,0.4);letter-spacing:3px;margin-bottom:10px;">QUICK PAYLOADS</div>', unsafe_allow_html=True)
    selected_quick = st.selectbox("Quick payload", list(QUICK_PAYLOADS.keys()), label_visibility="collapsed")
    if st.button("▶ LOAD PAYLOAD"):
        st.session_state["payload_val"] = QUICK_PAYLOADS[selected_quick]
        st.rerun()

with input_col:
    default_val = st.session_state.get("payload_val", "")
    payload_text = st.text_area(
        "Payload input",
        value=default_val,
        height=110,
        placeholder="Type any payload to analyze...\nExamples:\n  ' OR 1=1--\n  <script>alert(1)</script>\n  ; cat /etc/passwd",
        label_visibility="collapsed",
    )

a_col, _ = st.columns([1, 3])
with a_col:
    analyze_clicked = st.button("⚡ ANALYZE THREAT")

if analyze_clicked:
    if payload_text.strip():
        attack_type, risk = predict(payload_text.strip())
        color = ATTACK_COLORS.get(attack_type, "#00ff88")
        is_threat = attack_type != "normal"

        db.logs.insert_one({
            "ip": "dashboard-user",
            "endpoint": "/analyzer",
            "payload": payload_text.strip(),
            "attack_type": attack_type,
            "risk": risk
        })

        st.markdown(f"""
        <div class="result-box">
            <div style="display:flex;gap:40px;align-items:center;flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.6rem;color:rgba(0,255,136,0.4);letter-spacing:3px;margin-bottom:4px;">ATTACK TYPE</div>
                    <div style="font-family:Orbitron,monospace;font-size:1.8rem;font-weight:900;color:{color};text-shadow:0 0 20px {color};">{attack_type.upper()}</div>
                </div>
                <div>
                    <div style="font-size:0.6rem;color:rgba(0,255,136,0.4);letter-spacing:3px;margin-bottom:4px;">RISK SCORE</div>
                    <div style="font-family:Orbitron,monospace;font-size:1.8rem;font-weight:900;color:{color};text-shadow:0 0 20px {color};">{risk}/100</div>
                </div>
                <div>
                    <div style="font-size:0.6rem;color:rgba(0,255,136,0.4);letter-spacing:3px;margin-bottom:4px;">STATUS</div>
                    <div style="font-family:Orbitron,monospace;font-size:1rem;font-weight:700;color:{color};">{"⚠ THREAT DETECTED" if is_threat else "✓ NORMAL TRAFFIC"}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Enter a payload first.")

st.markdown('</div>', unsafe_allow_html=True)

# ── METRICS ──
df = fetch_logs()
total     = len(df)
threats   = len(df[df["attack_type"] != "normal"]) if total else 0
avg_risk  = int(df["risk"].mean()) if total else 0
top_ip    = df["ip"].value_counts().index[0] if total else "—"
top_count = int(df["ip"].value_counts().iloc[0]) if total else 0

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card info"><div class="metric-value">{total}</div><div class="metric-label">Total Requests</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card danger"><div class="metric-value">{threats}</div><div class="metric-label">Threats Detected</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card warning"><div class="metric-value">{avg_risk}</div><div class="metric-label">Avg Risk Score</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="font-size:1.3rem">{top_ip}</div><div class="metric-label">Top Attacker · {top_count} hits</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── CHARTS ──
if total:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-header">Attack Distribution</div>', unsafe_allow_html=True)
        ac = df["attack_type"].value_counts()
        colors = [ATTACK_COLORS.get(t, "#888888") for t in ac.index]
        fig_pie = go.Figure(go.Pie(
            labels=ac.index, values=ac.values, hole=0.6,
            marker=dict(colors=colors, line=dict(color="#020810", width=2)),
            textfont=dict(family="Share Tech Mono", size=10),
            textinfo="label+percent",
        ))
        fig_pie.update_layout(**PLOTLY_THEME, height=260,
            annotations=[dict(text=f"<b>{total}</b><br>total", x=0.5, y=0.5,
                font=dict(color="#00ff88", size=13, family="Orbitron"), showarrow=False)])
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown('<div class="section-header">Risk by Attack Type</div>', unsafe_allow_html=True)
        ra = df.groupby("attack_type")["risk"].mean().sort_values(ascending=True)
        colors_bar = [ATTACK_COLORS.get(t, "#888888") for t in ra.index]
        fig_bar = go.Figure(go.Bar(
            x=ra.values, y=ra.index, orientation="h",
            marker=dict(color=colors_bar, opacity=0.85),
            text=[f"{v:.0f}" for v in ra.values],
            textposition="outside",
            textfont=dict(color="#00ff88", size=10),
        ))
        fig_bar.update_layout(**PLOTLY_THEME, height=260,
            xaxis=dict(range=[0,110], showgrid=True, gridcolor="rgba(0,255,136,0.07)", zeroline=False),
            yaxis=dict(showgrid=False))
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

# ── LOG TABLE ──
st.markdown('<div class="section-header">Live Attack Log</div>', unsafe_allow_html=True)
if total:
    fc, _ = st.columns([2, 4])
    with fc:
        types = ["ALL"] + list(df["attack_type"].unique())
        sel = st.selectbox("Filter", types, label_visibility="collapsed")
    ddf = df if sel == "ALL" else df[df["attack_type"] == sel]
    ddf = ddf[["ip","endpoint","attack_type","risk","payload"]].copy()
    ddf.columns = ["IP","Endpoint","Attack Type","Risk","Payload"]
    st.dataframe(ddf[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
else:
    st.markdown('<div style="border:1px solid rgba(0,255,136,0.1);padding:40px;text-align:center;color:rgba(0,255,136,0.3);"><div style="font-family:Orbitron;font-size:1.2rem">NO ATTACKS DETECTED</div><div style="font-size:0.75rem;letter-spacing:2px;margin-top:8px;">SYSTEM MONITORING · AWAITING THREATS</div></div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center;font-size:0.6rem;color:rgba(0,255,136,0.2);letter-spacing:3px;margin-top:20px;">HONEYPOTX v1.0 · AI THREAT DETECTION · {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

if auto:
    import time; time.sleep(5); st.rerun()