import asyncio, csv, json, random, re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st
from supabase import create_client
import edge_tts

st.set_page_config(page_title="German A1 Complete",page_icon="🇩🇪",layout="wide",initial_sidebar_state="collapsed")
BASE=Path(__file__).resolve().parent
READINGS=json.loads((BASE/"readings.json").read_text(encoding="utf-8"))
SUPPLEMENT=json.loads((BASE/"course_vocab_supplement.json").read_text(encoding="utf-8"))
VOICE="de-DE-KatjaNeural"

st.markdown("""
<style>
:root{--bg:#0f172a;--panel:#172033;--border:#2b3a50;--text:#f8fafc;--muted:#94a3b8;--accent:#6d5dfb;--blue:#38bdf8;}
.stApp{background:var(--bg);color:var(--text)} .block-container{max-width:1000px;padding-top:.8rem;padding-bottom:5rem}
#MainMenu,footer{visibility:hidden}
.brand,.card,.hero,.stat{background:var(--panel);border:1px solid var(--border);border-radius:18px}
.brand{display:flex;gap:12px;align-items:center;padding:14px 16px;margin-bottom:12px}
.logo{background:var(--accent);width:46px;height:46px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-weight:900}
.title{font-size:1.22rem;font-weight:900}.muted{color:var(--muted);font-size:.82rem}
.hero{padding:20px;margin:10px 0 14px}.hero h1{font-size:1.7rem;margin:0 0 4px}.hero p{color:var(--muted);margin:0}
.card{padding:17px;margin:9px 0}.word{text-align:center;font-size:2.3rem;font-weight:900}.ipa{text-align:center;color:var(--blue);font-weight:800;font-size:1.08rem}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.stat{padding:13px}.sl{font-size:.72rem;color:var(--muted);font-weight:800}.sv{font-size:1.3rem;font-weight:900}
div.stButton>button,div.stFormSubmitButton>button{width:100%;min-height:48px;border-radius:13px;font-weight:800}
@media(max-width:700px){.block-container{padding:.6rem .65rem 5rem}.stats{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:1.4rem}.word{font-size:2rem}}
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
def vocab_rows():
    with (BASE/"German_A1_800_with_IPA.csv").open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

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
def vocab_pool(topic):
    out=[];seen=set()
    for r in READINGS:
        if topic!="All topics" and r["topic"]!=topic:continue
        for w in r["vocabulary"]:
            if w.lower() in seen:continue
            seen.add(w.lower());item=resolve(w) or {"German":w,"IPA":"—","English":""}
            g=(item.get("German") or w).strip()
            out.append({"id":g.lower(),"german":g,"ipa":item.get("IPA","—"),"english":item.get("English",""),"topic":r["topic"]})
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
    st.markdown('<div class="brand"><div class="logo">DE</div><div><div class="title">German A1 Complete</div><div class="muted">Mobile · synced progress · natural audio</div></div></div>',unsafe_allow_html=True)
    a,b=st.tabs(["Sign in","Create account"])
    with a:
        with st.form("login"):
            email=st.text_input("Email");password=st.text_input("Password",type="password");go=st.form_submit_button("Sign in",type="primary")
        if go:
            try:
                r=supabase.auth.sign_in_with_password({"email":email,"password":password});st.session_state.user=r.user;st.rerun()
            except:st.error("Could not sign in.")
    with b:
        with st.form("signup"):
            e=st.text_input("Email",key="se");p=st.text_input("Password",type="password",key="sp");go2=st.form_submit_button("Create account")
        if go2:
            try:
                r=supabase.auth.sign_up({"email":e,"password":p})
                if r.session:st.session_state.user=r.user;st.rerun()
                else:st.success("Account created. Check your email to confirm it, then sign in.")
            except:st.error("Could not create account.")
    st.stop()

u=current_user()
st.markdown(f'<div class="brand"><div class="logo">DE</div><div><div class="title">German A1 Complete</div><div class="muted">{u.email}</div></div></div>',unsafe_allow_html=True)
home,course,vocab,progress,account=st.tabs(["Home","Course","Vocabulary","Progress","Account"])

with home:
    rp=read_progress();done=sum(bool(rp.get(r["id"])) for r in READINGS);pool=vocab_pool("All topics");ss=load_srs()
    studied=sum(1 for c in pool if int(ss.get(c["id"],{}).get("reviews",0) or 0)>0);mastered=sum(1 for c in pool if ss.get(c["id"],{}).get("mastered",False))
    stats=load_stats();att=int(stats.get("attempts",0));acc=int(stats.get("correct",0))/att*100 if att else 0
    st.markdown('<div class="hero"><h1>Ready for German?</h1><p>Your progress is synced between your phone and PC.</p></div>',unsafe_allow_html=True)
    st.progress(done/125);st.caption(f"{done}/125 readings completed")
    st.markdown(f'<div class="stats"><div class="stat"><div class="sl">Studied</div><div class="sv">{studied}</div></div><div class="stat"><div class="sl">Mastered</div><div class="sv">{mastered}</div></div><div class="stat"><div class="sl">Accuracy</div><div class="sv">{acc:.0f}%</div></div><div class="stat"><div class="sl">Attempts</div><div class="sv">{att}</div></div></div>',unsafe_allow_html=True)

with course:
    st.markdown('<div class="hero"><h1>German A1 Course</h1><p>25 topics · 5 readings per topic</p></div>',unsafe_allow_html=True)
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
    st.markdown('<div class="hero"><h1>Vocabulary Trainer</h1><p>Type every answer. SRS schedules reviews automatically.</p></div>',unsafe_allow_html=True)
    if "session" not in st.session_state:
        t=st.selectbox("Topic",["All topics"]+sorted({r["topic"] for r in READINGS}),key="vt")
        direction=st.radio("Direction",["German → English","English → German"],horizontal=True)
        amount=st.select_slider("Number of words",options=[5,10,20,30,50],value=10)
        pool=vocab_pool(t);due_cards=[];new=[];future=[]
        for c in pool:
            x=srs(c["id"])
            if int(x.get("reviews",0))==0:new.append(c)
            elif due(c["id"]):due_cards.append(c)
            else:future.append(c)
        random.shuffle(due_cards);random.shuffle(new);future.sort(key=lambda c:srs(c["id"]).get("due") or "9999")
        st.caption(f"{len(pool)} words · {len(due_cards)} due · {len(new)} new")
        if st.button("Start session",type="primary"):
            st.session_state.session=(due_cards+new+future)[:amount];st.session_state.idx=0;st.session_state.direction=direction;st.session_state.fb=None;st.rerun()
    else:
        session=st.session_state.session;i=st.session_state.idx
        if i>=len(session):
            st.success("Session complete. Progress saved online.")
            if st.button("New session"):
                for k in ["session","idx","direction","fb"]:st.session_state.pop(k,None)
                st.rerun()
        else:
            c=session[i];direction=st.session_state.direction
            if direction=="German → English":front=c["german"];sub=c["ipa"];expected=c["english"];prompt="Type the English meaning";ans=c["english"]
            else:front=c["english"];sub="";expected=c["german"];prompt="Type the German word";ans=f'{c["german"]} · {c["ipa"]}'
            st.caption(f"Card {i+1}/{len(session)} · {c['topic']}")
            st.markdown(f'<div class="card"><div class="word">{front}</div><div class="ipa">{sub}</div></div>',unsafe_allow_html=True)
            with st.expander("🔊 Listen"):audio(c["german"])
            if st.session_state.fb is None:
                with st.form("answer"):
                    a=st.text_input(prompt);check=st.form_submit_button("Check answer",type="primary")
                if check and a.strip():
                    ok=matches(a,expected);nxt=apply_result(c,ok);st.session_state.fb={"ok":ok,"user":a,"answer":ans,"due":nxt.isoformat()};st.rerun()
            else:
                f=st.session_state.fb
                if f["ok"]:
                    st.success("Correct")
                else:
                    st.error("Review this one")
                st.write("**Your answer:**",f["user"]);st.write("**Correct answer:**",f["answer"]);st.write("**Next review:**",due_text(datetime.fromisoformat(f["due"])))
                if st.button("Next card",type="primary"):
                    st.session_state.idx+=1;st.session_state.fb=None;st.rerun()

with progress:
    rp=read_progress();rd=sum(bool(rp.get(r["id"])) for r in READINGS);pool=vocab_pool("All topics");ss=load_srs();stt=load_stats()
    studied=sum(1 for c in pool if int(ss.get(c["id"],{}).get("reviews",0) or 0)>0);mastered=sum(1 for c in pool if ss.get(c["id"],{}).get("mastered",False))
    due_now=sum(1 for c in pool if int(ss.get(c["id"],{}).get("reviews",0) or 0)>0 and due(c["id"]))
    att=int(stt.get("attempts",0));cor=int(stt.get("correct",0));wrong=int(stt.get("wrong",0));acc=cor/att*100 if att else 0
    st.markdown(f'<div class="stats"><div class="stat"><div class="sl">Readings</div><div class="sv">{rd}/125</div></div><div class="stat"><div class="sl">Studied</div><div class="sv">{studied}</div></div><div class="stat"><div class="sl">Mastered</div><div class="sv">{mastered}</div></div><div class="stat"><div class="sl">Due</div><div class="sv">{due_now}</div></div><div class="stat"><div class="sl">Correct</div><div class="sv">{cor}</div></div><div class="stat"><div class="sl">Wrong</div><div class="sv">{wrong}</div></div><div class="stat"><div class="sl">Attempts</div><div class="sv">{att}</div></div><div class="stat"><div class="sl">Accuracy</div><div class="sv">{acc:.1f}%</div></div></div>',unsafe_allow_html=True)

with account:
    st.write(u.email);st.caption("Your progress is stored in Supabase under this account.")
    if st.button("Sign out"):
        try:supabase.auth.sign_out()
        except:pass
        st.session_state.clear();st.rerun()

