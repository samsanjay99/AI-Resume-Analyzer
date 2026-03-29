"""
Mock Interview Page — Smart Resume AI
100% FREE — No paid APIs required.
Uses: Web SpeechRecognition (browser STT) + SpeechSynthesis (browser TTS) + Gemini (evaluation)
"""
import os, json, time
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

from auth.auth_manager import AuthManager
from utils.interview_manager import InterviewManager
from utils.interview_standalone import build_standalone_html
from config.job_roles import JOB_ROLES
from config.course_recommendation_manager import CourseRecommendationManager


def _sc(s): return "#4CAF50" if s >= 75 else "#FF9800" if s >= 50 else "#F44336"
def _sl(s): return "Excellent" if s >= 75 else "Good" if s >= 50 else "Needs Work"

def _reset():
    for k in ["iv_id","iv_q","iv_exp","iv_skills","iv_cfg",
              "iv_focus","iv_transcript","iv_feedback","iv_phase","iv_pdf"]:
        st.session_state.pop(k, None)


# ──────────────────────────────────────────────────────────
# PHASE 0 — SETUP
# ──────────────────────────────────────────────────────────
def render_setup(manager):
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
    padding:1.8rem 2rem;border-radius:14px;margin-bottom:1.8rem;
    border:1px solid rgba(76,175,80,.3);'>
    <h2 style='color:#4CAF50;margin:0 0 4px;'>🎤 AI Mock Interview</h2>
    <p style='color:#aaa;margin:0;font-size:.92rem;'>
    100% free · Uses browser microphone · AI evaluates with Gemini · Full PDF report</p>
    </div>""", unsafe_allow_html=True)

    # Free tech badge
    st.markdown("""
    <div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1.2rem;'>
    <span style='background:rgba(76,175,80,.15);color:#4CAF50;padding:4px 12px;
    border-radius:20px;font-size:.78rem;font-weight:600;border:1px solid rgba(76,175,80,.3);'>
    ✅ FREE — No paid API</span>
    <span style='background:rgba(33,150,243,.15);color:#42A5F5;padding:4px 12px;
    border-radius:20px;font-size:.78rem;font-weight:600;border:1px solid rgba(33,150,243,.3);'>
    🎙️ Browser Microphone (STT)</span>
    <span style='background:rgba(156,39,176,.15);color:#CE93D8;padding:4px 12px;
    border-radius:20px;font-size:.78rem;font-weight:600;border:1px solid rgba(156,39,176,.3);'>
    🔊 Browser Voice (TTS)</span>
    <span style='background:rgba(255,152,0,.15);color:#FF9800;padding:4px 12px;
    border-radius:20px;font-size:.78rem;font-weight:600;border:1px solid rgba(255,152,0,.3);'>
    🧠 Gemini Evaluation</span>
    </div>""", unsafe_allow_html=True)

    all_roles = sorted(r for cat in JOB_ROLES.values() for r in cat)
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("### 📋 Interview Setup")
        job_role   = st.selectbox("Job Role *", all_roles)
        itype      = st.selectbox("Interview Type *",
            ["mixed","technical","behavioral","hr"],
            format_func={"mixed":"Mixed (Technical + Behavioral)",
                         "technical":"Technical Only",
                         "behavioral":"Behavioral / HR",
                         "hr":"HR Round"}.get)
        difficulty = st.selectbox("Difficulty *",
            ["easy","medium","hard"], index=1, format_func=str.capitalize)
        q_count    = st.slider("Number of Questions", 3, 10, 5)

    with c2:
        st.markdown("### 📄 Optional Context")
        jd = st.text_area("Job Description (optional)", height=110,
            placeholder="Paste the JD for highly personalised questions...")
        # Auto-populate skills from last resume analysis if available
        auto_skills = ""
        try:
            from config.analysis_manager import AnalysisManager
            user_id = AuthManager.get_current_user_id()
            recent = AnalysisManager.get_user_all_analyses(user_id)
            if recent:
                latest = recent[0]
                detected = latest.get("detected_skills", [])
                if isinstance(detected, list) and detected:
                    auto_skills = ", ".join(detected[:15])
        except Exception:
            pass

        skills_txt = st.text_input("Your Key Skills (comma separated)",
            value=auto_skills,
            placeholder="Python, React, SQL, Communication...",
            help="Auto-filled from your last resume analysis. Edit as needed.")

        st.markdown("### 🎙️ How It Works")
        st.markdown("""
        <div style='background:rgba(76,175,80,.07);border-left:3px solid #4CAF50;
        padding:12px 15px;border-radius:0 8px 8px 0;font-size:.83rem;color:#ccc;'>
        ① AI generates your questions<br>
        ② Click <b style='color:#4CAF50;'>Start Interview</b> — mic activates<br>
        ③ AI <b>speaks</b> Q1 aloud using browser voice<br>
        ④ You answer by <b>speaking</b> — browser transcribes<br>
        ⑤ After 4 sec silence → next question auto-advances<br>
        ⑥ All questions done → AI evaluates with Gemini<br>
        ⑦ Full report + PDF ready instantly<br><br>
        <b style='color:#FF9800;'>Requires Chrome or Edge browser.</b>
        </div>""", unsafe_allow_html=True)

        consent = st.checkbox(
            "I allow this page to access my microphone for the interview session.")

    st.markdown("---")
    _, cb, _ = st.columns([1, 2, 1])
    with cb:
        if st.button("🚀 Generate Questions & Prepare",
                     type="primary", use_container_width=True,
                     disabled=not consent):
            if not consent:
                st.error("Please allow microphone access first.")
                return
            with st.spinner("🧠 Generating your personalised questions..."):
                resume_skills = [s.strip() for s in skills_txt.split(",") if s.strip()]
                result = manager.generate_questions(
                    job_role=job_role, difficulty=difficulty,
                    interview_type=itype, question_count=q_count,
                    job_description=jd, resume_skills=resume_skills)

            if not result.get("success"):
                st.error("Failed to generate questions. Please try again.")
                return

            user_id = AuthManager.get_current_user_id()
            iv_id   = InterviewManager.save_interview_session(
                user_id=user_id, job_role=job_role, difficulty=difficulty,
                interview_type=itype, question_count=q_count,
                questions=result["questions"],
                expected_answers=result["expected_answers"],
                skills_to_test=result["skills_to_test"],
                job_description=jd)

            if not iv_id:
                st.error("Could not save session. Check database connection.")
                return

            st.session_state.iv_id     = iv_id
            st.session_state.iv_q      = result["questions"]
            st.session_state.iv_exp    = result["expected_answers"]
            st.session_state.iv_skills = result["skills_to_test"]
            st.session_state.iv_cfg    = {
                "job_role": job_role, "difficulty": difficulty,
                "interview_type": itype, "question_count": q_count}
            st.session_state.iv_phase = "ready"
            st.rerun()


# ──────────────────────────────────────────────────────────
# PHASE 1 — READY (review questions before starting)
# ──────────────────────────────────────────────────────────
def render_ready():
    cfg = st.session_state.iv_cfg
    qs  = st.session_state.iv_q

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
    padding:1.5rem 2rem;border-radius:14px;margin-bottom:1.5rem;
    border:1px solid rgba(76,175,80,.3);'>
    <h3 style='color:#4CAF50;margin:0;'>✅ {len(qs)} Questions Ready</h3>
    <p style='color:#aaa;margin:4px 0 0;font-size:.88rem;'>
    {cfg['difficulty'].capitalize()} · {cfg['interview_type'].capitalize()} ·
    {cfg['job_role']}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 📋 Your Interview Questions")
    for i, q in enumerate(qs):
        st.markdown(f"""
        <div style='background:rgba(255,255,255,.03);border-left:3px solid #4CAF50;
        padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;'>
        <span style='color:#666;font-size:.72rem;'>Q{i+1}</span><br>
        <span style='color:#ddd;font-size:.92rem;'>{q}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='background:rgba(255,152,0,.07);border:1px solid rgba(255,152,0,.25);
    border-radius:10px;padding:14px 16px;margin-bottom:1rem;'>
    <b style='color:#FF9800;'>📌 Before you start:</b>
    <ul style='color:#ccc;margin:8px 0 0 18px;font-size:.85rem;line-height:2;'>
    <li>Use <b>Chrome or Edge</b> browser (required for Web Speech API)</li>
    <li>Allow microphone access when the browser asks</li>
    <li>Sit in a <b>quiet place</b> — silence helps transcription accuracy</li>
    <li>Speak <b>clearly at normal pace</b> — pause 1–2 sec when done answering</li>
    <li>The AI listens until you pause for ~4 seconds, then advances automatically</li>
    <li><b>No buttons to click</b> during the interview — just speak</li>
    </ul>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c1:
        if st.button("← Back", use_container_width=True):
            _reset(); st.rerun()
    with c2:
        if st.button("🎙️ START LIVE INTERVIEW",
                     type="primary", use_container_width=True):
            st.session_state.iv_phase = "live"
            st.rerun()
    with c3:
        if st.button("🔄 New Questions", use_container_width=True):
            st.session_state.pop("iv_id", None)
            st.session_state.pop("iv_q", None)
            st.session_state.iv_phase = "setup"
            st.rerun()


# ──────────────────────────────────────────────────────────
# PHASE 2 — LIVE (the actual interview)
# ──────────────────────────────────────────────────────────

def render_live():
    iv_id     = st.session_state.iv_id
    questions = st.session_state.iv_q
    cfg       = st.session_state.iv_cfg
    name      = AuthManager.get_current_user_name()

    # ══════════════════════════════════════════════════════════════
    # RECEIVE RESULTS — poll for iv_result_{id}.json written by
    # the mini HTTP server when the interview page POSTs /submit.
    # No URL navigation → no session loss → no login redirect.
    # ══════════════════════════════════════════════════════════════
    static_dir  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    result_file = os.path.join(static_dir, f"iv_result_{iv_id}.json")

    if os.path.exists(result_file):
        try:
            with open(result_file, "r", encoding="utf-8") as _f:
                transcript = json.load(_f)
            if transcript:
                os.remove(result_file)   # clean up
                st.session_state.iv_transcript = transcript
                st.session_state.iv_phase      = "evaluating"
                st.rerun()
        except Exception as e:
            print(f"Result file read error: {e}")

    # Also handle legacy query-param redirect (fallback)
    params = st.query_params
    if params.get("iv_done") == str(iv_id) and "iv_data" in params:
        try:
            transcript = json.loads(params["iv_data"])
            if transcript:
                st.session_state.iv_transcript = transcript
                st.session_state.iv_phase      = "evaluating"
                st.query_params.clear()
                st.rerun()
        except Exception as e:
            print(f"Param decode error: {e}")
            st.query_params.clear()

    # ══════════════════════════════════════════════════════════════
    # GENERATE HTML FILE
    # Local dev:  mini HTTP server on port 8765 (correct MIME type)
    # Cloud:      Streamlit's /app/static/ path (cloud serves HTML correctly)
    # ══════════════════════════════════════════════════════════════
    from utils.interview_standalone import build_standalone_html

    # Detect environment — use env var (most reliable) then fall back to host header
    # Streamlit Cloud sets STREAMLIT_SHARING_MODE=true or runs without local .env
    try:
        host = st.context.headers.get("Host", "localhost:8501")
        scheme = "https" if ("streamlit.app" in host or "share.streamlit.io" in host or "https" in host) else "http"
        streamlit_base_url = f"{scheme}://{host}"
    except Exception:
        host = "localhost:8501"
        scheme = "http"
        streamlit_base_url = "http://localhost:8501"

    # is_cloud: true if NOT running locally
    # Most reliable: try to bind a socket to 127.0.0.1:8765 — if it fails with
    # permission error it's cloud; also check env vars and host header.
    def _detect_cloud():
        # Streamlit Cloud sets this env var
        if os.getenv("STREAMLIT_SHARING_MODE") == "true":
            return True
        if os.getenv("HOME") == "/home/adminuser":  # Streamlit Cloud container
            return True
        if "streamlit.app" in host or "share.streamlit.io" in host:
            return True
        # If no .env file exists at project root, assume cloud
        project_root = os.path.dirname(os.path.dirname(__file__))
        if not os.path.exists(os.path.join(project_root, ".env")):
            return True
        return False

    is_cloud = _detect_cloud()

    # Save to static folder
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    filename = f"interview_{iv_id}.html"
    filepath = os.path.join(static_dir, filename)

    # Determine submit URL (local only — cloud uses query-param redirect)
    if is_cloud:
        submit_url = ""
    else:
        from utils.interview_server import ensure_interview_server
        server_base = ensure_interview_server(static_dir)
        submit_url = f"{server_base}/submit" if server_base else ""

    html = build_standalone_html(
        questions          = questions,
        job_role           = cfg["job_role"],
        candidate_name     = name,
        interview_id       = iv_id,
        vapi_token         = os.getenv("VAPI_WEB_TOKEN", ""),
        vapi_assistant_id  = os.getenv("VAPI_ASSISTANT_ID",
                                       "ab9b228d-3b3f-4ff0-9678-a6de2c20674c"),
        streamlit_base_url = streamlit_base_url,
        submit_url         = submit_url,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    if is_cloud:
        # On Streamlit Cloud: open /app/static/ in new tab
        # The "Page not found" popup was a Streamlit routing issue —
        # it happens because Streamlit intercepts the navigation.
        # Fix: use window.open() from JS instead of st.link_button()
        # so the browser opens it directly without Streamlit's router.
        interview_url = f"{streamlit_base_url}/app/static/{filename}"
    else:
        from utils.interview_server import ensure_interview_server
        server_base = ensure_interview_server(static_dir)
        if server_base:
            interview_url = f"{server_base}/{filename}"
        else:
            interview_url = f"{streamlit_base_url}/app/static/{filename}"
    _iframe_src = None

    # ══════════════════════════════════════════════════════════════
    # INFO BANNER + INTERVIEW UI
    # ══════════════════════════════════════════════════════════════
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
    padding:1.8rem 2rem;border-radius:14px;text-align:center;
    border:2px solid rgba(76,175,80,.4);margin-bottom:1rem;'>
    <div style='font-size:2.8rem;'>🎤</div>
    <h3 style='color:#4CAF50;margin:.4rem 0;'>Interview Ready</h3>
    <p style='color:#aaa;font-size:.86rem;margin:0 0 .4rem;'>
    <b style='color:white;'>{cfg["job_role"]}</b> &nbsp;·&nbsp;
    {len(questions)} questions &nbsp;·&nbsp; VAPI Clara + Free Voice fallback
    </p>
    </div>
    """, unsafe_allow_html=True)

    if interview_url:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Use JS window.open() to bypass Streamlit's router interception
            components.html(f"""
            <div style="display:flex;justify-content:center;padding:4px 0;">
            <button onclick="window.open('{interview_url}','_blank','noopener')"
            style="padding:12px 32px;border-radius:50px;border:none;
            font-size:1rem;font-weight:700;cursor:pointer;color:white;
            background:linear-gradient(135deg,#4CAF50,#388E3C);
            box-shadow:0 4px 18px rgba(76,175,80,.38);
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            width:100%;">🎙️ Open Interview</button>
            </div>
            """, height=60)
        st.caption(
            "Chrome or Edge required · Allow microphone when prompted · "
            "Complete the interview, then click 'Check for Results' below."
        )
    else:
        st.caption("Chrome or Edge required · Allow microphone when prompted · Complete all questions, then click 'Check for Results' below.")

    st.markdown("---")
    
    # ══════════════════════════════════════════════════════════════
    # MANUAL RESULTS CHECK
    # User clicks this button after completing the interview
    # ══════════════════════════════════════════════════════════════
    st.info(
        "⏳ **Complete the interview above.** When done, click the button below — "
        "or wait a few seconds and it will auto-detect."
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Check for Results", use_container_width=True, key=f"poll_{iv_id}"):
            if os.path.exists(result_file):
                try:
                    with open(result_file, "r", encoding="utf-8") as _f:
                        transcript = json.load(_f)
                    if transcript:
                        os.remove(result_file)
                        st.session_state.iv_transcript = transcript
                        st.session_state.iv_phase = "evaluating"
                        st.rerun()
                except Exception as e:
                    st.error(f"Error reading results: {e}")
            else:
                st.warning("No results yet — complete the interview first.")

    # ══════════════════════════════════════════════════════════════
    # MANUAL TEXT FALLBACK (last resort)
    # ══════════════════════════════════════════════════════════════
    st.markdown("---")
    with st.expander("🔧 Manual fallback — only if automatic results don't appear",
                     expanded=False):
        st.markdown(
            "*Type your answers here only if you completed the interview "
            "but no report appeared after 30 seconds.*"
        )
        manual_answers = []
        for i, q in enumerate(questions):
            ans = st.text_area(
                f"Q{i+1}: {q}",
                key=f"live_manual_{iv_id}_{i}",   # unique: includes iv_id + index
                height=65,
                placeholder="Type what you said in your voice answer…"
            )
            manual_answers.append(ans)

        mc1, mc2 = st.columns(2)
        with mc1:
            if st.button("🧠 Evaluate My Answers", type="primary",
                         use_container_width=True,
                         key=f"live_eval_manual_{iv_id}"):
                if not any(a.strip() for a in manual_answers):
                    st.error("Please type at least one answer before evaluating.")
                else:
                    tr = []
                    for q, ans in zip(questions, manual_answers):
                        tr.append({"role":"assistant","content":q,
                                   "ts":datetime.now().isoformat()})
                        tr.append({"role":"user",
                                   "content": ans.strip() or "(No answer provided)",
                                   "ts":datetime.now().isoformat()})
                    st.session_state.iv_transcript = tr
                    st.session_state.iv_phase = "evaluating"
                    st.rerun()
        with mc2:
            if st.button("← Back to Setup", use_container_width=True,
                         key=f"live_back_{iv_id}"):
                _reset(); st.rerun()




# ──────────────────────────────────────────────────────────
# PHASE 3 — EVALUATING
# ──────────────────────────────────────────────────────────
def render_evaluating(manager):
    iv_id      = st.session_state.iv_id
    transcript = st.session_state.get("iv_transcript", [])
    questions  = st.session_state.iv_q
    expected   = st.session_state.iv_exp
    skills     = st.session_state.iv_skills
    cfg        = st.session_state.iv_cfg

    st.markdown("""
    <div style='text-align:center;padding:2.5rem 1rem;'>
    <div style='font-size:3rem;margin-bottom:.8rem;'>🧠</div>
    <h2 style='color:#4CAF50;margin:0;'>Evaluating Your Interview</h2>
    <p style='color:#aaa;margin:.5rem 0 0;'>
    Gemini AI is scoring your performance across 5 competencies...</p>
    </div>""", unsafe_allow_html=True)

    prog  = st.progress(0)
    label = st.empty()

    steps = [
        (15, "📝 Processing transcript..."),
        (35, "🗣️ Scoring communication skills..."),
        (52, "💻 Evaluating technical knowledge..."),
        (68, "🧩 Assessing problem-solving..."),
        (80, "📄 Generating PDF report..."),
        (93, "💾 Saving to history..."),
    ]
    for pct, msg in steps:
        label.markdown(
            f"<p style='text-align:center;color:#aaa;margin:.3rem 0;'>{msg}</p>",
            unsafe_allow_html=True)
        prog.progress(pct)
        time.sleep(0.25)

    feedback = manager.evaluate_interview(
        transcript=transcript, questions=questions,
        expected_answers=expected, skills_to_test=skills,
        job_role=cfg["job_role"])

    pdf_buf = manager.generate_pdf_report(
        interview_data=cfg, feedback=feedback,
        candidate_name=AuthManager.get_current_user_name())

    pdf_path = None
    if pdf_buf:
        try:
            os.makedirs("interview_reports", exist_ok=True)
            fname = (f"interview_{iv_id}_"
                     f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            pdf_path = os.path.join("interview_reports", fname)
            with open(pdf_path, "wb") as f:
                f.write(pdf_buf.getvalue())
            pdf_buf.seek(0)
        except Exception as e:
            print(f"PDF save error: {e}")

    user_id = AuthManager.get_current_user_id()
    InterviewManager.save_feedback(
        interview_id=iv_id, user_id=user_id,
        transcript=transcript, feedback=feedback,
        pdf_path=pdf_path)

    gaps = feedback.get("skill_gaps", [])
    if gaps and user_id:
        try:
            CourseRecommendationManager.save_recommendations_for_user(
                user_id=user_id, resume_id=None,
                analysis_id=None, missing_skills=gaps)
        except Exception as e:
            print(f"Course rec error: {e}")

    prog.progress(100)
    label.empty()
    st.session_state.iv_feedback = feedback
    st.session_state.iv_pdf      = pdf_buf
    st.session_state.iv_phase    = "report"
    st.rerun()


# ──────────────────────────────────────────────────────────
# PHASE 4 — REPORT
# ──────────────────────────────────────────────────────────
def render_report():
    feedback   = st.session_state.iv_feedback
    cfg        = st.session_state.iv_cfg
    pdf_buf    = st.session_state.get("iv_pdf")
    transcript = st.session_state.get("iv_transcript", [])

    total = feedback.get("total_score", 0)
    sc, sl = _sc(total), _sl(total)

    # Score banner
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
    padding:2rem;border-radius:16px;margin-bottom:1.5rem;
    border:2px solid {sc};text-align:center;'>
    <div style='font-size:3.5rem;font-weight:800;color:{sc};line-height:1;'>{total}/100</div>
    <div style='font-size:1.3rem;color:white;margin:.4rem 0;'>{sl}</div>
    <div style='color:#aaa;font-size:.85rem;'>
    {cfg["job_role"]} &nbsp;·&nbsp; {cfg["difficulty"].capitalize()}
    &nbsp;·&nbsp; {datetime.now().strftime("%B %d, %Y")}
    </div>
    <div style='color:#666;font-size:.78rem;margin-top:.3rem;'>
    Filler words: {feedback.get("filler_word_count",0)} &nbsp;|&nbsp;
    Avg answer length: {feedback.get("avg_answer_length",0)} words
    </div>
    </div>""", unsafe_allow_html=True)

    # Action buttons
    ca, cb, cc = st.columns(3)
    with ca:
        if pdf_buf:
            pdf_buf.seek(0)
            st.download_button("📥 Download PDF Report", data=pdf_buf,
                file_name=f"interview_{cfg['job_role'].replace(' ','_')}_"
                          f"{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True, type="primary")
    with cb:
        if st.button("🎓 Learning Dashboard", use_container_width=True):
            st.session_state.page = "learning_dashboard"; st.rerun()
    with cc:
        if st.button("🔄 New Interview", use_container_width=True):
            _reset(); st.rerun()

    st.markdown("---")

    t1,t2,t3,t4,t5 = st.tabs([
        "📊 Scores","💬 Per-Question",
        "💪 Feedback","🎯 Skill Gaps","📝 Transcript"])

    # Tab 1 — scores
    with t1:
        cats = feedback.get("category_scores",{})
        for lbl, key in [
            ("🗣️ Communication",       "communication"),
            ("💻 Technical Knowledge",  "technical_knowledge"),
            ("🧩 Problem Solving",      "problem_solving"),
            ("😎 Confidence & Clarity", "confidence_clarity"),
            ("🎯 Answer Relevance",     "relevance"),
        ]:
            c  = cats.get(key,{}); sv = c.get("score",0); bc = _sc(sv)
            st.markdown(f"""
            <div style='margin-bottom:1.2rem;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
            <span style='color:#ddd;'>{lbl}</span>
            <span style='color:{bc};font-weight:700;'>{sv}/100 — {_sl(sv)}</span>
            </div>
            <div style='background:rgba(255,255,255,.07);border-radius:4px;height:8px;'>
            <div style='width:{sv}%;background:{bc};height:8px;border-radius:4px;'></div>
            </div>
            <p style='color:#666;font-size:.78rem;margin-top:4px;'>{c.get("comment","")[:250]}</p>
            </div>""", unsafe_allow_html=True)

    # Tab 2 — per-question
    with t2:
        pqf = feedback.get("per_question_feedback",[])
        if not pqf:
            st.info("No per-question breakdown available.")
        else:
            for i, qf in enumerate(pqf):
                qs = qf.get("score",0); qc = _sc(qs)
                with st.expander(
                    f"Q{i+1}  [{qs}/100]  "
                    f"{str(qf.get('question',''))[:60]}...",
                    expanded=(i==0)):
                    st.markdown(
                        f"**Score:** <span style='color:{qc};font-weight:700;'>"
                        f"{qs}/100 — {_sl(qs)}</span>",
                        unsafe_allow_html=True)
                    st.markdown(f"**Feedback:** {qf.get('feedback','')}")
                    if qf.get("suggested_rephrasing"):
                        st.info(f"💡 **Better answer:** {qf['suggested_rephrasing']}")
                    missed = qf.get("key_points_missed",[])
                    if missed:
                        st.markdown("**❌ Key points missed:** " +
                                    ", ".join(missed[:5]))

    # Tab 3 — feedback
    with t3:
        cs, ci = st.columns(2)
        with cs:
            st.markdown("### 💪 Strengths")
            st.success(feedback.get("strengths","N/A"))
        with ci:
            st.markdown("### 🔧 Areas to Improve")
            st.warning(feedback.get("areas_for_improvement","N/A"))
        st.markdown("### 🗺️ Improvement Plan")
        plan = feedback.get("improvement_plan","")
        for line in (plan.split("\n") if plan else []):
            if line.strip():
                st.markdown(f"✦ {line.strip()}")
        st.markdown("### 🏆 Final Assessment")
        st.info(feedback.get("final_assessment","N/A"))

    # Tab 4 — skill gaps
    with t4:
        gaps = feedback.get("skill_gaps",[])
        if not gaps:
            st.success("🎉 No major skill gaps — great performance!")
        else:
            st.markdown(f"### 🎯 {len(gaps)} Skill Gap(s) Found")
            cols = st.columns(min(len(gaps),4))
            for i,g in enumerate(gaps[:8]):
                with cols[i%4]:
                    st.markdown(f"""
                    <div style='background:rgba(244,67,54,.1);border:1px solid #f44336;
                    border-radius:8px;padding:8px 12px;text-align:center;
                    color:#ff6b6b;font-size:.83rem;font-weight:600;
                    margin-bottom:8px;'>{g}</div>""", unsafe_allow_html=True)
            st.markdown("---")
            st.success("✅ Courses added to your **Learning Dashboard** for these gaps!")
            if st.button("🎓 Go to Learning Dashboard →", type="primary"):
                st.session_state.page = "learning_dashboard"; st.rerun()

    # Tab 5 — transcript
    with t5:
        user_msgs = [m for m in transcript if m.get("role") == "user"]
        ai_msgs   = [m for m in transcript if m.get("role") == "assistant"]
        st.caption(f"{len(ai_msgs)} AI messages · {len(user_msgs)} answers captured")
        st.markdown("---")
        if not transcript:
            st.info("No transcript captured.")
        else:
            for msg in transcript:
                role, content = msg.get("role",""), msg.get("content","")
                if role == "assistant":
                    st.markdown(f"""
                    <div style='background:rgba(33,150,243,.08);
                    border-left:3px solid #2196F3;
                    padding:9px 14px;border-radius:0 8px 8px 0;margin-bottom:7px;'>
                    <span style='color:#64b5f6;font-size:.7rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:.5px;'>🤖 AI Interviewer</span><br>
                    <span style='color:#ddd;'>{content}</span></div>""",
                    unsafe_allow_html=True)
                elif role == "user":
                    st.markdown(f"""
                    <div style='background:rgba(76,175,80,.08);
                    border-left:3px solid #4CAF50;
                    padding:9px 14px;border-radius:0 8px 8px 0;margin-bottom:7px;'>
                    <span style='color:#81c784;font-size:.7rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:.5px;'>👤 Your Answer</span><br>
                    <span style='color:#ddd;'>{content}</span></div>""",
                    unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# HISTORY (called from user_history.py)
# ──────────────────────────────────────────────────────────
def render_interview_history():
    user_id    = AuthManager.get_current_user_id()
    interviews = InterviewManager.get_user_interviews(user_id)
    if not interviews:
        st.info("No mock interviews yet.")
        if st.button("🎤 Take Your First Interview", type="primary"):
            st.session_state.page = "mock_interview"; st.rerun()
        return

    st.markdown(f"**{len(interviews)} interview session(s)**")
    for iv in interviews:
        score    = iv.get("total_score")
        sc       = _sc(score) if score else "#888"
        date_str = iv["created_at"].strftime("%b %d, %Y")
        score_str = f"Score: {score}/100" if score else "Pending"
        with st.expander(
            f"🎤  {iv['job_role']}  ·  {iv['difficulty'].capitalize()}"
            f"  ·  {date_str}  ·  {score_str}"):
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Score", f"{score}/100" if score else "—")
            with c2:
                st.write(f"**Type:** {iv['interview_type'].capitalize()}")
                st.write(f"**Questions:** {iv['question_count']}")
            with c3:
                st.write(f"**Status:** {iv['status'].upper()}")
            if iv.get("pdf_path") and os.path.exists(iv["pdf_path"]):
                with open(iv["pdf_path"],"rb") as f:
                    st.download_button("📥 Download Report",
                        data=f.read(),
                        file_name=f"interview_{iv['id']}.pdf",
                        mime="application/pdf",
                        key=f"hist_{iv['id']}")
            if st.button("🔄 Retake", key=f"rt_{iv['id']}"):
                _reset(); st.session_state.page="mock_interview"; st.rerun()


# ──────────────────────────────────────────────────────────
# MAIN ENTRY
# ──────────────────────────────────────────────────────────
def _recover_session_from_db(interview_id: int):
    """
    If iv_q / iv_cfg are missing from session state (e.g. after a long popup session),
    reload them from the database so render_evaluating() doesn't crash.
    """
    if st.session_state.get("iv_q") and st.session_state.get("iv_cfg"):
        return  # already have everything we need

    try:
        row = InterviewManager.get_interview_by_id(interview_id)
        if not row:
            return
        st.session_state.iv_id     = interview_id
        st.session_state.iv_q      = row["questions"]
        st.session_state.iv_exp    = row["expected_answers"]
        st.session_state.iv_skills = row["skills_to_test"]
        st.session_state.iv_cfg    = {
            "job_role"       : row["job_role"],
            "difficulty"     : row["difficulty"],
            "interview_type" : row["interview_type"],
            "question_count" : row["question_count"],
        }
    except Exception as e:
        print(f"Session recovery failed: {e}")


def render_mock_interview():
    if not AuthManager.is_authenticated():
        st.warning("⚠️ Please log in to access Mock Interview")
        return

    InterviewManager.setup_interview_tables()
    manager = InterviewManager()

    # ── Receive transcript delivered by the interview popup ───────────────
    # The standalone interview page does:
    #   window.opener.location.href = window.location.origin + '/?iv_done=ID&iv_data=...'
    # OR if opener is null:
    #   window.location.href = same URL (popup tab navigates itself to Streamlit)
    # Either way, Streamlit reloads and we read st.query_params here.
    params = st.query_params
    if "iv_done" in params and "iv_data" in params:
        try:
            iv_done_id = int(params["iv_done"])
            raw        = params["iv_data"]
            transcript = json.loads(raw)

            if transcript:
                expected_id = st.session_state.get("iv_id")
                # Accept if IDs match OR if no ID in session (e.g. session expired)
                if expected_id is None or iv_done_id == expected_id:
                    st.session_state.iv_id        = iv_done_id
                    st.session_state.iv_transcript = transcript
                    # Recover iv_q / iv_cfg from DB if session state was lost
                    _recover_session_from_db(iv_done_id)
                    st.session_state.iv_phase      = "evaluating"
                    st.query_params.clear()
                    st.rerun()  # ← only rerun when we actually set the phase
                else:
                    # ID mismatch — clear params and continue normally
                    st.query_params.clear()
            else:
                st.query_params.clear()

        except Exception as e:
            print(f"iv_done param error: {e}")
            st.query_params.clear()

    phase = st.session_state.get("iv_phase", "setup")
    if   phase == "setup":      render_setup(manager)
    elif phase == "ready":      render_ready()
    elif phase == "live":       render_live()
    elif phase == "evaluating": render_evaluating(manager)
    elif phase == "report":     render_report()
    else:                       render_setup(manager)
