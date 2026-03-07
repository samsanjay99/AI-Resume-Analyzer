"""
Login Page for Multi-User System - Beautiful Sunset Theme
Adapted from animated-sign-up-design with flying birds and mountain animations
"""
import streamlit as st
from auth.auth_manager import AuthManager


def render_login_page():
    """Render the stunning sunset-themed login page"""
    
    # Hide default Streamlit UI immediately
    st.markdown("""
    <style>
    /* Hide everything until CSS loads */
    .stApp { opacity: 0; }
    </style>
    """, unsafe_allow_html=True)
    
    # Force style refresh - v4.0 (cache-busted)
    st.markdown("""
    <style>
    /* Show app after CSS loads */
    .stApp { opacity: 1 !important; transition: opacity 0.3s ease-in; }
    
    /* CRITICAL: Force override all Streamlit defaults - v4.0 */
    div[data-testid="stAppViewContainer"] > .main {
        padding: 0 !important;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Reset body and html - HIGHEST PRIORITY */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        min-height: 100vh !important;
        height: auto !important;
        overflow-x: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Beautiful Sunset Gradient Background with Flexbox Centering */
    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom, 
            #ffd1b3 0%,
            #ffb3ba 40%,
            #d4a5d4 100%
        ) !important;
        display: flex !important;
        align-items: flex-start !important;\n        padding-top: 2vh !important;
        justify-content: center !important;
        position: relative !important;
    }
    
    /* Ensure main container is centered */
    .main, .main .block-container {
        padding: 0 !important;
        max-width: none !important;
        flex: 1 !important;
        display: flex !important;
        align-items: flex-start !important;\n        padding-top: 2vh !important;
        justify-content: center !important;
    }
    
    /* Animated Sun */
    .sun {
        position: fixed;
        top: 50px;
        right: 80px;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.4) 50%, transparent 70%);
        box-shadow: 0 0 80px 30px rgba(255, 255, 255, 0.3);
        animation: sunPulse 4s ease-in-out infinite;
        z-index: 1;
    }
    
    @keyframes sunPulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    
    /* Flying Birds */
    .bird {
        position: fixed;
        width: 40px;
        height: 40px;
        z-index: 2;
        opacity: 0;
    }
    
    .bird svg {
        width: 100%;
        height: 100%;
    }
    
    .bird1 {
        animation: flyBird1 15s linear infinite;
        top: 80px;
    }
    
    .bird2 {
        animation: flyBird2 18s linear infinite 3s;
        top: 120px;
    }
    
    .bird3 {
        animation: flyBird3 16s linear infinite 6s;
        top: 60px;
    }
    
    .bird4 {
        animation: flyBird4 20s linear infinite 9s;
        top: 100px;
    }
    
    .bird5 {
        animation: flyBird5 17s linear infinite 12s;
        top: 140px;
    }
    
    @keyframes flyBird1 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird2 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.8; }
        90% { opacity: 0.8; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird3 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.9; }
        90% { opacity: 0.9; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird4 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.7; }
        90% { opacity: 0.7; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird5 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.85; }
        90% { opacity: 0.85; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    /* Floating Particles */
    .particle {
        position: fixed;
        width: 4px;
        height: 4px;
        background: white;
        border-radius: 50%;
        opacity: 0.4;
        animation: floatParticle 4s ease-in-out infinite;
        z-index: 2;
    }
    
    @keyframes floatParticle {
        0%, 100% { transform: translateY(0) scale(1); opacity: 0.2; }
        50% { transform: translateY(-30px) scale(1.5); opacity: 0.6; }
    }
    
    .particle1 { left: 10%; top: 20%; animation-delay: 0s; }
    .particle2 { left: 25%; top: 35%; animation-delay: 1s; }
    .particle3 { left: 70%; top: 25%; animation-delay: 2s; }
    .particle4 { left: 85%; top: 40%; animation-delay: 1.5s; }
    .particle5 { left: 50%; top: 15%; animation-delay: 0.5s; }
    .particle6 { left: 15%; top: 50%; animation-delay: 2.5s; }
    .particle7 { left: 90%; top: 30%; animation-delay: 3s; }
    
    /* Mountain Layers */
    .mountains {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        z-index: 3;
        pointer-events: none;
    }
    
    .mountain-layer {
        position: absolute;
        bottom: 0;
        width: 100%;
        animation: mountainFloat 8s ease-in-out infinite;
    }
    
    .mountain1 {
        height: 250px;
        background: #9b7cb6;
        clip-path: polygon(0% 100%, 10% 60%, 20% 70%, 30% 50%, 40% 65%, 50% 55%, 60% 70%, 70% 50%, 80% 65%, 90% 60%, 100% 100%);
        animation-delay: 0s;
    }
    
    .mountain2 {
        height: 180px;
        background: #b8a1c9;
        clip-path: polygon(0% 100%, 15% 70%, 25% 60%, 40% 75%, 55% 65%, 70% 70%, 85% 60%, 100% 100%);
        animation-delay: 0.5s;
    }
    
    .mountain3 {
        height: 120px;
        background: #d4b5c4;
        clip-path: polygon(0% 100%, 20% 75%, 35% 70%, 50% 80%, 65% 75%, 80% 70%, 100% 100%);
        animation-delay: 1s;
    }
    
    @keyframes mountainFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    /* Glassmorphism Container - Compact and Centered */
    div[data-testid="stForm"] {
        position: relative;
        width: min(380px, 92vw);
        padding: 1.6rem 1.6rem;
        background: rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.15),
            inset 0 0 20px rgba(255, 255, 255, 0.1);
        z-index: 10;
        animation: slideUp 0.8s ease-out;
        margin: 2rem auto;
        overflow: visible !important;
        }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(50px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Remove scroll from form */
    div[data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
        overflow: visible !important;
    }
    
    div[data-testid="stForm"] > div {
        overflow: visible !important;
    }
    
    section.main {
        overflow: hidden !important;
    }
    
    /* Title Styling - Compact */
    .auth-title {
        text-align: center;
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        margin-top: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    
    .auth-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin-bottom: 1rem;
        margin-top: 0;
        font-weight: 500;
    }
    
    /* Hide the link icon after title - aggressive */
    span[data-testid="stHeaderActionElements"],
    .st-emotion-cache-gi0tri,
    .et2rgd23,
    a.st-emotion-cache-ubko3j,
    .et2rgd21,
    h1 span,
    h1 a {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    /* Input Field Styling */
    .stTextInput > div > div > input {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 0 !important;
        color: white !important;
        padding: 0.55rem 0.3rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-bottom: 2px solid white !important;
        box-shadow: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stTextInput > label {
        display: none !important;
    }
    
    /* Minimal spacing between inputs */
    .stTextInput {
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
    }
    
    .stTextInput > div {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2d1b4e, #4a2c6d) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.7rem 1.5rem !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(45, 27, 78, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(45, 27, 78, 0.5) !important;
        background: linear-gradient(135deg, #4a2c6d, #6b3fa0) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Hide checkbox and forgot password to save space */
    .stCheckbox {
        display: none !important;
    }
    
    /* Checkbox Styling */
    .stCheckbox {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.6rem !important;
    }
    
    .stCheckbox > label {
        font-size: 0.6rem !important;
    }
    
    /* Link Styling */
    a {
        color: rgba(255, 255, 255, 0.9) !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }
    
    a:hover {
        color: white !important;
        text-decoration: underline !important;
    }
    
    /* Footer - Compact */
    .auth-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.85rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Gradient Overlay */
    .gradient-overlay {
        position: fixed;
        inset: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.1), transparent);
        pointer-events: none;
        z-index: 4;
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stInfo {
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    </style>
    
    <!-- Animated Sun -->
    <div class="sun"></div>
    
    <!-- Flying Birds -->
    <div class="bird bird1">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird2">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird3">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird4">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird5">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    
    <!-- Floating Particles -->
    <div class="particle particle1"></div>
    <div class="particle particle2"></div>
    <div class="particle particle3"></div>
    <div class="particle particle4"></div>
    <div class="particle particle5"></div>
    <div class="particle particle6"></div>
    <div class="particle particle7"></div>
    
    <!-- Mountain Layers -->
    <div class="mountains">
        <div class="mountain-layer mountain1"></div>
        <div class="mountain-layer mountain2"></div>
        <div class="mountain-layer mountain3"></div>
    </div>
    
    <!-- Gradient Overlay -->
    <div class="gradient-overlay"></div>
    """, unsafe_allow_html=True)
    
    # Login form with title INSIDE
    with st.form("login_form", clear_on_submit=False):
        # Title and subtitle INSIDE form (so they're in glass container)
        st.markdown('<div class="auth-title">Login Form</div>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Welcome back! Please login to your account</p>', unsafe_allow_html=True)
        
        # Email input
        email = st.text_input("📧 Email", placeholder="Enter your email", key="login_email")
        
        # Password input
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
        
        # Remember me and forgot password - HIDDEN TO SAVE SPACE
        # col_check, col_forgot = st.columns(2)
        # with col_check:
        #     remember = st.checkbox("Remember me", key="remember_me")
        # with col_forgot:
        #     st.markdown('<a href="#" style="float: right; margin-top: 0.1rem; color: rgba(255,255,255,0.9);">Forgot password?</a>', unsafe_allow_html=True)
        
        # Submit buttons
        col_a, col_b = st.columns(2)
        with col_a:
            submit = st.form_submit_button("🚀 Log In", use_container_width=True, type="primary")
        with col_b:
            signup_btn = st.form_submit_button("✨ Sign Up", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("⚠️ Please enter both email and password")
            else:
                with st.spinner("🔍 Authenticating..."):
                    result = AuthManager.authenticate_user(email, password)
                    
                    if result['success']:
                        AuthManager.login_user(result['user'])
                        st.success(f"✅ Welcome back, {result['user'].get('full_name', email)}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
        
        if signup_btn:
            st.session_state['show_signup'] = True
            st.rerun()
        
        # Footer INSIDE form (so it's in glass container) - MINIMAL
        st.markdown('''
        <div class="auth-footer">
            <p style="color: rgba(255,255,255,0.95); font-size: 1rem; font-weight: 600;">Don't have an account? <a href="#" onclick="return false;" style="color: white; font-weight: 700;"><strong>Register</strong></a></p>
        </div>
        ''', unsafe_allow_html=True)
    # End form


def render_signup_page():
    """Render the stunning sunset-themed signup page"""
    
    # Hide default Streamlit UI immediately
    st.markdown("""
    <style>
    /* Hide everything until CSS loads */
    .stApp { opacity: 0; }
    </style>
    """, unsafe_allow_html=True)
    
    # Force style refresh - v4.0 (cache-busted)
    st.markdown("""
    <style>
    /* Show app after CSS loads */
    .stApp { opacity: 1 !important; transition: opacity 0.3s ease-in; }
    
    /* CRITICAL: Force override all Streamlit defaults - v4.0 */
    div[data-testid="stAppViewContainer"] > .main {
        padding: 0 !important;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Reset body and html - HIGHEST PRIORITY */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        min-height: 100vh !important;
        height: auto !important;
        overflow-x: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Beautiful Sunset Gradient Background with Flexbox Centering */
    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom, 
            #ffd1b3 0%,
            #ffb3ba 40%,
            #d4a5d4 100%
        ) !important;
        display: flex !important;
        align-items: flex-start !important;\n        padding-top: 2vh !important;
        justify-content: center !important;
        position: relative !important;
    }
    
    /* Ensure main container is centered */
    .main, .main .block-container {
        padding: 0 !important;
        max-width: none !important;
        flex: 1 !important;
        display: flex !important;
        align-items: flex-start !important;\n        padding-top: 2vh !important;
        justify-content: center !important;
    }
    
    /* Animated Sun */
    .sun {
        position: fixed;
        top: 50px;
        right: 80px;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.4) 50%, transparent 70%);
        box-shadow: 0 0 80px 30px rgba(255, 255, 255, 0.3);
        animation: sunPulse 4s ease-in-out infinite;
        z-index: 1;
    }
    
    @keyframes sunPulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    
    /* Flying Birds */
    .bird {
        position: fixed;
        width: 40px;
        height: 40px;
        z-index: 2;
        opacity: 0;
    }
    
    .bird svg {
        width: 100%;
        height: 100%;
    }
    
    .bird1 {
        animation: flyBird1 15s linear infinite;
        top: 80px;
    }
    
    .bird2 {
        animation: flyBird2 18s linear infinite 3s;
        top: 120px;
    }
    
    .bird3 {
        animation: flyBird3 16s linear infinite 6s;
        top: 60px;
    }
    
    .bird4 {
        animation: flyBird4 20s linear infinite 9s;
        top: 100px;
    }
    
    .bird5 {
        animation: flyBird5 17s linear infinite 12s;
        top: 140px;
    }
    
    @keyframes flyBird1 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird2 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.8; }
        90% { opacity: 0.8; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird3 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.9; }
        90% { opacity: 0.9; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird4 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.7; }
        90% { opacity: 0.7; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    @keyframes flyBird5 {
        0% { left: -100px; opacity: 0; }
        10% { opacity: 0.85; }
        90% { opacity: 0.85; }
        100% { left: calc(100% + 100px); opacity: 0; }
    }
    
    /* Floating Particles */
    .particle {
        position: fixed;
        width: 4px;
        height: 4px;
        background: white;
        border-radius: 50%;
        opacity: 0.4;
        animation: floatParticle 4s ease-in-out infinite;
        z-index: 2;
    }
    
    @keyframes floatParticle {
        0%, 100% { transform: translateY(0) scale(1); opacity: 0.2; }
        50% { transform: translateY(-30px) scale(1.5); opacity: 0.6; }
    }
    
    .particle1 { left: 10%; top: 20%; animation-delay: 0s; }
    .particle2 { left: 25%; top: 35%; animation-delay: 1s; }
    .particle3 { left: 70%; top: 25%; animation-delay: 2s; }
    .particle4 { left: 85%; top: 40%; animation-delay: 1.5s; }
    .particle5 { left: 50%; top: 15%; animation-delay: 0.5s; }
    .particle6 { left: 15%; top: 50%; animation-delay: 2.5s; }
    .particle7 { left: 90%; top: 30%; animation-delay: 3s; }
    
    /* Mountain Layers */
    .mountains {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        z-index: 3;
        pointer-events: none;
    }
    
    .mountain-layer {
        position: absolute;
        bottom: 0;
        width: 100%;
        animation: mountainFloat 8s ease-in-out infinite;
    }
    
    .mountain1 {
        height: 250px;
        background: #9b7cb6;
        clip-path: polygon(0% 100%, 10% 60%, 20% 70%, 30% 50%, 40% 65%, 50% 55%, 60% 70%, 70% 50%, 80% 65%, 90% 60%, 100% 100%);
        animation-delay: 0s;
    }
    
    .mountain2 {
        height: 180px;
        background: #b8a1c9;
        clip-path: polygon(0% 100%, 15% 70%, 25% 60%, 40% 75%, 55% 65%, 70% 70%, 85% 60%, 100% 100%);
        animation-delay: 0.5s;
    }
    
    .mountain3 {
        height: 120px;
        background: #d4b5c4;
        clip-path: polygon(0% 100%, 20% 75%, 35% 70%, 50% 80%, 65% 75%, 80% 70%, 100% 100%);
        animation-delay: 1s;
    }
    
    @keyframes mountainFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    /* Glassmorphism Container - Compact and Centered */
    div[data-testid="stForm"] {
        position: relative;
        width: min(380px, 92vw);
        padding: 1.6rem 1.6rem;
        background: rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.15),
            inset 0 0 20px rgba(255, 255, 255, 0.1);
        z-index: 10;
        animation: slideUp 0.8s ease-out;
        margin: 2rem auto;
        overflow: visible !important;
        }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(50px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Remove scroll from form */
    div[data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
        overflow: visible !important;
    }
    
    div[data-testid="stForm"] > div {
        overflow: visible !important;
    }
    
    section.main {
        overflow: hidden !important;
    }
    
    /* Title Styling - Compact */
    .auth-title {
        text-align: center;
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        margin-top: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    
    .auth-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin-bottom: 1rem;
        margin-top: 0;
        font-weight: 500;
    }
    
    /* Input Field Styling */
    .stTextInput > div > div > input {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 0 !important;
        color: white !important;
        padding: 0.55rem 0.3rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-bottom: 2px solid white !important;
        box-shadow: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stTextInput > label {
        display: none !important;
    }
    
    /* Minimal spacing between inputs */
    .stTextInput {
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
    }
    
    .stTextInput > div {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2d1b4e, #4a2c6d) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.7rem 1.5rem !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(45, 27, 78, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(45, 27, 78, 0.5) !important;
        background: linear-gradient(135deg, #4a2c6d, #6b3fa0) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Footer - Compact */
    .auth-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.85rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Gradient Overlay */
    .gradient-overlay {
        position: fixed;
        inset: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.1), transparent);
        pointer-events: none;
        z-index: 4;
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stInfo {
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    </style>
    
    <!-- Animated Sun -->
    <div class="sun"></div>
    
    <!-- Flying Birds -->
    <div class="bird bird1">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird2">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird3">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird4">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    <div class="bird bird5">
        <svg viewBox="0 0 40 40">
            <path d="M5 20 Q15 10 20 20 Q25 10 35 20" stroke="#2d1b4e" stroke-width="2" fill="none">
                <animate attributeName="d" 
                    values="M5 20 Q15 10 20 20 Q25 10 35 20;
                            M5 20 Q15 25 20 20 Q25 25 35 20;
                            M5 20 Q15 10 20 20 Q25 10 35 20"
                    dur="0.8s" repeatCount="indefinite"/>
            </path>
        </svg>
    </div>
    
    <!-- Floating Particles -->
    <div class="particle particle1"></div>
    <div class="particle particle2"></div>
    <div class="particle particle3"></div>
    <div class="particle particle4"></div>
    <div class="particle particle5"></div>
    <div class="particle particle6"></div>
    <div class="particle particle7"></div>
    
    <!-- Mountain Layers -->
    <div class="mountains">
        <div class="mountain-layer mountain1"></div>
        <div class="mountain-layer mountain2"></div>
        <div class="mountain-layer mountain3"></div>
    </div>
    
    <!-- Gradient Overlay -->
    <div class="gradient-overlay"></div>
    """, unsafe_allow_html=True)
    
    # Signup form with title INSIDE
    with st.form("signup_form", clear_on_submit=True):
        # Title and subtitle INSIDE form (so they're in glass container)
        st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Join us today and get started</p>', unsafe_allow_html=True)
        
        # Full Name
        full_name = st.text_input("👤 Full Name", placeholder="Enter your full name", key="signup_name")
        
        # Email
        email = st.text_input("📧 Email", placeholder="Enter your email", key="signup_email")
        
        # Password
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password", key="signup_password")
        
        # Confirm Password
        password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password", key="signup_password_confirm")
        
        col_a, col_b = st.columns(2)
        with col_a:
            submit = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
        with col_b:
            back_btn = st.form_submit_button("← Back to Login", use_container_width=True)
        
        if submit:
            # Validation
            if not email or not password or not full_name:
                st.error("⚠️ Please fill in all required fields")
            elif len(password) < 6:
                st.error("⚠️ Password must be at least 6 characters long")
            elif password != password_confirm:
                st.error("⚠️ Passwords do not match")
            else:
                with st.spinner("✨ Creating your account..."):
                    result = AuthManager.create_user(email, password, full_name)
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.info("🎉 Logging you in...")
                        st.balloons()
                        # Auto-login the user
                        AuthManager.login_user(result['user'])
                        st.session_state['show_signup'] = False
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
        
        if back_btn:
            st.session_state['show_signup'] = False
            st.rerun()
        
        # Footer INSIDE form (so it's in glass container) - MINIMAL for signup
        st.markdown('''
        <div class="auth-footer">
            <p style="color: rgba(255,255,255,0.95); font-size: 1rem; font-weight: 600;">Already have an account? <a href="#" onclick="return false;" style="color: white; font-weight: 700;"><strong>Login</strong></a></p>
        </div>
        ''', unsafe_allow_html=True)
    # End form
