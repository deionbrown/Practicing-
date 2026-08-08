import csv
import json
import random
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="German A1 Trainer",
    page_icon="🇩🇪",
    layout="centered",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "German_A1_800_with_IPA.csv"
INITIAL_PROGRESS_FILE = BASE_DIR / "german_a1_progress.json"

# ------------------------------------------------------------
# FRIENDLIER VISUAL DESIGN
# ------------------------------------------------------------
st.markdown("""
<style>
:root {
    --bg: #f6f7fb;
    --card: #ffffff;
    --text: #1f2937;
    --muted: #6b7280;
    --border: #e5e7eb;
    --accent: #ff5a5f;
    --accent2: #7c3aed;
    --good: #ecfdf5;
    --good-text: #166534;
    --bad: #fff1f2;
    --bad-text: #9f1239;
}

html, body, [class*="css"] {
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(124,58,237,.06), transparent 28%),
        radial-gradient(circle at 85% 15%, rgba(255,90,95,.08), transparent 24%),
        var(--bg);
    color: var(--text);
}

.block-container {
    max-width: 820px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

.hero {
    background: linear-gradient(135deg, rgba(124,58,237,.10), rgba(255,90,95,.10));
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 28px 28px 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(17,24,39,.05);
}

.hero-title {
    font-size: 2rem;
    font-weight: 850;
    margin: 0;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    color: var(--muted);
    margin-top: 6px;
    font-size: .98rem;
}

.stats-wrap {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 14px 0 18px 0;
}

.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 4px 14px rgba(17,24,39,.04);
}

.stat-label {
    color: var(--muted);
    font-size: .8rem;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 1.45rem;
    font-weight: 800;
}

.study-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 26px;
    padding: 38px 28px 34px 28px;
    text-align: center;
    box-shadow: 0 14px 34px rgba(17,24,39,.07);
    margin: 18px 0;
}

.topic-pill {
    display: inline-block;
    background: rgba(124,58,237,.09);
    color: #6d28d9;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 700;
    margin-bottom: 18px;
}

.word {
    font-size: 3rem;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 12px;
}

.ipa {
    font-size: 1.2rem;
    color: var(--muted);
    margin-top: 8px;
}

.helper {
    text-align: center;
    color: var(--muted);
    margin: 4px 0 12px 0;
    font-size: .92rem;
}

.feedback-good {
    background: var(--good);
    color: var(--good-text);
    border: 1px solid #bbf7d0;
    border-radius: 18px;
    padding: 18px 20px;
    margin: 16px 0;
    font-weight: 700;
}

.feedback-bad {
    background: var(--bad);
    color: var(--bad-text);
    border: 1px solid #fecdd3;
    border-radius: 18px;
    padding: 18px 20px;
    margin: 16px 0;
    font-weight: 700;
}

.answer-box {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 18px 20px;
    margin: 12px 0;
}

.answer-label {
    color: var(--muted);
    font-size: .82rem;
    margin-bottom: 4px;
}

.answer-text {
    font-size: 1.15rem;
    font-weight: 700;
}

.mastered {
    background: #fff7ed;
    color: #9a3412;
    border: 1px solid #fed7aa;
    border-radius: 16px;
    padding: 14px 18px;
    margin: 14px 0;
    font-weight: 700;
    text-align: center;
}

div.stButton > button,
div.stFormSubmitButton > button {
    width: 100%;
    min-height: 52px;
    border-radius: 14px;
    font-weight: 750;
    font-size: 1rem;
}

div[data-testid="stTextInput"] input {
    min-height: 52px;
    border-radius: 14px;
    font-size: 1rem;
}

[data-testid="stProgress"] > div > div > div > div {
    border-radius: 999px;
}

.small-note {
    color: var(--muted);
    text-align: center;
    font-size: .85rem;
    margin-top: 8px;
}

@media (max-width: 700px) {
    .block-container {padding-top: 1rem;}
    .hero {padding: 22px 18px;}
    .hero-title {font-size: 1.55rem;}
    .word {font-size: 2.25rem;}
    .study-card {padding: 28px 18px;}
    .stats-wrap {grid-template-columns: 1fr;}
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------
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

def load_initial_progress():
    if INITIAL_PROGRESS_FILE.exists():
        try:
            with INITIAL_PROGRESS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def normalize(text):
    text = text.lower().strip()
    replacements = {"ä":"ae", "ö":"oe", "ü":"ue", "ß":"ss"}
    for a, b in replacements.items():
        text = text.replace(a, b)
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())

def answer_matches(user_answer, expected):
    user = normalize(user_answer)
    expected_norm = normalize(expected)

    if user == expected_norm:
        return True

    alternatives = []
    for part in expected.replace(";", "/").replace(",", "/").split("/"):
        part = normalize(part)
        if part:
            alternatives.append(part)

    return user in alternatives

VOCAB = load_vocabulary()

if not VOCAB:
    st.error("Missing German_A1_800_with_IPA.csv. Put it in the same GitHub folder as app.py.")
    st.stop()

defaults = {
    "progress": load_initial_progress(),
    "current_card": None,
    "show_result": False,
    "last_correct": None,
    "last_user_answer": "",
    "session_correct": 0,
    "session_total": 0,
    "mode": "German → English",
    "answer_input": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def ensure_progress(card_id):
    if card_id not in st.session_state.progress:
        st.session_state.progress[card_id] = {
            "correct": 0,
            "wrong": 0,
            "streak": 0,
            "mastered": False
        }

def update_progress(card_id, correct):
    ensure_progress(card_id)
    p = st.session_state.progress[card_id]

    if correct:
        p["correct"] += 1
        p["streak"] += 1
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

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
st.sidebar.markdown("## 🇩🇪 German A1")
st.sidebar.caption("Your personal vocabulary trainer")

mode = st.sidebar.radio(
    "Study mode",
    ["German → English", "English → German", "Flashcards"]
)

if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.current_card = None
    st.session_state.show_result = False
    st.session_state.answer_input = ""

topics = sorted({v["topic"] for v in VOCAB})
selected_topic = st.sidebar.selectbox("Topic", ["All topics"] + topics)
mistakes_only = st.sidebar.checkbox("Review mistakes only", value=False)

pool = VOCAB[:] if selected_topic == "All topics" else [
    v for v in VOCAB if v["topic"] == selected_topic
]

if mistakes_only:
    pool = [
        v for v in pool
        if st.session_state.progress.get(v["id"], {}).get("wrong", 0) > 0
        and not st.session_state.progress.get(v["id"], {}).get("mastered", False)
    ]

if st.sidebar.button("🎲 Give me another card"):
    next_card(pool)

st.sidebar.divider()

progress_json = json.dumps(st.session_state.progress, ensure_ascii=False, indent=2)
st.sidebar.download_button(
    "💾 Save my progress",
    data=progress_json,
    file_name="german_a1_progress.json",
    mime="application/json"
)

uploaded_progress = st.sidebar.file_uploader("Restore saved progress", type=["json"])
if uploaded_progress is not None:
    try:
        new_progress = json.load(uploaded_progress)
        if st.sidebar.button("Load this progress"):
            st.session_state.progress = new_progress
            st.session_state.current_card = None
            st.rerun()
    except Exception:
        st.sidebar.error("Invalid JSON file.")

# ------------------------------------------------------------
# STATS
# ------------------------------------------------------------
studied = sum(1 for v in VOCAB if v["id"] in st.session_state.progress)
mastered = sum(
    1 for v in VOCAB
    if st.session_state.progress.get(v["id"], {}).get("mastered", False)
)

attempts = sum(
    x.get("correct",0) + x.get("wrong",0)
    for x in st.session_state.progress.values()
)
correct_total = sum(x.get("correct",0) for x in st.session_state.progress.values())
accuracy = (correct_total / attempts * 100) if attempts else 0

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">🇩🇪 German A1 Trainer</div>
    <div class="hero-subtitle">Build your German vocabulary one card at a time.</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="stats-wrap">
        <div class="stat-card">
            <div class="stat-label">Studied</div>
            <div class="stat-value">{studied} / {len(VOCAB)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Mastered</div>
            <div class="stat-value">{mastered}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Accuracy</div>
            <div class="stat-value">{accuracy:.0f}%</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.progress(mastered / len(VOCAB) if VOCAB else 0)
st.markdown(
    f'<div class="small-note">Mastery progress · {mastered} of {len(VOCAB)} words</div>',
    unsafe_allow_html=True
)

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
    ipa_line = card["ipa"]
    expected = card["english"]
    input_label = "What does this mean in English?"

elif st.session_state.mode == "English → German":
    question = card["english"]
    ipa_line = ""
    expected = card["german"]
    input_label = "Write it in German"

else:
    question = card["german"]
    ipa_line = card["ipa"]
    expected = card["english"]
    input_label = ""

st.markdown(
    f"""
    <div class="study-card">
        <div class="topic-pill">{card["topic"]}</div>
        <div class="word">{question}</div>
        <div class="ipa">{ipa_line}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# FLASHCARD MODE
if st.session_state.mode == "Flashcards":
    st.markdown('<div class="helper">Think of the answer before revealing it.</div>', unsafe_allow_html=True)

    if not st.session_state.show_result:
        if st.button("👀 Show answer", type="primary"):
            st.session_state.show_result = True
            st.rerun()
    else:
        st.markdown(
            f"""
            <div class="answer-box">
                <div class="answer-label">Answer</div>
                <div class="answer-text">{expected}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("➡️ Next card", type="primary"):
            next_card(pool)
            st.rerun()

# QUIZ MODES
else:
    if not st.session_state.show_result:
        st.markdown(
            f'<div class="helper">{input_label}</div>',
            unsafe_allow_html=True
        )

        with st.form("answer_form", clear_on_submit=False):
            user_answer = st.text_input(
                "Your answer",
                key="answer_input",
                placeholder="Type your answer here...",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Check answer", type="primary")

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
        if st.session_state.last_correct:
            st.markdown(
                '<div class="feedback-good">✅ Excellent! You got it right.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="feedback-bad">💡 Almost! Review the correct answer below.</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f"""
            <div class="answer-box">
                <div class="answer-label">Your answer</div>
                <div class="answer-text">{st.session_state.last_user_answer}</div>
            </div>
            <div class="answer-box">
                <div class="answer-label">Correct answer</div>
                <div class="answer-text">{expected}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.mode == "English → German":
            st.markdown(
                f"""
                <div class="answer-box">
                    <div class="answer-label">Pronunciation</div>
                    <div class="answer-text">{card["ipa"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        ensure_progress(card["id"])
        p = st.session_state.progress[card["id"]]

        st.markdown(
            f'<div class="small-note">This word · {p["correct"]} correct · {p["wrong"]} wrong · streak {p["streak"]}/3</div>',
            unsafe_allow_html=True
        )

        if p["mastered"]:
            st.markdown(
                '<div class="mastered">⭐ Mastered — great work!</div>',
                unsafe_allow_html=True
            )

        if st.button("➡️ Next card", type="primary"):
            next_card(pool)
            st.rerun()

# SESSION FOOTER
st.divider()

session_accuracy = (
    st.session_state.session_correct /
    st.session_state.session_total * 100
    if st.session_state.session_total else 0
)

st.markdown("#### Today's session")
c1, c2, c3 = st.columns(3)
c1.metric("Cards", st.session_state.session_total)
c2.metric("Correct", st.session_state.session_correct)
c3.metric("Accuracy", f"{session_accuracy:.0f}%")

st.caption("Keep going — short, consistent sessions work best.")
