"""
Free Interview Component — Browser Web Speech API
Uses ONLY free technologies:
  - SpeechRecognition API (Chrome built-in) → STT, free, no key
  - SpeechSynthesis API (Browser built-in)  → TTS, free, no key
  - Gemini API (already in your project)    → question flow logic in Python
  
Zero cost. Zero new API keys. Works in Chrome and Edge.
The component handles the FULL interview autonomously.
"""
import json
import os


def build_free_interview_component(
    questions: list,
    job_role: str,
    candidate_name: str,
    interview_id: int,
    google_api_key: str = None,
) -> str:
    """
    Build a fully autonomous interview component using only free browser APIs.
    
    Flow:
    1. Browser SpeechSynthesis reads the question aloud (TTS)
    2. Browser SpeechRecognition listens for the answer (STT)  
    3. After silence, next question auto-advances
    4. All transcripts stored and sent to Streamlit when done
    """
    if not google_api_key:
        google_api_key = os.getenv("GOOGLE_API_KEY", "")

    total_q = len(questions)
    questions_js = json.dumps(questions)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Mock Interview</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0d0d1a;
  color: #fff;
  min-height: 580px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 18px;
  gap: 18px;
}}

/* ── HEADER BANNER ── */
.banner {{
  width:100%; max-width:660px;
  background: linear-gradient(135deg,#1a1a3e,#16213e);
  border: 1px solid rgba(76,175,80,.35);
  border-radius: 12px;
  padding: 14px 20px;
  display: flex; justify-content: space-between; align-items: center;
}}
.banner-left h3 {{ color:#4CAF50; font-size:1rem; margin-bottom:2px; }}
.banner-left p  {{ color:#888; font-size:.78rem; }}
.timer {{ font-size:1.1rem; font-weight:700; color:#4CAF50; font-variant-numeric:tabular-nums; }}

/* ── AVATAR STAGE ── */
.stage {{
  display:flex; align-items:center; justify-content:center;
  gap:44px; width:100%; max-width:660px;
}}
.av-wrap {{
  display:flex; flex-direction:column; align-items:center; gap:10px;
}}
.av {{
  width:92px; height:92px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:2.3rem;
  border:3px solid #222;
  transition: border-color .3s, box-shadow .3s;
  position: relative;
}}
.av.ai-bg   {{ background: linear-gradient(135deg,#1a1a3e,#2a2a6e); }}
.av.user-bg {{ background: linear-gradient(135deg,#1a3e1a,#2a6e2a); }}
.av.speaking {{
  border-color:#4CAF50 !important;
  animation: pulse-green 1.1s ease-out infinite;
}}
.av.listening {{
  border-color:#2196F3 !important;
  animation: pulse-blue 1.3s ease-out infinite;
}}
@keyframes pulse-green {{
  0%   {{ box-shadow:0 0 0 0 rgba(76,175,80,.55); }}
  70%  {{ box-shadow:0 0 0 18px rgba(76,175,80,0); }}
  100% {{ box-shadow:0 0 0 0 rgba(76,175,80,0); }}
}}
@keyframes pulse-blue {{
  0%   {{ box-shadow:0 0 0 0 rgba(33,150,243,.55); }}
  70%  {{ box-shadow:0 0 0 18px rgba(33,150,243,0); }}
  100% {{ box-shadow:0 0 0 0 rgba(33,150,243,0); }}
}}
.av-name {{ font-size:.8rem; color:#bbb; font-weight:500; }}

/* sound wave */
.wave {{ display:flex; align-items:center; gap:3px; height:18px; visibility:hidden; }}
.wave.visible {{ visibility:visible; }}
.wave span {{
  width:4px; border-radius:2px;
  animation: wavebar .8s ease-in-out infinite;
}}
.wave.green span {{ background:#4CAF50; }}
.wave.blue  span {{ background:#2196F3; }}
.wave span:nth-child(1) {{ height:5px; }}
.wave span:nth-child(2) {{ height:12px; animation-delay:.12s; }}
.wave span:nth-child(3) {{ height:18px; animation-delay:.24s; }}
.wave span:nth-child(4) {{ height:10px; animation-delay:.36s; }}
.wave span:nth-child(5) {{ height:14px; animation-delay:.48s; }}
@keyframes wavebar {{
  0%,100% {{ height:4px; opacity:.5; }}
  50%      {{ height:18px; opacity:1; }}
}}
.vs {{ font-size:1.3rem; color:#333; font-weight:800; }}

/* ── PROGRESS ── */
.progress-wrap {{ width:100%; max-width:660px; display:none; }}
.progress-top {{
  display:flex; justify-content:space-between;
  font-size:.78rem; color:#888; margin-bottom:5px;
}}
.progress-track {{
  width:100%; height:7px;
  background:rgba(255,255,255,.07);
  border-radius:4px; overflow:hidden;
}}
.progress-fill {{
  height:100%; border-radius:4px;
  background:linear-gradient(90deg,#4CAF50,#81C784);
  transition:width .5s ease; width:0%;
}}
.dots {{ display:flex; gap:7px; margin-top:8px; flex-wrap:wrap; }}
.dot {{
  width:11px; height:11px; border-radius:50%;
  background:rgba(255,255,255,.12);
  transition:all .4s;
}}
.dot.done    {{ background:#4CAF50; }}
.dot.current {{ background:#FF9800; animation:dotblink .7s ease infinite alternate; }}
@keyframes dotblink {{ from{{transform:scale(1)}} to{{transform:scale(1.45)}} }}

/* ── STATUS CHIP ── */
.chip {{
  display:inline-flex; align-items:center; gap:7px;
  padding:6px 16px; border-radius:20px;
  font-size:.82rem; font-weight:600;
  transition:all .3s;
}}
.chip-ready      {{ background:rgba(255,255,255,.07); color:#aaa; }}
.chip-speaking   {{ background:rgba(76,175,80,.15);   color:#4CAF50; }}
.chip-listening  {{ background:rgba(33,150,243,.15);  color:#42A5F5; }}
.chip-processing {{ background:rgba(255,152,0,.15);   color:#FF9800; }}
.chip-done       {{ background:rgba(33,150,243,.15);  color:#42A5F5; }}
.chip-error      {{ background:rgba(244,67,54,.15);   color:#ef5350; }}
.chip-dot {{ width:8px; height:8px; border-radius:50%; background:currentColor; }}

/* ── QUESTION CARD ── */
.q-card {{
  width:100%; max-width:660px;
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.09);
  border-radius:12px; padding:16px 18px;
  display:none;
}}
.q-label {{ font-size:.72rem; color:#888; text-transform:uppercase;
            letter-spacing:1px; margin-bottom:6px; }}
.q-text  {{ font-size:.95rem; color:#e8e8e8; line-height:1.6; }}

/* ── LIVE TRANSCRIPT ── */
.tx-panel {{
  width:100%; max-width:660px;
  background:rgba(255,255,255,.03);
  border:1px solid rgba(255,255,255,.08);
  border-radius:12px; overflow:hidden;
  max-height:200px; display:none; flex-direction:column;
}}
.tx-header {{
  padding:7px 14px;
  background:rgba(255,255,255,.04);
  font-size:.7rem; color:#888;
  text-transform:uppercase; letter-spacing:1px;
  border-bottom:1px solid rgba(255,255,255,.06);
  display:flex; align-items:center; gap:6px;
}}
.live-dot {{
  width:7px; height:7px; border-radius:50%;
  background:#f44336; animation:liveblink 1s infinite;
}}
@keyframes liveblink {{ 0%,100%{{opacity:1}} 50%{{opacity:.25}} }}
.tx-body {{
  flex:1; overflow-y:auto; padding:10px 14px;
  display:flex; flex-direction:column; gap:7px;
  scrollbar-width:thin; scrollbar-color:#333 transparent;
}}
.bubble {{
  padding:8px 12px; border-radius:10px;
  font-size:.86rem; line-height:1.5; max-width:90%;
  animation:fadein .25s ease;
}}
@keyframes fadein {{ from{{opacity:0;transform:translateY(5px)}} to{{opacity:1;transform:translateY(0)}} }}
.bubble.ai {{
  background:rgba(33,150,243,.1); border-left:3px solid #2196F3;
  color:#bbdefb; align-self:flex-start;
}}
.bubble.user {{
  background:rgba(76,175,80,.1); border-right:3px solid #4CAF50;
  border-left:none; color:#c8e6c9; align-self:flex-end; text-align:right;
}}
.bubble-label {{
  font-size:.66rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.5px; opacity:.65; margin-bottom:3px;
}}

/* ── PARTIAL TRANSCRIPT (live preview while speaking) ── */
.partial-bar {{
  width:100%; max-width:660px;
  background:rgba(33,150,243,.08);
  border:1px dashed rgba(33,150,243,.3);
  border-radius:8px; padding:8px 14px;
  font-size:.84rem; color:#90CAF9;
  min-height:36px; display:none;
  font-style:italic;
}}

/* ── BUTTONS ── */
.btn-start {{
  padding:15px 52px; border-radius:50px; border:none;
  font-size:1.1rem; font-weight:700; cursor:pointer;
  background:linear-gradient(135deg,#4CAF50,#388E3C);
  color:white;
  box-shadow:0 5px 22px rgba(76,175,80,.45);
  transition:all .3s; letter-spacing:.3px;
}}
.btn-start:hover {{ transform:translateY(-2px); box-shadow:0 8px 28px rgba(76,175,80,.55); }}
.btn-start:disabled {{ background:#2a2a2a; color:#555; box-shadow:none;
                       cursor:not-allowed; transform:none; }}
.btn-end {{
  padding:10px 28px; border-radius:50px;
  border:2px solid #f44336; background:transparent;
  color:#f44336; font-size:.88rem; font-weight:600;
  cursor:pointer; transition:all .3s; display:none;
}}
.btn-end:hover {{ background:rgba(244,67,54,.12); }}
.controls {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap; justify-content:center; }}

/* ── DONE CARD ── */
.done-card {{
  width:100%; max-width:660px;
  background:rgba(76,175,80,.1); border:1px solid rgba(76,175,80,.35);
  border-radius:12px; padding:20px; text-align:center; display:none;
}}
.done-card h3 {{ color:#4CAF50; margin-bottom:8px; font-size:1.2rem; }}
.done-card p  {{ color:#ccc; font-size:.86rem; line-height:1.7; }}

/* ── ERROR ── */
.err-box {{
  width:100%; max-width:660px;
  background:rgba(244,67,54,.1); border:1px solid rgba(244,67,54,.25);
  border-radius:10px; padding:12px 16px;
  color:#ff6b6b; font-size:.83rem; display:none;
}}

/* ── BROWSER WARNING ── */
.browser-warn {{
  width:100%; max-width:660px;
  background:rgba(255,152,0,.1); border:1px solid rgba(255,152,0,.3);
  border-radius:10px; padding:12px 16px;
  color:#FFB74D; font-size:.83rem;
}}
</style>
</head>
<body>

<!-- BROWSER CHECK -->
<div class="browser-warn" id="browser-warn" style="display:none">
  ⚠️ <b>Chrome or Edge required.</b>
  The Web Speech API (free, no key needed) is only supported in Chrome and Edge.
  Please open this page in Chrome for the voice interview to work.
</div>

<!-- HEADER -->
<div class="banner">
  <div class="banner-left">
    <h3>🎤 {job_role}</h3>
    <p>Candidate: {candidate_name} &nbsp;·&nbsp; {total_q} questions</p>
  </div>
  <div class="timer" id="timer">00:00</div>
</div>

<!-- AVATARS -->
<div class="stage">
  <div class="av-wrap">
    <div class="av ai-bg" id="ai-av">🤖</div>
    <div class="wave green" id="ai-wave">
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <div class="av-name">AI Interviewer</div>
  </div>
  <div class="vs">⟺</div>
  <div class="av-wrap">
    <div class="av user-bg" id="user-av">👤</div>
    <div class="wave blue" id="user-wave">
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <div class="av-name">{candidate_name}</div>
  </div>
</div>

<!-- PROGRESS -->
<div class="progress-wrap" id="prog-wrap">
  <div class="progress-top">
    <span id="prog-label">Starting...</span>
    <span id="prog-fraction">0 / {total_q}</span>
  </div>
  <div class="progress-track">
    <div class="progress-fill" id="prog-fill"></div>
  </div>
  <div class="dots" id="q-dots"></div>
</div>

<!-- STATUS CHIP -->
<div class="chip chip-ready" id="chip">
  <span class="chip-dot"></span>
  <span id="chip-txt">Ready — click Start Interview</span>
</div>

<!-- CURRENT QUESTION CARD -->
<div class="q-card" id="q-card">
  <div class="q-label" id="q-label-num">Question 1</div>
  <div class="q-text"  id="q-text">...</div>
</div>

<!-- PARTIAL TRANSCRIPT (live while user is speaking) -->
<div class="partial-bar" id="partial-bar">🎤 Listening...</div>

<!-- FULL TRANSCRIPT -->
<div class="tx-panel" id="tx-panel">
  <div class="tx-header">
    <div class="live-dot"></div>
    Live Transcript
  </div>
  <div class="tx-body" id="tx-body"></div>
</div>

<!-- BUTTONS -->
<div class="controls">
  <button class="btn-start" id="btn-start" onclick="startInterview()">
    🎙️ Start Interview
  </button>
  <button class="btn-end" id="btn-end" onclick="endEarly()">
    ⏹ End Early
  </button>
</div>

<!-- DONE CARD -->
<div class="done-card" id="done-card">
  <h3>✅ Interview Complete!</h3>
  <p id="done-msg">Sending your responses for AI evaluation…<br>
  <span style="color:#888;font-size:.78rem">Your report will appear above in a few seconds.</span></p>
</div>

<!-- ERROR -->
<div class="err-box" id="err-box"></div>

<script>
// ─── DATA ─────────────────────────────────────────────────
const QUESTIONS   = {questions_js};
const TOTAL_Q     = {total_q};
const IV_ID       = {interview_id};
const CANDIDATE   = "{candidate_name}";
const JOB_ROLE    = "{job_role}";

// ─── STATE ────────────────────────────────────────────────
let currentQ      = 0;         // index of question being asked
let messages      = [];        // {{role,content,ts}}
let timerSec      = 0;
let timerHandle   = null;
let recognition   = null;
let synth         = window.speechSynthesis;
let isRunning     = false;
let silenceTimer  = null;
let currentAnswer = "";        // accumulates STT partial results
let voiceReady    = false;

// ─── DOM ──────────────────────────────────────────────────
const aiAv       = document.getElementById('ai-av');
const userAv     = document.getElementById('user-av');
const aiWave     = document.getElementById('ai-wave');
const userWave   = document.getElementById('user-wave');
const progWrap   = document.getElementById('prog-wrap');
const progFill   = document.getElementById('prog-fill');
const progFrac   = document.getElementById('prog-fraction');
const progLabel  = document.getElementById('prog-label');
const qDots      = document.getElementById('q-dots');
const chip       = document.getElementById('chip');
const chipTxt    = document.getElementById('chip-txt');
const qCard      = document.getElementById('q-card');
const qLabelNum  = document.getElementById('q-label-num');
const qText      = document.getElementById('q-text');
const partialBar = document.getElementById('partial-bar');
const txPanel    = document.getElementById('tx-panel');
const txBody     = document.getElementById('tx-body');
const btnStart   = document.getElementById('btn-start');
const btnEnd     = document.getElementById('btn-end');
const doneCard   = document.getElementById('done-card');
const errBox     = document.getElementById('err-box');
const timerDisp  = document.getElementById('timer');

// ─── BROWSER CHECK ────────────────────────────────────────
(function() {{
  const ok = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
  if (!ok) {{
    document.getElementById('browser-warn').style.display = 'block';
    document.getElementById('btn-start').disabled = true;
    document.getElementById('chip-txt').textContent = 'Chrome/Edge required for voice';
  }}
}})();

// ─── HELPERS ──────────────────────────────────────────────
function setChip(cls, txt) {{
  chip.className = 'chip ' + cls;
  chipTxt.textContent = txt;
}}

function showErr(msg) {{
  errBox.textContent = '⚠️ ' + msg;
  errBox.style.display = 'block';
}}

function buildDots() {{
  qDots.innerHTML = '';
  for (let i = 0; i < TOTAL_Q; i++) {{
    const d = document.createElement('div');
    d.className = 'q-dot'; d.id = 'dot' + i;
    qDots.appendChild(d);
  }}
}}

function updateProgress(idx) {{
  const pct = Math.round((idx / TOTAL_Q) * 100);
  progFill.style.width = pct + '%';
  progFrac.textContent = idx + ' / ' + TOTAL_Q;
  progLabel.textContent = idx >= TOTAL_Q
    ? '✅ All questions answered!'
    : 'Question ' + (idx + 1) + ' of ' + TOTAL_Q;
  for (let i = 0; i < TOTAL_Q; i++) {{
    const d = document.getElementById('dot' + i);
    if (!d) continue;
    if (i < idx)        d.className = 'q-dot done';
    else if (i === idx) d.className = 'q-dot current';
    else                d.className = 'q-dot';
  }}
}}

function addBubble(role, content) {{
  const wrap = document.createElement('div');
  wrap.className = 'bubble ' + (role === 'ai' ? 'ai' : 'user');
  const lbl = document.createElement('div');
  lbl.className = 'bubble-label';
  lbl.textContent = role === 'ai' ? '🤖 Interviewer' : '👤 You';
  const txt = document.createElement('div');
  txt.textContent = content;
  wrap.appendChild(lbl); wrap.appendChild(txt);
  txBody.appendChild(wrap);
  txBody.scrollTop = txBody.scrollHeight;
}}

function pushMsg(role, content) {{
  messages.push({{ role, content, ts: new Date().toISOString() }});
  addBubble(role, content);
}}

function startTimer() {{
  timerHandle = setInterval(() => {{
    timerSec++;
    const m = String(Math.floor(timerSec/60)).padStart(2,'0');
    const s = String(timerSec%60).padStart(2,'0');
    timerDisp.textContent = m + ':' + s;
  }}, 1000);
}}

// ─── TTS — speak text, then call onDone ───────────────────
function speak(text, onDone) {{
  synth.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.rate  = 0.92;
  utt.pitch = 1.05;
  utt.volume = 1.0;

  // Prefer a natural English voice
  const voices = synth.getVoices();
  const preferred = voices.find(v =>
    v.lang.startsWith('en') &&
    (v.name.includes('Natural') || v.name.includes('Google') ||
     v.name.includes('Samantha') || v.name.includes('Karen') ||
     v.name.includes('Female') || v.name.includes('US'))
  ) || voices.find(v => v.lang.startsWith('en')) || voices[0];
  if (preferred) utt.voice = preferred;

  // AI speaking state
  aiAv.className = 'av ai-bg speaking';
  userAv.className = 'av user-bg';
  aiWave.classList.add('visible');
  userWave.classList.remove('visible');
  setChip('chip-speaking', '🔊 AI is speaking...');

  utt.onend = () => {{
    aiAv.className = 'av ai-bg';
    aiWave.classList.remove('visible');
    if (onDone) onDone();
  }};
  utt.onerror = (e) => {{
    console.warn('TTS error:', e);
    aiAv.className = 'av ai-bg';
    aiWave.classList.remove('visible');
    if (onDone) onDone();   // still advance
  }};

  // Chrome bug: voices may not be loaded yet
  if (synth.getVoices().length === 0) {{
    window.speechSynthesis.onvoiceschanged = () => {{
      synth.speak(utt);
    }};
  }} else {{
    synth.speak(utt);
  }}
}}

// ─── STT — listen for one answer ─────────────────────────
function listenForAnswer(onResult) {{
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {{ showErr('SpeechRecognition not supported. Use Chrome/Edge.'); return; }}

  recognition = new SR();
  recognition.continuous   = true;
  recognition.interimResults = true;
  recognition.lang         = 'en-US';
  recognition.maxAlternatives = 1;

  currentAnswer = '';
  partialBar.style.display = 'block';
  partialBar.textContent   = '🎤 Speak now...';

  // User listening state
  userAv.className  = 'av user-bg listening';
  userWave.classList.add('visible');
  aiAv.className    = 'av ai-bg';
  aiWave.classList.remove('visible');
  setChip('chip-listening', '🎤 Listening to you...');

  // Auto-advance after 4 seconds of silence
  function resetSilence() {{
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {{
      if (currentAnswer.trim().length > 3) {{
        recognition.stop();
      }}
    }}, 4000);
  }}

  recognition.onresult = (e) => {{
    let interim = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {{
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) {{
        currentAnswer += ' ' + t;
        resetSilence();
      }} else {{
        interim = t;
      }}
    }}
    partialBar.textContent = '🎤 ' + (currentAnswer + ' ' + interim).trim();
  }};

  recognition.onspeechend = () => {{
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {{ recognition.stop(); }}, 1500);
  }};

  recognition.onend = () => {{
    partialBar.style.display = 'none';
    userAv.className  = 'av user-bg';
    userWave.classList.remove('visible');
    const ans = currentAnswer.trim() || '(No answer)';
    onResult(ans);
  }};

  recognition.onerror = (e) => {{
    console.warn('STT error:', e.error);
    partialBar.style.display = 'none';
    userAv.className = 'av user-bg';
    userWave.classList.remove('visible');
    // network or no-speech — still advance
    const ans = currentAnswer.trim() || '(Could not capture — microphone issue)';
    onResult(ans);
  }};

  recognition.start();
  resetSilence();
}}

// ─── INTERVIEW LOOP ───────────────────────────────────────
function askQuestion(idx) {{
  if (idx >= TOTAL_Q) {{
    // All questions done
    finishInterview();
    return;
  }}

  currentQ = idx;
  const q  = QUESTIONS[idx];

  // Update UI
  updateProgress(idx);
  qLabelNum.textContent = 'Question ' + (idx+1) + ' of ' + TOTAL_Q;
  qText.textContent     = q;
  qCard.style.display   = 'block';
  setChip('chip-speaking', '🔊 AI is speaking question ' + (idx+1));

  // Add AI message to transcript
  pushMsg('ai', q);

  // Speak the question, then listen
  speak(q, () => {{
    setChip('chip-listening', '🎤 Your turn — answer Q' + (idx+1));
    listenForAnswer((answer) => {{
      // Save user answer
      pushMsg('user', answer);
      updateProgress(idx + 1);

      // Brief acknowledgement then next question
      setChip('chip-processing', '⏳ Moving to next question...');
      const acks = [
        'Thank you, that was helpful.',
        'I see, noted.',
        'Good answer, moving on.',
        'Thank you for sharing that.',
        'Alright, understood.',
      ];
      const ack = acks[idx % acks.length];
      speak(ack, () => {{
        setTimeout(() => askQuestion(idx + 1), 600);
      }});
    }});
  }});
}}

function finishInterview() {{
  isRunning = false;
  clearTimeout(silenceTimer);
  if (timerHandle) clearInterval(timerHandle);
  btnEnd.style.display = 'none';

  const closing =
    'Thank you ' + CANDIDATE + ', that completes all ' + TOTAL_Q +
    ' questions of your mock interview for the ' + JOB_ROLE + ' position. ' +
    'Your answers have been recorded and our AI will now evaluate your performance. ' +
    'You will see your results in just a moment. Best of luck!';

  setChip('chip-done', '✅ Interview complete!');
  speak(closing, () => {{
    doneCard.style.display = 'block';
    sendResults();
  }});
}}

// ─── SEND RESULTS TO STREAMLIT ────────────────────────────
function sendResults() {{
  const payload = {{
    type: 'interview_complete',
    interview_id: IV_ID,
    messages: messages,
    q_answered: messages.filter(m => m.role === 'user').length,
    duration_sec: timerSec,
    timestamp: new Date().toISOString(),
  }};
  const str = JSON.stringify(payload);

  // 1. sessionStorage + localStorage (primary)
  try {{
    sessionStorage.setItem('iv_result_' + IV_ID, str);
    sessionStorage.setItem('iv_latest', String(IV_ID));
    localStorage.setItem('iv_result_' + IV_ID, str);
  }} catch(e) {{ console.warn('Storage:', e); }}

  // 2. postMessage to Streamlit parent
  try {{ window.parent.postMessage(payload, '*'); }} catch(e) {{}}

  // 3. Navigate parent URL to trigger Streamlit rerun
  setTimeout(() => {{
    try {{
      const msgs_b64 = btoa(unescape(encodeURIComponent(JSON.stringify(messages))));
      const base = window.parent.location.href.split('?')[0];
      window.parent.location.href = base + '?iv_done=' + IV_ID +
        '&iv_data=' + encodeURIComponent(JSON.stringify(messages));
    }} catch(e) {{
      console.warn('Parent nav:', e);
      // Cross-origin fallback: user must click
      document.getElementById('done-msg').innerHTML =
        '<b style="color:#4CAF50">' +
        messages.filter(m=>m.role==='user').length +
        ' answers captured.</b><br>' +
        '<span style="color:#aaa">Please click the <b>Evaluate</b> button below the panel.</span>';
    }}
  }}, 1800);
}}

// ─── START ────────────────────────────────────────────────
function startInterview() {{
  btnStart.disabled = true;
  btnStart.textContent = 'Starting...';
  isRunning = true;

  // Show all UI sections
  progWrap.style.display = 'block';
  txPanel.style.display  = 'flex';
  btnStart.style.display = 'none';
  btnEnd.style.display   = 'block';
  buildDots();
  startTimer();

  // Greeting then start questions
  const greeting =
    'Hello ' + CANDIDATE + '! Welcome to your mock interview for the ' +
    JOB_ROLE + ' position. I am your AI interviewer today. ' +
    'I will ask you ' + TOTAL_Q + ' questions one by one. ' +
    'Please speak your answers clearly after each question. ' +
    "Let's begin now.";

  setChip('chip-speaking', '🔊 AI is greeting you...');
  speak(greeting, () => {{
    setTimeout(() => askQuestion(0), 400);
  }});
}}

function endEarly() {{
  if (!isRunning) return;
  isRunning = false;
  synth.cancel();
  if (recognition) {{ try {{ recognition.stop(); }} catch(e) {{}} }}
  clearTimeout(silenceTimer);
  setChip('chip-done', 'Interview ended early');
  btnEnd.style.display = 'none';
  finishInterview();
}}

// Preload voices on page load (Chrome async issue fix)
if (synth.onvoiceschanged !== undefined) {{
  synth.onvoiceschanged = () => {{ synth.getVoices(); }};
}}
synth.getVoices();
</script>
</body>
</html>"""
    return html
