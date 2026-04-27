"""
Video Player Page
In-app YouTube embed with watch-time tracking and certificate generation.
"""
import streamlit as st
import time
from auth.auth_manager import AuthManager
from utils.certificate_manager import (
    setup_certificate_tables, save_progress, get_progress,
    is_completed, generate_certificate, get_certificate, _delete_certificate
)


def render_video_player():
    """Render the in-app video player with progress tracking and certificate."""

    if not AuthManager.is_authenticated():
        st.error("Please login to watch videos.")
        return

    setup_certificate_tables()

    user_id   = AuthManager.get_current_user_id()
    user_name = st.session_state.get("user_name", "Learner")

    course = st.session_state.get("current_video")
    if not course:
        st.warning("No video selected. Go back to the Learning Dashboard.")
        if st.button("← Back to Learning Dashboard"):
            st.session_state.page = "learning_dashboard"
            st.rerun()
        return

    video_id = course["youtube_video_id"]
    title    = course["course_title"]
    channel  = course["channel_name"]
    skill    = course["skill_covered"]

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:16px;
    padding:1.5rem 2rem;margin-bottom:1.5rem;border:1px solid rgba(0,255,136,0.2);'>
    <h2 style='color:#f0f0ff;margin:0 0 0.3rem 0;font-size:1.4rem;'>{title}</h2>
    <p style='color:#a0a0c0;margin:0;font-size:0.9rem;'>
        📺 {channel} &nbsp;·&nbsp;
        <span style='background:rgba(0,255,136,0.1);color:#00ff88;border:1px solid rgba(0,255,136,0.25);
        padding:2px 10px;border-radius:50px;font-size:0.78rem;font-weight:600;'>{skill}</span>
    </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back to Learning Dashboard", key="back_btn"):
        st.session_state.page = "learning_dashboard"
        st.rerun()

    st.markdown("---")

    # ── Embedded video ────────────────────────────────────────────────────────
    embed_url = f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
    st.markdown(f"""
    <div style='border-radius:14px;overflow:hidden;border:2px solid rgba(0,255,136,0.25);
    box-shadow:0 8px 32px rgba(0,0,0,0.5);'>
    <iframe width="100%" height="480"
        src="{embed_url}"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Watch-time tracking ───────────────────────────────────────────────────
    progress     = get_progress(user_id, video_id)
    already_done = progress["completed"]

    session_key = f"watch_start_{video_id}"
    elapsed_key = f"watch_elapsed_{video_id}"

    if session_key not in st.session_state:
        st.session_state[session_key] = time.time()
    if elapsed_key not in st.session_state:
        st.session_state[elapsed_key] = progress["watch_time"]

    session_seconds = int(time.time() - st.session_state[session_key])
    total_seconds   = st.session_state[elapsed_key] + session_seconds

    COMPLETION_THRESHOLD = 60
    completed  = already_done or (total_seconds >= COMPLETION_THRESHOLD)
    pct        = min(100, int((total_seconds / COMPLETION_THRESHOLD) * 100))
    bar_color  = "#00ff88" if completed else "#00b4ff"
    status_txt = "✅ Completed!" if completed else f"⏱ {total_seconds}s watched — need {COMPLETION_THRESHOLD}s"

    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:1rem 1.2rem;
    border:1px solid rgba(255,255,255,0.08);margin-bottom:1rem;'>
    <div style='display:flex;justify-content:space-between;margin-bottom:0.5rem;'>
        <span style='color:#a0a0c0;font-size:0.85rem;'>Watch Progress</span>
        <span style='color:{bar_color};font-size:0.85rem;font-weight:600;'>{status_txt}</span>
    </div>
    <div style='background:rgba(255,255,255,0.08);border-radius:50px;height:8px;'>
        <div style='background:{bar_color};width:{pct}%;height:8px;border-radius:50px;
        box-shadow:0 0 8px {bar_color};'></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Progress", use_container_width=True, key="save_progress_btn"):
            save_progress(user_id, video_id, total_seconds, completed)
            st.session_state[elapsed_key] = total_seconds
            st.session_state[session_key] = time.time()
            st.success("Progress saved! ✅" if completed else f"Saved — {total_seconds}s watched.")
    with col2:
        if st.button("🔄 Refresh Timer", use_container_width=True, key="refresh_timer_btn"):
            st.rerun()

    # ── Certificate section ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("<h3 style='color:#f0f0ff;'>🎓 Certificate</h3>", unsafe_allow_html=True)

    if not completed:
        st.markdown(f"""
        <div style='background:rgba(255,180,0,0.08);border:1px solid rgba(255,180,0,0.25);
        border-radius:12px;padding:1rem 1.2rem;color:#ffd700;'>
        ⚠️ Watch at least <strong>{COMPLETION_THRESHOLD} seconds</strong> to unlock your certificate.
        Currently at <strong>{total_seconds}s</strong>.
        </div>
        """, unsafe_allow_html=True)
        return

    save_progress(user_id, video_id, total_seconds, True)

    existing_cert = get_certificate(user_id, video_id)

    if existing_cert:
        st.success("🎉 Certificate already generated!")
        _show_certificate_ui(existing_cert, user_name, skill, key_suffix="existing")
        if st.button("🔄 Regenerate Certificate", key="regen_cert_btn", use_container_width=True):
            _delete_certificate(user_id, video_id)
            st.session_state.pop("last_certificate", None)
            st.rerun()
    else:
        st.success("🎉 Video completed! You can now generate your certificate.")
        if st.button("🏆 Generate Certificate", type="primary", use_container_width=True, key="gen_cert_btn"):
            with st.spinner("Generating your certificate..."):
                try:
                    result = generate_certificate(user_name, skill, user_id, video_id)
                    st.session_state["last_certificate"] = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Certificate generation failed: {e}")

    if "last_certificate" in st.session_state and not existing_cert:
        _show_certificate_ui(st.session_state["last_certificate"], user_name, skill, key_suffix="new")


def _show_certificate_ui(cert: dict, user_name: str, skill: str, key_suffix: str = ""):
    """Display certificate preview and download buttons."""
    st.markdown(f"""
    <div style='background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.25);
    border-radius:12px;padding:1rem 1.2rem;margin:1rem 0;'>
    <p style='color:#00ff88;font-weight:700;margin:0 0 0.3rem 0;'>✅ Certificate Ready</p>
    <p style='color:#a0a0c0;font-size:0.85rem;margin:0;'>
        ID: <code style='color:#00b4ff;'>{cert.get("certificate_id","")}</code>
        &nbsp;·&nbsp; Date: {cert.get("date","")}
    </p>
    </div>
    """, unsafe_allow_html=True)

    if cert.get("png_bytes"):
        st.image(cert["png_bytes"], caption=f"Certificate — {skill}", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if cert.get("png_bytes"):
            st.download_button(
                "⬇ Download PNG",
                data=cert["png_bytes"],
                file_name=f"certificate_{skill.replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True,
                key=f"dl_png_{key_suffix}",
            )
    with col2:
        if cert.get("pdf_bytes"):
            st.download_button(
                "⬇ Download PDF",
                data=cert["pdf_bytes"],
                file_name=f"certificate_{skill.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"dl_pdf_{key_suffix}",
            )
