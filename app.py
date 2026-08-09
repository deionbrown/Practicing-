import csv, json, random, re, unicodedata
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Inglés A1", page_icon="🇬🇧", layout="wide", initial_sidebar_state="expanded")
BASE_DIR=Path(__file__).resolve().parent
CSV_FILE=BASE_DIR/"English_A1_800_with_IPA.csv"
PROGRESS_FILE=BASE_DIR/"english_a1_progress.json"

st.markdown("""
<style>
:root{--bg:#f7fbff;--ink:#223047;--muted:#718096;--border:#e4eaf2;--green:#58cc02;--green2:#46a302;--blue:#1cb0f6}
.stApp{background:var(--bg);color:var(--ink)}
.block-container{max-width:1100px;padding-top:1.2rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--border)}
#MainMenu{visibility:hidden} footer{visibility:hidden}
.hero{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center;margin-bottom:16px}
.welcome{background:#fff;border:2px solid var(--border);border-radius:22px;padding:18px 22px}
.welcome h1{font-size:1.75rem;margin:0;font-weight:850}.welcome p{margin:4px 0 0;color:var(--muted)}
.stats{display:flex;gap:10px}.stat{background:#fff;border:2px solid var(--border);border-radius:18px;padding:10px 15px;text-align:center;min-width:100px}
.stat b{display:block;font-size:1.1rem}.stat small{color:var(--muted)}
.progressbox{background:#fff;border:2px solid var(--border);border-radius:20px;padding:15px 18px;margin-bottom:18px}
.proghead{display:flex;justify-content:space-between;font-weight:700;color:var(--muted);font-size:.86rem;margin-bottom:9px}
.track{height:16px;background:#edf1f5;border-radius:99px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#58cc02,#82df26);border-radius:99px}
.card{background:#fff;border:2px solid var(--border);border-radius:28px;padding:30px 32px;box-shadow:0 7px 0 #dfe6ee;margin-bottom:18px;text-align:center}
.topic{display:inline-block;background:#eef9e8;color:#46a302;border:2px solid #d7efca;border-radius:99px;padding:7px 12px;font-weight:800;font-size:.82rem}
.word{font-size:3.1rem;font-weight:900;letter-spacing:-.03em;margin:22px 0 8px}.ipa{font-size:1.15rem;color:var(--muted);font-weight:650}
.instruction{margin-top:20px;font-weight:800}
.good,.bad{border-radius:22px;padding:18px 20px;margin:14px 0}.good{background:#effce9;border:2px solid #bceaa3;color:#2d7f08}.bad{background:#fff0f0;border:2px solid #ffc8c8;color:#b72c2c}
.feedbacktitle{font-size:1.18rem;font-weight:900}.answers{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}.ans{background:#fff;border-radius:16px;padding:12px 14px}.ans small{color:var(--muted)}.ans b{display:block;margin-top:3px}
.mastered{background:#fff9de;border:2px solid #ffe982;color:#946700;border-radius:18px;padding:13px;text-align:center;font-weight:850;margin:12px 0}
.session{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:18px}.session>div{background:#fff;border:2px solid var(--border);border-radius:18px;padding:14px}.session small{color:var(--muted)}.session b{display:block;font-size:1.35rem;margin-top:3px}
div.stButton>button,div.stFormSubmitButton>button{width:100%;min-height:50px;border-radius:16px;font-weight:800;box-shadow:0 4px 0 rgba(0,0,0,.12)}
div.stFormSubmitButton>button,div.stButton>button[kind="primary"]{background:#58cc02;color:#fff;border:0}
div[data-testid="stTextInput"] input{min-height:54px;border-radius:16px;border:2px solid #dce3eb;font-size:1rem;font-weight:700}
@media(max-width:800px){.hero{grid-template-columns:1fr}.stats{display:grid;grid-template-columns:repeat(3,1fr)}.stat{min-width:0}.word{font-size:2.3rem}.session{grid-template-columns:repeat(2,1fr)}.answers{grid-template-columns:1fr}}
</style>
""",unsafe_allow_html=True)

@st.cache_data
def load_vocab():
    if not CSV_FILE.exists(): return []
    with CSV_FILE.open("r",encoding="utf-8-sig",newline="") as f:
        out=[]
        for i,r in enumerate(csv.DictReader(f)):
            if r.get("English") and r.get("Spanish"):
                out.append({"id":str(i),"english":r["English"].strip(),"spanish":r["Spanish"].strip(),"ipa":r.get("IPA","").strip(),"topic":r.get("Topic","General").strip()})
        return out

def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except: pass
    return {}

def norm(s):
    s=unicodedata.normalize("NFD",s.lower().strip())
    s="".join(c for c in s if unicodedata.category(c)!="Mn")
    s=re.sub(r"[^\w\s]","",s)
    return " ".join(s.split())

def matches(user,expected):
    u=norm(user)
    alts=[norm(x) for x in re.split(r"[;,/]",expected) if x.strip()]
    return u==norm(expected) or u in alts

V=load_vocab()
if not V:
    st.error("No se encontró English_A1_800_with_IPA.csv"); st.stop()

defaults={"progress":load_progress(),"current":None,"result":False,"last_ok":None,"last_answer":"","mode":"Inglés → Español","answer_input":"","session_total":0,"session_correct":0,"xp":0}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def ensure(i):
    if i not in st.session_state.progress:
        st.session_state.progress[i]={"correct":0,"wrong":0,"streak":0,"mastered":False}

def update(i,ok):
    ensure(i); p=st.session_state.progress[i]
    if ok:
        p["correct"]+=1;p["streak"]+=1;st.session_state.xp+=10
        if p["streak"]>=3:p["mastered"]=True
    else:
        p["wrong"]+=1;p["streak"]=0;p["mastered"]=False
    st.session_state.session_total+=1
    if ok:st.session_state.session_correct+=1

def choose(pool):
    if not pool:return None
    cards=pool[:];random.shuffle(cards)
    def pri(c):
        p=st.session_state.progress.get(c["id"],{})
        if p.get("mastered"):return 3
        if p.get("wrong",0)>0:return 0
        if p.get("correct",0)==0:return 1
        return 2
    cards.sort(key=pri);return cards[0]

def next_card(pool):
    st.session_state.current=choose(pool);st.session_state.result=False;st.session_state.last_ok=None;st.session_state.last_answer="";st.session_state.answer_input=""

st.sidebar.markdown("## 🇬🇧 Inglés A1")
st.sidebar.caption("Aprende inglés un poco cada día")
st.sidebar.markdown("### Modo de estudio")
mode=st.sidebar.radio("Modo",["Inglés → Español","Español → Inglés","Tarjetas"],label_visibility="collapsed")
if mode!=st.session_state.mode:
    st.session_state.mode=mode;st.session_state.current=None;st.session_state.result=False;st.session_state.answer_input=""

topics=sorted({x["topic"] for x in V})
st.sidebar.markdown("### Tema")
topic=st.sidebar.selectbox("Tema",["Todos los temas"]+topics,label_visibility="collapsed")
mistakes=st.sidebar.checkbox("Repasar mis errores")
pool=V[:] if topic=="Todos los temas" else [x for x in V if x["topic"]==topic]
if mistakes:
    pool=[x for x in pool if st.session_state.progress.get(x["id"],{}).get("wrong",0)>0 and not st.session_state.progress.get(x["id"],{}).get("mastered",False)]
if st.sidebar.button("🎲 Nueva palabra"):next_card(pool)

studied=sum(1 for x in V if x["id"] in st.session_state.progress)
mastered=sum(1 for x in V if st.session_state.progress.get(x["id"],{}).get("mastered",False))
attempts=sum(p.get("correct",0)+p.get("wrong",0) for p in st.session_state.progress.values())
correct=sum(p.get("correct",0) for p in st.session_state.progress.values())
accuracy=correct/attempts*100 if attempts else 0
streak=max((p.get("streak",0) for p in st.session_state.progress.values()),default=0)

st.sidebar.markdown("### Tu progreso")
st.sidebar.write(f"📚 **Estudiadas:** {studied} / {len(V)}")
st.sidebar.write(f"⭐ **Dominadas:** {mastered}")
st.sidebar.write(f"🎯 **Precisión:** {accuracy:.0f}%")
st.sidebar.write(f"⚡ **XP de esta sesión:** {st.session_state.xp}")
st.sidebar.divider()
data=json.dumps(st.session_state.progress,ensure_ascii=False,indent=2)
st.sidebar.download_button("💾 Guardar progreso",data,"english_a1_progress.json","application/json")
up=st.sidebar.file_uploader("Restaurar progreso",type=["json"])
if up is not None:
    try:
        new=json.load(up)
        if st.sidebar.button("Cargar progreso"):
            st.session_state.progress=new;st.session_state.current=None;st.rerun()
    except:st.sidebar.error("Archivo de progreso no válido.")

st.markdown(f"""
<div class="hero">
<div class="welcome"><h1>👋 ¡Vamos a practicar inglés!</h1><p>Aprende vocabulario A1 de forma breve, clara y constante.</p></div>
<div class="stats">
<div class="stat">🔥<b>{streak}</b><small>racha</small></div>
<div class="stat">⭐<b>{mastered}</b><small>dominadas</small></div>
<div class="stat">🎯<b>{accuracy:.0f}%</b><small>precisión</small></div>
</div></div>
""",unsafe_allow_html=True)

pct=studied/len(V)*100 if V else 0
st.markdown(f"""<div class="progressbox"><div class="proghead"><span>Progreso general</span><span>{studied} / {len(V)} palabras</span></div><div class="track"><div class="fill" style="width:{pct:.2f}%"></div></div></div>""",unsafe_allow_html=True)

if not pool:st.warning("No hay palabras disponibles con estos filtros.");st.stop()
if st.session_state.current is None:next_card(pool)
if st.session_state.current["id"] not in {x["id"] for x in pool}:next_card(pool)
c=st.session_state.current

if mode=="Inglés → Español":
    q,ipa,expected,instruction=c["english"],c["ipa"],c["spanish"],"Escribe el significado en español"
elif mode=="Español → Inglés":
    q,ipa,expected,instruction=c["spanish"],"",c["english"],"Escribe la palabra o frase en inglés"
else:
    q,ipa,expected,instruction=c["english"],c["ipa"],c["spanish"],"Piensa en el significado y luego revela la respuesta"

st.markdown(f"""<div class="card"><span class="topic">📘 {c["topic"]}</span><div class="word">{q}</div><div class="ipa">{ipa}</div><div class="instruction">{instruction}</div></div>""",unsafe_allow_html=True)

if mode=="Tarjetas":
    if not st.session_state.result:
        if st.button("👀 Mostrar respuesta",type="primary"):st.session_state.result=True;st.rerun()
    else:
        st.markdown(f'<div class="good"><div class="feedbacktitle">Respuesta</div><b style="font-size:1.35rem">{expected}</b></div>',unsafe_allow_html=True)
        if st.button("➡️ Siguiente",type="primary"):next_card(pool);st.rerun()
else:
    if not st.session_state.result:
        with st.form("quiz"):
            ua=st.text_input("Respuesta",key="answer_input",placeholder="Escribe tu respuesta aquí...",label_visibility="collapsed")
            submit=st.form_submit_button("Comprobar")
        if submit:
            if not ua.strip():st.warning("Primero escribe una respuesta.")
            else:
                ok=matches(ua,expected);st.session_state.last_answer=ua;st.session_state.last_ok=ok;st.session_state.result=True;update(c["id"],ok);st.rerun()
    else:
        cls="good" if st.session_state.last_ok else "bad"
        title="🎉 ¡Excelente! Respuesta correcta." if st.session_state.last_ok else "💡 Sigue practicando. Revisa la respuesta."
        st.markdown(f"""<div class="{cls}"><div class="feedbacktitle">{title}</div><div class="answers"><div class="ans"><small>Tu respuesta</small><b>{st.session_state.last_answer}</b></div><div class="ans"><small>Respuesta correcta</small><b>{expected}</b></div></div></div>""",unsafe_allow_html=True)
        if mode=="Español → Inglés" and c["ipa"]:st.info(f"🔊 Pronunciación: {c['ipa']}")
        ensure(c["id"]);p=st.session_state.progress[c["id"]]
        st.caption(f"Esta palabra · {p['correct']} correctas · {p['wrong']} errores · racha {p['streak']}/3")
        if p["mastered"]:st.markdown('<div class="mastered">⭐ ¡Palabra dominada!</div>',unsafe_allow_html=True)
        if st.button("➡️ Continuar",type="primary"):next_card(pool);st.rerun()

sa=st.session_state.session_correct/st.session_state.session_total*100 if st.session_state.session_total else 0
st.markdown(f"""<div class="session"><div><small>Palabras hoy</small><b>{st.session_state.session_total}</b></div><div><small>Correctas</small><b>{st.session_state.session_correct}</b></div><div><small>Precisión</small><b>{sa:.0f}%</b></div><div><small>XP ganados</small><b>{st.session_state.xp}</b></div></div>""",unsafe_allow_html=True)
