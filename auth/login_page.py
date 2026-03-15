"""
Login Page - Glass card over background image
"""
import streamlit as st
import base64
import os
from auth.auth_manager import AuthManager


def _get_bg_b64():
    for path in ["assets/login.jpeg", "login.jpeg"]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""


def _inject_base_css(bg_b64):
    if bg_b64:
        bg_css = f'url("data:image/jpeg;base64,{bg_b64}") center center / cover no-repeat fixed'
    else:
        bg_css = "linear-gradient(135deg,#1a1a2e,#16213e)"

    st.markdown(f"""
    <style>
    #MainMenu, footer, header, .stDeployButton {{visibility: hidden;}}
    [data-testid="stSidebar"] {{display: none !important;}}
    [data-testid="stHeader"] {{background: transparent !important;}}

    /* Flash prevention overlay - covers unstyled flash, fades out after 0.4s */
    [data-testid="stAppViewContainer"]::after {{
        content: "";
        position: fixed;
        inset: 0;
        background: #0f172a;
        z-index: 99999;
        animation: fadeOutOverlay 0.01s 0.4s forwards;
    }}
    @keyframes fadeOutOverlay {{
        to {{ opacity: 0; pointer-events: none; visibility: hidden; }}
    }}

    [data-testid="stAppViewContainer"] {{
        background: {bg_css} !important;
        min-height: 100vh;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: linear-gradient(to right, rgba(0,0,0,0.18), rgba(0,0,0,0.05), rgba(0,0,0,0));
        pointer-events: none;
        z-index: 0;
    }}

    .block-container {{
        padding: 2rem 1rem !important;
        max-width: 100% !important;
        min-height: 100vh !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        padding-left: 12vw !important;
    }}

    div[data-testid="stForm"] form {{
        background: rgba(255,255,255,0.28) !important;
        backdrop-filter: blur(40px) !important;
        -webkit-backdrop-filter: blur(40px) !important;
        border: 1px solid rgba(255,255,255,0.45) !important;
        border-radius: 24px !important;
        padding: 2.5rem 2rem !important;
        box-shadow: 0 8px 40px rgba(0,0,0,0.45) !important;
    }}
    div[data-testid="stForm"] {{
        max-width: 440px !important;
        width: 100% !important;
    }}

    .stTextInput > div > div > input {{
        border-radius: 10px !important;
        border: 1.5px solid rgba(255,255,255,0.4) !important;
        padding: 0.72rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        background: rgba(255,255,255,0.15) !important;
        color: #ffffff !important;
        min-height: 48px !important;
    }}
    .stTextInput > div > div > input::placeholder {{color: rgba(255,255,255,0.6) !important;}}
    .stTextInput > div > div > input:focus {{
        border-color: rgba(255,255,255,0.75) !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.15) !important;
        background: rgba(255,255,255,0.22) !important;
        outline: none !important;
    }}
    .stTextInput label {{
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}

    .stFormSubmitButton > button {{
        width: 100% !important;
        border-radius: 11px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        min-height: 48px !important;
        border: none !important;
        background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.45) !important;
        cursor: pointer !important;
    }}
    .stFormSubmitButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(99,102,241,0.6) !important;
    }}

    .stButton > button {{
        width: 100% !important;
        max-width: 440px !important;
        border-radius: 11px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        min-height: 48px !important;
        background: rgba(255,255,255,0.1) !important;
        border: 1.5px solid rgba(255,255,255,0.3) !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }}
    .stButton > button:hover {{
        background: rgba(255,255,255,0.18) !important;
        border-color: rgba(255,255,255,0.5) !important;
    }}

    .stAlert {{border-radius: 10px !important; font-size: 0.9rem !important;}}

    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            justify-content: center !important;
        }}
        div[data-testid="stForm"] {{max-width: 100% !important;}}
    }}
    </style>
    """, unsafe_allow_html=True)


def render_login_page():
    bg = _get_bg_b64()
    _inject_base_css(bg)

    with st.form("login_form"):
        st.markdown("""
        <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:1.2rem;">
            <span style="font-size:1.6rem;">&#129504;</span>
            <span style="font-size:1.1rem;font-weight:800;color:#fff;">AI Resume Analyzer</span>
        </div>
        <div style="font-size:1.9rem;font-weight:800;color:#fff;margin-bottom:.4rem;">Welcome Back</div>
        <div style="font-size:1rem;color:rgba(255,255,255,.85);margin-bottom:1.6rem;line-height:1.5;font-weight:500;">
            Login to analyze your resume and unlock AI career insights.
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="........")
        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Login", use_container_width=True)
        with col2:
            signup_clicked = st.form_submit_button("Create Account", use_container_width=True)

        st.markdown("""
        <div style="text-align:center;font-size:.82rem;color:rgba(255,255,255,.65);margin-top:1.2rem;font-weight:500;">
            By continuing you agree to our Terms &amp; Privacy Policy
        </div>
        """, unsafe_allow_html=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            result = AuthManager.authenticate_user(email, password)
            if result.get("success"):
                AuthManager.login_user(result["user"])
                st.success("Login successful!")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error(result.get("message", "Login failed."))

    if signup_clicked:
        st.session_state["show_signup"] = True
        st.rerun()


def render_signup_page():
    bg = _get_bg_b64()
    _inject_base_css(bg)

    with st.form("signup_form"):
        st.markdown("""
        <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:1.2rem;">
            <span style="font-size:1.6rem;">&#129504;</span>
            <span style="font-size:1.1rem;font-weight:800;color:#fff;">AI Resume Analyzer</span>
        </div>
        <div style="font-size:1.9rem;font-weight:800;color:#fff;margin-bottom:.4rem;">Create Account</div>
        <div style="font-size:1rem;color:rgba(255,255,255,.85);margin-bottom:1.6rem;line-height:1.5;font-weight:500;">
            Start improving your resume with AI-powered insights.
        </div>
        """, unsafe_allow_html=True)

        name = st.text_input("Full Name", placeholder="Jane Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Create Account", use_container_width=True)
        with col2:
            back_clicked = st.form_submit_button("Back to Login", use_container_width=True)

        st.markdown("""
        <div style="text-align:center;font-size:.82rem;color:rgba(255,255,255,.65);margin-top:1.2rem;font-weight:500;">
            By continuing you agree to our Terms &amp; Privacy Policy
        </div>
        """, unsafe_allow_html=True)

    if submitted:
        if not name or not email or not password:
            st.error("Please fill in all fields.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            result = AuthManager.create_user(email, password, name)
            if result.get("success"):
                AuthManager.login_user(result["user"])
                st.success("Account created successfully!")
                st.session_state["show_signup"] = False
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error(result.get("message", "Registration failed."))

    if back_clicked:
        st.session_state["show_signup"] = False
        st.rerun()
