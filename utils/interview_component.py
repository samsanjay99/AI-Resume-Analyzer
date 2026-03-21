"""
Smart Interview Component — Production Rewrite
Fixes:
  1. Smart silence detection (3s countdown, cancels on resume)
  2. Real-time answer validation + AI follow-up if too short
  3. Strict dedup — messages fingerprinted, never duplicated
  4. Natural conversation flow — thinking state, pacing delays
  5. Automatic final evaluation trigger on last question
"""
import json, os
from dotenv import load_dotenv
load_dotenv()


def build_interview_component(
    questions: list,
    job_role: str,
    candidate_name: str,
    interview_id: int,
    vapi_token: str = None,
    vapi_assistant_id: str = None,
) -> str:
    if not vapi_token:
        vapi_token = os.getenv("VAPI_WEB_TOKEN", "")
    if not vapi_assistant_id:
        vapi_assistant_id = os.getenv("VAPI_ASSISTANT_ID", "ab9b228d-3b3f-4ff0-9678-a6de2c20674c")

    total_q      = len(questions)
    questions_js = json.dumps(questions)
    # Build numbered question list to inject into the pre-built assistant via variableValues
    q_lines_display = "\\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

    HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Interview</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:#0d0d1a;color:#fff;
     display:flex;flex-direction:column;align-items:center;
     padding:18px 14px;gap:12px;
     overflow-y:auto;height:auto}}

.badge{{padding:3px 12px;border-radius:20px;font-size:.7rem;font-weight:700;
       text-transform:uppercase;letter-spacing:.5px;align-self:flex-start}}
.badge-vapi{{background:rgba(103,78,234,.2);color:#a78bfa;border:1px solid #7c3aed}}
.badge-free{{background:rgba(76,175,80,.14);color:#4CAF50;border:1px solid #388E3C}}

.banner{{width:100%;max-width:660px;background:linear-gradient(135deg,#1a1a3e,#16213e);
        border:1px solid rgba(76,175,80,.28);border-radius:12px;
        padding:11px 16px;display:flex;justify-content:space-between;align-items:center}}
.b-role{{color:#4CAF50;font-size:.95rem;font-weight:700;margin-bottom:1px}}
.b-meta{{color:#888;font-size:.72rem}}
.timer{{color:#4CAF50;font-size:.98rem;font-weight:700;font-variant-numeric:tabular-nums}}

.stage{{display:flex;align-items:center;justify-content:center;gap:38px;
       width:100%;max-width:660px}}
.av-wrap{{display:flex;flex-direction:column;align-items:center;gap:7px}}
.av{{width:82px;height:82px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:2rem;border:3px solid #1e1e2e;transition:all .3s}}
.av.ai-bg {{background:linear-gradient(135deg,#1a1a3e,#2a2a6e)}}
.av.usr-bg{{background:linear-gradient(135deg,#1a3e1a,#2a6e2a)}}
.av.speaking {{border-color:#4CAF50!important;animation:pG 1.1s ease-out infinite}}
.av.listening{{border-color:#2196F3!important;animation:pB 1.3s ease-out infinite}}
.av.thinking {{border-color:#FF9800!important;animation:pO 1.5s ease-out infinite}}
@keyframes pG{{0%{{box-shadow:0 0 0 0 rgba(76,175,80,.5)}}
              70%{{box-shadow:0 0 0 16px rgba(76,175,80,0)}}100%{{box-shadow:0 0 0 0 rgba(76,175,80,0))}}}}
@keyframes pB{{0%{{box-shadow:0 0 0 0 rgba(33,150,243,.5)}}
              70%{{box-shadow:0 0 0 16px rgba(33,150,243,0)}}100%{{box-shadow:0 0 0 0 rgba(33,150,243,0))}}}}
@keyframes pO{{0%{{box-shadow:0 0 0 0 rgba(255,152,0,.5)}}
              70%{{box-shadow:0 0 0 16px rgba(255,152,0,0)}}100%{{box-shadow:0 0 0 0 rgba(255,152,0,0))}}}}
.wave{{display:flex;align-items:center;gap:3px;height:16px;visibility:hidden}}
.wave.on{{visibility:visible}}
.wave span{{width:3px;border-radius:2px;animation:wb .8s ease-in-out infinite}}
.wave.g span{{background:#4CAF50}}.wave.b span{{background:#2196F3}}
.wave span:nth-child(1){{height:4px}}.wave span:nth-child(2){{height:11px;animation-delay:.12s}}
.wave span:nth-child(3){{height:16px;animation-delay:.24s}}.wave span:nth-child(4){{height:9px;animation-delay:.36s}}
.wave span:nth-child(5){{height:13px;animation-delay:.48s}}
@keyframes wb{{0%,100%{{height:3px;opacity:.5}}50%{{height:16px;opacity:1}}}}
.av-name{{font-size:.74rem;color:#bbb;font-weight:500}}
.vs{{font-size:1.1rem;color:#252535;font-weight:800}}

.prog-wrap{{width:100%;max-width:660px;display:none}}
.prog-top{{display:flex;justify-content:space-between;font-size:.72rem;color:#888;margin-bottom:4px}}
.prog-track{{width:100%;height:6px;background:rgba(255,255,255,.07);border-radius:4px;overflow:hidden}}
.prog-fill{{height:100%;border-radius:4px;
           background:linear-gradient(90deg,#4CAF50,#81C784);
           transition:width .5s ease;width:0%}}
.dots{{display:flex;gap:5px;margin-top:6px;flex-wrap:wrap}}
.dot{{width:9px;height:9px;border-radius:50%;background:rgba(255,255,255,.1);transition:all .4s}}
.dot.done{{background:#4CAF50}}.dot.cur{{background:#FF9800;animation:db .7s ease infinite alternate}}
@keyframes db{{from{{transform:scale(1)}}to{{transform:scale(1.5)}}}}

.chip{{display:inline-flex;align-items:center;gap:6px;padding:5px 13px;
      border-radius:20px;font-size:.77rem;font-weight:600}}
.c-idle{{background:rgba(255,255,255,.07);color:#aaa}}
.c-speaking{{background:rgba(76,175,80,.14);color:#4CAF50}}
.c-listening{{background:rgba(33,150,243,.14);color:#42A5F5}}
.c-thinking{{background:rgba(255,152,0,.14);color:#FF9800}}
.c-waiting{{background:rgba(255,235,59,.12);color:#FDD835}}
.c-done{{background:rgba(33,150,243,.14);color:#42A5F5}}
.c-followup{{background:rgba(156,39,176,.14);color:#CE93D8}}
.cdot{{width:7px;height:7px;border-radius:50%;background:currentColor}}

/* SILENCE COUNTDOWN BAR */
.sil-bar{{width:100%;max-width:660px;display:none}}
.sil-top{{display:flex;justify-content:space-between;font-size:.7rem;color:#888;margin-bottom:3px}}
.sil-track{{width:100%;height:4px;background:rgba(255,255,255,.06);border-radius:3px}}
.sil-fill{{height:100%;border-radius:3px;width:0%;
          background:linear-gradient(90deg,#FDD835,#FF9800);transition:width .1s linear}}

.q-card{{width:100%;max-width:660px;background:rgba(255,255,255,.04);
        border:1px solid rgba(255,255,255,.09);border-radius:11px;
        padding:12px 15px;display:none}}
.q-num{{font-size:.67rem;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px}}
.q-txt{{font-size:.91rem;color:#e8e8e8;line-height:1.6}}

.tx-panel{{width:100%;max-width:660px;background:rgba(255,255,255,.03);
          border:1px solid rgba(255,255,255,.07);border-radius:11px;overflow:hidden;
          max-height:205px;display:none;flex-direction:column}}
.tx-head{{padding:5px 12px;background:rgba(255,255,255,.04);
         font-size:.65rem;color:#888;text-transform:uppercase;letter-spacing:1px;
         border-bottom:1px solid rgba(255,255,255,.05);
         display:flex;align-items:center;gap:5px}}
.live-dot{{width:6px;height:6px;border-radius:50%;background:#f44336;animation:lb 1s infinite}}
@keyframes lb{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
.tx-body{{flex:1;overflow-y:auto;padding:8px 12px;
         display:flex;flex-direction:column;gap:5px;
         scrollbar-width:thin;scrollbar-color:#333 transparent}}
.bbl{{padding:6px 10px;border-radius:9px;font-size:.82rem;
     line-height:1.5;max-width:92%;animation:fi .22s ease}}
@keyframes fi{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:translateY(0)}}}}
.bbl.ai{{background:rgba(33,150,243,.1);border-left:3px solid #2196F3;
        color:#bbdefb;align-self:flex-start}}
.bbl.usr{{background:rgba(76,175,80,.1);border-right:3px solid #4CAF50;
         border-left:none;color:#c8e6c9;align-self:flex-end;text-align:right}}
.bbl.sys{{background:rgba(255,152,0,.08);border-left:3px solid #FF9800;
         color:#ffe082;align-self:center;font-style:italic;font-size:.76rem}}
.bbl.partial{{opacity:.55;border-style:dashed!important;font-style:italic}}
.bbl-lbl{{font-size:.61rem;font-weight:700;text-transform:uppercase;
         letter-spacing:.5px;opacity:.55;margin-bottom:2px}}

.btn-start{{padding:12px 46px;border-radius:50px;border:none;font-size:1rem;font-weight:700;
           cursor:pointer;color:white;background:linear-gradient(135deg,#4CAF50,#388E3C);
           box-shadow:0 4px 18px rgba(76,175,80,.38);transition:all .3s}}
.btn-start:hover{{transform:translateY(-2px);box-shadow:0 7px 24px rgba(76,175,80,.48)}}
.btn-start:disabled{{background:#252535;color:#555;box-shadow:none;cursor:not-allowed;transform:none}}
.btn-end{{padding:8px 22px;border-radius:50px;border:2px solid #f44336;
         background:transparent;color:#f44336;font-size:.83rem;font-weight:600;
         cursor:pointer;transition:all .3s;display:none}}
.btn-end:hover{{background:rgba(244,67,54,.1)}}
.btn-retry{{padding:7px 18px;border-radius:50px;border:2px solid #FF9800;
           background:transparent;color:#FF9800;font-size:.8rem;font-weight:600;
           cursor:pointer;transition:all .3s;display:none}}
.btn-retry:hover{{background:rgba(255,152,0,.1)}}
.ctrls{{display:flex;gap:9px;align-items:center;flex-wrap:wrap;justify-content:center}}

.done-card{{width:100%;max-width:660px;background:rgba(76,175,80,.08);
           border:1px solid rgba(76,175,80,.28);border-radius:11px;
           padding:16px;text-align:center;display:none}}
.done-card h3{{color:#4CAF50;font-size:1.1rem;margin-bottom:5px}}
.done-card p{{color:#bbb;font-size:.82rem;line-height:1.7}}

.err{{width:100%;max-width:660px;background:rgba(244,67,54,.08);
     border:1px solid rgba(244,67,54,.2);border-radius:9px;
     padding:9px 13px;color:#ff6b6b;font-size:.79rem;display:none}}
</style>
</head>
<body>

<div id="mode-badge" class="badge badge-free">🎙️ Free Voice Mode</div>

<div class="banner">
  <div>
    <div class="b-role">🎤 {job_role}</div>
    <div class="b-meta">Candidate: {candidate_name} · {total_q} questions</div>
  </div>
  <div class="timer" id="timer">00:00</div>
</div>

<div class="stage">
  <div class="av-wrap">
    <div class="av ai-bg" id="ai-av">🤖</div>
    <div class="wave g" id="ai-wave"><span></span><span></span><span></span><span></span><span></span></div>
    <div class="av-name">AI Interviewer</div>
  </div>
  <span class="vs">⟺</span>
  <div class="av-wrap">
    <div class="av usr-bg" id="usr-av">👤</div>
    <div class="wave b" id="usr-wave"><span></span><span></span><span></span><span></span><span></span></div>
    <div class="av-name">{candidate_name}</div>
  </div>
</div>

<div class="prog-wrap" id="prog-wrap">
  <div class="prog-top"><span id="prog-lbl">Starting…</span><span id="prog-frac">0 / {total_q}</span></div>
  <div class="prog-track"><div class="prog-fill" id="prog-fill"></div></div>
  <div class="dots" id="dots"></div>
</div>

<div class="chip c-idle" id="chip">
  <span class="cdot"></span><span id="chip-txt">Ready — click Start Interview</span>
</div>

<div class="sil-bar" id="sil-bar">
  <div class="sil-top"><span>Submitting in…</span><span id="sil-count">3.0s</span></div>
  <div class="sil-track"><div class="sil-fill" id="sil-fill"></div></div>
</div>

<div class="q-card" id="q-card">
  <div class="q-num" id="q-num">Question 1</div>
  <div class="q-txt" id="q-txt">…</div>
</div>

<div class="tx-panel" id="tx-panel">
  <div class="tx-head"><div class="live-dot"></div>Live Transcript</div>
  <div class="tx-body" id="tx-body"></div>
</div>

<div class="ctrls">
  <button class="btn-start" id="btn-start" onclick="startInterview()">🎙️ Start Interview</button>
  <button class="btn-retry" id="btn-retry" onclick="retryAnswer()">🔁 Re-answer</button>
  <button class="btn-end"   id="btn-end"   onclick="endEarly()">⏹ End Early</button>
</div>

<div class="done-card" id="done-card">
  <h3>✅ Interview Complete!</h3>
  <p id="done-msg">Sending your answers for AI evaluation…<br>
  <span style="color:#888;font-size:.75rem">Your full report will appear above shortly.</span></p>
</div>
<div class="err" id="err-box"></div>

<script>
const VAPI_TOKEN    = "{vapi_token}";
const ASSISTANT_ID  = "{vapi_assistant_id}";
const QUESTIONS     = {questions_js};
const TOTAL_Q       = {total_q};
const IV_ID         = {interview_id};
const CNAME         = "{candidate_name}";
const ROLE          = "{job_role}";
// Questions formatted for VAPI variableValues injection
const Q_LINES       = {questions_js}.map((q,i)=>(i+1)+'. '+q).join('\\n');

// ── Tuning ─────────────────────────────────────────────
const SILENCE_MS       = 3000;   // ms of quiet before submitting
const MIN_WORDS        = 8;      // silence only triggers above this
const VERY_SHORT_WORDS = 4;      // always prompt to elaborate if under this
const TICK_MS          = 100;

// ── State ──────────────────────────────────────────────
const S = {{
  messages:[],msgSet:new Set(),
  timerSec:0,timerH:null,
  isRunning:false,currentQ:0,currentAns:"",
  followUpCount:0,answerStartTs:0,
  allAnswers:[],answerDurations:[],
  silH:null,silBarH:null,silRem:SILENCE_MS,
  recog:null,synth:window.speechSynthesis,
  vapiObj:null,usingVapi:false,listeningActive:false
}};

// ── DOM ────────────────────────────────────────────────
const D={{
  aiAv:  document.getElementById('ai-av'),
  usrAv: document.getElementById('usr-av'),
  aiW:   document.getElementById('ai-wave'),
  usrW:  document.getElementById('usr-wave'),
  progW: document.getElementById('prog-wrap'),
  fill:  document.getElementById('prog-fill'),
  frac:  document.getElementById('prog-frac'),
  pLbl:  document.getElementById('prog-lbl'),
  dots:  document.getElementById('dots'),
  chip:  document.getElementById('chip'),
  chipT: document.getElementById('chip-txt'),
  qCard: document.getElementById('q-card'),
  qNum:  document.getElementById('q-num'),
  qTxt:  document.getElementById('q-txt'),
  txPan: document.getElementById('tx-panel'),
  txB:   document.getElementById('tx-body'),
  btnS:  document.getElementById('btn-start'),
  btnE:  document.getElementById('btn-end'),
  btnR:  document.getElementById('btn-retry'),
  doneC: document.getElementById('done-card'),
  err:   document.getElementById('err-box'),
  timerD:document.getElementById('timer'),
  badge: document.getElementById('mode-badge'),
  silBar:document.getElementById('sil-bar'),
  silFil:document.getElementById('sil-fill'),
  silCnt:document.getElementById('sil-count'),
}};

// ── Helpers ────────────────────────────────────────────
const setChip=(c,t)=>{{D.chip.className='chip '+c;D.chipT.textContent=t;}};
const showErr=(m)=>{{D.err.textContent='⚠️ '+m;D.err.style.display='block';}};
const hideErr=()=>{{D.err.style.display='none';}};
const wc=(t)=>t.trim().split(/\s+/).filter(w=>w.length>0).length;
const fp=(r,c)=>r+'::'+c.trim().slice(0,80);

function pushMsg(role,content) {{
  if(!content||!content.trim()) return;
  const key=fp(role,content);
  if(S.msgSet.has(key)) return;
  S.msgSet.add(key);
  if(role!=='sys') S.messages.push({{role,content:content.trim(),ts:new Date().toISOString()}});
  addBubble(role,content.trim(),false);
}}

function addBubble(role,content,isPartial,extraCls) {{
  const w=document.createElement('div');
  w.className='bbl '+(role==='ai'?'ai':role==='sys'?'sys':'usr');
  if(isPartial){{w.className+=' partial';w.id='pbbl';}}
  if(extraCls) w.className+=' '+extraCls;
  if(role!=='sys'){{
    const l=document.createElement('div');l.className='bbl-lbl';
    l.textContent=role==='ai'?'🤖 Interviewer':isPartial?'👤 You (speaking…)':'👤 You';
    w.appendChild(l);
  }}
  const t=document.createElement('div');t.textContent=content;w.appendChild(t);
  D.txB.appendChild(w);D.txB.scrollTop=D.txB.scrollHeight;
}}

function updatePartial(text) {{
  let pb=document.getElementById('pbbl');
  if(!pb){{addBubble('user','🎤 '+text,true);return;}}
  pb.querySelector('div:last-child').textContent='🎤 '+text;
  D.txB.scrollTop=D.txB.scrollHeight;
}}

function finalPartial() {{
  // Only remove the partial bubble — pushMsg will add the final one with dedup
  const pb=document.getElementById('pbbl');if(pb)pb.remove();
}}

function buildDots() {{
  D.dots.innerHTML='';
  for(let i=0;i<TOTAL_Q;i++){{
    const d=document.createElement('div');d.className='dot';d.id='d'+i;D.dots.appendChild(d);
  }}
}}

function upProg(n) {{
  D.fill.style.width=Math.round((n/TOTAL_Q)*100)+'%';
  D.frac.textContent=n+' / '+TOTAL_Q;
  D.pLbl.textContent=n>=TOTAL_Q?'✅ All answered!':'Question '+(n+1)+' of '+TOTAL_Q;
  for(let i=0;i<TOTAL_Q;i++){{
    const d=document.getElementById('d'+i);if(!d)continue;
    d.className=i<n?'dot done':i===n?'dot cur':'dot';
  }}
}}

function startTimer() {{
  S.timerH=setInterval(()=>{{
    S.timerSec++;
    D.timerD.textContent=String(Math.floor(S.timerSec/60)).padStart(2,'0')+':'+
                         String(S.timerSec%60).padStart(2,'0');
  }},1000);
}}

function showUI() {{
  D.progW.style.display='block';D.txPan.style.display='flex';
  D.btnS.style.display='none';D.btnE.style.display='block';
  buildDots();upProg(0);startTimer();
}}

// ── Silence bar ────────────────────────────────────────
function startSilBar(onExpire) {{
  stopSilBar();
  S.silRem=SILENCE_MS;
  D.silBar.style.display='block';
  S.silBarH=setInterval(()=>{{
    S.silRem-=TICK_MS;
    const pct=Math.max(0,100-(S.silRem/SILENCE_MS)*100);
    D.silFil.style.width=pct+'%';
    D.silCnt.textContent=Math.max(0,(S.silRem/1000).toFixed(1))+'s';
    if(S.silRem<=0){{stopSilBar();onExpire();}}
  }},TICK_MS);
}}

function stopSilBar() {{
  if(S.silBarH){{clearInterval(S.silBarH);S.silBarH=null;}}
  D.silBar.style.display='none';D.silFil.style.width='0%';
}}

// ── TTS ────────────────────────────────────────────────
function speak(text,onDone) {{
  S.synth.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.rate=0.91;u.pitch=1.04;u.volume=1.0;
  const voices=S.synth.getVoices();
  const v=voices.find(v=>v.lang.startsWith('en')&&
    (v.name.includes('Natural')||v.name.includes('Google')||
     v.name.includes('Samantha')||v.name.includes('US')))||
    voices.find(v=>v.lang.startsWith('en'))||voices[0];
  if(v)u.voice=v;
  D.aiAv.className='av ai-bg speaking';D.usrAv.className='av usr-bg';
  D.aiW.classList.add('on');D.usrW.classList.remove('on');
  setChip('c-speaking','🔊 AI is speaking…');
  u.onend=u.onerror=()=>{{
    D.aiAv.className='av ai-bg';D.aiW.classList.remove('on');if(onDone)onDone();
  }};
  S.synth.getVoices().length===0
    ?(window.speechSynthesis.onvoiceschanged=()=>S.synth.speak(u))
    :S.synth.speak(u);
}}

// ── STT with smart silence detection ──────────────────
function listenForAnswer(onResult) {{
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){{onResult('(Chrome or Edge required for voice)');return;}}
  if(S.recog){{try{{S.recog.stop();}}catch(e){{}}}}

  S.recog=new SR();
  S.recog.continuous=true;S.recog.interimResults=true;S.recog.lang='en-US';
  S.listeningActive=true;S.currentAns='';S.answerStartTs=Date.now();

  D.usrAv.className='av usr-bg listening';D.usrW.classList.add('on');
  D.aiAv.className='av ai-bg';D.aiW.classList.remove('on');
  D.btnR.style.display='block';
  setChip('c-listening','🎤 Listening… speak your answer');

  S.recog.onresult=e=>{{
    let interim='';
    for(let i=e.resultIndex;i<e.results.length;i++){{
      const t=e.results[i][0].transcript;
      if(e.results[i].isFinal){{
        S.currentAns+=' '+t;
        // User is still speaking — cancel any active silence countdown
        stopSilBar();
        setChip('c-waiting','⏳ Keep speaking or pause to submit…');
      }} else {{
        interim=t;
      }}
    }}
    updatePartial((S.currentAns+' '+interim).trim());
    // Only start silence bar once we have meaningful content
    if(S.currentAns.trim().split(/\s+/).length>=MIN_WORDS){{
      startSilBar(()=>{{if(S.listeningActive)S.recog.stop();}});
    }}
  }};

  S.recog.onspeechend=()=>{{
    stopSilBar();
    if(S.currentAns.trim().split(/\s+/).length>=MIN_WORDS){{
      startSilBar(()=>{{if(S.listeningActive)S.recog.stop();}});
    }}
  }};

  S.recog.onend=()=>{{
    if(!S.listeningActive)return;
    S.listeningActive=false;stopSilBar();
    D.usrAv.className='av usr-bg';D.usrW.classList.remove('on');D.btnR.style.display='none';
    const final=S.currentAns.trim();
    finalPartial(); // remove partial bubble only
    onResult(final||'(No answer captured)');
  }};

  S.recog.onerror=e=>{{
    if(!S.listeningActive)return;
    S.listeningActive=false;stopSilBar();
    D.usrAv.className='av usr-bg';D.usrW.classList.remove('on');D.btnR.style.display='none';
    const final=S.currentAns.trim();
    finalPartial(); // remove partial bubble only
    onResult(final||'(Mic error: '+e.error+')');
  }};

  S.recog.start();
}}

function retryAnswer() {{
  if(!S.isRunning)return;
  S.listeningActive=false;
  if(S.recog){{try{{S.recog.stop();}}catch(e){{}}}}
  stopSilBar();S.currentAns='';
  const pb=document.getElementById('pbbl');if(pb)pb.remove();
  addBubble('sys','🔄 Re-listening — speak your answer again',false);
  setTimeout(()=>listenForAnswer(ans=>processAnswer(ans)),400);
}}

// ── Answer validation + flow ───────────────────────────
const FOLLOWUPS=[
  "Could you elaborate a bit more on that?",
  "Can you give a specific example from your experience?",
  "That is a start — can you expand your answer?",
  "Tell me more about how you handled that.",
];

function processAnswer(ans) {{
  const words=wc(ans);
  const isReal=ans&&!ans.startsWith('(');

  if(!isReal||words<VERY_SHORT_WORDS){{
    if(S.followUpCount<1){{
      S.followUpCount++;
      D.aiAv.className='av ai-bg thinking';
      setChip('c-thinking','💭 Checking your answer…');
      setTimeout(()=>{{
        D.aiAv.className='av ai-bg';
        const fb="I did not quite catch that. "+FOLLOWUPS[S.currentQ%FOLLOWUPS.length];
        pushMsg('ai',fb);
        addBubble('sys','💡 Please elaborate your answer',false);
        setChip('c-followup','💬 Please elaborate…');
        speak(fb,()=>listenForAnswer(a2=>processAnswer(a2)));
      }},900);
      return;
    }}
  }}

  // Answer accepted
  pushMsg('user',ans);
  S.allAnswers[S.currentQ]=ans;
  S.answerDurations[S.currentQ]=Math.round((Date.now()-S.answerStartTs)/1000);
  S.followUpCount=0;
  upProg(S.currentQ+1);

  // Natural thinking pause
  D.aiAv.className='av ai-bg thinking';
  setChip('c-thinking','💭 Thinking…');
  const delay=600+Math.random()*700;

  setTimeout(()=>{{
    D.aiAv.className='av ai-bg';
    if(S.currentQ>=TOTAL_Q-1){{finishFree();return;}}
    const acks=["Thank you, that is helpful.","I see, good to know.","That makes sense.",
                "Understood, thank you.","Good, noted."];
    speak(acks[S.currentQ%acks.length],()=>setTimeout(()=>askQuestion(S.currentQ+1),450));
  }},delay);
}}

function askQuestion(idx) {{
  if(!S.isRunning)return;
  S.currentQ=idx;S.followUpCount=0;
  const q=QUESTIONS[idx];
  upProg(idx);
  D.qNum.textContent='Question '+(idx+1)+' of '+TOTAL_Q;
  D.qTxt.textContent=q;D.qCard.style.display='block';
  pushMsg('ai',q);
  setChip('c-speaking','🔊 Question '+(idx+1)+'…');
  speak(q,()=>{{
    setChip('c-listening','🎤 Your turn — answer Q'+(idx+1));
    listenForAnswer(ans=>processAnswer(ans));
  }});
}}

function finishFree() {{
  S.isRunning=false;clearInterval(S.timerH);stopSilBar();
  D.btnE.style.display='none';D.btnR.style.display='none';
  D.aiAv.className='av ai-bg';D.usrAv.className='av usr-bg';
  const closing='Thank you '+CNAME+', that completes all '+TOTAL_Q+
    ' questions of your mock interview for the '+ROLE+' position. '+
    'Your answers have been recorded and our AI will now evaluate your performance. '+
    'You will see your detailed results in just a moment. Best of luck!';
  setChip('c-done','✅ Interview complete — evaluating…');
  upProg(TOTAL_Q);
  speak(closing,()=>{{D.doneC.style.display='block';sendResults();}});
}}

function startFreeMode() {{
  D.badge.className='badge badge-free';D.badge.textContent='🎙️ Free Voice Mode';
  S.isRunning=true;showUI();S.synth.getVoices();
  const greeting='Hello '+CNAME+'! Welcome to your mock interview for the '+ROLE+
    ' position. I will ask you '+TOTAL_Q+' questions. Take your time — I will wait '+
    'until you finish speaking before moving on. Let us begin.';
  setChip('c-speaking','🔊 AI is greeting you…');
  speak(greeting,()=>setTimeout(()=>askQuestion(0),500));
}}

// ── VAPI path — uses pre-built assistant via ID + overrides ──
async function tryVapi() {{
  await loadScript('https://cdn.jsdelivr.net/npm/@vapi-ai/web@2.3.8/dist/vapi.iife.js');
  S.vapiObj=new window.Vapi(VAPI_TOKEN);

  S.vapiObj.on('call-start',()=>{{
    S.usingVapi=true;
    D.badge.className='badge badge-vapi';D.badge.textContent='⚡ VAPI · Clara Voice';
    showUI();setChip('c-speaking','🔊 AI Interviewer speaking…');
  }});

  S.vapiObj.on('call-end',()=>{{
    clearInterval(S.timerH);D.btnE.style.display='none';
    D.aiAv.className='av ai-bg';D.usrAv.className='av usr-bg';
    D.aiW.classList.remove('on');D.usrW.classList.remove('on');
    setChip('c-done','✅ Interview complete');
    D.doneC.style.display='block';sendResults();
  }});

  S.vapiObj.on('speech-start',()=>{{
    D.aiAv.className='av ai-bg speaking';D.usrAv.className='av usr-bg';
    D.aiW.classList.add('on');D.usrW.classList.remove('on');
    setChip('c-speaking','🔊 AI is speaking…');
  }});

  S.vapiObj.on('speech-end',()=>{{
    D.aiAv.className='av ai-bg';D.aiW.classList.remove('on');
    D.usrAv.className='av usr-bg listening';D.usrW.classList.add('on');
    setChip('c-listening','🎤 Listening to you…');
  }});

  S.vapiObj.on('message',msg=>{{
    if(msg.type==='transcript'&&msg.transcriptType==='partial'){{
      if(msg.role==='user') updatePartial(msg.transcript);
    }}
    if(msg.type==='transcript'&&msg.transcriptType==='final'){{
      const key=fp(msg.role==='assistant'?'ai':'user',msg.transcript);
      if(S.msgSet.has(key)) return;  // STRICT DEDUP
      S.msgSet.add(key);
      const cleanRole=msg.role==='assistant'?'ai':'user';
      S.messages.push({{role:cleanRole,content:msg.transcript.trim(),ts:new Date().toISOString()}});

      if(cleanRole==='user'){{
        finalPartial(); // remove partial bubble
        addBubble('user',msg.transcript.trim(),false); // add final bubble ONCE (deduped by msgSet above)
        const answered=S.messages.filter(m=>m.role==='user').length;
        upProg(Math.min(answered,TOTAL_Q));
        D.usrAv.className='av usr-bg';D.usrW.classList.remove('on');
        D.aiAv.className='av ai-bg thinking';
        setChip('c-thinking','💭 AI thinking…');
        setTimeout(()=>{{D.aiAv.className='av ai-bg';}},800);
      }} else {{
        addBubble('ai',msg.transcript.trim(),false);
        const aiMsgs=S.messages.filter(m=>m.role==='ai');
        const qi=aiMsgs.length-1;
        if(qi<TOTAL_Q){{
          D.qNum.textContent='Question '+(qi+1)+' of '+TOTAL_Q;
          D.qTxt.textContent=QUESTIONS[qi];
          D.qCard.style.display='block';upProg(qi);
        }}
      }}
    }}
  }});

  S.vapiObj.on('error',err=>{{
    console.warn('VAPI:',err);
    if(!S.usingVapi){{
      S.vapiObj=null;
      showErr('VAPI failed — switching to free mode…');
      setTimeout(()=>{{hideErr();startFreeMode();}},2000);
    }}
  }});

  // Start using pre-built assistant ID — inject questions + username at runtime
  await S.vapiObj.start(ASSISTANT_ID, {{
    assistantOverrides: {{
      variableValues: {{
        username   : CNAME,
        job_role   : ROLE,
        questions  : Q_LINES,
        total_q    : String(TOTAL_Q),
        first_q    : QUESTIONS[0] || ''
      }},
      // Ensure it ends after all questions — append our end phrases
      endCallPhrases: [
        'that completes our interview',
        'interview is now complete',
        'we will review your answers',
        'have a great day'
      ]
    }}
  }});
}}

// ── Send results to Streamlit ──────────────────────────
function sendResults() {{
  const userMsgs=S.messages.filter(m=>m.role==='user');
  const payload={{type:'interview_complete',interview_id:IV_ID,
    messages:S.messages,q_answered:userMsgs.length,
    duration_sec:S.timerSec,answer_durations:S.answerDurations,
    timestamp:new Date().toISOString()}};
  const str=JSON.stringify(payload);

  // Update done card first
  document.getElementById('done-msg').innerHTML=
    '<b style="color:#4CAF50">'+userMsgs.length+' answers captured.</b><br>'+
    '<span style="color:#aaa;font-size:.78rem">Redirecting to evaluation… please wait.</span>';

  // Write to storage as backup
  try{{
    sessionStorage.setItem('iv_result_'+IV_ID,str);
    sessionStorage.setItem('iv_ready','1');
    localStorage.setItem('iv_result_'+IV_ID,str);
    localStorage.setItem('iv_ready','1');
  }}catch(e){{console.warn('Storage write:',e);}}

  // PRIMARY: Navigate window.top directly to trigger Streamlit rerun
  // This is the most reliable method — fires after a short delay to
  // let the done card render first
  setTimeout(function(){{
    try{{
      var base = window.top.location.href.split('?')[0];
      var msgs = encodeURIComponent(JSON.stringify(S.messages));
      window.top.location.href = base + '?iv_done=' + IV_ID + '&iv_data=' + msgs;
    }}catch(e){{
      // Cross-origin fallback: postMessage then storage poll
      try{{window.parent.postMessage(payload,'*');}}catch(e2){{}}
      try{{window.top.postMessage(payload,'*');}}catch(e2){{}}
      document.getElementById('done-msg').innerHTML=
        '<b style="color:#4CAF50">'+userMsgs.length+' answers captured.</b><br>'+
        '<span style="color:#aaa;font-size:.76rem">Scroll up and click Evaluate Manually if the report does not appear automatically.</span>';
    }}
  }}, 2200);
}}

// ── Entry ──────────────────────────────────────────────
async function startInterview() {{
  hideErr();D.btnS.disabled=true;D.btnS.textContent='Starting…';
  if(VAPI_TOKEN&&VAPI_TOKEN.length>10){{
    setChip('c-thinking','⚡ Connecting to VAPI…');
    try{{await tryVapi();}}
    catch(err){{
      console.warn('VAPI failed:',err);
      showErr('VAPI: '+err.message+'. Using free mode…');
      setTimeout(()=>{{hideErr();startFreeMode();}},2000);
    }}
  }} else {{
    startFreeMode();
  }}
}}

function endEarly() {{
  if(S.usingVapi&&S.vapiObj){{try{{S.vapiObj.stop();}}catch(e){{}}return;}}
  S.isRunning=false;S.listeningActive=false;
  S.synth.cancel();if(S.recog){{try{{S.recog.stop();}}catch(e){{}}}}
  stopSilBar();clearInterval(S.timerH);
  D.btnE.style.display='none';D.btnR.style.display='none';
  setChip('c-done','Ended — evaluating answers…');
  D.doneC.style.display='block';sendResults();
}}

function loadScript(src) {{
  return new Promise((res,rej)=>{{
    if(document.querySelector('script[src="'+src+'"]')){{res();return;}}
    const s=document.createElement('script');s.src=src;s.onload=res;
    s.onerror=()=>rej(new Error('Load failed: '+src));document.head.appendChild(s);
  }});
}}

if(S.synth.onvoiceschanged!==undefined)S.synth.onvoiceschanged=()=>S.synth.getVoices();
S.synth.getVoices();
</script>
</body>
</html>"""
    return HTML
