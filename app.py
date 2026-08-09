import csv
import json
import random
import re
import unicodedata
from pathlib import Path

import streamlit as st

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="Inglés A1",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "English_A1_800_with_IPA.csv"
PROGRESS_FILE = BASE_DIR / "english_a1_progress.json"

# ============================================================
# DISEÑO VISUAL — optimizado para 1366x768 y móvil
# ============================================================
st.markdown(
    """
<style>
:root{
    --bg:#f6f9fc;
    --panel:#ffffff;
    --ink:#243247;
    --muted:#6f7d90;
    --border:#e2e8f0;
    --green:#58cc02;
    --green-dark:#46a302;
    --green-soft:#effbe8;
    --red:#ff4b4b;
    --red-soft:#fff0f0;
    --blue:#1cb0f6;
    --shadow:#dce4ec;
}

/* ---------- Base ---------- */
html, body, [class*="css"]{
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

html, body{
    background:var(--bg) !important;
}

.stApp{
    background:var(--bg) !important;
    color:var(--ink) !important;
}

[data-testid="stAppViewContainer"]{
    background:var(--bg) !important;
}

[data-testid="stHeader"]{
    background:rgba(246,249,252,.96) !important;
    height:3rem !important;
}

/* ---------- Main ---------- */
.block-container{
    max-width:1040px !important;
    padding-top:3.5rem !important;
    padding-bottom:2.5rem !important;
    padding-left:2rem !important;
    padding-right:2rem !important;
}

/* ---------- Sidebar: force readable colors ---------- */
[data-testid="stSidebar"]{
    background:#ffffff !important;
    border-right:1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div{
    background:#ffffff !important;
}

[data-testid="stSidebar"] *{
    color:var(--ink) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span{
    color:var(--ink) !important;
}

[data-testid="stSidebar"] .block-container{
    padding:1rem 1rem 2rem !important;
}

/* select */
[data-testid="stSidebar"] [data-baseweb="select"] > div{
    background:#f8fafc !important;
    color:var(--ink) !important;
    border:2px solid var(--border) !important;
    border-radius:12px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] *{
    color:var(--ink) !important;
}

/* radio + checkbox labels */
[data-testid="stSidebar"] [data-testid="stRadio"] label,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label{
    color:var(--ink) !important;
    opacity:1 !important;
}

/* sidebar buttons */
[data-testid="stSidebar"] div.stButton > button{
    background:#ffffff !important;
    color:var(--ink) !important;
    border:2px solid var(--border) !important;
    box-shadow:0 3px 0 var(--shadow) !important;
}

[data-testid="stSidebar"] div.stButton > button:hover{
    border-color:var(--blue) !important;
    color:#0879b3 !important;
}

/* ---------- Custom sidebar ---------- */
.side-brand{
    background:linear-gradient(135deg,#f1f8ff,#f3ffe9);
    border:2px solid var(--border);
    border-radius:18px;
    padding:14px 15px;
    margin-bottom:16px;
}

.side-brand-title{
    font-weight:900;
    font-size:1.18rem;
    color:var(--ink) !important;
}

.side-brand-sub{
    color:var(--muted) !important;
    font-size:.78rem;
    margin-top:3px;
}

.side-label{
    color:var(--muted) !important;
    font-weight:900;
    font-size:.72rem;
    letter-spacing:.06em;
    text-transform:uppercase;
    margin:13px 0 5px;
}

/* ---------- Header ---------- */
.hero{
    display:grid;
    grid-template-columns:1fr auto;
    gap:14px;
    align-items:center;
    margin-bottom:12px;
}

.welcome{
    background:#ffffff;
    border:2px solid var(--border);
    border-radius:18px;
    padding:15px 18px;
    box-shadow:0 4px 0 var(--shadow);
}

.welcome-title{
    color:var(--ink) !important;
    font-size:1.55rem;
    font-weight:900;
    line-height:1.1;
}

.welcome-sub{
    color:var(--muted) !important;
    font-size:.88rem;
    margin-top:4px;
}

.stats{
    display:flex;
    gap:8px;
}

.stat{
    width:92px;
    background:#ffffff;
    border:2px solid var(--border);
    border-radius:17px;
    padding:9px 7px;
    text-align:center;
    box-shadow:0 3px 0 var(--shadow);
}

.stat-icon{font-size:1.05rem}
.stat-value{
    color:var(--ink) !important;
    font-size:1rem;
    font-weight:900;
}
.stat-label{
    color:var(--muted) !important;
    font-size:.68rem;
}

/* ---------- Progress ---------- */
.progressbox{
    background:#ffffff;
    border:2px solid var(--border);
    border-radius:17px;
    padding:11px 15px;
    margin-bottom:12px;
}

.progresshead{
    display:flex;
    justify-content:space-between;
    color:var(--muted) !important;
    font-size:.78rem;
    font-weight:800;
    margin-bottom:7px;
}

.track{
    height:12px;
    background:#e9eef4;
    border-radius:999px;
    overflow:hidden;
}

.fill{
    height:100%;
    background:linear-gradient(90deg,#58cc02,#83df26);
    border-radius:999px;
}

/* ---------- Study card ---------- */
.study-card{
    background:#ffffff;
    border:2px solid var(--border);
    border-radius:22px;
    padding:20px 25px 18px;
    box-shadow:0 6px 0 var(--shadow);
    text-align:center;
    margin-bottom:14px;
}

.topic-chip{
    display:inline-block;
    background:var(--green-soft);
    color:var(--green-dark) !important;
    border:1.5px solid #cfeeba;
    border-radius:999px;
    padding:5px 10px;
    font-size:.72rem;
    font-weight:900;
}

.word{
    color:var(--ink) !important;
    font-size:2.55rem;
    font-weight:900;
    letter-spacing:-.03em;
    line-height:1.05;
    margin:14px 0 5px;
}

.ipa{
    color:var(--muted) !important;
    font-size:1.02rem;
    font-weight:650;
}

.instruction{
    color:var(--ink) !important;
    margin-top:14px;
    font-size:.9rem;
    font-weight:850;
}

/* ---------- Input ---------- */
div[data-testid="stTextInput"]{
    margin-top:-2px !important;
}

div[data-testid="stTextInput"] input{
    background:#ffffff !important;
    color:var(--ink) !important;
    min-height:48px !important;
    border:2px solid #d7e0e9 !important;
    border-radius:14px !important;
    font-size:1rem !important;
    font-weight:700 !important;
    padding:0 14px !important;
}

div[data-testid="stTextInput"] input::placeholder{
    color:#9aa6b5 !important;
}

div[data-testid="stTextInput"] input:focus{
    border-color:var(--blue) !important;
    box-shadow:0 0 0 2px rgba(28,176,246,.13) !important;
}

/* ---------- Buttons ---------- */
div.stButton > button,
div.stFormSubmitButton > button{
    width:100% !important;
    min-height:46px !important;
    border-radius:14px !important;
    font-weight:900 !important;
    font-size:.95rem !important;
}

div.stFormSubmitButton > button,
div.stButton > button[kind="primary"]{
    background:var(--green) !important;
    color:#ffffff !important;
    border:0 !important;
    box-shadow:0 4px 0 var(--green-dark) !important;
}

div.stFormSubmitButton > button:hover,
div.stButton > button[kind="primary"]:hover{
    background:#62d90a !important;
    color:#ffffff !important;
}

/* ---------- Feedback ---------- */
.good,.bad{
    border-radius:18px;
    padding:14px 16px;
    margin:10px 0;
}

.good{
    background:var(--green-soft);
    border:2px solid #c5ecad;
    color:#287b08 !important;
}

.bad{
    background:var(--red-soft);
    border:2px solid #ffcaca;
    color:#a92d2d !important;
}

.feedback-title{
    font-size:1.05rem;
    font-weight:900;
}

.answers{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
    margin-top:10px;
}

.answer-box{
    background:#ffffff;
    border-radius:13px;
    padding:9px 11px;
    color:var(--ink) !important;
}

.answer-label{
    color:var(--muted) !important;
    font-size:.68rem;
    font-weight:800;
}

.answer-value{
    color:var(--ink) !important;
    font-size:.95rem;
    font-weight:900;
    margin-top:2px;
}

.mastered{
    background:#fff8d7;
    border:2px solid #ffe36e;
    color:#876100 !important;
    border-radius:14px;
    padding:10px;
    text-align:center;
    font-weight:900;
    margin:10px 0;
}

/* ---------- Session ---------- */
.session-title{
    color:var(--ink) !important;
    font-size:.86rem;
    font-weight:900;
    margin:15px 0 7px;
}

.session-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:8px;
}

.session-item{
    background:#ffffff;
    border:2px solid var(--border);
    border-radius:14px;
    padding:9px 11px;
}

.session-label{
    color:var(--muted) !important;
    font-size:.66rem;
    font-weight:800;
}

.session-value{
    color:var(--ink) !important;
    font-size:1.05rem;
    font-weight:900;
    margin-top:2px;
}

/* Hide Streamlit clutter */
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}

/* ---------- Responsive ---------- */
@media(max-width:850px){
    .block-container{
        padding-top:3.3rem !important;
        padding-left:1rem !important;
        padding-right:1rem !important;
    }
    .hero{grid-template-columns:1fr;}
    .stats{display:grid;grid-template-columns:repeat(3,1fr);}
    .stat{width:auto;}
    .word{font-size:2.15rem;}
}

@media(max-width:560px){
    .welcome-title{font-size:1.25rem;}
    .study-card{padding:17px 13px 15px;}
    .word{font-size:1.9rem;}
    .answers{grid-template-columns:1fr;}
    .session-grid{grid-template-columns:repeat(2,1fr);}
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# DATOS
# ============================================================
@st.cache_data
def load_vocab():
    if not CSV_FILE.exists():
        return []

    out = []
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            english = (row.get("English") or "").strip()
            spanish = (row.get("Spanish") or "").strip()
            if english and spanish:
                out.append(
                    {
                        "id": str(i),
                        "english": english,
                        "spanish": spanish,
                        "ipa": (row.get("IPA") or "").strip(),
                        "topic": (row.get("Topic") or "General").strip(),
                    }
                )
    return out


def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def normalize(text):
    text = unicodedata.normalize("NFD", text.lower().strip())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def answer_matches(user_answer, expected):
    user = normalize(user_answer)
    alternatives = [
        normalize(x)
        for x in re.split(r"[;,/]", expected)
        if x.strip()
    ]
    return user == normalize(expected) or user in alternatives


VOCAB = load_vocab()

if not VOCAB:
    st.error("No se encontró el archivo English_A1_800_with_IPA.csv.")
    st.stop()

# ============================================================
# ESTADO
# ============================================================
defaults = {
    "progress": load_progress(),
    "current": None,
    "result": False,
    "last_ok": None,
    "last_answer": "",
    "mode": "Inglés → Español",
    "answer_input": "",
    "session_total": 0,
    "session_correct": 0,
    "xp": 0,
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
            "mastered": False,
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

    cards = pool[:]
    random.shuffle(cards)

    def priority(card):
        p = st.session_state.progress.get(card["id"], {})
        if p.get("mastered", False):
            return 3
        if p.get("wrong", 0) > 0:
            return 0
        if p.get("correct", 0) == 0:
            return 1
        return 2

    cards.sort(key=priority)
    return cards[0]


def next_card(pool):
    st.session_state.current = choose_card(pool)
    st.session_state.result = False
    st.session_state.last_ok = None
    st.session_state.last_answer = ""
    st.session_state.answer_input = ""


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown(
    """
<div class="side-brand">
    <div class="side-brand-title">📘 INGLÉS A1</div>
    <div class="side-brand-sub">Entrena vocabulario y pronunciación</div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="side-label">Modo de estudio</div>', unsafe_allow_html=True)

mode = st.sidebar.radio(
    "Modo de estudio",
    ["Inglés → Español", "Español → Inglés", "Tarjetas"],
    label_visibility="collapsed",
)

if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.current = None
    st.session_state.result = False
    st.session_state.answer_input = ""

topics = sorted({x["topic"] for x in VOCAB})

st.sidebar.markdown('<div class="side-label">Tema</div>', unsafe_allow_html=True)

selected_topic = st.sidebar.selectbox(
    "Tema",
    ["Todos los temas"] + topics,
    label_visibility="collapsed",
)

mistakes_only = st.sidebar.checkbox("Repasar mis errores")

pool = (
    VOCAB[:]
    if selected_topic == "Todos los temas"
    else [x for x in VOCAB if x["topic"] == selected_topic]
)

if mistakes_only:
    pool = [
        x
        for x in pool
        if st.session_state.progress.get(x["id"], {}).get("wrong", 0) > 0
        and not st.session_state.progress.get(x["id"], {}).get("mastered", False)
    ]

if st.sidebar.button("🎲 Nueva palabra"):
    next_card(pool)

# ============================================================
# ESTADÍSTICAS
# ============================================================
studied = sum(1 for x in VOCAB if x["id"] in st.session_state.progress)

mastered = sum(
    1
    for x in VOCAB
    if st.session_state.progress.get(x["id"], {}).get("mastered", False)
)

attempts = sum(
    p.get("correct", 0) + p.get("wrong", 0)
    for p in st.session_state.progress.values()
)

correct_total = sum(
    p.get("correct", 0)
    for p in st.session_state.progress.values()
)

accuracy = correct_total / attempts * 100 if attempts else 0

current_streak = max(
    (p.get("streak", 0) for p in st.session_state.progress.values()),
    default=0,
)

st.sidebar.markdown('<div class="side-label">Tu progreso</div>', unsafe_allow_html=True)
st.sidebar.write(f"📚 **Estudiadas:** {studied} / {len(VOCAB)}")
st.sidebar.write(f"⭐ **Dominadas:** {mastered}")
st.sidebar.write(f"🎯 **Precisión:** {accuracy:.0f}%")
st.sidebar.write(f"⚡ **XP:** {st.session_state.xp}")

st.sidebar.divider()

progress_json = json.dumps(
    st.session_state.progress,
    ensure_ascii=False,
    indent=2,
)

st.sidebar.download_button(
    "💾 Guardar progreso",
    progress_json,
    "english_a1_progress.json",
    "application/json",
)

uploaded = st.sidebar.file_uploader(
    "Restaurar progreso",
    type=["json"],
)

if uploaded is not None:
    try:
        uploaded_progress = json.load(uploaded)
        if st.sidebar.button("Cargar progreso"):
            st.session_state.progress = uploaded_progress
            st.session_state.current = None
            st.rerun()
    except Exception:
        st.sidebar.error("El archivo de progreso no es válido.")

# ============================================================
# ENCABEZADO
# ============================================================
st.markdown(
    f"""
<div class="hero">
    <div class="welcome">
        <div class="welcome-title">👋 ¡Vamos a practicar inglés!</div>
        <div class="welcome-sub">Una palabra a la vez. Practica, corrige y avanza.</div>
    </div>
    <div class="stats">
        <div class="stat">
            <div class="stat-icon">🔥</div>
            <div class="stat-value">{current_streak}</div>
            <div class="stat-label">racha</div>
        </div>
        <div class="stat">
            <div class="stat-icon">⭐</div>
            <div class="stat-value">{mastered}</div>
            <div class="stat-label">dominadas</div>
        </div>
        <div class="stat">
            <div class="stat-icon">🎯</div>
            <div class="stat-value">{accuracy:.0f}%</div>
            <div class="stat-label">precisión</div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

pct = studied / len(VOCAB) * 100 if VOCAB else 0

st.markdown(
    f"""
<div class="progressbox">
    <div class="progresshead">
        <span>Progreso general</span>
        <span>{studied} / {len(VOCAB)} palabras</span>
    </div>
    <div class="track">
        <div class="fill" style="width:{pct:.2f}%"></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# TARJETA
# ============================================================
if not pool:
    st.warning("No hay palabras disponibles con estos filtros.")
    st.stop()

if st.session_state.current is None:
    next_card(pool)

valid_ids = {x["id"] for x in pool}
if st.session_state.current["id"] not in valid_ids:
    next_card(pool)

card = st.session_state.current

if mode == "Inglés → Español":
    question = card["english"]
    ipa = card["ipa"]
    expected = card["spanish"]
    instruction = "Escribe el significado en español"

elif mode == "Español → Inglés":
    question = card["spanish"]
    ipa = ""
    expected = card["english"]
    instruction = "Escribe la palabra o frase en inglés"

else:
    question = card["english"]
    ipa = card["ipa"]
    expected = card["spanish"]
    instruction = "Piensa en el significado y revela la respuesta"

st.markdown(
    f"""
<div class="study-card">
    <div class="topic-chip">📘 {card["topic"]}</div>
    <div class="word">{question}</div>
    <div class="ipa">{ipa}</div>
    <div class="instruction">{instruction}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# MODO TARJETAS
# ============================================================
if mode == "Tarjetas":
    if not st.session_state.result:
        if st.button("👀 Mostrar respuesta", type="primary"):
            st.session_state.result = True
            st.rerun()
    else:
        st.markdown(
            f"""
<div class="good">
    <div class="feedback-title">Respuesta</div>
    <div style="font-size:1.15rem;font-weight:900;margin-top:5px;">{expected}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("➡️ Siguiente", type="primary"):
            next_card(pool)
            st.rerun()

# ============================================================
# QUIZ
# ============================================================
else:
    if not st.session_state.result:
        with st.form("quiz"):
            user_answer = st.text_input(
                "Respuesta",
                key="answer_input",
                placeholder="Escribe tu respuesta aquí...",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("COMPROBAR")

        if submitted:
            if not user_answer.strip():
                st.warning("Primero escribe una respuesta.")
            else:
                ok = answer_matches(user_answer, expected)
                st.session_state.last_answer = user_answer
                st.session_state.last_ok = ok
                st.session_state.result = True
                update_progress(card["id"], ok)
                st.rerun()

    else:
        feedback_class = "good" if st.session_state.last_ok else "bad"
        feedback_title = (
            "🎉 ¡Excelente! Respuesta correcta."
            if st.session_state.last_ok
            else "💡 Sigue practicando. Revisa la respuesta."
        )

        st.markdown(
            f"""
<div class="{feedback_class}">
    <div class="feedback-title">{feedback_title}</div>
    <div class="answers">
        <div class="answer-box">
            <div class="answer-label">Tu respuesta</div>
            <div class="answer-value">{st.session_state.last_answer}</div>
        </div>
        <div class="answer-box">
            <div class="answer-label">Respuesta correcta</div>
            <div class="answer-value">{expected}</div>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if mode == "Español → Inglés" and card["ipa"]:
            st.info(f"🔊 Pronunciación: {card['ipa']}")

        ensure_progress(card["id"])
        p = st.session_state.progress[card["id"]]

        st.caption(
            f"Esta palabra · {p['correct']} correctas · "
            f"{p['wrong']} errores · racha {p['streak']}/3"
        )

        if p["mastered"]:
            st.markdown(
                '<div class="mastered">⭐ ¡Palabra dominada!</div>',
                unsafe_allow_html=True,
            )

        if st.button("➡️ CONTINUAR", type="primary"):
            next_card(pool)
            st.rerun()

# ============================================================
# RESUMEN DE SESIÓN
# ============================================================
session_accuracy = (
    st.session_state.session_correct
    / st.session_state.session_total
    * 100
    if st.session_state.session_total
    else 0
)

st.markdown(
    '<div class="session-title">SESIÓN DE HOY</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="session-grid">
    <div class="session-item">
        <div class="session-label">Palabras</div>
        <div class="session-value">{st.session_state.session_total}</div>
    </div>
    <div class="session-item">
        <div class="session-label">Correctas</div>
        <div class="session-value">{st.session_state.session_correct}</div>
    </div>
    <div class="session-item">
        <div class="session-label">Precisión</div>
        <div class="session-value">{session_accuracy:.0f}%</div>
    </div>
    <div class="session-item">
        <div class="session-label">XP</div>
        <div class="session-value">{st.session_state.xp}</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
