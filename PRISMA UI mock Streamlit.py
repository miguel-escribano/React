# app.py
# Streamlit PRISMA mock: GIS map (top), Chat (left), Agent Brain & A2A Logs (right)
# Run: streamlit run app.py

import time
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="PRISMA Mock (Streamlit)", layout="wide", page_icon="⚡")

# ---------- Helpers ----------
def now():
    return datetime.now().strftime("%H:%M:%S")

def severity_badge(level: str | None):
    if not level:
        return ""
    colors = {
        "HIGH": ("#FEE2E2", "#DC2626"),
        "MEDIUM": ("#FFEDD5", "#EA580C"),
        "LOW": ("#DCFCE7", "#16A34A"),
    }
    bg, fg = colors.get(level, ("#E5E7EB", "#374151"))
    return f"""
    <span style="
        background:{bg};
        color:{fg};
        padding:2px 8px;
        border-radius:999px;
        font-size:11px;
        font-weight:600;
        margin-left:6px;
        ">
        {level}
    </span>
    """

def render_log_card(step, detail, ts, severity=None):
    st.markdown(
        f"""
        <div style="background:white;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#6B7280;margin-bottom:6px;">
            <div style="font-weight:700;color:#111827;display:flex;align-items:center;gap:6px;">
              <span>{step}</span>
              {severity_badge(severity)}
            </div>
            <div>{ts}</div>
          </div>
          <div style="font-size:13px;color:#4B5563;">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- State ----------
if "chat" not in st.session_state:
    st.session_state.chat = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "demo_started" not in st.session_state:
    st.session_state.demo_started = False
if "log_index" not in st.session_state:
    st.session_state.log_index = 0

# Pre-scripted chat (includes human-in-the-loop)
CHAT_SEQUENCE = [
    {"sender": "System", "text": "⚡ Blackout detected in District 3."},
    {"sender": "Agent", "text": "Analyzing cascading impacts…"},
    {"sender": "Agent", "text": "Three scenarios identified:\n1) Hospital power failure\n2) Public transport disruption\n3) Communication breakdown"},
    {"sender": "Agent", "text": "Recommended action: Trigger backup generators, reroute traffic, and issue citizen alerts."},
    {"sender": "Operator", "text": "✅ Acknowledged. Alert received."},
    {"sender": "Operator", "text": "📝 Please create draft SMS and custom alerts for citizens and city managers."},
    {"sender": "Operator", "text": "🚨 Activate the contingency plan as suggested."},
    {"sender": "Operator", "text": "🔄 Generate next suggestion for follow-up measures."},
    {"sender": "Agent", "text": "Drafting alerts and monitoring impact. Preparing follow-up options…"},
]

# Pre-scripted logs with icons, loop checks, severity
LOG_SEQUENCE = [
    {"step": "⚡ Event Detection", "detail": "Blackout event received from grid sensor feed.", "severity": None},
    {"step": "🗺️ Context Update", "detail": "State updated (District 3 at 19:05).", "severity": None},
    {"step": "Cascade Analysis", "detail": "Evaluating critical infrastructures: hospitals, transport, communications.", "severity": None},
    {"step": "🏥 Scenario 1", "detail": "Hospital emergency power may last < 2h.", "severity": "HIGH"},
    {"step": "🚇 Scenario 2", "detail": "Public transport outage → expected traffic jams.", "severity": "MEDIUM"},
    {"step": "📡 Scenario 3", "detail": "Mobile networks unstable. Citizen reports unreliable.", "severity": "HIGH"},
    {"step": "☎️ Signal Loop", "detail": "Checking 112 emergency calls: multiple blackout-related incidents.", "severity": None},
    {"step": "📱 Signal Loop", "detail": "Scanning social networks: high volume of posts about outages.", "severity": None},
    {"step": "😟 Signal Loop", "detail": "Confirmation: citizens starting to panic, unrest risk rising.", "severity": None},
    {"step": "📜 Policy Reasoning", "detail": "Applied alerting protocol (CAP) + municipal emergency rules.", "severity": None},
    {"step": "👤 Operator Action", "detail": "Operator acknowledged alert.", "severity": None},
    {"step": "👤 Operator Action", "detail": "Operator requested draft SMS + targeted alerts.", "severity": None},
    {"step": "👤 Operator Action", "detail": "Operator activated contingency plan.", "severity": None},
    {"step": "👤 Operator Action", "detail": "Operator requested next suggestion.", "severity": None},
    {"step": "✅ Proposed Action", "detail": "Backup generators ON, reroute traffic, send alerts via SMS and app.", "severity": None},
]

# ---------- Header / Map ----------
st.markdown(
    """
    <div style="position:relative;width:100%;height:220px;border-radius:14px;overflow:hidden;">
      <img src="https://lh3.googleusercontent.com/rhODm7jWpKv2LG798WhqbrqPuoEfonh7po2NYBUfJ8m9JPyFl_I2wzYe9GloVqln-Hwc-wtRfb1y9mrxVsCZwF0NIg=s1280-w1280-h800"
           style="width:100%;height:100%;object-fit:cover;" />
      <div style="position:absolute;top:10px;left:10px;background:rgba(0,0,0,0.55);color:white;
                  padding:6px 10px;border-radius:10px;font-weight:700;font-size:13px;">
        🌍 GIS Map (mock)
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")  # spacing

# ---------- Controls ----------
c1, c2, c3 = st.columns([1,1,6])
with c1:
    if st.button("▶️ Start Demo", use_container_width=True):
        # Reset and seed chat/logs
        st.session_state.demo_started = True
        st.session_state.logs = []
        st.session_state.log_index = 0
        st.session_state.chat = CHAT_SEQUENCE.copy()
with c2:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.demo_started = False
        st.session_state.logs = []
        st.session_state.log_index = 0
        st.session_state.chat = []

st.write("")  # spacing

# ---------- Layout: Chat (left) & Logs (right) ----------
left, right = st.columns([1, 1])

# ----- Chat Panel -----
with left:
    st.markdown(
        "<div style='background:#1F2937;color:white;padding:10px 12px;border-radius:10px;font-weight:700;'>💬 Orchestrator Chat</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    # Render chat messages
    for msg in st.session_state.chat:
        bg = (
            "#D1FAE5" if msg["sender"] == "Agent"
            else "#FEF3C7" if msg["sender"] == "System"
            else "#DBEAFE" if msg["sender"] == "Operator"
            else "#E5E7EB"
        )
        align = "flex-start" if msg["sender"] in ("Agent", "System") else "flex-end"
        st.markdown(
            f"""
            <div style="display:flex;justify-content:{align};margin-bottom:10px;">
              <div style="max-width:520px;background:{bg};padding:10px 12px;border-radius:12px;">
                <div style="font-size:12px;color:#6B7280;">{msg['sender']}</div>
                <div style="white-space:pre-wrap;font-size:14px;color:#111827;">{msg['text']}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Chat input
    user_input = st.chat_input("Type a message to the Orchestrator…")
    if user_input:
        st.session_state.chat.append({"sender": "User", "text": user_input})
        st.rerun()

# ----- Logs Panel -----
with right:
    st.markdown(
        "<div style='background:#1F2937;color:white;padding:10px 12px;border-radius:10px;font-weight:700;'>🧠 Agent Brain & A2A Logs</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    log_container = st.container()

    # Animate logs
    if st.session_state.demo_started:
        # Add one new log per render until all logs added
        if st.session_state.log_index < len(LOG_SEQUENCE):
            # Append next log
            nxt = LOG_SEQUENCE[st.session_state.log_index]
            st.session_state.logs.append(
                {"step": nxt["step"], "detail": nxt["detail"], "severity": nxt.get("severity"), "time": now()}
            )
            st.session_state.log_index += 1

            # Render current logs
            with log_container:
                for entry in st.session_state.logs:
                    render_log_card(entry["step"], entry["detail"], entry["time"], entry.get("severity"))

            # Small delay then rerun to simulate streaming/“thinking”
            time.sleep(1.1)
            st.rerun()
        else:
            # Render final state
            with log_container:
                for entry in st.session_state.logs:
                    render_log_card(entry["step"], entry["detail"], entry["time"], entry.get("severity"))
    else:
        # Not started: show any existing logs (likely none)
        with log_container:
            for entry in st.session_state.logs:
                render_log_card(entry["step"], entry["detail"], entry["time"], entry.get("severity"))
