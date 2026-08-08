import csv
import json
import random
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="German A1 Trainer",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "German_A1_800_with_IPA.csv"
INITIAL_PROGRESS_FILE = BASE_DIR / "german_a1_progress.json"

# ============================================================
# STYLE — friendly, modern language-learning app
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&display=swap');

:root{
  --bg:#f7fbff;
  --panel:#ffffff;
  --ink:#223047;
  --muted:#738096;
  --border:#e4eaf2;
  --green:#58cc02;
  --green-dark:#46a302;
  --blue:#1cb0f6;
  --blue-dark:#168bd0;
  --yellow:#ffc800;
  --orange:#ff9600;
  --red:#ff4b4b;
  --purple:#9069cd;
}

html, body, [class*="css"]{
  font-family:"Nunito", system-ui, sans-serif;
}

.stApp{
  background:var(--bg);
  color:var(--ink);
}

.block-container{
  max-width:1100px;
  padding-top:1.2rem;
  padding-bottom:4rem;
}

[data-testid="stSidebar"]{
  background:#ffffff;
  border-right:1px solid var(--border);
}

[data-testid="stSidebar"] .block-container{
  padding-top:1.1rem;
}

[data-testid="stSidebar"] *{
  color:var(--ink);
}

/* hide streamlit visual clutter */
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}

.brand{
  display:flex;
  align-items:center;
  gap:12px;
  margin-bottom:18px;
}

.brand-badge{
  width:46px;height:46px;
  border-radius:16px;
  background:#111827;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:25px;
  box-shadow:0 4px 0 rgba(0,0,0,.12);
}

.brand-title{
  font-weight:900;
  font-size:1.18rem;
  line-height:1.05;
}

.brand-sub{
  color:var(--muted);
  font-size:.78rem;
  margin-top:4px;
}

.topbar{
  display:grid;
  grid-template-columns:1fr auto;
  align-items:center;
  gap:18px;
  margin-bottom:16px;
}

.hello{
  background:var(--panel);
  border:2px solid var(--border);
  border-radius:22px;
  padding:18px 22px;
}

.hello-title{
  font-size:1.7rem;
  font-weight:900;
  margin:0;
}

.hello-sub{
  color:var(--muted);
  font-size:.95rem;
  margin-top:3px;
}

.top-stats{
  display:flex;
  gap:10px;
}

.pill-stat{
  min-width:100px;
  background:#fff;
  border:2px solid var(--border);
  border-radius:18px;
  padding:10px 14px;
  text-align:center;
}

.pill-icon{font-size:1.1rem;}
.pill-value{font-weight:900;font-size:1.05rem;margin-top:1px;}
.pill-label{font-size:.72rem;color:var(--muted);}

.progress-shell{
  background:white;
  border:2px solid var(--border);
  border-radius:20px;
  padding:15px 18px;
  margin-bottom:18px;
}

.progress-head{
  display:flex;
  justify-content:space-between;
  color:var(--muted);
  font-size:.84rem;
  font-weight:800;
  margin-bottom:9px;
}

.progress-track{
  height:16px;
  background:#edf1f5;
  border-radius:999px;
  overflow:hidden;
  box-shadow:inset 0 2px 0 rgba(0,0,0,.04);
}

.progress-fill{
  height:100%;
  background:linear-gradient(90deg,var(--green),#84e223);
  border-radius:999px;
}

.lesson-card{
  background:#fff;
  border:2px solid var(--border);
  border-radius:28px;
  padding:30px 32px 28px;
  box-shadow:0 7px 0 #dfe6ee;
  margin-bottom:18px;
}

.lesson-top{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:16px;
}

.topic-chip{
  display:inline-flex;
  align-items:center;
  background:#eef9e8;
  color:var(--green-dark);
  border:2px solid #d7efca;
  border-radius:999px;
  padding:7px 12px;
  font-weight:900;
  font-size:.82rem;
}

.card-count{
  color:var(--muted);
  font-size:.8rem;
  font-weight:800;
}

.word{
  font-size:3.1rem;
  font-weight:900;
  letter-spacing:-.03em;
  text-align:center;
  margin-top:10px;
  margin-bottom:8px;
}

.ipa{
  text-align:center;
  color:var(--muted);
  font-size:1.14rem;
  font-weight:700;
  margin-bottom:22px;
}

.prompt{
  font-size:.92rem;
  font-weight:900;
  color:var(--ink);
  margin:8px 0 8px;
}

.feedback-good{
  background:#effce9;
  border:2px solid #bceaa3;
  border-radius:22px;
  padding:18px 20px;
  color:#2d7f08;
  margin:14px 0;
}

.feedback-bad{
  background:#fff0f0;
  border:2px solid #ffc8c8;
  border-radius:22px;
  padding:18px 20px;
  color:#b72c2c;
  margin:14px 0;
}

.feedback-title{
  font-weight:900;
  font-size:1.18rem;
}

.feedback-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:12px;
  margin-top:12px;
}

.answer-mini{
  background:#fff;
  border-radius:16px;
  padding:12px 14px;
  border:1px solid rgba(0,0,0,.06);
}

.answer-label{
  color:var(--muted);
  font-size:.72rem;
  font-weight:800;
}

.answer-value{
  font-weight:900;
  margin-top:3px;
}

.mastered-box{
  background:#fff9de;
  border:2px solid #ffe982;
  color:#9a6b00;
  border-radius:18px;
  padding:13px 15px;
  text-align:center;
  font-weight:900;
  margin:12px 0;
}

.session-grid{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:12px;
  margin-top:14px;
}

.session-card{
  background:#fff;
  border:2px solid var(--border);
  border-radius:18px;
  padding:14px 16px;
}

.session-label{
  color:var(--muted);
  font-size:.72rem;
  font-weight:800;
}

.session-value{
  font-size:1.35rem;
  font-weight:900;
  margin-top:2px;
}

.sidebar-section{
  color:var(--muted);
  font-size:.72rem;
  font-weight:900;
  letter-spacing:.06em;
  text-transform:uppercase;
  margin:14px 0 6px;
}

/* Streamlit widgets */
div.stButton > button,
div.stFormSubmitButton > button{
  width:100%;
  min-height:50px;
  border-radius:16px;
  font-weight:900;
  font-size:.98rem;
  border:0;
  box-shadow:0 4px 0 rgba(0,0,0,.12);
}

div.stFormSubmitButton > button{
  background:var(--green);
  color:white;
}

div.stFormSubmitButton > button:hover{
  background:var(--green-dark);
  color:white;
}

div.stButton > button[kind="primary"]{
  background:var(--green);
  color:#fff;
}

div.stButton > button[kind="secondary"]{
  background:#fff;
  border:2px solid var(--border);
  color:var(--ink);
}

div[data-testid="stTextInput"] input{
  min-height:54px;
  border-radius:16px;
  border:2px solid #dce3eb;
  font-size:1rem;
  font-weight:800;
  padding:0 16px;
}

div[data-testid="stTextInput"] input:focus{
  border-color:var(--blue);
  box-shadow:0 0 0 2px rgba(28,176,246,.12);
}

[data-baseweb="select"] > div{
  border-radius:14px !important;
  border:2px solid #dce3eb !important;
}

@media(max-width:850px){
  .topbar{grid-template-columns:1fr;}
  .top-stats{display:grid;grid-template-columns:repeat(3,1fr);}
  .word{font-size:2.35rem;}
  .session-grid{grid-template-columns:repeat(2,1fr);}
  .feedback-grid{grid-template-columns:1fr;}
}

@media(max-width:560px){
  .block-container{padding:1rem .85rem 3rem;}
  .lesson-card{padding:22px 18px;}
  .hello-title{font-size:1.35rem;}
  .top-stats{grid-template-columns:repeat(3,1fr);}
  .pill-stat{min-width:0;padding:8px 7px;}
  .word{font-size:2rem;}
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_vocabulary():
    if not CSV_FILE.exists():
        return []
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    vocab = []
    for i, row in enumerate(rows):
        german = (row.get("German") or "").strip()
        ipa = (row.get("IPA") or "").strip()
        english = (row.get("English") or "").strip()
        topic = (row.get("Topic") or "Unknown").strip()
        if german and english:
            vocab.append({
                "id": str(i),
                "german": german,
                "ipa": ipa,
                "english": english,
                "topic": topic
            })
    return vocab

def initial_progress():
    if INITIAL_PROGRESS_FILE.exists():
        try:
            with INITIAL_PROGRESS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def normalize(text):
    text = text.lower().strip()
    repl = {"ä":"ae","ö":"oe","ü":"ue","ß":"ss"}
    for a,b in repl.items():
        text = text.replace(a,b)
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())

def answer_matches(user_answer, expected):
    u = normalize(user_answer)
    e = normalize(expected)
    if u == e:
        return True

    parts = []
    for part in expected.replace(";", "/").replace(",", "/").split("/"):
        p = normalize(part)
        if p:
            parts.append(p)
    return u in parts

VOCAB = load_vocabulary()
if not VOCAB:
    st.error("Missing German_A1_800_with_IPA.csv")
    st.stop()

# ============================================================
# STATE
# ============================================================
defaults = {
    "progress": initial_progress(),
    "current_card": None,
    "show_result": False,
    "last_correct": None,
    "last_user_answer": "",
    "session_correct": 0,
    "session_total": 0,
    "mode": "German → English",
    "answer_input": "",
    "xp": 0
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def ensure_progress(card_id):
    if card_id not in st.session_state.progress:
        st.session_state.progress[card_id] = {
            "correct":0,"wrong":0,"streak":0,"mastered":False
        }

def update_progress(card_id, correct):
    ensure_progress(card_id)
    p = st.session_state.progress[card_id]
    if correct:
        p["correct"] += 1
        p["streak"] += 1
        st.session_state.xp += 10
        if p["streak"] >= 3:
            p["mastered"] = True
    else:
        p["wrong"] += 1
        p["streak"] = 0
        p["mastered"] = False

    st.session_state.session_total += 1
    if correct:
        st.session_state.session_correct += 1

def choose_card(pool):
    if not pool:
        return None

    def priority(card):
        p = st.session_state.progress.get(card["id"], {})
        if p.get("mastered", False):
            return 3
        if p.get("wrong", 0) > 0:
            return 0
        if p.get("correct", 0) == 0:
            return 1
        return 2

    cards = pool[:]
    random.shuffle(cards)
    cards.sort(key=priority)
    return cards[0]

def next_card(pool):
    st.session_state.current_card = choose_card(pool)
    st.session_state.show_result = False
    st.session_state.last_correct = None
    st.session_state.last_user_answer = ""
    st.session_state.answer_input = ""

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("""
<div class="brand">
  <div class="brand-badge">🇩🇪</div>
  <div>
    <div class="brand-title">German A1<br>Trainer</div>
    <div class="brand-sub">Learn a little every day</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-section">Study mode</div>', unsafe_allow_html=True)
mode = st.sidebar.radio(
    "Study mode",
    ["German → English", "English → German", "Flashcards"],
    label_visibility="collapsed"
)

if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.current_card = None
    st.session_state.show_result = False
    st.session_state.answer_input = ""

topics = sorted({v["topic"] for v in VOCAB})

st.sidebar.markdown('<div class="sidebar-section">Topic</div>', unsafe_allow_html=True)
selected_topic = st.sidebar.selectbox(
    "Topic",
    ["All topics"] + topics,
    label_visibility="collapsed"
)

mistakes_only = st.sidebar.checkbox("Review mistakes only", value=False)

pool = VOCAB[:] if selected_topic == "All topics" else [
    v for v in VOCAB if v["topic"] == selected_topic
]

if mistakes_only:
    pool = [
        v for v in pool
        if st.session_state.progress.get(v["id"], {}).get("wrong",0) > 0
        and not st.session_state.progress.get(v["id"], {}).get("mastered",False)
    ]

if st.sidebar.button("🎲  New random card"):
    next_card(pool)

# ============================================================
# STATS
# ============================================================
studied = sum(1 for v in VOCAB if v["id"] in st.session_state.progress)
mastered = sum(
    1 for v in VOCAB
    if st.session_state.progress.get(v["id"], {}).get("mastered",False)
)
attempts = sum(
    p.get("correct",0)+p.get("wrong",0)
    for p in st.session_state.progress.values()
)
correct_total = sum(p.get("correct",0) for p in st.session_state.progress.values())
accuracy = (correct_total/attempts*100) if attempts else 0

# simple gamified streak: maximum current per-card streak
current_streak = 0
if st.session_state.progress:
    current_streak = max((p.get("streak",0) for p in st.session_state.progress.values()), default=0)

st.sidebar.markdown('<div class="sidebar-section">Your progress</div>', unsafe_allow_html=True)
st.sidebar.write(f"📚 **Studied:** {studied} / {len(VOCAB)}")
st.sidebar.write(f"⭐ **Mastered:** {mastered}")
st.sidebar.write(f"🎯 **Accuracy:** {accuracy:.0f}%")
st.sidebar.write(f"⚡ **XP this session:** {st.session_state.xp}")

st.sidebar.divider()

progress_json = json.dumps(st.session_state.progress, ensure_ascii=False, indent=2)
st.sidebar.download_button(
    "💾 Save progress",
    progress_json,
    file_name="german_a1_progress.json",
    mime="application/json"
)

uploaded = st.sidebar.file_uploader("Restore progress", type=["json"])
if uploaded is not None:
    try:
        new_p = json.load(uploaded)
        if st.sidebar.button("Load progress"):
            st.session_state.progress = new_p
            st.session_state.current_card = None
            st.rerun()
    except Exception:
        st.sidebar.error("Invalid progress file.")

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="topbar">
  <div class="hello">
    <div class="hello-title">👋 Ready for German?</div>
    <div class="hello-sub">A few focused cards today can make a big difference.</div>
  </div>
  <div class="top-stats">
    <div class="pill-stat">
      <div class="pill-icon">🔥</div>
      <div class="pill-value">{current_streak}</div>
      <div class="pill-label">streak</div>
    </div>
    <div class="pill-stat">
      <div class="pill-icon">⭐</div>
      <div class="pill-value">{mastered}</div>
      <div class="pill-label">mastered</div>
    </div>
    <div class="pill-stat">
      <div class="pill-icon">🎯</div>
      <div class="pill-value">{accuracy:.0f}%</div>
      <div class="pill-label">accuracy</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

pct = (studied/len(VOCAB)*100) if VOCAB else 0
st.markdown(f"""
<div class="progress-shell">
  <div class="progress-head">
    <span>Overall progress</span>
    <span>{studied} / {len(VOCAB)} words</span>
  </div>
  <div class="progress-track">
    <div class="progress-fill" style="width:{pct:.2f}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

if not pool:
    st.warning("There are no cards available with these filters.")
    st.stop()

if st.session_state.current_card is None:
    next_card(pool)

valid_ids = {v["id"] for v in pool}
if st.session_state.current_card["id"] not in valid_ids:
    next_card(pool)

card = st.session_state.current_card

if st.session_state.mode == "German → English":
    question = card["german"]
    ipa = card["ipa"]
    expected = card["english"]
    prompt = "Type the English meaning"
elif st.session_state.mode == "English → German":
    question = card["english"]
    ipa = ""
    expected = card["german"]
    prompt = "Write it in German"
else:
    question = card["german"]
    ipa = card["ipa"]
    expected = card["english"]
    prompt = "Think of the meaning, then reveal it"

# ============================================================
# CARD
# ============================================================
st.markdown(f"""
<div class="lesson-card">
  <div class="lesson-top">
    <div class="topic-chip">📘 {card["topic"]}</div>
    <div class="card-count">Practice card</div>
  </div>
  <div class="word">{question}</div>
  <div class="ipa">{ipa}</div>
  <div class="prompt">{prompt}</div>
</div>
""", unsafe_allow_html=True)

# FLASHCARDS
if st.session_state.mode == "Flashcards":
    if not st.session_state.show_result:
        if st.button("👀 Reveal answer", type="primary"):
            st.session_state.show_result = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="feedback-good">
          <div class="feedback-title">Answer</div>
          <div style="font-size:1.35rem;font-weight:900;margin-top:8px;">{expected}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➡️ Next card", type="primary"):
            next_card(pool)
            st.rerun()

# QUIZ MODES
else:
    if not st.session_state.show_result:
        with st.form("answer_form", clear_on_submit=False):
            user_answer = st.text_input(
                "answer",
                key="answer_input",
                placeholder="Type your answer here...",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Check answer")

        if submitted:
            if not user_answer.strip():
                st.warning("Type an answer first.")
            else:
                correct = answer_matches(user_answer, expected)
                st.session_state.last_user_answer = user_answer
                st.session_state.last_correct = correct
                st.session_state.show_result = True
                update_progress(card["id"], correct)
                st.rerun()

    else:
        css_class = "feedback-good" if st.session_state.last_correct else "feedback-bad"
        title = "🎉 Excellent! You got it right." if st.session_state.last_correct else "💡 Keep going — review this one."

        st.markdown(f"""
        <div class="{css_class}">
          <div class="feedback-title">{title}</div>
          <div class="feedback-grid">
            <div class="answer-mini">
              <div class="answer-label">Your answer</div>
              <div class="answer-value">{st.session_state.last_user_answer}</div>
            </div>
            <div class="answer-mini">
              <div class="answer-label">Correct answer</div>
              <div class="answer-value">{expected}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.mode == "English → German":
            st.info(f"Pronunciation: {card['ipa']}")

        ensure_progress(card["id"])
        p = st.session_state.progress[card["id"]]

        if p["mastered"]:
            st.markdown(
                '<div class="mastered-box">⭐ Mastered — this word is becoming yours!</div>',
                unsafe_allow_html=True
            )

        st.caption(
            f"This word · {p['correct']} correct · {p['wrong']} wrong · streak {p['streak']}/3"
        )

        if st.button("➡️ Continue", type="primary"):
            next_card(pool)
            st.rerun()

# ============================================================
# SESSION SUMMARY
# ============================================================
session_accuracy = (
    st.session_state.session_correct/st.session_state.session_total*100
    if st.session_state.session_total else 0
)

st.markdown(f"""
<div class="session-grid">
  <div class="session-card">
    <div class="session-label">Cards today</div>
    <div class="session-value">{st.session_state.session_total}</div>
  </div>
  <div class="session-card">
    <div class="session-label">Correct</div>
    <div class="session-value">{st.session_state.session_correct}</div>
  </div>
  <div class="session-card">
    <div class="session-label">Session accuracy</div>
    <div class="session-value">{session_accuracy:.0f}%</div>
  </div>
  <div class="session-card">
    <div class="session-label">XP earned</div>
    <div class="session-value">{st.session_state.xp}</div>
  </div>
</div>
""", unsafe_allow_html=True)
