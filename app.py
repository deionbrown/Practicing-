import asyncio, csv, json, random, re, base64
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
import edge_tts

st.set_page_config(page_title="German A1 + A2",page_icon="🇩🇪",layout="wide",initial_sidebar_state="collapsed")
BASE=Path(__file__).resolve().parent

def image_data_uri(path):
    data=Path(path).read_bytes()
    return "data:image/png;base64,"+base64.b64encode(data).decode("ascii")

ADLER_URI=image_data_uri(BASE/"adler_mascot.png")
READINGS=json.loads((BASE/"readings.json").read_text(encoding="utf-8"))
SUPPLEMENT=json.loads((BASE/"course_vocab_supplement.json").read_text(encoding="utf-8"))
VOICE="de-DE-KatjaNeural"

st.markdown("""
<style>
:root{
  --bg:#0b1220;
  --bg2:#0f172a;
  --panel:#121c2f;
  --panel2:#17243a;
  --panel3:#1b2a43;
  --border:#263754;
  --text:#f8fafc;
  --muted:#9fb0c7;
  --accent:#7c5cff;
  --accent2:#9b7dff;
  --blue:#38bdf8;
  --green:#22c55e;
  --green2:#16a34a;
  --red:#ef4444;
  --yellow:#f59e0b;
  --shadow:0 18px 50px rgba(0,0,0,.22);
}

.stApp{
  background:
    radial-gradient(circle at 15% 0%, rgba(124,92,255,.09), transparent 30%),
    radial-gradient(circle at 100% 10%, rgba(56,189,248,.05), transparent 25%),
    linear-gradient(180deg,var(--bg),var(--bg2));
  color:var(--text);
}

.block-container{
  max-width:1120px;
  padding-top:4.8rem !important;
  padding-bottom:6rem;
}

#MainMenu, footer{visibility:hidden;}
header[data-testid="stHeader"]{
  background:rgba(11,18,32,.94);
  backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(38,55,84,.55);
}

.premium-brand{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
  padding:14px 18px;
  margin:0 0 16px;
  background:rgba(18,28,47,.92);
  border:1px solid var(--border);
  border-radius:22px;
  box-shadow:var(--shadow);
}
.brand-left{display:flex;align-items:center;gap:13px;}
.brand-logo{
  width:58px;
  height:58px;
  border-radius:18px;
  overflow:hidden;
  flex:0 0 58px;
  background:#15223a;
  border:2px solid rgba(124,92,255,.55);
  box-shadow:0 12px 28px rgba(124,92,255,.22);
}
.brand-logo img{
  width:100%;
  height:100%;
  object-fit:cover;
  display:block;
}
.brand-title{font-size:1.25rem;font-weight:900;line-height:1.05;}
.brand-sub{color:var(--muted);font-size:.78rem;margin-top:3px;}
.user-chip{
  color:#d9dff0;background:var(--panel2);border:1px solid var(--border);
  border-radius:999px;padding:8px 12px;font-size:.78rem;font-weight:700;
}

.hero{
  background:linear-gradient(135deg,rgba(124,92,255,.12),rgba(23,36,58,.96));
  border:1px solid var(--border);
  border-radius:24px;
  padding:24px;
  margin:12px 0 18px;
  box-shadow:var(--shadow);
}
.hero h1{font-size:1.8rem;line-height:1.1;margin:0 0 6px;font-weight:900;letter-spacing:-.02em;}
.hero p{color:var(--muted);margin:0;font-size:.95rem;}

.section-title{
  font-size:1rem;font-weight:900;margin:18px 0 8px;color:#eaf0ff;
}

.card{
  background:linear-gradient(180deg,var(--panel),#101a2d);
  border:1px solid var(--border);
  border-radius:20px;
  padding:18px;
  margin:10px 0;
  box-shadow:0 12px 30px rgba(0,0,0,.14);
}

.topic-card{
  background:var(--panel);
  border:1px solid var(--border);
  border-radius:17px;
  padding:15px 17px;
  margin:8px 0;
}

.word-card{
  background:linear-gradient(180deg,#16233a,#121c2f);
  border:1px solid var(--border);
  border-radius:24px;
  padding:28px 22px 24px;
  margin:14px 0 10px;
  box-shadow:var(--shadow);
  text-align:center;
}
.word{
  font-size:2.7rem;
  line-height:1.05;
  font-weight:950;
  letter-spacing:-.03em;
  margin:2px 0 8px;
}
.ipa{
  color:var(--blue);
  font-size:1.08rem;
  font-weight:850;
  margin-top:5px;
}
.small-label{
  color:var(--muted);
  font-size:.76rem;
  font-weight:850;
  letter-spacing:.04em;
  text-transform:uppercase;
}
.answer-line{
  font-size:1.15rem;
  font-weight:850;
  margin-top:8px;
}

.progress-shell{
  height:10px;border-radius:999px;background:#21304a;overflow:hidden;margin:8px 0 4px;
}
.progress-fill{
  height:100%;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--accent2));
}

.stats{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:10px;
  margin:10px 0 18px;
}
.stat{
  background:var(--panel);
  border:1px solid var(--border);
  border-radius:18px;
  padding:15px;
  min-height:90px;
}
.sl{
  color:var(--muted);
  font-size:.72rem;
  font-weight:850;
  text-transform:uppercase;
  letter-spacing:.04em;
}
.sv{
  font-size:1.45rem;
  font-weight:950;
  margin-top:7px;
  letter-spacing:-.02em;
}

.result-good{
  background:linear-gradient(135deg,rgba(34,197,94,.22),rgba(22,163,74,.12));
  border:1px solid rgba(34,197,94,.42);
  border-radius:19px;
  padding:18px;
  margin-top:14px;
}
.result-bad{
  background:linear-gradient(135deg,rgba(239,68,68,.20),rgba(185,28,28,.10));
  border:1px solid rgba(239,68,68,.38);
  border-radius:19px;
  padding:18px;
  margin-top:14px;
}
.result-title{font-size:1.15rem;font-weight:950;margin-bottom:4px;}
.result-sub{color:#dce7f6;font-size:.92rem;}
.review-chip{
  display:inline-block;margin-top:10px;padding:7px 10px;border-radius:999px;
  background:rgba(255,255,255,.07);color:#dce7f6;font-size:.78rem;font-weight:800;
}

.reading-line{
  font-size:1.06rem;
  line-height:1.72;
  margin:8px 0;
  color:#e8edf7;
}

div.stButton>button,
div.stFormSubmitButton>button{
  width:100%;
  min-height:50px;
  border-radius:15px;
  font-weight:900;
  border:1px solid var(--border);
  transition:.18s ease;
}
div.stButton>button:hover,
div.stFormSubmitButton>button:hover{
  transform:translateY(-1px);
  box-shadow:0 10px 24px rgba(124,92,255,.18);
}

div[data-testid="stTextInput"] input{
  min-height:52px;
  border-radius:15px;
  font-size:1rem;
  background:#111b2e;
  border:1px solid var(--border);
}
div[data-testid="stTextInput"] input:focus{
  border-color:var(--accent);
  box-shadow:0 0 0 2px rgba(124,92,255,.16);
}

[data-baseweb="select"]>div{
  border-radius:15px!important;
  min-height:48px;
}
.stRadio > div{gap:8px;}
.stTabs [data-baseweb="tab-list"]{
  gap:6px;
  flex-wrap:wrap;
  border-bottom:1px solid var(--border);
  padding-bottom:7px;
}
.stTabs [data-baseweb="tab"]{
  background:transparent;
  border-radius:12px;
  padding:10px 13px;
  color:var(--muted);
  font-weight:850;
}
.stTabs [aria-selected="true"]{
  background:rgba(124,92,255,.12)!important;
  color:#fff!important;
}

div[data-testid="stExpander"]{
  background:var(--panel);
  border:1px solid var(--border);
  border-radius:15px;
}

@media(max-width:760px){
  .block-container{padding:4.2rem .7rem 5.8rem !important;}
  .premium-brand{padding:11px 12px;border-radius:18px;}
  .brand-logo{width:49px;height:49px;flex-basis:49px;border-radius:15px;}
  .brand-title{font-size:1.08rem;}
  .user-chip{display:none;}
  .hero{padding:18px;border-radius:20px;}
  .hero h1{font-size:1.43rem;}
  .word-card{padding:23px 16px 20px;border-radius:20px;}
  .word{font-size:2.15rem;}
  .stats{grid-template-columns:repeat(2,1fr);}
  .stat{min-height:82px;padding:13px;}
  .stTabs [data-baseweb="tab"]{padding:8px 10px;font-size:.82rem;}
}

/* ===== Focused vocabulary card ===== */
.vocab-overall{
  background:#101a2d;border:1px solid #263754;border-radius:20px;
  padding:16px 18px 14px;margin:8px 0 16px;
}
.vocab-overall-row{
  display:flex;justify-content:space-between;gap:12px;
  font-size:.82rem;font-weight:900;color:#f8fafc;
}
.vocab-overall-value{color:#9fb7e9;white-space:nowrap;}
.vocab-overall-track{
  width:100%;height:14px;margin-top:11px;border-radius:999px;
  overflow:hidden;background:#25354f;
}
.vocab-overall-fill{
  height:100%;border-radius:999px;background:#48d400;
}

.vocab-study-card{
  background:#101a2d;border:1px solid #263754;border-radius:24px;
  padding:42px 34px 34px;margin:8px 0 14px;min-height:460px;
  box-shadow:0 16px 40px rgba(0,0,0,.16);text-align:center;
}
.vocab-topic-pill{
  display:inline-flex;align-items:center;justify-content:center;
  background:#18371f;color:#7ef443;border-radius:999px;
  padding:7px 16px;font-size:.78rem;font-weight:950;
}
.vocab-card-counter{
  color:#9bb2d8;font-size:.8rem;font-weight:800;margin-top:12px;
}
.vocab-main-word{
  color:#f8fafc;font-size:3rem;line-height:1.08;font-weight:500;
  letter-spacing:-.025em;margin-top:28px;
}
.vocab-main-ipa{
  color:#a8b9dc;font-size:1.1rem;line-height:1.2;margin-top:10px;
}
.vocab-prompt{
  color:#a9bbdf;font-size:.82rem;font-weight:850;
  margin-top:27px;margin-bottom:10px;
}
.vocab-result-good,.vocab-result-bad{
  max-width:885px;margin:14px auto 0;text-align:left;
  border-radius:16px;padding:15px 18px;
}
.vocab-result-good{
  background:rgba(34,197,94,.14);border:1px solid rgba(34,197,94,.36);
}
.vocab-result-bad{
  background:rgba(239,68,68,.13);border:1px solid rgba(239,68,68,.34);
}
.vocab-result-title{font-weight:950;font-size:1.03rem;margin-bottom:5px;}
.vocab-result-meta{color:#c7d4eb;font-size:.86rem;line-height:1.45;}

div[data-testid="stForm"]{
  max-width:885px;margin:0 auto;border:none!important;
  padding:0!important;background:transparent!important;
}
div[data-testid="stForm"] div[data-testid="stTextInput"] input{
  min-height:54px!important;border-radius:15px!important;
  background:#15213a!important;border:1px solid #314462!important;
  color:#f8fafc!important;font-size:1rem!important;font-weight:700!important;
}
div[data-testid="stForm"] div[data-testid="stTextInput"] input::placeholder{
  color:#9eb1d2!important;
}
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button{
  min-height:54px!important;margin-top:10px!important;border-radius:15px!important;
  border:none!important;background:#48d400!important;color:white!important;
  font-size:1rem!important;font-weight:950!important;box-shadow:none!important;
}
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button:hover{
  background:#53df09!important;transform:none!important;box-shadow:none!important;
}
.vocab-audio-wrap{
  max-width:885px;margin:0 auto 10px;
}
@media(max-width:760px){
  .vocab-overall{padding:14px 14px 12px;border-radius:17px;}
  .vocab-overall-track{height:12px;}
  .vocab-study-card{min-height:390px;border-radius:20px;padding:30px 16px 25px;}
  .vocab-main-word{font-size:2.35rem;margin-top:24px;}
  .vocab-main-ipa{font-size:1rem;}
}


/* ===== v5.3 focused single-card exercise ===== */
.vocab-shell{
  background:#101a2d;
  border:1px solid #263754;
  border-radius:24px;
  padding:34px 34px 30px;
  margin:8px 0 14px;
  box-shadow:0 16px 40px rgba(0,0,0,.16);
}
.vocab-shell-top{
  text-align:center;
}
.vocab-shell .vocab-topic-pill{
  display:inline-flex;
}
.vocab-shell .vocab-card-counter{
  margin-top:12px;
}
.vocab-shell .vocab-main-word{
  margin-top:28px;
}
.vocab-shell .vocab-main-ipa{
  margin-top:10px;
}
.vocab-shell .vocab-prompt{
  margin-top:22px;
  margin-bottom:10px;
}
.audio-direct-wrap{
  display:flex;
  justify-content:center;
  margin:14px 0 4px;
}
.audio-direct-note{
  color:#9fb0c7;
  font-size:.76rem;
  text-align:center;
  margin-top:3px;
}

/* Full-width buttons */
div[data-testid="stButton"]{
  max-width:885px;
  margin-left:auto;
  margin-right:auto;
}
div[data-testid="stButton"] > button{
  width:100%!important;
  min-height:54px!important;
  border-radius:15px!important;
  font-size:1rem!important;
  font-weight:950!important;
}
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button{
  width:100%!important;
}

/* Continue button: purple and wide */
button[kind="primary"]{
  background:linear-gradient(90deg,#6d5dfb,#8b5cf6)!important;
  border:none!important;
}
button[kind="primary"]:hover{
  background:linear-gradient(90deg,#755fff,#9567ff)!important;
}

/* Keep the check-answer button green inside form */
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button{
  background:#48d400!important;
  color:#fff!important;
}
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button:hover{
  background:#53df09!important;
}

/* Remove wasted vertical height from old card styling */
.vocab-study-card{
  min-height:0!important;
  padding:0!important;
  margin:0!important;
  border:none!important;
  background:transparent!important;
  box-shadow:none!important;
}

/* Hide native audio UI when we autoplay after button press */
.autoplay-audio{
  height:0;
  overflow:hidden;
}

@media(max-width:760px){
  .vocab-shell{
    padding:26px 15px 22px;
    border-radius:20px;
  }
}


/* ===== v5.5 integrated vocabulary card ===== */
.st-key-vocab_card{
  background:#101a2d !important;
  border:1px solid #263754 !important;
  border-radius:24px !important;
  padding:34px 34px 30px !important;
  margin-top:8px !important;
  margin-bottom:14px !important;
  box-shadow:0 16px 40px rgba(0,0,0,.16);
}

.st-key-vocab_card .vocab-card-head{
  text-align:center;
}
.st-key-vocab_card .vocab-topic-pill{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  background:#18371f;
  color:#7ef443;
  border-radius:999px;
  padding:7px 16px;
  font-size:.78rem;
  font-weight:950;
}
.st-key-vocab_card .vocab-card-counter{
  color:#9bb2d8;
  font-size:.8rem;
  font-weight:800;
  margin-top:12px;
}
.st-key-vocab_card .vocab-main-word{
  color:#f8fafc;
  font-size:3rem;
  line-height:1.08;
  font-weight:500;
  letter-spacing:-.025em;
  margin-top:28px;
}
.st-key-vocab_card .vocab-main-ipa{
  color:#a8b9dc;
  font-size:1.1rem;
  line-height:1.2;
  margin-top:10px;
}
.st-key-vocab_card .vocab-prompt{
  color:#a9bbdf;
  font-size:.82rem;
  font-weight:850;
  text-align:center;
  margin:16px 0 7px;
}

/* Direct Listen button — compact, centered, repeatable */
.st-key-vocab_card .st-key-listen_btn{
  max-width:180px;
  margin:14px auto 8px;
}
.st-key-vocab_card .st-key-listen_btn button{
  width:100% !important;
  min-height:48px !important;
  border-radius:14px !important;
  background:#16233a !important;
  border:1px solid #395174 !important;
  color:#f8fafc !important;
  font-weight:900 !important;
  box-shadow:none !important;
}
.st-key-vocab_card .st-key-listen_btn button:hover{
  background:#1b2b47 !important;
  border-color:#5572a0 !important;
  transform:none !important;
}

/* Input immediately after prompt */
.st-key-vocab_card div[data-testid="stForm"]{
  max-width:none !important;
  width:100% !important;
  margin:0 !important;
}
.st-key-vocab_card div[data-testid="stTextInput"]{
  width:100% !important;
  margin:0 !important;
}
.st-key-vocab_card div[data-testid="stTextInput"] input{
  width:100% !important;
  min-height:54px !important;
  border-radius:15px !important;
  background:#15213a !important;
  border:1px solid #314462 !important;
  color:#f8fafc !important;
  font-size:1rem !important;
  font-weight:700 !important;
  padding-left:16px !important;
}
.st-key-vocab_card div[data-testid="stTextInput"] input::placeholder{
  color:#9eb1d2 !important;
}

/* Full horizontal green Check button */
.st-key-vocab_card div[data-testid="stFormSubmitButton"]{
  width:100% !important;
}
.st-key-vocab_card div[data-testid="stFormSubmitButton"] button{
  width:100% !important;
  min-height:54px !important;
  margin-top:10px !important;
  border-radius:15px !important;
  border:none !important;
  background:#48d400 !important;
  color:#fff !important;
  font-size:1rem !important;
  font-weight:950 !important;
  box-shadow:none !important;
}
.st-key-vocab_card div[data-testid="stFormSubmitButton"] button:hover{
  background:#55df0c !important;
  transform:none !important;
}

/* Full horizontal Continue button */
.st-key-vocab_card .st-key-continue_btn{
  width:100% !important;
  margin-top:12px !important;
}
.st-key-vocab_card .st-key-continue_btn button{
  width:100% !important;
  min-height:54px !important;
  border-radius:15px !important;
  border:none !important;
  background:linear-gradient(90deg,#6d5dfb,#8b5cf6) !important;
  color:white !important;
  font-size:1rem !important;
  font-weight:950 !important;
  box-shadow:none !important;
}
.st-key-vocab_card .st-key-continue_btn button:hover{
  background:linear-gradient(90deg,#755fff,#9567ff) !important;
  transform:none !important;
}

/* Results remain inside same card */
.st-key-vocab_card .vocab-result-good,
.st-key-vocab_card .vocab-result-bad{
  width:100%;
  margin:12px 0 0;
  text-align:left;
  border-radius:16px;
  padding:15px 18px;
}
.st-key-vocab_card .vocab-result-good{
  background:rgba(34,197,94,.14);
  border:1px solid rgba(34,197,94,.36);
}
.st-key-vocab_card .vocab-result-bad{
  background:rgba(239,68,68,.13);
  border:1px solid rgba(239,68,68,.34);
}

@media(max-width:760px){
  .st-key-vocab_card{
    padding:25px 15px 22px !important;
    border-radius:20px !important;
  }
  .st-key-vocab_card .vocab-main-word{
    font-size:2.35rem;
    margin-top:24px;
  }
  .st-key-vocab_card .vocab-main-ipa{
    font-size:1rem;
  }
  .st-key-vocab_card .st-key-listen_btn{
    max-width:160px;
  }
}


/* ===== v5.7 full-width Check answer ===== */
.st-key-vocab_card div[data-testid="stForm"] {
    width:100% !important;
    max-width:100% !important;
}
.st-key-vocab_card div[data-testid="stFormSubmitButton"],
.st-key-vocab_card div[data-testid="stFormSubmitButton"] > div,
.st-key-vocab_card div[data-testid="stFormSubmitButton"] button,
.st-key-vocab_card form button[kind="primaryFormSubmit"],
.st-key-vocab_card form button {
    width:100% !important;
    max-width:100% !important;
    display:block !important;
}
.st-key-vocab_card div[data-testid="stFormSubmitButton"] button,
.st-key-vocab_card form button[kind="primaryFormSubmit"] {
    min-height:54px !important;
    border-radius:15px !important;
    background:#48d400 !important;
    border:none !important;
    color:#fff !important;
    font-size:1rem !important;
    font-weight:950 !important;
}


/* ===== v5.8 FORCE Check answer to input width ===== */
.st-key-vocab_card [data-testid="stForm"] {
    width:100% !important;
}
.st-key-vocab_card [data-testid="stForm"] [data-testid="stFormSubmitButton"],
.st-key-vocab_card [data-testid="stForm"] [data-testid="stFormSubmitButton"] > div,
.st-key-vocab_card [data-testid="stForm"] [data-testid="stFormSubmitButton"] > div > div {
    width:100% !important;
    max-width:none !important;
    flex:1 1 100% !important;
}
.st-key-vocab_card [data-testid="stForm"] [data-testid="stFormSubmitButton"] button,
.st-key-vocab_card [data-testid="stForm"] button[kind="primaryFormSubmit"] {
    width:100% !important;
    max-width:none !important;
    min-width:100% !important;
    display:flex !important;
    flex:1 1 100% !important;
    justify-content:center !important;
    align-items:center !important;
    min-height:54px !important;
    border-radius:15px !important;
    background:#48d400 !important;
    border:0 !important;
    color:white !important;
    font-weight:950 !important;
}

/* Modern Streamlit wrappers */
.st-key-vocab_card div:has(> [data-testid="stFormSubmitButton"]) {
    width:100% !important;
    max-width:none !important;
}

</style>
""",unsafe_allow_html=True)

@st.cache_resource
def make_client(url,key):
    return create_client(url,key)

try:
    supabase=make_client(st.secrets["SUPABASE_URL"],st.secrets["SUPABASE_KEY"])
except Exception:
    st.error("Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets.")
    st.stop()

def current_user(): return st.session_state.get("user")
def uid(): return current_user().id

@st.cache_data
def vocab_rows(level="A1"):
    filename="German_A1_800_with_IPA.csv" if level=="A1" else "German_A2_1200_with_IPA.csv"
    with (BASE/filename).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

@st.cache_data
def lookup_maps():
    exact,bare={},{}
    for row in vocab_rows():
        g=(row.get("German") or "").strip()
        if not g:continue
        exact[g.lower()]=row
        low=g.lower()
        for a in ("der ","die ","das ","ein ","eine "):
            if low.startswith(a):bare[low[len(a):]]=row
    return exact,bare

def resolve(word):
    exact,bare=lookup_maps();k=word.lower().strip()
    if k in exact:return exact[k]
    if k in bare:return bare[k]
    forms={"heiße":"heißen","komme":"kommen","kommt":"kommen","wohne":"wohnen","wohnt":"wohnen","spreche":"sprechen","spricht":"sprechen","lerne":"lernen","lernt":"lernen","arbeite":"arbeiten","arbeitet":"arbeiten","fahre":"fahren","fährt":"fahren","lese":"lesen","liest":"lesen"}
    if k in forms:return exact.get(forms[k]) or bare.get(forms[k])
    return SUPPLEMENT.get(k)

@st.cache_data
def vocabulary_topics(level="A1"):
    return sorted({
        (row.get("Topic") or "Uncategorized").strip()
        for row in vocab_rows(level)
        if (row.get("Topic") or "").strip()
    })

@st.cache_data
def vocab_pool(topic, level="A1"):
    out=[]
    for row in vocab_rows(level):
        g=(row.get("German") or "").strip()
        ipa=(row.get("IPA") or "—").strip()
        eng=(row.get("English") or "").strip()
        row_topic=(row.get("Topic") or "Uncategorized").strip()

        if not g:
            continue
        if topic!="All topics" and row_topic!=topic:
            continue

        out.append({
            "id":f"{level}:{g.lower()}",
            "german":g,
            "ipa":ipa,
            "english":eng,
            "topic":row_topic
        })
    return out

def norm(s):
    s=(s or "").lower().strip()
    for a,b in {"ä":"ae","ö":"oe","ü":"ue","ß":"ss"}.items():s=s.replace(a,b)
    return " ".join("".join(c for c in s if c.isalnum() or c.isspace()).split())

def matches(user,expected):
    u=norm(user);e=norm(expected)
    if u==e:return True
    alts=[norm(x) for x in expected.replace(";", "/").replace(",", "/").split("/") if norm(x)]
    if u in alts:return True
    for c in [e]+alts:
        for art in ("der","die","das","ein","eine"):
            if c.startswith(art+" ") and u==c[len(art)+1:]:return True
    return False

@st.cache_data(show_spinner=False,ttl=2592000)
def audio_bytes(text):
    async def go():
        b=bytearray()
        async for chunk in edge_tts.Communicate(text=text,voice=VOICE).stream():
            if chunk["type"]=="audio":b.extend(chunk["data"])
        return bytes(b)
    return asyncio.run(go())

def audio(text):
    try: st.audio(audio_bytes(text),format="audio/mp3")
    except Exception: st.caption("Internet is needed the first time this audio is generated.")


def direct_audio_button(text, key):
    try:
        data=audio_bytes(text)
        encoded=base64.b64encode(data).decode("ascii")
        html=f"""
        <html>
        <head>
        <style>
          html,body {{
            margin:0;
            padding:0;
            background:transparent;
            overflow:hidden;
          }}
          .audio-wrap {{
            display:flex;
            justify-content:center;
            align-items:center;
            width:100%;
            padding:7px 8px;
            box-sizing:border-box;
          }}
          .listen-btn {{
            min-width:154px;
            height:48px;
            box-sizing:border-box;
            border-radius:14px;
            border:1px solid #486287;
            background:#16233a;
            color:#f8fafc;
            font-size:14px;
            font-weight:800;
            cursor:pointer;
            font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            outline:none;
            box-shadow:none;
          }}
          .listen-btn:hover {{
            background:#1b2b47;
            border-color:#6a84ad;
          }}
        </style>
        </head>
        <body>
          <div class="audio-wrap">
            <audio id="word_audio_{key}" preload="auto">
              <source src="data:audio/mp3;base64,{encoded}" type="audio/mpeg">
            </audio>
            <button class="listen-btn" onclick="
              const a=document.getElementById('word_audio_{key}');
              a.pause();
              a.currentTime=0;
              const p=a.play();
              if (p !== undefined) {{ p.catch(() => {{}}); }}
            ">🔊 Listen</button>
          </div>
        </body>
        </html>
        """
        components.html(html,height=66,scrolling=False)
    except Exception:
        st.warning("Internet is needed the first time this audio is generated.")


def read_progress():
    d=supabase.table("reading_progress").select("reading_id,completed").eq("user_id",uid()).execute().data or []
    return {x["reading_id"]:x["completed"] for x in d}

def set_reading(rid,val):
    supabase.table("reading_progress").upsert({"user_id":uid(),"reading_id":rid,"completed":bool(val),"updated_at":datetime.now(timezone.utc).isoformat()}).execute()

def load_srs():
    d=supabase.table("vocab_srs").select("*").eq("user_id",uid()).execute().data or []
    return {x["card_id"]:x for x in d}

def srs(cid):
    cache=st.session_state.setdefault("srs_cache",load_srs())
    if cid not in cache:
        cache[cid]={"user_id":uid(),"card_id":cid,"correct":0,"wrong":0,"reviews":0,"lapses":0,"interval_days":0.0,"ease":2.5,"due":None,"mastered":False}
    return cache[cid]

def save_srs(row):
    row=dict(row);row["user_id"]=uid();row["updated_at"]=datetime.now(timezone.utc).isoformat()
    supabase.table("vocab_srs").upsert(row).execute()

def load_stats():
    d=supabase.table("user_stats").select("*").eq("user_id",uid()).execute().data or []
    if d:return d[0]
    row={"user_id":uid(),"correct":0,"wrong":0,"attempts":0,"card_views":0}
    supabase.table("user_stats").upsert(row).execute();return row

def save_stats(row):
    row=dict(row);row["user_id"]=uid();row["updated_at"]=datetime.now(timezone.utc).isoformat()
    supabase.table("user_stats").upsert(row).execute()

def due(cid):
    x=srs(cid).get("due")
    if not x:return True
    try:return datetime.fromisoformat(x.replace("Z","+00:00"))<=datetime.now(timezone.utc)
    except:return True

def due_text(dt):
    sec=max(0,int((dt-datetime.now(timezone.utc)).total_seconds()))
    if sec<3600:return f"{max(1,round(sec/60))}m"
    if sec<86400:return f"{max(1,round(sec/3600))}h"
    return f"{max(1,round(sec/86400))}d"

def apply_result(card,ok):
    x=srs(card["id"]);stats=st.session_state.setdefault("stats_cache",load_stats())
    interval=float(x.get("interval_days",0) or 0);ease=float(x.get("ease",2.5) or 2.5)
    x["reviews"]=int(x.get("reviews",0))+1;stats["attempts"]=int(stats.get("attempts",0))+1
    if ok:
        x["correct"]=int(x.get("correct",0))+1;stats["correct"]=int(stats.get("correct",0))+1
        days=1 if interval<=0 else max(1,round(interval*ease));x["interval_days"]=float(days)
        if x["correct"]>=3:x["ease"]=min(3.0,ease+.03)
        nxt=datetime.now(timezone.utc)+timedelta(days=days);x["mastered"]=x["correct"]>=4 and days>=21
    else:
        x["wrong"]=int(x.get("wrong",0))+1;x["lapses"]=int(x.get("lapses",0))+1;stats["wrong"]=int(stats.get("wrong",0))+1
        x["interval_days"]=0.0;x["ease"]=max(1.3,ease-.2);x["mastered"]=False;nxt=datetime.now(timezone.utc)+timedelta(minutes=10)
    x["due"]=nxt.isoformat();save_srs(x);save_stats(stats);return nxt

if not current_user():
    st.markdown(f'''<div class="premium-brand"><div class="brand-left"><div class="brand-logo"><img src="{ADLER_URI}" alt="Adler mascot"></div><div><div class="brand-title">German A1 + A2</div><div class="brand-sub">Learn with Adler · synced progress · natural audio</div></div></div></div>''',unsafe_allow_html=True)
    a,b=st.tabs(["Sign in","Create account"])
    with a:
        with st.form("login"):
            email=st.text_input("Email");password=st.text_input("Password",type="password");go=st.form_submit_button("Sign in",type="primary")
        if go:
            try:
                response=supabase.auth.sign_in_with_password({
                    "email":email.strip(),
                    "password":password
                })

                if response.user is not None and response.session is not None:
                    st.session_state.user=response.user
                    st.session_state.auth_session=response.session

                    # Clear stale login messages/state before rerunning.
                    for key in ["srs_cache","stats_cache","session","idx","direction","vocab_level","fb"]:
                        st.session_state.pop(key, None)

                    st.rerun()
                else:
                    st.error("Could not sign in. Please check your email and password.")
            except Exception as exc:
                message=str(exc).lower()
                if "email not confirmed" in message:
                    st.error("Your email has not been confirmed yet.")
                elif "invalid login credentials" in message:
                    st.error("Incorrect email or password.")
                else:
                    st.error("Could not sign in. Please try again.")
    with b:
        with st.form("signup"):
            e=st.text_input("Email",key="se");p=st.text_input("Password",type="password",key="sp");go2=st.form_submit_button("Create account")
        if go2:
            try:
                r=supabase.auth.sign_up({
                    "email":e.strip(),
                    "password":p
                })
                if r.session is not None and r.user is not None:
                    st.session_state.user=r.user
                    st.session_state.auth_session=r.session
                    st.rerun()
                else:
                    st.success("Account created. Check your email to confirm it, then sign in.")
            except Exception as exc:
                message=str(exc).lower()
                if "already registered" in message or "user already registered" in message:
                    st.warning("This email already has an account. Use Sign in.")
                else:
                    st.error("Could not create account.")
    st.stop()

u=current_user()
st.markdown(f'''<div class="premium-brand"><div class="brand-left"><div class="brand-logo"><img src="{ADLER_URI}" alt="Adler mascot"></div><div><div class="brand-title">German A1 Complete</div><div class="brand-sub">Learn with Adler · A1 + A2 vocabulary · SRS · natural audio</div></div></div><div class="user-chip">{u.email}</div></div>''',unsafe_allow_html=True)
home,course,vocab,progress,account=st.tabs(["Home","Course","Vocabulary","Progress","Account"])

with home:
    rp=read_progress();done=sum(bool(rp.get(r["id"])) for r in READINGS);pool=vocab_pool("All topics","A1")+vocab_pool("All topics","A2");ss=load_srs()
    studied=sum(1 for c in pool if int(ss.get(c["id"],{}).get("reviews",0) or 0)>0);mastered=sum(1 for c in pool if ss.get(c["id"],{}).get("mastered",False))
    stats=load_stats();att=int(stats.get("attempts",0));acc=int(stats.get("correct",0))/att*100 if att else 0
    st.markdown('<div class="hero"><div class="small-label">Today</div><h1>Ready for German?</h1><p>Continue your course, review due vocabulary, and keep your progress moving.</p></div>',unsafe_allow_html=True)
    st.progress(done/125);st.caption(f"{done}/125 readings completed")
    st.markdown(f'<div class="stats"><div class="stat"><div class="sl">Studied</div><div class="sv">{studied}</div></div><div class="stat"><div class="sl">Mastered</div><div class="sv">{mastered}</div></div><div class="stat"><div class="sl">Accuracy</div><div class="sv">{acc:.0f}%</div></div><div class="stat"><div class="sl">Attempts</div><div class="sv">{att}</div></div></div>',unsafe_allow_html=True)

with course:
    st.markdown('<div class="hero"><div class="small-label">Course</div><h1>German A1</h1><p>25 topics · 5 progressive readings per topic</p></div>',unsafe_allow_html=True)
    rp=read_progress();tn=sorted({r["topic"] for r in READINGS});t=st.selectbox("Topic",tn);rs=[r for r in READINGS if r["topic"]==t]
    labels=[f"{'✓' if rp.get(r['id']) else '○'} Text {r['reading']} · {r['title']}" for r in rs];choice=st.radio("Reading",labels);r=rs[labels.index(choice)]
    st.markdown(f'<div class="card"><b>{r["title"]}</b>',unsafe_allow_html=True)
    for s in [x.strip() for x in re.split(r'(?<=[.!?])\s+',r["text"]) if x.strip()]:st.write(s)
    st.markdown('</div>',unsafe_allow_html=True)
    st.subheader("Key vocabulary")
    for w in r["vocabulary"]:
        item=resolve(w) or {"German":w,"IPA":"—","English":""};g=item.get("German",w)
        st.markdown(f'<div class="card"><b>{g}</b><div style="color:#38bdf8;font-weight:800">{item.get("IPA","—")}</div><div class="muted">{item.get("English","")}</div></div>',unsafe_allow_html=True)
        with st.expander(f"🔊 {g}"):audio(g)
    for i,q in enumerate(r["questions"],1):st.write(f"{i}. {q}")
    done=bool(rp.get(r["id"]))
    if st.button("Mark as not completed" if done else "Mark as completed",key="done"):
        set_reading(r["id"],not done);st.rerun()

with vocab:
    if "session" not in st.session_state:
        st.markdown(
            '<div class="hero"><div class="small-label">Practice</div>'
            '<h1>Vocabulary Trainer</h1>'
            '<p>Type every answer. Your SRS schedules the next review automatically.</p></div>',
            unsafe_allow_html=True
        )

        level=st.segmented_control(
            "Vocabulary level",
            options=["A1","A2"],
            default="A1",
            key="vlevel"
        ) or "A1"

        t=st.selectbox(
            "Topic",
            ["All topics"]+vocabulary_topics(level),
            key=f"vt_{level}"
        )

        direction=st.radio(
            "Direction",
            ["German → English","English → German"],
            horizontal=True
        )

        pool=vocab_pool(t,level)

        if not pool:
            st.warning("No vocabulary was found for this selection.")
        else:
            max_words=len(pool)

            amount_options=[5,10,20,30,50,100,200,400,800,1200]
            amount_options=[x for x in amount_options if x <= max_words]

            if max_words not in amount_options:
                amount_options.append(max_words)

            amount_options=sorted(set(amount_options))
            default_amount=10 if max_words >= 10 else max_words

            st.markdown("#### Number of words")

            quick_amount=st.select_slider(
                "Quick selection",
                options=amount_options,
                value=default_amount if default_amount in amount_options else amount_options[0],
                key=f"quick_amount_{level}_{t}",
                label_visibility="collapsed"
            )

            manual_amount=st.number_input(
                "Or enter an exact number",
                min_value=1,
                max_value=max_words,
                value=int(quick_amount),
                step=1,
                key=f"manual_amount_{level}_{t}",
                help=f"You can choose any number from 1 to {max_words}."
            )

            amount=int(manual_amount)

            # Render count and Start button immediately.
            # This avoids processing 800/1200 SRS records before the UI appears.
            srs_snapshot=st.session_state.setdefault("srs_cache",load_srs())

            pool_ids={c["id"] for c in pool}
            reviewed_count=sum(
                1 for word_id,row in srs_snapshot.items()
                if word_id in pool_ids and int(row.get("reviews",0) or 0)>0
            )
            new_count=max(0,len(pool)-reviewed_count)

            st.caption(
                f"{len(pool)} words available · {new_count} not yet studied"
            )

            if st.button(
                "Start practice →",
                type="primary",
                use_container_width=True,
                key=f"start_{level}_{t}"
            ):
                # Only calculate SRS priority after the user presses Start.
                due_cards=[]
                new_cards=[]
                future=[]

                for c in pool:
                    row=srs_snapshot.get(c["id"],{})
                    reviews=int(row.get("reviews",0) or 0)

                    if reviews==0:
                        new_cards.append(c)
                    else:
                        due_value=row.get("due")
                        if due_value:
                            try:
                                due_dt=datetime.fromisoformat(due_value)
                                if due_dt <= now_utc():
                                    due_cards.append(c)
                                else:
                                    future.append(c)
                            except Exception:
                                due_cards.append(c)
                        else:
                            due_cards.append(c)

                random.shuffle(due_cards)
                random.shuffle(new_cards)
                future.sort(
                    key=lambda c:srs_snapshot.get(c["id"],{}).get("due") or "9999"
                )

                selected=(due_cards+new_cards+future)[:amount]

                if not selected:
                    st.warning("There are no cards available for this selection.")
                else:
                    st.session_state.session=selected
                    st.session_state.idx=0
                    st.session_state.direction=direction
                    st.session_state.vocab_level=level
                    st.session_state.fb=None
                    st.rerun()

    else:
        session=st.session_state.session
        i=st.session_state.idx
        level=st.session_state.get("vocab_level","A1")

        if i>=len(session):
            st.success("Session complete. Progress saved online.")

            if st.button("New session"):
                for k in ["session","idx","direction","vocab_level","fb"]:
                    st.session_state.pop(k,None)
                st.rerun()

        else:
            c=session[i]
            direction=st.session_state.direction

            if direction=="German → English":
                front=c["german"]
                sub=c["ipa"]
                expected=c["english"]
                prompt="Type the English meaning"
                ans=c["english"]
            else:
                front=c["english"]
                sub=""
                expected=c["german"]
                prompt="Type the German word"
                ans=f'{c["german"]} · {c["ipa"]}'

            # Overall vocabulary progress
            full_srs=st.session_state.setdefault("srs_cache",load_srs())
            total_vocab=len(vocab_rows(level))

            level_prefix=f"{level}:"
            studied_total=sum(
                1 for word_id,row in full_srs.items()
                if str(word_id).startswith(level_prefix)
                and int(row.get("reviews",0) or 0)>0
            )
            overall_pct=min(
                100,
                max(0,(studied_total/total_vocab*100) if total_vocab else 0)
            )

            st.markdown(
                f'<div class="vocab-overall">'
                f'<div class="vocab-overall-row">'
                f'<span>Overall progress</span>'
                f'<span class="vocab-overall-value">{studied_total} / {total_vocab} words</span>'
                f'</div>'
                f'<div class="vocab-overall-track">'
                f'<div class="vocab-overall-fill" style="width:{overall_pct:.1f}%"></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

            # TRUE integrated card: native Streamlit container holds all widgets.
            with st.container(border=True, key="vocab_card"):
                st.markdown(
                    f'<div class="vocab-card-head">'
                    f'<div class="vocab-topic-pill">▣&nbsp; {c["topic"]}</div>'
                    f'<div class="vocab-card-counter">Card {i+1} of {len(session)}</div>'
                    f'<div class="vocab-main-word">{front}</div>'
                    f'<div class="vocab-main-ipa">{sub}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # One-click direct audio, repeatable as many times as wanted.
                direct_audio_button(
                    c["german"],
                    key=f"{i}_{c['id']}"
                )

                st.markdown(
                    f'<div class="vocab-prompt">{prompt}</div>',
                    unsafe_allow_html=True
                )

                if st.session_state.fb is None:
                    with st.form("answer"):
                        a=st.text_input(
                            prompt,
                            placeholder="Type your answer here...",
                            label_visibility="collapsed"
                        )
                        check=st.form_submit_button(
                            "Check answer",
                            type="primary",
                            use_container_width=True
                        )

                    if check:
                        if not a.strip():
                            st.warning("Write an answer first.")
                        else:
                            ok=matches(a,expected)
                            nxt=apply_result(c,ok)

                            st.session_state.fb={
                                "ok":ok,
                                "user":a,
                                "answer":ans,
                                "due":nxt.isoformat()
                            }
                            st.rerun()

                else:
                    f=st.session_state.fb
                    review_text=due_text(
                        datetime.fromisoformat(f["due"])
                    )

                    if f["ok"]:
                        st.markdown(
                            f'<div class="vocab-result-good">'
                            f'<div class="vocab-result-title" style="color:#65e88a">'
                            f'✓ Correct</div>'
                            f'<div class="vocab-result-meta">'
                            f'Correct answer: <b>{f["answer"]}</b><br>'
                            f'Next review: <b>{review_text}</b>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="vocab-result-bad">'
                            f'<div class="vocab-result-title" style="color:#ff8e8e">'
                            f'Review this one</div>'
                            f'<div class="vocab-result-meta">'
                            f'Your answer: <b>{f["user"]}</b><br>'
                            f'Correct answer: <b>{f["answer"]}</b><br>'
                            f'Next review: <b>{review_text}</b>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )

                    if st.button(
                        "Continue →",
                        type="primary",
                        key="continue_btn"
                    ):
                        st.session_state.idx+=1
                        st.session_state.fb=None
                        st.rerun()


with progress:
    st.markdown(
        '<div class="hero"><div class="small-label">Progress</div>'
        '<h1>Your learning dashboard</h1>'
        '<p>Track A1 and A2 independently, plus your total German vocabulary progress.</p></div>',
        unsafe_allow_html=True
    )

    rp=read_progress()
    readings_done=sum(bool(rp.get(r["id"])) for r in READINGS)
    stats=load_stats()
    total_attempts=int(stats.get("attempts",0) or 0)
    total_correct=int(stats.get("correct",0) or 0)
    total_wrong=int(stats.get("wrong",0) or 0)
    total_accuracy=(total_correct/total_attempts*100) if total_attempts else 0
    srs_data=load_srs()

    def level_progress_stats(level):
        pool=vocab_pool("All topics",level)
        ids={c["id"] for c in pool}
        studied=mastered=due_count=correct=wrong=0
        for word_id in ids:
            row=srs_data.get(word_id,{})
            reviews=int(row.get("reviews",0) or 0)
            if reviews>0:
                studied+=1
            if bool(row.get("mastered",False)):
                mastered+=1
            if reviews>0 and due(word_id):
                due_count+=1
            correct+=int(row.get("correct",0) or 0)
            wrong+=int(row.get("wrong",0) or 0)
        attempts=correct+wrong
        accuracy=(correct/attempts*100) if attempts else 0
        return {
            "total":len(pool),"studied":studied,"mastered":mastered,
            "due":due_count,"correct":correct,"wrong":wrong,
            "attempts":attempts,"accuracy":accuracy
        }

    a1s=level_progress_stats("A1")
    a2s=level_progress_stats("A2")

    overall_total=a1s["total"]+a2s["total"]
    overall_studied=a1s["studied"]+a2s["studied"]
    overall_mastered=a1s["mastered"]+a2s["mastered"]
    overall_due=a1s["due"]+a2s["due"]
    overall_pct=(overall_studied/overall_total*100) if overall_total else 0

    st.markdown(
        f'<div class="vocab-overall" style="margin-top:18px">'
        f'<div class="vocab-overall-row"><span>Overall vocabulary progress</span>'
        f'<span class="vocab-overall-value">{overall_studied} / {overall_total} words</span></div>'
        f'<div class="vocab-overall-track">'
        f'<div class="vocab-overall-fill" style="width:{overall_pct:.1f}%"></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Readings",f"{readings_done}/125")
    c2.metric("Studied",overall_studied)
    c3.metric("Mastered",overall_mastered)
    c4.metric("Due",overall_due)

    st.markdown("### A1 Vocabulary")
    st.progress(a1s["studied"]/a1s["total"] if a1s["total"] else 0)
    st.caption(f'{a1s["studied"]} / {a1s["total"]} words studied')
    a,b,c,d=st.columns(4)
    a.metric("A1 Studied",a1s["studied"])
    b.metric("A1 Mastered",a1s["mastered"])
    c.metric("A1 Due",a1s["due"])
    d.metric("A1 Accuracy",f'{a1s["accuracy"]:.1f}%')

    st.markdown("### A2 Vocabulary")
    st.progress(a2s["studied"]/a2s["total"] if a2s["total"] else 0)
    st.caption(f'{a2s["studied"]} / {a2s["total"]} words studied')
    a,b,c,d=st.columns(4)
    a.metric("A2 Studied",a2s["studied"])
    b.metric("A2 Mastered",a2s["mastered"])
    c.metric("A2 Due",a2s["due"])
    d.metric("A2 Accuracy",f'{a2s["accuracy"]:.1f}%')

    st.markdown("### Combined performance")
    a,b,c,d=st.columns(4)
    a.metric("Correct",total_correct)
    b.metric("Wrong",total_wrong)
    c.metric("Attempts",total_attempts)
    d.metric("Accuracy",f"{total_accuracy:.1f}%")

with account:
    st.markdown('<div class="hero"><div class="small-label">Account</div><h1>Your profile</h1><p>Your progress stays synced across devices.</p></div>',unsafe_allow_html=True)
    st.write(u.email);st.caption("Your progress is stored in Supabase under this account.")
    if st.button("Sign out"):
        try:supabase.auth.sign_out()
        except:pass
        st.session_state.clear();st.rerun()
