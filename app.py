
import csv
import json
import random
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="German A1 Trainer", page_icon="🇩🇪", layout="centered")

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "German_A1_800_with_IPA.csv"
INITIAL_PROGRESS_FILE = BASE_DIR / "german_a1_progress.json"

st.markdown("""
<style>
.block-container {max-width: 760px; padding-top: 2rem; padding-bottom: 3rem;}
.main-title {text-align:center;font-size:2.3rem;font-weight:800;margin-bottom:.2rem;}
.subtitle {text-align:center;color:#888;margin-bottom:1.5rem;}
.flashcard {border:1px solid rgba(128,128,128,.30);border-radius:18px;padding:32px 22px;text-align:center;margin:18px 0;box-shadow:0 4px 18px rgba(0,0,0,.08);}
.topic {font-size:.9rem;opacity:.65;margin-bottom:12px;}
.german-word {font-size:2.5rem;font-weight:800;line-height:1.15;margin-top:8px;}
.ipa {font-size:1.25rem;opacity:.70;margin-top:10px;}
.answer {font-size:1.7rem;font-weight:650;margin-top:14px;}
div.stButton > button {width:100%;min-height:48px;border-radius:12px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_vocabulary():
    if not CSV_FILE.exists():
        return []
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    vocabulary = []
    for i, row in enumerate(rows):
        german = (row.get("German") or "").strip()
        ipa = (row.get("IPA") or "").strip()
        english = (row.get("English") or "").strip()
        topic = (row.get("Topic") or "Unknown").strip()
        if german and english:
            vocabulary.append({"id": str(i), "german": german, "ipa": ipa, "english": english, "topic": topic})
    return vocabulary

def initial_progress():
    if INITIAL_PROGRESS_FILE.exists():
        try:
            with INITIAL_PROGRESS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

VOCAB = load_vocabulary()

if not VOCAB:
    st.error("I cannot find German_A1_800_with_IPA.csv. Put it in the same GitHub folder as app.py.")
    st.stop()

if "progress" not in st.session_state:
    st.session_state.progress = initial_progress()
if "current_card" not in st.session_state:
    st.session_state.current_card = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "session_correct" not in st.session_state:
    st.session_state.session_correct = 0
if "session_total" not in st.session_state:
    st.session_state.session_total = 0
if "mode" not in st.session_state:
    st.session_state.mode = "German → English"

def ensure_progress(card_id):
    if card_id not in st.session_state.progress:
        st.session_state.progress[card_id] = {"correct":0,"wrong":0,"streak":0,"mastered":False}

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
    st.session_state.show_answer = False

st.sidebar.title("🇩🇪 German A1")

mode = st.sidebar.radio("Study mode", ["German → English", "English → German", "Flashcards"])
if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.current_card = None
    st.session_state.show_answer = False

topics = sorted({v["topic"] for v in VOCAB})
selected_topic = st.sidebar.selectbox("Topic", ["All topics"] + topics)
mistakes_only = st.sidebar.checkbox("Review mistakes only", value=False)

pool = VOCAB[:] if selected_topic == "All topics" else [v for v in VOCAB if v["topic"] == selected_topic]

if mistakes_only:
    pool = [v for v in pool if st.session_state.progress.get(v["id"], {}).get("wrong", 0) > 0 and not st.session_state.progress.get(v["id"], {}).get("mastered", False)]

if st.sidebar.button("🔀 New random card"):
    next_card(pool)

st.sidebar.divider()
studied = sum(1 for v in VOCAB if v["id"] in st.session_state.progress)
mastered = sum(1 for v in VOCAB if st.session_state.progress.get(v["id"], {}).get("mastered", False))
st.sidebar.metric("Studied", f"{studied}/{len(VOCAB)}")
st.sidebar.metric("Mastered", mastered)

attempts = sum(x.get("correct",0)+x.get("wrong",0) for x in st.session_state.progress.values())
correct_total = sum(x.get("correct",0) for x in st.session_state.progress.values())
accuracy = (correct_total/attempts*100) if attempts else 0
st.sidebar.metric("Overall accuracy", f"{accuracy:.1f}%")

progress_json = json.dumps(st.session_state.progress, ensure_ascii=False, indent=2)
st.sidebar.download_button("⬇️ Download progress", data=progress_json, file_name="german_a1_progress.json", mime="application/json")

uploaded_progress = st.sidebar.file_uploader("Upload saved progress", type=["json"])
if uploaded_progress is not None:
    try:
        new_progress = json.load(uploaded_progress)
        if st.sidebar.button("Load this progress"):
            st.session_state.progress = new_progress
            st.session_state.current_card = None
            st.rerun()
    except Exception:
        st.sidebar.error("Invalid JSON progress file.")

st.markdown('<div class="main-title">German A1 Trainer 🇩🇪</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{len(VOCAB)} words · IPA · 25 topics</div>', unsafe_allow_html=True)

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
    secondary = card["ipa"]
    answer = card["english"]
elif st.session_state.mode == "English → German":
    question = card["english"]
    secondary = ""
    answer = card["german"]
else:
    question = card["german"]
    secondary = card["ipa"]
    answer = card["english"]

st.markdown(f"""
<div class="flashcard">
<div class="topic">{card["topic"]}</div>
<div class="german-word">{question}</div>
<div class="ipa">{secondary}</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.show_answer:
    if st.button("Show answer", type="primary"):
        st.session_state.show_answer = True
        st.rerun()
else:
    ipa_answer = card["ipa"] if st.session_state.mode == "English → German" else ""
    st.markdown(f"""
    <div class="flashcard">
    <div class="answer">{answer}</div>
    <div class="ipa">{ipa_answer}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.mode == "Flashcards":
        if st.button("Next card", type="primary"):
            next_card(pool)
            st.rerun()
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ Again"):
                update_progress(card["id"], False)
                next_card(pool)
                st.rerun()
        with col2:
            if st.button("✅ I knew it", type="primary"):
                update_progress(card["id"], True)
                next_card(pool)
                st.rerun()

        ensure_progress(card["id"])
        p = st.session_state.progress[card["id"]]
        st.caption(f"This word: {p['correct']} correct · {p['wrong']} wrong · streak {p['streak']}/3")
        if p["mastered"]:
            st.success("★ Mastered")

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Session cards", st.session_state.session_total)
c2.metric("Correct", st.session_state.session_correct)
session_accuracy = (st.session_state.session_correct/st.session_state.session_total*100) if st.session_state.session_total else 0
c3.metric("Session accuracy", f"{session_accuracy:.0f}%")

st.progress(mastered/len(VOCAB) if VOCAB else 0)
st.caption(f"Mastery progress: {mastered}/{len(VOCAB)} words")

with st.expander("About progress saving"):
    st.write("This version keeps progress during your Streamlit session. Use Download progress to save a copy and Upload saved progress to continue later. Automatic cross-device sync can be added later with a database/login.")
