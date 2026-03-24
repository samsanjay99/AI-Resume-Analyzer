"""
interview_standalone.py
Generates a self-contained interview HTML page that is served by Streamlit's
static file server at a real HTTP origin (e.g. http://localhost:8501/app/static/).

WHY THIS EXISTS:
  Streamlit's components.html() renders inside an `about:srcdoc` sandboxed iframe.
  VAPI/Daily.co uses postMessage between iframes and requires a real HTTP origin.
  `about:srcdoc` has origin = null → Daily.co's postMessage fails → VAPI never connects.

HOW IT WORKS:
  1. Python writes the HTML to ./static/interview_{id}.html
  2. Streamlit serves it at http://localhost:8501/app/static/interview_{id}.html
  3. User opens that URL in a new browser tab (real origin → VAPI works)
  4. On interview end, the popup does:
       window.opener.location.href = streamlit_base + '?iv_done=ID&iv_data=TRANSCRIPT'
       window.close()
  5. The Streamlit tab reloads with those URL params
  6. Python reads st.query_params and transitions to the evaluating phase
"""

import json
import os


def build_standalone_html(
    questions: list,
    job_role: str,
    candidate_name: str,
    interview_id: int,
    vapi_token: str,
    vapi_assistant_id: str,
    streamlit_base_url: str = "",  # unused — JS uses window.location.origin instead
) -> str:
    """
    Returns a complete standalone HTML string.
    Normal Python strings (single braces) — not f-string with escaped JS braces.
    """
    total_q       = len(questions)
    questions_js  = json.dumps(questions)
    q_lines       = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
    first_q       = questions[0] if questions else "Tell me about yourself."

    # Escape for safe embedding in JS string literals
    cname_js   = candidate_name.replace("'", "\\'").replace('"', '\\"')
    role_js    = job_role.replace("'", "\\'").replace('"', '\\"')
    q_lines_js = q_lines.replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")
    first_q_js = first_q.replace("'", "\\'").replace('"', '\\"')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Interview — {job_role}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%}}
body{{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:#0d0d1a;color:#fff;
  display:flex;flex-direction:column;align-items:center;
  padding:20px 16px;gap:14px;min-height:100vh;
  overflow-y:auto;
}}

.badge{{padding:3px 13px;border-radius:20px;font-size:.7rem;font-weight:700;
       text-transform:uppercase;letter-spacing:.5px;align-self:flex-start;
       transition:all .3s}}
.badge-wait{{background:rgba(255,152,0,.15);color:#FF9800;border:1px solid #FF9800}}
.badge-vapi{{background:rgba(103,78,234,.2);color:#a78bfa;border:1px solid #7c3aed}}
.badge-free{{background:rgba(76,175,80,.14);color:#4CAF50;border:1px solid #388E3C}}

.banner{{width:100%;max-width:680px;background:linear-gradient(135deg,#1a1a3e,#16213e);
        border:1px solid rgba(76,175,80,.3);border-radius:12px;
        padding:12px 18px;display:flex;justify-content:space-between;align-items:center}}
.b-role{{color:#4CAF50;font-size:.96rem;font-weight:700;margin-bottom:2px}}
.b-meta{{color:#888;font-size:.73rem}}
.timer{{color:#4CAF50;font-size:.98rem;font-weight:700;font-variant-numeric:tabular-nums}}

/* ── Avatars ── */
.stage{{display:flex;align-items:center;justify-content:center;gap:40px;
       width:100%;max-width:680px}}
.av-wrap{{display:flex;flex-direction:column;align-items:center;gap:8px}}
.av{{width:84px;height:84px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:2.1rem;border:3px solid #1e1e2e;transition:all .3s}}
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

/* ── Progress ── */
.prog-wrap{{width:100%;max-width:680px;display:none}}
.prog-top{{display:flex;justify-content:space-between;font-size:.72rem;color:#888;margin-bottom:4px}}
.prog-track{{width:100%;height:6px;background:rgba(255,255,255,.07);border-radius:4px;overflow:hidden}}
.prog-fill{{height:100%;border-radius:4px;
           background:linear-gradient(90deg,#4CAF50,#81C784);
           transition:width .5s ease;width:0%}}
.dots{{display:flex;gap:5px;margin-top:6px;flex-wrap:wrap}}
.dot{{width:9px;height:9px;border-radius:50%;background:rgba(255,255,255,.1);transition:all .4s}}
.dot.done{{background:#4CAF50}}.dot.cur{{background:#FF9800;animation:db .7s ease infinite alternate}}
@keyframes db{{from{{transform:scale(1)}}to{{transform:scale(1.5)}}}}

/* ── Chip ── */
.chip{{display:inline-flex;align-items:center;gap:6px;padding:5px 13px;
      border-radius:20px;font-size:.77rem;font-weight:600;transition:all .3s}}
.c-idle    {{background:rgba(255,255,255,.07);color:#aaa}}
.c-speaking{{background:rgba(76,175,80,.14);color:#4CAF50}}
.c-listening{{background:rgba(33,150,243,.14);color:#42A5F5}}
.c-thinking{{background:rgba(255,152,0,.14);color:#FF9800}}
.c-waiting {{background:rgba(255,235,59,.12);color:#FDD835}}
.c-followup{{background:rgba(156,39,176,.14);color:#CE93D8}}
.c-done    {{background:rgba(33,150,243,.14);color:#42A5F5}}
.cdot{{width:7px;height:7px;border-radius:50%;background:currentColor}}

/* ── Silence bar ── */
.sil-bar{{width:100%;max-width:680px;display:none}}
.sil-top{{display:flex;justify-content:space-between;font-size:.7rem;color:#888;margin-bottom:3px}}
.sil-track{{width:100%;height:4px;background:rgba(255,255,255,.06);border-radius:3px}}
.sil-fill{{height:100%;border-radius:3px;width:0%;
          background:linear-gradient(90deg,#FDD835,#FF9800);transition:width .1s linear}}

/* ── Question card ── */
.q-card{{width:100%;max-width:680px;background:rgba(255,255,255,.04);
        border:1px solid rgba(255,255,255,.09);border-radius:11px;
        padding:12px 16px;display:none}}
.q-num{{font-size:.67rem;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px}}
.q-txt{{font-size:.91rem;color:#e8e8e8;line-height:1.6}}

/* ── Transcript ── */
.tx-panel{{width:100%;max-width:680px;background:rgba(255,255,255,.03);
          border:1px solid rgba(255,255,255,.07);border-radius:11px;overflow:hidden;
          max-height:220px;display:none;flex-direction:column}}
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

/* ── Controls ── */
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

/* ── Done card ── */
.done-card{{width:100%;max-width:680px;background:rgba(76,175,80,.08);
           border:1px solid rgba(76,175,80,.28);border-radius:11px;
           padding:18px;text-align:center;display:none}}
.done-card h3{{color:#4CAF50;font-size:1.1rem;margin-bottom:5px}}
.done-card p{{color:#bbb;font-size:.82rem;line-height:1.7}}

/* ── Error ── */
.err{{width:100%;max-width:680px;background:rgba(244,67,54,.08);
     border:1px solid rgba(244,67,54,.2);border-radius:9px;
     padding:9px 13px;color:#ff6b6b;font-size:.79rem;display:none}}
</style>
</head>
<body>

<div id="mode-badge" class="badge badge-wait">⏳ Initialising…</div>

<div class="banner">
  <div>
    <div class="b-role">🎤 {job_role}</div>
    <div class="b-meta">Candidate: {candidate_name} &nbsp;·&nbsp; {total_q} questions</div>
  </div>
  <div class="timer" id="timer">00:00</div>
</div>

<div class="stage">
  <div class="av-wrap">
    <div class="av ai-bg" id="ai-av">🤖</div>
    <div class="wave g" id="ai-wave">
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <div class="av-name">AI Interviewer</div>
  </div>
  <span class="vs">⟺</span>
  <div class="av-wrap">
    <div class="av usr-bg" id="usr-av">👤</div>
    <div class="wave b" id="usr-wave">
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <div class="av-name">{candidate_name}</div>
  </div>
</div>

<div class="prog-wrap" id="prog-wrap">
  <div class="prog-top">
    <span id="prog-lbl">Starting…</span>
    <span id="prog-frac">0 / {total_q}</span>
  </div>
  <div class="prog-track"><div class="prog-fill" id="prog-fill"></div></div>
  <div class="dots" id="dots"></div>
</div>

<div class="chip c-idle" id="chip">
  <span class="cdot"></span>
  <span id="chip-txt">Ready — click Start Interview</span>
</div>

<div class="sil-bar" id="sil-bar">
  <div class="sil-top">
    <span>Submitting in…</span>
    <span id="sil-count">3.0s</span>
  </div>
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
  <button class="btn-start" id="btn-start" onclick="startInterview()">
    🎙️ Start Interview
  </button>
  <button class="btn-retry" id="btn-retry" onclick="retryAnswer()">🔁 Re-answer</button>
  <button class="btn-end"   id="btn-end"   onclick="endEarly()">⏹ End Early</button>
</div>

<div class="done-card" id="done-card">
  <h3>✅ Interview Complete!</h3>
  <p id="done-msg">
    Sending your answers for evaluation…<br>
    <span style="color:#888;font-size:.75rem">
      This window will close and your results will appear in the main app.
    </span>
  </p>
</div>

<div class="err" id="err-box"></div>

<script type="module">
// ═══════════════════════════════════════════════════════
// CONFIG — injected by Python at generation time
// ═══════════════════════════════════════════════════════
const VAPI_TOKEN   = '{vapi_token}';
const ASSISTANT_ID = '{vapi_assistant_id}';
const QUESTIONS    = {questions_js};
const TOTAL_Q      = {total_q};
const IV_ID        = {interview_id};
const CNAME        = '{cname_js}';
const ROLE         = '{role_js}';
const Q_LINES      = '{q_lines_js}';
const FIRST_Q      = '{first_q_js}';
// Streamlit base URL — derived from where THIS page is hosted.
// Since this file is served by Streamlit at /app/static/interview_ID.html,
// window.location.origin gives us exactly http://localhost:8501 (or cloud URL).
// This is always correct — no Python computation needed.
const STREAMLIT_BASE = window.location.origin;

// ═══════════════════════════════════════════════════════
// TUNING
// ═══════════════════════════════════════════════════════
const SILENCE_MS       = 3000;
const MIN_WORDS        = 8;
const VERY_SHORT_WORDS = 4;
const TICK_MS          = 100;

// ═══════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════
const S = {{
  messages:[],msgSet:new Set(),
  timerSec:0,timerH:null,
  isRunning:false,currentQ:0,currentAns:'',
  followUpCount:0,answerStartTs:0,
  allAnswers:[],answerDurations:[],
  silH:null,silBarH:null,silRem:SILENCE_MS,
  recog:null,synth:window.speechSynthesis,
  vapiObj:null,usingVapi:false,listeningActive:false
}};

// ═══════════════════════════════════════════════════════
// DOM
// ═══════════════════════════════════════════════════════
const D = {{
  aiAv : document.getElementById('ai-av'),
  usrAv: document.getElementById('usr-av'),
  aiW  : document.getElementById('ai-wave'),
  usrW : document.getElementById('usr-wave'),
  progW: document.getElementById('prog-wrap'),
  fill : document.getElementById('prog-fill'),
  frac : document.getElementById('prog-frac'),
  pLbl : document.getElementById('prog-lbl'),
  dots : document.getElementById('dots'),
  chip : document.getElementById('chip'),
  chipT: document.getElementById('chip-txt'),
  qCard: document.getElementById('q-card'),
  qNum : document.getElementById('q-num'),
  qTxt : document.getElementById('q-txt'),
  txPan: document.getElementById('tx-panel'),
  txB  : document.getElementById('tx-body'),
  btnS : document.getElementById('btn-start'),
  btnE : document.getElementById('btn-end'),
  btnR : document.getElementById('btn-retry'),
  doneC: document.getElementById('done-card'),
  err  : document.getElementById('err-box'),
  timerD:document.getElementById('timer'),
  badge: document.getElementById('mode-badge'),
  silBar:document.getElementById('sil-bar'),
  silFil:document.getElementById('sil-fill'),
  silCnt:document.getElementById('sil-count'),
}};

// ═══════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════
const setChip = (c,t) => {{ D.chip.className='chip '+c; D.chipT.textContent=t; }};
const showErr = (m) => {{ D.err.textContent='⚠️ '+m; D.err.style.display='block'; }};
const hideErr = () => {{ D.err.style.display='none'; }};
const wc      = (t) => t.trim().split(/\s+/).filter(w=>w.length>0).length;
const fp      = (r,c) => r+'::'+c.trim().slice(0,80);

function pushMsg(role, content) {{
  if (!content || !content.trim()) return;
  const key = fp(role, content);
  if (S.msgSet.has(key)) return;
  S.msgSet.add(key);
  if (role !== 'sys') S.messages.push({{role, content:content.trim(), ts:new Date().toISOString()}});
  addBubble(role, content.trim(), false);
}}

function addBubble(role, content, isPartial) {{
  const w = document.createElement('div');
  w.className = 'bbl ' + (role==='ai'?'ai':role==='sys'?'sys':'usr');
  if (isPartial) {{ w.className += ' partial'; w.id = 'pbbl'; }}
  if (role !== 'sys') {{
    const l = document.createElement('div'); l.className = 'bbl-lbl';
    l.textContent = role==='ai' ? '🤖 Interviewer' : isPartial ? '👤 You (speaking…)' : '👤 You';
    w.appendChild(l);
  }}
  const t = document.createElement('div'); t.textContent = content; w.appendChild(t);
  D.txB.appendChild(w); D.txB.scrollTop = D.txB.scrollHeight;
}}

function updatePartial(text) {{
  let pb = document.getElementById('pbbl');
  if (!pb) {{ addBubble('user', '🎤 '+text, true); return; }}
  pb.querySelector('div:last-child').textContent = '🎤 '+text;
  D.txB.scrollTop = D.txB.scrollHeight;
}}

function finalPartial() {{
  const pb = document.getElementById('pbbl'); if (pb) pb.remove();
}}

function buildDots() {{
  D.dots.innerHTML = '';
  for (let i=0; i<TOTAL_Q; i++) {{
    const d = document.createElement('div'); d.className='dot'; d.id='d'+i;
    D.dots.appendChild(d);
  }}
}}

function upProg(n) {{
  D.fill.style.width = Math.round((n/TOTAL_Q)*100)+'%';
  D.frac.textContent = n+' / '+TOTAL_Q;
  D.pLbl.textContent = n>=TOTAL_Q ? '✅ All answered!' : 'Question '+(n+1)+' of '+TOTAL_Q;
  for (let i=0; i<TOTAL_Q; i++) {{
    const d = document.getElementById('d'+i); if (!d) continue;
    d.className = i<n ? 'dot done' : i===n ? 'dot cur' : 'dot';
  }}
}}

function startTimer() {{
  S.timerH = setInterval(() => {{
    S.timerSec++;
    D.timerD.textContent =
      String(Math.floor(S.timerSec/60)).padStart(2,'0')+':'+
      String(S.timerSec%60).padStart(2,'0');
  }}, 1000);
}}

function showUI() {{
  D.progW.style.display = 'block';
  D.txPan.style.display = 'flex';
  D.btnS.style.display  = 'none';
  D.btnE.style.display  = 'block';
  buildDots(); upProg(0); startTimer();
}}

// ── Silence bar ─────────────────────────────────────────
function startSilBar(onExpire) {{
  stopSilBar();
  S.silRem = SILENCE_MS;
  D.silBar.style.display = 'block';
  S.silBarH = setInterval(() => {{
    S.silRem -= TICK_MS;
    const pct = Math.max(0, 100-(S.silRem/SILENCE_MS)*100);
    D.silFil.style.width = pct+'%';
    D.silCnt.textContent = Math.max(0,(S.silRem/1000).toFixed(1))+'s';
    if (S.silRem<=0) {{ stopSilBar(); onExpire(); }}
  }}, TICK_MS);
}}

function stopSilBar() {{
  if (S.silBarH) {{ clearInterval(S.silBarH); S.silBarH=null; }}
  D.silBar.style.display = 'none';
  D.silFil.style.width   = '0%';
}}

// ═══════════════════════════════════════════════════════
// SEND RESULTS BACK TO STREAMLIT
// Strategy (in order):
//  1. window.opener.location.href  — works when opened via target="_blank" link
//  2. window.location.href         — navigates THIS tab to Streamlit (always works)
//  3. localStorage                 — last-resort signal for Streamlit to read
// ═══════════════════════════════════════════════════════
function sendResults() {{
  const userMsgs = S.messages.filter(m => m.role === 'user');

  if (userMsgs.length === 0) {{
    document.getElementById('done-msg').innerHTML =
      '<b style="color:#FF9800">No answers were captured.</b><br>'+
      '<span style="color:#aaa;font-size:.75rem">Please use the manual fallback in the main app tab.</span>';
    return;
  }}

  document.getElementById('done-msg').innerHTML =
    '<b style="color:#4CAF50">'+userMsgs.length+' answer'+
    (userMsgs.length!==1?'s':'')+' captured!</b><br>'+
    '<span style="color:#aaa;font-size:.75rem">Sending results to the main app…</span>';

  // Build the Streamlit return URL.
  // window.location.origin = http://localhost:8501 (same server, always correct)
  const msgsJson  = JSON.stringify(S.messages);
  const encoded   = encodeURIComponent(msgsJson);
  // window.location.origin = http://localhost:8501 (the Streamlit server)
  // The Streamlit app always lives at the root path /
  const returnUrl = window.location.origin + '/?iv_done={interview_id}&iv_data=' + encoded;

  // ── Strategy A: localStorage (most reliable, no navigation needed) ────
  // Streamlit page has an inline JS that checks localStorage every 10s (via st.rerun).
  // Write FIRST before any navigation attempts.
  try {{
    localStorage.setItem('iv_result_{interview_id}', msgsJson);
    localStorage.setItem('iv_done_id', '{interview_id}');
    console.log('[Interview] Results written to localStorage');
  }} catch(e) {{ console.warn('[Interview] localStorage failed:', e); }}

  // ── Strategy B: window.opener (only available if opened via window.open()) ─
  let usedOpener = false;
  try {{
    if (window.opener && !window.opener.closed) {{
      window.opener.location.href = returnUrl;
      usedOpener = true;
      console.log('[Interview] Navigated opener tab to results');
      setTimeout(() => {{ try {{ window.close(); }} catch(e) {{}} }}, 2500);
    }}
  }} catch(e) {{ console.warn('[Interview] opener failed:', e); }}

  // ── Strategy C: navigate THIS tab to Streamlit with results ──────────────
  // Always works — this tab becomes the results page.
  // Runs whether or not opener succeeded (opener might be Streamlit waiting tab).
  if (!usedOpener) {{
    setTimeout(() => {{
      document.getElementById('done-msg').innerHTML =
        '<b style="color:#4CAF50">'+userMsgs.length+' answers captured!</b><br>'+
        '<span style="color:#aaa;font-size:.76rem">Taking you to your results now…</span>';
      window.location.href = returnUrl;
    }}, 2000);
  }}
}}

// ═══════════════════════════════════════════════════════
// FREE-MODE TTS
// ═══════════════════════════════════════════════════════
function speak(text, onDone) {{
  S.synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.rate=0.91; u.pitch=1.04; u.volume=1.0;
  const voices = S.synth.getVoices();
  const v = voices.find(v => v.lang.startsWith('en') &&
    (v.name.includes('Natural')||v.name.includes('Google')||
     v.name.includes('Samantha')||v.name.includes('US'))) ||
    voices.find(v => v.lang.startsWith('en')) || voices[0];
  if (v) u.voice = v;
  D.aiAv.className='av ai-bg speaking'; D.usrAv.className='av usr-bg';
  D.aiW.classList.add('on'); D.usrW.classList.remove('on');
  setChip('c-speaking','🔊 AI is speaking…');
  u.onend = u.onerror = () => {{
    D.aiAv.className='av ai-bg'; D.aiW.classList.remove('on'); if (onDone) onDone();
  }};
  S.synth.getVoices().length===0
    ? (window.speechSynthesis.onvoiceschanged = () => S.synth.speak(u))
    : S.synth.speak(u);
}}

// ═══════════════════════════════════════════════════════
// FREE-MODE STT WITH SMART SILENCE DETECTION
// ═══════════════════════════════════════════════════════
function listenForAnswer(onResult) {{
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {{
    // Speech recognition not available - show error and stop
    showErr('⚠️ Speech recognition not available. Please use Chrome or Edge browser.');
    S.isRunning = false;
    D.btnE.style.display = 'none';
    D.btnR.style.display = 'none';
    setChip('c-idle', '❌ Browser not supported');
    return;
  }}
  if (S.recog) {{ try {{ S.recog.stop(); }} catch(e) {{}} }}

  S.recog = new SR();
  S.recog.continuous=true; S.recog.interimResults=true; S.recog.lang='en-US';
  S.listeningActive=true; S.currentAns=''; S.answerStartTs=Date.now();

  D.usrAv.className='av usr-bg listening'; D.usrW.classList.add('on');
  D.aiAv.className='av ai-bg'; D.aiW.classList.remove('on');
  D.btnR.style.display='block';
  setChip('c-listening','🎤 Listening… speak your answer');

  S.recog.onresult = e => {{
    let interim = '';
    for (let i=e.resultIndex; i<e.results.length; i++) {{
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) {{ S.currentAns+=' '+t; stopSilBar(); }}
      else interim = t;
    }}
    updatePartial((S.currentAns+' '+interim).trim());
    if (S.currentAns.trim().split(/\s+/).length >= MIN_WORDS) {{
      setChip('c-waiting','⏳ Keep speaking or pause to submit…');
      startSilBar(() => {{ if (S.listeningActive) S.recog.stop(); }});
    }}
  }};

  S.recog.onspeechend = () => {{
    stopSilBar();
    if (S.currentAns.trim().split(/\s+/).length >= MIN_WORDS)
      startSilBar(() => {{ if (S.listeningActive) S.recog.stop(); }});
  }};

  S.recog.onend = () => {{
    if (!S.listeningActive) return;
    S.listeningActive=false; stopSilBar();
    D.usrAv.className='av usr-bg'; D.usrW.classList.remove('on'); D.btnR.style.display='none';
    const final = S.currentAns.trim();
    finalPartial(); onResult(final || '(No answer captured)');
  }};

  S.recog.onerror = e => {{
    if (!S.listeningActive) return;
    S.listeningActive=false; stopSilBar();
    D.usrAv.className='av usr-bg'; D.usrW.classList.remove('on'); D.btnR.style.display='none';
    const final = S.currentAns.trim();
    finalPartial(); onResult(final || '(Mic error: '+e.error+')');
  }};

  S.recog.start();
}}

function retryAnswer() {{
  if (!S.isRunning) return;
  S.listeningActive=false;
  if (S.recog) {{ try {{ S.recog.stop(); }} catch(e) {{}} }}
  stopSilBar(); S.currentAns='';
  const pb = document.getElementById('pbbl'); if (pb) pb.remove();
  addBubble('sys','🔄 Re-listening — speak your answer again',false);
  setTimeout(() => listenForAnswer(ans => processAnswer(ans)), 400);
}}

// ═══════════════════════════════════════════════════════
// ANSWER VALIDATION + FLOW CONTROL
// ═══════════════════════════════════════════════════════
const FOLLOWUPS = [
  'Could you elaborate a bit more on that?',
  'Can you give a specific example?',
  'Tell me a little more about that.',
  'That is a start — can you expand on your answer?',
];

function processAnswer(ans) {{
  const words = wc(ans);
  const isReal = ans && !ans.startsWith('(');

  if (!isReal || words < VERY_SHORT_WORDS) {{
    if (S.followUpCount < 1) {{
      S.followUpCount++;
      D.aiAv.className='av ai-bg thinking';
      setChip('c-thinking','💭 Checking answer…');
      setTimeout(() => {{
        D.aiAv.className='av ai-bg';
        const fb = 'I did not quite catch that. '+FOLLOWUPS[S.currentQ % FOLLOWUPS.length];
        pushMsg('ai', fb);
        addBubble('sys','💡 Please elaborate your answer',false);
        setChip('c-followup','💬 Please elaborate…');
        speak(fb, () => listenForAnswer(a2 => processAnswer(a2)));
      }}, 900);
      return;
    }}
  }}

  pushMsg('user', ans);
  S.allAnswers[S.currentQ] = ans;
  S.answerDurations[S.currentQ] = Math.round((Date.now()-S.answerStartTs)/1000);
  S.followUpCount = 0;
  upProg(S.currentQ+1);

  D.aiAv.className='av ai-bg thinking';
  setChip('c-thinking','💭 Thinking…');
  const delay = 600 + Math.random()*700;

  setTimeout(() => {{
    D.aiAv.className='av ai-bg';
    if (S.currentQ >= TOTAL_Q-1) {{ finishFree(); return; }}
    const acks = ['Thank you, that is helpful.','I see, good to know.',
                  'That makes sense.','Understood, thank you.','Good, noted.'];
    speak(acks[S.currentQ % acks.length], () =>
      setTimeout(() => askQuestion(S.currentQ+1), 450));
  }}, delay);
}}

function askQuestion(idx) {{
  if (!S.isRunning) return;
  S.currentQ=idx; S.followUpCount=0;
  const q = QUESTIONS[idx];
  upProg(idx);
  D.qNum.textContent='Question '+(idx+1)+' of '+TOTAL_Q;
  D.qTxt.textContent=q; D.qCard.style.display='block';
  pushMsg('ai', q);
  setChip('c-speaking','🔊 Question '+(idx+1)+'…');
  speak(q, () => {{
    setChip('c-listening','🎤 Your turn — answer Q'+(idx+1));
    listenForAnswer(ans => processAnswer(ans));
  }});
}}

function finishFree() {{
  S.isRunning=false; clearInterval(S.timerH); stopSilBar();
  D.btnE.style.display='none'; D.btnR.style.display='none';
  D.aiAv.className='av ai-bg'; D.usrAv.className='av usr-bg';
  const closing = 'Thank you '+CNAME+', that completes all '+TOTAL_Q+
    ' questions of your mock interview for the '+ROLE+' position. '+
    'Your answers have been recorded. Your evaluation results will appear in the main app shortly. Best of luck!';
  setChip('c-done','✅ Interview complete — sending results…');
  upProg(TOTAL_Q);
  speak(closing, () => {{ D.doneC.style.display='block'; sendResults(); }});
}}

function startFreeMode() {{
  D.badge.className='badge badge-free';
  D.badge.textContent='🎙️ Free Voice Mode';
  S.isRunning=true; showUI(); S.synth.getVoices();
  const greeting = 'Hello '+CNAME+'! Welcome to your mock interview for the '+
    ROLE+' position. I will ask you '+TOTAL_Q+
    ' questions. Take your time with each answer — I will wait until you finish. Let us begin.';
  setChip('c-speaking','🔊 AI is greeting you…');
  speak(greeting, () => setTimeout(() => askQuestion(0), 500));
}}

// ═══════════════════════════════════════════════════════
// VAPI PATH — Real HTTP origin (served by Streamlit static)
// Daily.co postMessage now has a real target origin → works!
// ═══════════════════════════════════════════════════════
async function tryVapi() {{
  console.log('[VAPI] Loading SDK…');
  const mod = await import('https://esm.sh/@vapi-ai/web');
  const VapiClass = mod.default || mod.Vapi || mod;
  console.log('[VAPI] SDK loaded, creating instance…');
  S.vapiObj = new VapiClass(VAPI_TOKEN);

  S.vapiObj.on('call-start', () => {{
    S.usingVapi=true;
    D.badge.className='badge badge-vapi';
    D.badge.textContent='⚡ VAPI · Clara Voice';
    showUI(); setChip('c-speaking','🔊 Clara is greeting you…');
    console.log('[VAPI] Call started successfully');
  }});

  S.vapiObj.on('call-end', () => {{
    console.log('[VAPI] Call ended');
    clearInterval(S.timerH);
    D.btnE.style.display='none'; D.btnR.style.display='none';
    D.aiAv.className='av ai-bg'; D.usrAv.className='av usr-bg';
    D.aiW.classList.remove('on'); D.usrW.classList.remove('on');
    setChip('c-done','✅ Interview complete');
    D.doneC.style.display='block'; sendResults();
  }});

  S.vapiObj.on('speech-start', () => {{
    D.aiAv.className='av ai-bg speaking'; D.usrAv.className='av usr-bg';
    D.aiW.classList.add('on'); D.usrW.classList.remove('on');
    setChip('c-speaking','🔊 Clara is speaking…');
  }});

  S.vapiObj.on('speech-end', () => {{
    D.aiAv.className='av ai-bg'; D.aiW.classList.remove('on');
    D.usrAv.className='av usr-bg listening'; D.usrW.classList.add('on');
    setChip('c-listening','🎤 Listening to you…');
  }});

  S.vapiObj.on('message', (msg) => {{
    if (msg?.type === 'transcript' && msg.transcriptType === 'partial') {{
      if (msg.role === 'user') updatePartial(msg.transcript);
    }}
    if (msg?.type === 'transcript' && msg.transcriptType === 'final') {{
      const key = fp(msg.role==='assistant' ? 'ai' : 'user', msg.transcript);
      if (S.msgSet.has(key)) return;
      S.msgSet.add(key);
      const role = msg.role==='assistant' ? 'ai' : 'user';
      S.messages.push({{role, content:msg.transcript.trim(), ts:new Date().toISOString()}});

      if (role === 'user') {{
        finalPartial();
        addBubble('user', msg.transcript.trim(), false);
        const answered = S.messages.filter(m => m.role==='user').length;
        upProg(Math.min(answered, TOTAL_Q));
        D.usrAv.className='av usr-bg'; D.usrW.classList.remove('on');
        D.aiAv.className='av ai-bg thinking';
        setChip('c-thinking','💭 Clara is thinking…');
        setTimeout(() => {{ D.aiAv.className='av ai-bg'; }}, 800);
      }} else {{
        addBubble('ai', msg.transcript.trim(), false);
        const aiCount = S.messages.filter(m => m.role==='ai').length;
        const qi = aiCount-1;
        if (qi >= 0 && qi < TOTAL_Q) {{
          D.qNum.textContent='Question '+(qi+1)+' of '+TOTAL_Q;
          D.qTxt.textContent=QUESTIONS[qi];
          D.qCard.style.display='block'; upProg(qi);
        }}
      }}
    }}
  }});

  S.vapiObj.on('error', (e) => {{
    console.error('[VAPI] Error:', e);
    if (!S.usingVapi) {{
      S.vapiObj=null;
      showErr('VAPI could not connect — switching to free voice mode…');
      setTimeout(() => {{ hideErr(); startFreeMode(); }}, 2500);
    }}
  }});

  console.log('[VAPI] Starting call with assistant:', ASSISTANT_ID);
  await S.vapiObj.start(ASSISTANT_ID, {{
    variableValues: {{
      username : CNAME,
      job_role : ROLE,
      questions: Q_LINES,
      total_q  : String(TOTAL_Q),
      first_q  : FIRST_Q
    }}
  }});
  console.log('[VAPI] start() resolved');
}}

// ═══════════════════════════════════════════════════════
// ENTRY
// ═══════════════════════════════════════════════════════
async function startInterview() {{
  hideErr();
  D.btnS.disabled=true; D.btnS.textContent='Connecting…';

  if (VAPI_TOKEN && VAPI_TOKEN.length > 10) {{
    D.badge.className='badge badge-wait';
    D.badge.textContent='⏳ Connecting to VAPI…';
    setChip('c-thinking','⚡ Connecting to Clara…');
    try {{
      await tryVapi();
    }} catch(err) {{
      console.warn('[VAPI] Failed, falling back to free mode:', err);
      showErr('VAPI error: '+(err.message||err)+'. Using free voice mode…');
      setTimeout(() => {{ hideErr(); startFreeMode(); }}, 2500);
    }}
  }} else {{
    startFreeMode();
  }}
}}

function endEarly() {{
  if (S.usingVapi && S.vapiObj) {{ try {{ S.vapiObj.stop(); }} catch(e) {{}} return; }}
  S.isRunning=false; S.listeningActive=false;
  S.synth.cancel();
  if (S.recog) {{ try {{ S.recog.stop(); }} catch(e) {{}} }}
  stopSilBar(); clearInterval(S.timerH);
  D.btnE.style.display='none'; D.btnR.style.display='none';
  setChip('c-done','Ended early — sending results…');
  D.doneC.style.display='block'; sendResults();
}}

// Preload TTS voices
if (S.synth.onvoiceschanged !== undefined) S.synth.onvoiceschanged = () => S.synth.getVoices();
S.synth.getVoices();

// ═══════════════════════════════════════════════════════
// EXPOSE FUNCTIONS TO GLOBAL SCOPE (for onclick handlers)
// ═══════════════════════════════════════════════════════
window.startInterview = startInterview;
window.endEarly = endEarly;
window.retryAnswer = retryAnswer;
</script>
</body>
</html>"""


def save_interview_page(
    questions: list,
    job_role: str,
    candidate_name: str,
    interview_id: int,
    vapi_token: str,
    vapi_assistant_id: str,
    static_dir: str,
    streamlit_base_url: str = "",  # no longer used — JS computes origin
) -> str:
    """
    Write the interview HTML to the static directory.
    Returns the relative URL path Streamlit will serve it at.
    """
    os.makedirs(static_dir, exist_ok=True)
    filename = f"interview_{interview_id}.html"
    filepath = os.path.join(static_dir, filename)

    html = build_standalone_html(
        questions=questions,
        job_role=job_role,
        candidate_name=candidate_name,
        interview_id=interview_id,
        vapi_token=vapi_token,
        vapi_assistant_id=vapi_assistant_id,
    )

    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(html)

    # Streamlit serves ./static/ at /app/static/
    return f"/app/static/{filename}"
