import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# Mengimpor modul dari engine.py
from engine import (
    init_db, register_user, authenticate_user, 
    save_respondent_data, save_capability_data, load_latest_respondent_data,
    calc_fuzzy_5, calc_fuzzy_3, calc_percentage_avg, calc_risk_profile,
    save_individual_answers, get_user_submission_status, get_user_saved_answers,
    get_all_submitted_respondents, aggregate_two_respondents,
    get_rating_level_cobit, generate_pdf_report, DB_FILE,
    load_checklist_questions, save_individual_checklist, get_user_checklist_answers,
    get_user_checklist_status, get_all_checklist_submitted_respondents,
    calculate_domain_checklist_score, get_preset_skripsi_capability
)

# Inisialisasi Database
init_db()

# ==========================================
# PAGE CONFIGURATION & METADATA
# ==========================================
st.set_page_config(
    page_title="COBIT 2019 Governance & Fuzzy Logic - UNKLAB",
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto"
)

# ==========================================
# ENTERPRISE & RESPONSIVE DESIGN SYSTEM (MOBILE-READY)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
        -webkit-font-smoothing: antialiased;
    }

    /* Mencegah overflow horizontal pada layar smartphone */
    html, body, .main, [data-testid="stAppViewContainer"], .block-container {
        max-width: 100% !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }

    .main {
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%);
    }

    /* Responsive Block Container Padding */
    @media (max-width: 768px) {
        .block-container {
            padding: 1.25rem 0.85rem !important;
        }
    }

    /* Executive Hero Header (Desktop & Mobile Adaptive) */
    .cobit-hero-header {
        background: linear-gradient(135deg, #091E3A 0%, #102A4E 40%, #1A365D 70%, #0F284B 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -5px rgba(9, 30, 58, 0.35);
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
    }
    
    .cobit-hero-header::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.22) 0%, rgba(79, 70, 229, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .cobit-badge-ribbon {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #38BDF8;
        margin-bottom: 10px;
        max-width: 100%;
        word-break: break-word;
    }

    .cobit-title {
        font-size: clamp(1.25rem, 3.2vw, 1.85rem);
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.25;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF 0%, #E2E8F0 50%, #BAE6FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        word-wrap: break-word;
    }

    .cobit-subtitle {
        font-size: clamp(0.78rem, 2vw, 0.92rem);
        color: #94A3B8;
        margin-top: 8px;
        margin-bottom: 0;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        line-height: 1.4;
    }

    /* Penyesuaian khusus Header di Mobile */
    @media (max-width: 768px) {
        .cobit-hero-header {
            padding: 16px 18px !important;
            border-radius: 12px !important;
            margin-bottom: 15px !important;
        }
        .cobit-badge-ribbon {
            font-size: 0.65rem !important;
            padding: 3px 9px !important;
        }
        .cobit-subtitle {
            font-size: 0.78rem !important;
            gap: 4px !important;
        }
    }

    /* Executive Metric & Stat Cards */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05);
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }

    .kpi-card-cobit { border-top: 4px solid #1E3A8A; }
    .kpi-card-fuzzy { border-top: 4px solid #4F46E5; }
    .kpi-card-teal  { border-top: 4px solid #0D9488; }
    .kpi-card-gold  { border-top: 4px solid #F59E0B; }

    .kpi-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: clamp(1.4rem, 2.5vw, 1.85rem);
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }

    .kpi-desc {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Login Portal Card */
    .auth-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px 26px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.08);
        margin: 0 auto 20px auto;
        max-width: 540px;
        width: 100%;
        box-sizing: border-box;
    }

    @media (max-width: 768px) {
        .auth-card {
            padding: 18px 16px !important;
            border-radius: 12px !important;
        }
    }

    /* User Profile Card & Sidebar Navigation Enhancements */
    .user-profile-badge {
        background: linear-gradient(135deg, #091E3A 0%, #102A4E 55%, #1E3A8A 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 18px 16px;
        color: #FFFFFF;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px -4px rgba(9, 30, 58, 0.35);
        position: relative;
        overflow: hidden;
    }

    .user-profile-badge::after {
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 110px;
        height: 110px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.25) 0%, rgba(255, 255, 255, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .user-avatar-circle {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #38BDF8 0%, #1D4ED8 100%);
        border: 2px solid rgba(255, 255, 255, 0.35);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        font-weight: 800;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        flex-shrink: 0;
    }

    .user-role-pill {
        display: inline-block;
        background: linear-gradient(90deg, #F59E0B 0%, #D97706 100%);
        color: #FFFFFF;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        box-shadow: 0 2px 6px rgba(217, 119, 6, 0.3);
    }

    .user-role-pill.respondent {
        background: linear-gradient(90deg, #0284C7 0%, #0369A1 100%);
        box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);
    }

    /* Modern Executive Sidebar Navigation styling */
    [data-testid="stSidebar"] [data-testid="stRadio"] > label {
        font-size: 0.74rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.08em !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        margin-bottom: 10px !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 8px !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 11px 14px !important;
        margin: 0 !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 5px -1px rgba(15, 23, 42, 0.04) !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        border-color: #0284C7 !important;
        background: #F0F9FF !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p {
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        line-height: 1.35 !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #091E3A 0%, #1E3A8A 100%) !important;
        border-color: #1E3A8A !important;
        box-shadow: 0 6px 16px -3px rgba(30, 58, 138, 0.35) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Touch-friendly Tabs with Horizontal Scrolling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 10px;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        white-space: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: thin !important;
    }

    .stTabs [data-baseweb="tab"] {
        flex-shrink: 0 !important;
        border-radius: 8px;
        padding: 7px 14px;
        font-weight: 600;
        font-size: 0.82rem;
        color: #475569;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0B192C !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* Responsive Button & Slider controls */
    .stButton>button {
        border-radius: 9px;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
        padding: 0.55rem 1.15rem;
    }

    .stSlider {
        margin-bottom: 8px;
    }

    /* Responsive Dataframe Scroll */
    div[data-testid="stDataFrame"] {
        width: 100% !important;
        overflow-x: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA STRUCTURE: 10 DESIGN FACTORS (COBIT 2019)
# ==========================================
df_definitions = {
    "DF1": {
        "title": "DF1: Enterprise Strategy", 
        "type": "fuzzy", 
        "scale": 5, 
        "desc": "Strategi institusi dalam mencapai visi misi universitas",
        "items": ["Growth / Acquisition", "Innovation / Differentiation", "Cost Leadership", "Client Service / Operational Stability"]
    },
    "DF2": {
        "title": "DF2: Enterprise Goals", 
        "type": "fuzzy", 
        "scale": 5, 
        "desc": "Pencapaian 13 Enterprise Goals institusi pendidikan",
        "items": ["EG01: Portfolio of products", "EG02: Financial risk", "EG03: Compliance laws", "EG04: Quality of financial info", "EG05: Customer-Oriented culture", "EG06: Business continuity", "EG07: Quality of management info", "EG08: Internal business process", "EG09: Optimization of process costs", "EG10: Staff skills & productivity", "EG11: Compliance with internal policies", "EG12: Managed digital transformation", "EG13: Product & business innovation"]
    },
    "DF3": {
        "title": "DF3: Risk Profile", 
        "type": "risk_profile", 
        "scale": 5, 
        "desc": "Profil dan mitigasi risiko Teknologi Informasi kampus (Impact & Likelihood, Skala 1–5)",
        "items": ["IT Investment Decision Making", "Program & Project Life Cycle", "IT Cost & Oversight", "IT Expertise & Skills", "Enterprise/IT Architecture", "IT Infrastructure Incidents", "Unauthorized Actions", "Software Adoption Problems", "Hardware Incidents", "Software Failures", "Logical Attacks (Hacking/Malware)", "Third-Party / Supplier Incidents", "Noncompliance", "Geopolitical Issues", "Industrial Action", "Acts of Nature", "Technology-Based Innovation", "Environmental", "Data & Information Management"]
    },
    "DF4": {
        "title": "DF4: I&T Related Issues", 
        "type": "fuzzy", 
        "scale": 3, 
        "desc": "Permasalahan operasional dan tata kelola I&T yang dihadapi",
        "items": ["Frustration antara entitas TI", "Frustration antara dept bisnis & TI", "Insiden TI serius (kehilangan data, keamanan)", "Masalah pengiriman layanan outsourcer", "Kegagalan memenuhi regulasi TI", "Temuan audit kinerja TI buruk", "Pengeluaran TI tidak resmi / tersembunyi", "Duplikasi & tumpang tindih inisiatif TI", "SDM TI tidak mencukupi / kurang keahlian", "Perubahan TI gagal memenuhi bisnis", "Eksekutif enggan terlibat keputusan TI", "Model operasi TI terlalu rumit", "Biaya TI dinilai terlalu tinggi", "Arsitektur TI menghambat inisiatif baru", "Kesenjangan pengetahuan bisnis & teknis", "Masalah kualitas & integrasi data", "End-user computing tinggi tanpa pengawasan", "Dept bisnis bangun solusi TI sendiri", "Pengabaian regulasi privasi", "Ketidakmampuan manfaatkan teknologi baru"]
    },
    "DF5": {
        "title": "DF5: Threat Landscape", 
        "type": "percentage", 
        "scale": 100, 
        "desc": "Tingkat paparan ancaman keamanan siber kampus",
        "items": ["High Threat Landscape (%)", "Normal Threat Landscape (%)"]
    },
    "DF6": {
        "title": "DF6: Compliance Requirements", 
        "type": "percentage", 
        "scale": 100, 
        "desc": "Kepatuhan terhadap regulasi eksternal (Kemendikbudristek, UU PDP, Akreditasi)",
        "items": ["High Compliance (%)", "Normal Compliance (%)", "Low Compliance (%)"]
    },
    "DF7": {
        "title": "DF7: Role of IT", 
        "type": "fuzzy", 
        "scale": 5, 
        "desc": "Peranan strategis TI terhadap operasional akademik dan kelembagaan",
        "items": ["Support Role", "Factory Role", "Turnaround Role", "Strategic Role"]
    },
    "DF8": {
        "title": "DF8: Sourcing Model for IT", 
        "type": "percentage", 
        "scale": 100, 
        "desc": "Model penyediaan infrastruktur dan layanan TI",
        "items": ["In-sourced (%)", "Outsourcing (%)", "Cloud Services (%)"]
    },
    "DF9": {
        "title": "DF9: IT Implementation Methods", 
        "type": "percentage", 
        "scale": 100, 
        "desc": "Metodologi implementasi dan pengembangan perangkat lunak",
        "items": ["Agile (%)", "DevOps (%)", "Traditional / Waterfall (%)"]
    },
    "DF10": {
        "title": "DF10: Tech Adoption Strategy", 
        "type": "percentage", 
        "scale": 100, 
        "desc": "Postur adopsi dan inovasi teknologi baru di lingkungan kampus",
        "items": ["First Mover (%)", "Follower (%)", "Slow Adopter (%)"]
    }
}

# Inisialisasi Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "calculated_results" not in st.session_state:
    st.session_state.calculated_results = {}

# ==========================================
# PAGE 1: AUTHENTICATION (RESPONSIVE PORTAL)
# ==========================================
if not st.session_state.authenticated:
    st.markdown("""
    <div class="cobit-hero-header" style="text-align: center; margin-top: 10px;">
        <div class="cobit-badge-ribbon" style="justify-content: center;">
            <span> ISACA COBIT 2019 & FUZZY LOGIC ENGINE</span>
        </div>
        <h1 class="cobit-title">Sistem Evaluasi Tata Kelola TI</h1>
        <p class="cobit-subtitle" style="justify-content: center;">
            <span>Universitas Klabat (UNKLAB)</span>
            <span>•</span>
            <span>Design Factors DF1–DF10</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Layout container yang presisi di Mobile & Desktop tanpa spacer kosong
    col_l, col_center, col_r = st.columns([0.1, 0.8, 0.1])
    with col_center:
        st.markdown("""
        <div class="auth-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
                <div style="background: linear-gradient(135deg, #1E3A8A, #0284C7); width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:1.25rem;">🔐</div>
                <div>
                    <h3 style="margin:0; font-size:1.15rem; font-weight:700; color:#0F172A;">Portal Akses Auditor</h3>
                    <p style="margin:0; font-size:0.8rem; color:#64748B;">Autentikasi terpusat berbasis Role-Based Access Control</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs([" Masuk (Sign In)", " Daftar Akun Baru"])
        
        with tab_login:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            login_user = st.text_input("Username Auditor / Responden:", placeholder="cth: admin1 / responden1", key="login_username")
            login_pass = st.text_input("Password:", type="password", placeholder="••••••••", key="login_password")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Masuk ke Sistem Audit", type="primary", use_container_width=True):
                if not login_user or not login_pass:
                    st.error("Harap isi username dan password lengkap.")
                else:
                    success, user_data = authenticate_user(login_user, login_pass)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_data
                        st.rerun()
                    else:
                        st.error("Kredensial tidak valid! Periksa kembali username dan password Anda.")

            st.markdown("""
            <div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:8px; padding:10px 12px; margin-top:14px; font-size:0.75rem; color:#0369A1; line-height:1.5;">
                <b> Akun Bawaan Sistem (Langsung Pakai):</b><br>
                • <b>Admin:</b> Username: <code>admin1</code> atau <code>admin</code> | Password: <code>admin123</code><br>
                • <b>Responden:</b> Username: <code>responden1</code> | Password: <code>responden123</code>
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            reg_user = st.text_input("Username Baru:", placeholder="cth: auditor_ti", key="reg_username")
            reg_name = st.text_input("Nama Lengkap beserta Gelar:", placeholder="cth: Douglas Rasuh, M.Kom", key="reg_fullname")
            reg_pos = st.selectbox(
                "Jabatan / Unit Kerja Terkait:", 
                ["IT Supervisor UNKLAB", "NOC Engineer", "Kepala SIU UNKLAB", "Staf IT & Infrastruktur", "Auditor Internal UNKLAB"],
                key="reg_position"
            )
            reg_role = st.selectbox("Peran Otoritas (Role):", ["Responden", "Admin"], key="reg_role_select")
            reg_pass1 = st.text_input("Password:", type="password", placeholder="Minimal 6 karakter", key="reg_pass1")
            reg_pass2 = st.text_input("Konfirmasi Password:", type="password", placeholder="Ulangi password", key="reg_pass2")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Daftarkan Akun Baru", type="primary", use_container_width=True):
                if not reg_user or not reg_name or not reg_pass1:
                    st.error("Semua kolom bertanda wajib harus diisi!")
                elif reg_pass1 != reg_pass2:
                    st.error("Konfirmasi password tidak cocok!")
                else:
                    ok, msg = register_user(reg_user, reg_name, reg_pos, reg_role, reg_pass1)
                    if ok:
                        st.success(f"{msg} Silakan buka tab 'Masuk' untuk login.")
                    else:
                        st.error(msg)
                        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; color: #64748B; font-size: 0.75rem; margin-top: 8px;">
            <span>Enkripsi Kata Sandi SHA-256</span> • <span>Algoritma Agregasi TFN Defuzzifikasi</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.stop()

# ==========================================
# PAGE 2: MAIN EXECUTIVE DASHBOARD
# ==========================================
user_p = st.session_state.user_info
is_admin = (user_p['role'] == "Admin")
role_class = "" if is_admin else "respondent"
role_label = "ADMINISTRATOR AUDIT" if is_admin else "AUDITOR RESPONDEN"

# SIDEBAR: USER BADGE & NAVIGATION
user_name = user_p.get('fullname', 'Auditor')
initials = "".join([w[0].upper() for w in user_name.split()[:2]]) if user_name else "A"

st.sidebar.markdown(f"""
<div class="user-profile-badge">
    <div class="user-avatar-wrapper">
        <div class="user-avatar-circle">{initials}</div>
        <div style="flex: 1; min-width: 0;">
            <div class="user-role-pill {role_class}">{role_label}</div>
            <div style="font-size: 1.02rem; font-weight: 700; color: #FFFFFF; line-height: 1.25; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_name}</div>
            <div style="font-size: 0.76rem; color: #94A3B8; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_p.get('position', 'Staff')}</div>
        </div>
    </div>
    <div style="padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.12); font-size: 0.72rem; color: #93C5FD; display: flex; align-items: center; justify-content: space-between;">
        <span style="display: flex; align-items: center; gap: 6px;">
            <span style="display:inline-block; width:7px; height:7px; background:#10B981; border-radius:50%; box-shadow: 0 0 8px #10B981;"></span>
            Sesi Aktif di SQLite
        </span>
        <span style="opacity: 0.7; font-size: 0.68rem; font-weight: 600;">COBIT 2019</span>
    </div>
</div>
""", unsafe_allow_html=True)

if is_admin:
    menu = st.sidebar.radio(
        "NAVIGASI MODUL AUDITOR (ADMIN)",
        [
            "📝  1. Pengolahan & Penggabungan Responden (DF1–DF10)", 
            "📊  2. Rekapitulasi & Visualisasi DF", 
            "🗄️  3. Riwayat Responden & Database", 
            "🎯  4. Capability Level & Export PDF"
        ]
    )
else:
    menu = st.sidebar.radio(
        "NAVIGASI AUDITOR RESPONDEN",
        [
            "📝  1. Wawancara 1: Kuesioner DF1–DF10",
            "📋  2. Wawancara 2: Checklist Capability Level"
        ]
    )
    is_sub_status, sub_time = get_user_submission_status(user_p['id'])
    is_chk_status, chk_count, chk_time = get_user_checklist_status(user_p['id'])
    
    if is_sub_status:
        st.sidebar.markdown(f"""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:9px 12px; margin-top:8px; font-size:0.75rem; color:#15803D;">
            <b>✓ Wawancara 1 (DF1–DF10):</b><br>Sudah Diserahkan ({sub_time[:16] if sub_time else ''})
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="background:#FEF3C7; border:1px solid #FDE68A; border-radius:10px; padding:9px 12px; margin-top:8px; font-size:0.75rem; color:#92400E;">
            <b>⏳ Wawancara 1 (DF1–DF10):</b><br>Belum Selesai Diisi
        </div>
        """, unsafe_allow_html=True)

    if is_chk_status:
        st.sidebar.markdown(f"""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:9px 12px; margin-top:6px; font-size:0.75rem; color:#15803D;">
            <b>✓ Wawancara 2 (Checklist):</b><br>Lengkap (124/124 Butir) ({chk_time[:16] if chk_time else ''})
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:9px 12px; margin-top:6px; font-size:0.75rem; color:#1E40AF;">
            <b>📋 Wawancara 2 (Checklist):</b><br>Terisi {chk_count}/124 Butir
        </div>
        """, unsafe_allow_html=True)

st.sidebar.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px; font-size:0.76rem; color:#475569; box-shadow: 0 2px 8px -2px rgba(15,23,42,0.05);">
    <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <span style="font-size:0.9rem;">📚</span>
        <strong style="color:#0F172A; font-size:0.82rem;">Landasan Kerangka Kerja:</strong>
    </div>
    <div style="line-height:1.6;">
        • <b>COBIT 2019:</b> 10 Design Factors & 4 Domain Prioritas UNKLAB (<code>APO12</code>, <code>APO13</code>, <code>DSS05</code>, <code>MEA03</code>).<br>
        • <b>Fuzzy Logic:</b> Triangular Fuzzy Number (TFN) & Defuzzifikasi $z^*$.
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button(" Keluar dari Sesi Audit", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.calculated_results = {}
    st.rerun()

# HERO HEADER AT TOP OF MAIN DASHBOARD
st.markdown("""
<div class="cobit-hero-header">
    <div class="cobit-badge-ribbon">
        <span> ISACA COBIT 2019</span>
        <span>•</span>
        <span>UNIVERSITAS KLABAT</span>
    </div>
    <h1 class="cobit-title">Sistem Evaluasi Tata Kelola TI & Capability Level</h1>
    <p class="cobit-subtitle">
        <span>Kombinasi Algoritma Triangular Fuzzy Numbers (TFN) & Multi-Factor Scoring</span>
        <span>•</span>
        <span>Dashboard Eksekutif</span>
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# MODUL 1 & WAWANCARA: INPUT / PENGOLAHAN (DF1 - DF10 & CHECKLIST)
# ----------------------------------------------------
if not is_admin:
    if ("Wawancara 1" in menu) or ("Formulir Kuesioner" in menu):
        # ========================================================
        # VIEW KHUSUS RESPONDEN (WAWANCARA 1: PENGISIAN MANDIRI DF1-DF10)
        # ========================================================
        st.markdown(f"""
        <div style="margin-bottom:14px;">
            <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">📝 Wawancara Tahap I: Kuesioner DF1 - DF10</h2>
            <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Pengisian kuesioner evaluasi 10 Design Factors tata kelola TI oleh auditor responden institusi</p>
        </div>
        """, unsafe_allow_html=True)
        
        is_sub_status, sub_time = get_user_submission_status(user_p['id'])
        if is_sub_status:
            st.success(f"✅ **Kuesioner Terkirim:** Jawaban Wawancara 1 Anda telah berhasil disimpan dan diserahkan ke Tim Administrator pada **{sub_time[:16] if sub_time else ''}**.")
            st.info("🔒 **Hak Akses Terbatas:** Seluruh hasil pengolahan agregat Fuzzy TFN, pemetaan Design Factor Map (Canvas), dan laporan Capability Level diproses secara terpusat dan hanya dapat dilihat serta diolah oleh Administrator.")
        else:
            st.info(f"Halo, **{user_p['fullname']}** ({user_p['position']})! Silakan isi seluruh indikator pada tab **DF1 sampai DF10** berikut sesuai observasi dan kondisi riil di unit kerja Anda. Setelah selesai, klik tombol **'Kirim Jawaban Kuesioner ke Administrator'**.")

        saved_user_answers = get_user_saved_answers(user_p['id'])
        
        tab_labels = [f"{code}" for code in df_definitions.keys()]
        tabs = st.tabs(tab_labels)
        resp_answers_dict = {}
        has_empty_field = False
        
        for idx, (df_code, df_info) in enumerate(df_definitions.items()):
            with tabs[idx]:
                is_fuzzy = (df_info["type"] == "fuzzy")
                is_risk  = (df_info["type"] == "risk_profile")
                method_badge = "Fuzzy TFN" if (is_fuzzy or is_risk) else "Direct Percentage"
                scale_badge  = f"Skala 1-{df_info['scale']}" if (is_fuzzy or is_risk) else "Skala 0-100%"
                
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 18px; margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div>
                            <h3 style="margin:0; font-size:1.05rem; font-weight:700; color:#0F172A;">{df_info["title"]}</h3>
                            <p style="margin:3px 0 0 0; color:#64748B; font-size:0.82rem;">{df_info["desc"]}</p>
                        </div>
                        <div style="display:flex; gap:6px;">
                            <span style="background:#EEF2FF; color:#4338CA; border:1px solid #C7D2FE; padding:3px 9px; border-radius:6px; font-size:0.72rem; font-weight:600;">{method_badge}</span>
                            <span style="background:#F0FDF4; color:#15803D; border:1px solid #BBF7D0; padding:3px 9px; border-radius:6px; font-size:0.72rem; font-weight:600;">{scale_badge}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                items = df_info["items"]
                df_items_data = []
                
                if is_risk:
                    opts5 = list(range(1, 6))
                    labels_5 = ["1 - Sangat Rendah", "2 - Rendah", "3 - Sedang", "4 - Tinggi", "5 - Sangat Tinggi"]
                    f5 = lambda x: labels_5[x-1] if x else ""
                    
                    st.caption("Tentukan tingkat Dampak (Impact) dan Kemungkinan (Likelihood) terjadinya setiap skenario risiko TI berikut:")
                    for i, item in enumerate(items):
                        saved_item = saved_user_answers.get(df_code, {}).get(item, {})
                        def_imp = int(saved_item.get('impact')) if saved_item.get('impact') else None
                        def_lik = int(saved_item.get('likelihood')) if saved_item.get('likelihood') else None
                        
                        st.markdown(f"<div style='font-size:0.86rem; font-weight:700; color:#1E293B; margin-top:8px;'>{i+1}. {item}</div>", unsafe_allow_html=True)
                        c_i, c_l = st.columns(2)
                        with c_i:
                            imp_val = st.selectbox(
                                f"Impact (Dampak):",
                                options=opts5,
                                index=(opts5.index(def_imp) if def_imp in opts5 else None),
                                format_func=f5,
                                placeholder="-- Pilih Tingkat Dampak --",
                                key=f"u_imp_{df_code}_{i}"
                            )
                        with c_l:
                            lik_val = st.selectbox(
                                f"Likelihood (Kemungkinan):",
                                options=opts5,
                                index=(opts5.index(def_lik) if def_lik in opts5 else None),
                                format_func=f5,
                                placeholder="-- Pilih Kemungkinan Terjadi --",
                                key=f"u_lik_{df_code}_{i}"
                            )
                        if imp_val is None or lik_val is None:
                            has_empty_field = True
                        df_items_data.append({"indicator": item, "impact": imp_val, "likelihood": lik_val, "score": (imp_val*lik_val if imp_val and lik_val else None)})
                        
                elif is_fuzzy:
                    scale_m = df_info["scale"]
                    opts = list(range(1, scale_m + 1))
                    if scale_m == 5:
                        labels = ["1 - Sangat Rendah", "2 - Rendah", "3 - Sedang", "4 - Tinggi", "5 - Sangat Tinggi"]
                    else:
                        labels = ["1 - No Issue", "2 - Issue", "3 - Serious Issue"]
                    f_lbl = lambda x: labels[x-1] if x else ""
                    
                    for i, item in enumerate(items):
                        saved_item = saved_user_answers.get(df_code, {}).get(item, {})
                        def_sc = int(saved_item.get('score')) if saved_item.get('score') else None
                        
                        val = st.selectbox(
                            f"{i+1}. {item}",
                            options=opts,
                            index=(opts.index(def_sc) if def_sc in opts else None),
                            format_func=f_lbl,
                            placeholder="-- Pilih Tingkat Penilaian --",
                            key=f"u_fuz_{df_code}_{i}"
                        )
                        if val is None:
                            has_empty_field = True
                        df_items_data.append({"indicator": item, "score": val})
                        
                else: # percentage
                    for i, item in enumerate(items):
                        saved_item = saved_user_answers.get(df_code, {}).get(item, {})
                        def_pct = float(saved_item.get('score')) if (saved_item.get('score') is not None) else None
                        
                        val = st.number_input(
                            f"{i+1}. {item}",
                            min_value=0.0,
                            max_value=100.0,
                            value=def_pct,
                            step=5.0,
                            placeholder="Ketik persentase (0 - 100%)...",
                            key=f"u_pct_{df_code}_{i}"
                        )
                        if val is None:
                            has_empty_field = True
                        df_items_data.append({"indicator": item, "score": val})
                        
                resp_answers_dict[df_code] = df_items_data
                
        st.markdown("<br>", unsafe_allow_html=True)
        col_sub_btn, col_sub_info = st.columns([1.3, 2])
        with col_sub_btn:
            if st.button("🚀 Kirim Jawaban Kuesioner ke Administrator", type="primary", use_container_width=True):
                if has_empty_field:
                    st.warning("⚠️ Masih terdapat pertanyaan kuesioner yang belum diisi. Harap lengkapi seluruh pertanyaan pada DF1 sampai DF10 sebelum mengirimkan.")
                else:
                    save_individual_answers(user_p['id'], user_p['username'], user_p['fullname'], user_p['position'], resp_answers_dict)
                    st.success("🎉 Terima kasih! Seluruh jawaban kuesioner DF1–DF10 Anda telah berhasil disimpan dan diserahkan kepada Tim Administrator Audit.")
                    st.balloons()
                    st.rerun()
        with col_sub_info:
            st.info("💡 **Hak Akses:** Data jawaban Anda tercatat secara aman dan hanya dapat diolah serta dianalisis oleh Administrator.")

        if is_sub_status:
            st.markdown("""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:12px 14px; margin-top:14px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="color:#1E40AF;">➡️ Lanjut ke Wawancara 2:</strong>
                    <span style="font-size:0.83rem; color:#1E3A8A; margin-left:6px;">Silakan buka menu <b>📋 2. Wawancara 2: Checklist Capability Level</b> di sidebar untuk melengkapi validasi 4 domain prioritas institusi.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    elif ("Wawancara 2" in menu) or ("Checklist" in menu):
        # ========================================================
        # VIEW KHUSUS RESPONDEN (WAWANCARA 2: CHECKLIST BINER YA/TIDAK)
        # ========================================================
        st.markdown(f"""
        <div style="margin-bottom:14px;">
            <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">📋 Wawancara Tahap II: Checklist Capability Level</h2>
            <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Checklist validasi implementasi tata kelola pada 4 Domain Prioritas UNKLAB (APO12, APO13, DSS05, MEA03) &bull; Metode Biner (Ya / Tidak)</p>
        </div>
        """, unsafe_allow_html=True)
        
        is_chk_status, chk_count, chk_time = get_user_checklist_status(user_p['id'])
        if is_chk_status:
            st.success(f"✅ **Checklist Wawancara 2 Lengkap:** Anda telah menjawab seluruh 124 butir pertanyaan checklist (Terakhir disimpan: **{chk_time[:16] if chk_time else ''}**). Anda dapat meninjau atau memperbarui jawaban di bawah ini.")
            st.info("🔒 **Hak Akses Terbatas:** Data jawaban checklist Anda akan diolah secara terpusat oleh Administrator untuk menghitung persentase Capability Level institusi.")
        else:
            st.info(f"Halo, **{user_p['fullname']}** ({user_p['position']})! Wawancara Tahap II ini mengonfirmasi keterpenuhan praktik pada 4 Domain Prioritas. Silakan jawab setiap butir dengan pilihan **Ya** (sudah diterapkan) atau **Tidak** (belum diterapkan). Terisi saat ini: **{chk_count}/124 butir**.")

        checklist_data = load_checklist_questions()
        saved_chk_answers = get_user_checklist_answers(user_p['id'])
        
        dom_keys = ["APO12", "APO13", "DSS05", "MEA03"]
        domain_tabs_labels = [
            f"APO12 — Risk ({len(checklist_data.get('APO12', []))} Butir)",
            f"APO13 — Security ({len(checklist_data.get('APO13', []))} Butir)",
            f"DSS05 — Sec. Services ({len(checklist_data.get('DSS05', []))} Butir)",
            f"MEA03 — Compliance ({len(checklist_data.get('MEA03', []))} Butir)"
        ]
        tabs_chk = st.tabs(domain_tabs_labels)
        dom_titles = {
            "APO12": ("APO12 — Managed Risk", "Manajemen Risiko TI Institusi (36 Butir Pertanyaan Validasi)"),
            "APO13": ("APO13 — Managed Security", "Sistem Manajemen Keamanan Informasi (19 Butir Pertanyaan Validasi)"),
            "DSS05": ("DSS05 — Managed Security Services", "Operasional Layanan Keamanan & Akses Data (49 Butir Pertanyaan Validasi)"),
            "MEA03": ("MEA03 — Managed Compliance", "Kepatuhan terhadap Regulasi Eksternal & Internal (20 Butir Pertanyaan Validasi)")
        }
        
        for idx, d_code in enumerate(dom_keys):
            with tabs_chk[idx]:
                d_title, d_desc = dom_titles.get(d_code, (d_code, ""))
                q_list = checklist_data.get(d_code, [])
                d_saved = saved_chk_answers.get(d_code, {})
                ya_in_d = sum(1 for q in q_list if d_saved.get(q['num']) == 1)
                
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 18px; margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div>
                            <h3 style="margin:0; font-size:1.05rem; font-weight:700; color:#0F172A;">{d_title}</h3>
                            <p style="margin:3px 0 0 0; color:#64748B; font-size:0.82rem;">{d_desc}</p>
                        </div>
                        <div style="display:flex; gap:6px;">
                            <span style="background:#EEF2FF; color:#4338CA; border:1px solid #C7D2FE; padding:3px 9px; border-radius:6px; font-size:0.72rem; font-weight:600;">Metode: Biner Ya/Tidak</span>
                            <span style="background:#F0FDF4; color:#15803D; border:1px solid #BBF7D0; padding:3px 9px; border-radius:6px; font-size:0.72rem; font-weight:600;">Terisi 'Ya': {ya_in_d}/{len(q_list)}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                for q in q_list:
                    q_num = q['num']
                    saved_val = d_saved.get(q_num, 0)
                    
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="background:#E2E8F0; color:#1E293B; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:700;">{q['practice']}</span>
                            <span style="font-size:0.74rem; color:#64748B; font-weight:600;">Butir Pertanyaan #{q_num}</span>
                        </div>
                        <div style="font-size:0.88rem; font-weight:600; color:#0F172A; line-height:1.45; margin-bottom:6px;">
                            {q['question']}
                        </div>
                        <div style="font-size:0.75rem; color:#64748B; font-style:italic; line-height:1.35;">
                            <b>Ref ISACA COBIT 2019:</b> {q['desc_en']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_opt, _ = st.columns([2, 3])
                    with c_opt:
                        st.radio(
                            f"Jawaban Butir {d_code} #{q_num}",
                            options=["Ya (Terpenuhi / Diterapkan)", "Tidak (Belum Terpenuhi)"],
                            index=(0 if saved_val == 1 else 1),
                            key=f"u_chk_{d_code}_{q_num}",
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_cbtn, col_cinfo = st.columns([1.3, 2])
        with col_cbtn:
            if st.button("🚀 Kirim Jawaban Checklist ke Administrator", type="primary", use_container_width=True):
                collected_chk = {}
                for d_code, q_list in checklist_data.items():
                    collected_chk[d_code] = {}
                    for q in q_list:
                        ans_str = st.session_state.get(f"u_chk_{d_code}_{q['num']}", "Tidak")
                        collected_chk[d_code][q['num']] = 1 if "Ya" in ans_str else 0
                
                save_individual_checklist(user_p['id'], user_p['username'], user_p['fullname'], user_p['position'], collected_chk)
                st.success("🎉 Terima kasih! Seluruh jawaban Checklist Wawancara 2 (124 butir) berhasil disimpan dan diserahkan ke Tim Administrator.")
                st.balloons()
                st.rerun()
        with col_cinfo:
            st.info("💡 **Hak Akses:** Data checklist tersimpan aman di database dan hanya dapat diolah serta dipublikasikan oleh Administrator.")

elif "1. Pengolahan" in menu:
    # ========================================================
    # VIEW KHUSUS ADMINISTRATOR (PENGOLAHAN MULTI-RESPONDEN & MANUAL)
    # ========================================================
    st.markdown("""
    <div style="margin-bottom:14px;">
        <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">⚙️ Pengolahan Data Kuesioner Multi-Responden (DF1–DF10)</h2>
        <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Pilih dan gabungkan data kuesioner dari responden terdaftar menggunakan algoritma Triangular Fuzzy Numbers (TFN)</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_admin_multi, tab_admin_manual = st.tabs([
        "👥 Pengolahan Multi-Responden (Data Database)", 
        "✍️ Input / Simulasi Manual (2 Responden)"
    ])
    
    with tab_admin_multi:
        submitted_list = get_all_submitted_respondents()
        
        # KPI Summary Responden
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div class="kpi-card kpi-card-cobit">
                <div class="kpi-title">Responden Mengisi Kuesioner</div>
                <div class="kpi-value">{len(submitted_list)}</div>
                <div class="kpi-desc">Tersimpan di Basis Data</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            lengkap_count = sum(1 for r in submitted_list if r['df_count'] >= 10)
            st.markdown(f"""
            <div class="kpi-card kpi-card-teal">
                <div class="kpi-title">Kuesioner Lengkap 10 DF</div>
                <div class="kpi-value">{lengkap_count}</div>
                <div class="kpi-desc">Siap Diolah dengan TFN</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="kpi-card kpi-card-gold">
                <div class="kpi-title">Metode Defuzzifikasi</div>
                <div class="kpi-value" style="font-size:1.3rem;">TFN Centroid</div>
                <div class="kpi-desc">Standar ISACA COBIT 2019</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:1.05rem; font-weight:700; color:#0F172A;'>📋 Daftar Responden yang Telah Mengisi Kuesioner:</h3>", unsafe_allow_html=True)
        
        if submitted_list:
            df_sub_show = pd.DataFrame([
                {
                    "User ID": r["user_id"],
                    "Username": r["username"],
                    "Nama Responden": r["fullname"],
                    "Jabatan / Unit": r["position"],
                    "Cakupan DF": f"{r['df_count']} / 10 DF",
                    "Waktu Pengisian": r["submitted_at"][:16] if r["submitted_at"] else "-"
                }
                for r in submitted_list
            ])
            st.dataframe(df_sub_show, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada responden yang mengisi kuesioner.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:16px 18px; margin-bottom:14px;">
            <h3 style="margin:0 0 6px 0; font-size:1.05rem; font-weight:700; color:#0F172A;">⚡ Pasangkan & Olah Data Dua Responden (Fuzzy TFN)</h3>
            <p style="margin:0 0 12px 0; font-size:0.82rem; color:#64748B;">Pilih Responden 1 (misal: Dept. SIU) dan Responden 2 (misal: Dept. IT) untuk diagregasikan secara matematis</p>
        """, unsafe_allow_html=True)
        
        if len(submitted_list) >= 2:
            resp_opts = {
                f"{r['fullname']} ({r['position']}) — @{r['username']}": r["user_id"]
                for r in submitted_list
            }
            opt_keys = list(resp_opts.keys())
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                r1_sel = st.selectbox("Pilih Responden 1 (R1 - Dept. SIU / Accountable):", options=opt_keys, index=0)
            with col_sel2:
                r2_sel = st.selectbox("Pilih Responden 2 (R2 - Dept. IT / Responsible):", options=opt_keys, index=1 if len(opt_keys) > 1 else 0)
            
            uid1 = resp_opts[r1_sel]
            uid2 = resp_opts[r2_sel]
            
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("⚡ Gabungkan & Olah Data dengan Fuzzy TFN", type="primary", use_container_width=True):
                aggregated_results = aggregate_two_respondents(uid1, uid2, df_definitions)
                st.session_state.calculated_results = aggregated_results
                
                r1_name = r1_sel.split(" (")[0]
                r2_name = r2_sel.split(" (")[0]
                r_id = save_respondent_data(f"{r1_name} & {r2_name}", f"Agregat {r1_name} & {r2_name}", aggregated_results)
                st.success(f"✅ Data kuesioner berhasil digabungkan dan diolah dengan Fuzzy TFN (Terekam dengan Respondent ID #{r_id})! Silakan buka **Modul 2** untuk melihat hasil analisis.")
                st.balloons()
        else:
            st.warning("⚠️ Dibutuhkan minimal 2 responden yang telah mengisi kuesioner untuk melakukan penggabungan data secara otomatis. Silakan tunggu responden lain mengisi kuesioner, atau gunakan tab 'Input / Simulasi Manual'.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.calculated_results:
            st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#0F172A; margin-top:10px;'>📊 Preview Hasil Agregasi Aktif:</h4>", unsafe_allow_html=True)
            sample_df = list(st.session_state.calculated_results.keys())[0]
            sample_rows = st.session_state.calculated_results[sample_df]
            prev_table = pd.DataFrame([{
                "Indikator": r["indicator"],
                "Skor R1": r["r1"],
                "Skor R2": r["r2"],
                "Nilai Akhir Agregat": r["final_display"],
                "Input Toolkit (Dibulatkan)": r["rounded_toolkit"]
            } for r in sample_rows[:5]])
            st.dataframe(prev_table, use_container_width=True, hide_index=True)
            st.caption("ℹ️ Menampilkan sampel hasil pengolahan data. Visualisasi lengkap dan Design Factor Map tersedia di Modul 2.")

    with tab_admin_manual:
        with st.expander(" Identitas Penilai & Metadata Audit", expanded=True):
            col_resp_a, col_resp_b = st.columns(2)
            resp_name = col_resp_a.text_input("Nama Penilai / Lead Auditor:", value="", placeholder="Ketik nama penilai...", key="m_resp_name")
            resp_pos = col_resp_b.text_input("Jabatan / Unit Kerja Evaluasi:", value="", placeholder="Ketik jabatan penilai...", key="m_resp_pos")

        tab_labels = [f"{code}" for code in df_definitions.keys()]
        tabs = st.tabs(tab_labels)
        temp_results = {}

        for idx, (df_code, df_info) in enumerate(df_definitions.items()):
            with tabs[idx]:
                is_fuzzy = (df_info["type"] == "fuzzy")
                is_risk  = (df_info["type"] == "risk_profile")
                method_badge = "Fuzzy TFN" if (is_fuzzy or is_risk) else " Direct Percentage"
                scale_badge  = f"Skala 1-{df_info['scale']}" if (is_fuzzy or is_risk) else "Skala 0-100%"
                
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 18px; margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div>
                            <h3 style="margin:0; font-size:1.05rem; font-weight:700; color:#0F172A;">{df_info["title"]}</h3>
                            <p style="margin:3px 0 0 0; color:#64748B; font-size:0.82rem;">{df_info["desc"]}</p>
                        </div>
                        <div style="display:flex; gap:6px;">
                            <span style="background:#EEF2FF; color:#4338CA; border:1px solid #C7D2FE; padding:3px 9px; border-radius:6px; font-size:0.72rem; font-weight:600;">{method_badge}</span>
                            <span style="background:#F0FDF4; color:#15803D; border:1px solid #BBF7D0; padding:3px 9px; border-radius:6px; font-size:0.72rem; font-weight:600;">{scale_badge}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                items = df_info["items"]

                if is_risk:
                    opts5 = list(range(1, 6))
                    labels_5 = ["1 - Sangat Rendah", "2 - Rendah", "3 - Sedang", "4 - Tinggi", "5 - Sangat Tinggi"]
                    f5 = lambda x: labels_5[x-1] if x else ""

                    col_ir1, col_ir2, col_lr1, col_lr2 = st.columns(4)
                    with col_ir1:
                        st.markdown("""<div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#4338CA; font-size:0.82rem;">🔴 Impact – R1</strong></div>""", unsafe_allow_html=True)
                    with col_ir2:
                        st.markdown("""<div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#4338CA; font-size:0.82rem;">🔴 Impact – R2</strong></div>""", unsafe_allow_html=True)
                    with col_lr1:
                        st.markdown("""<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#15803D; font-size:0.82rem;">🟡 Likelihood – R1</strong></div>""", unsafe_allow_html=True)
                    with col_lr2:
                        st.markdown("""<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#15803D; font-size:0.82rem;">🟡 Likelihood – R2</strong></div>""", unsafe_allow_html=True)

                    rows = []
                    for i, item in enumerate(items):
                        st.markdown(f"<div style='font-size:0.86rem; font-weight:700; color:#1E293B; margin-top:8px;'>{i+1}. {item}</div>", unsafe_allow_html=True)
                        c_ir1, c_ir2, c_lr1, c_lr2 = st.columns(4)
                        with c_ir1:
                            i_r1 = st.selectbox(f"I-R1", options=opts5, index=None, format_func=f5, placeholder="Pilih Impact R1", key=f"ir1_{df_code}_{i}", label_visibility="collapsed")
                        with c_ir2:
                            i_r2 = st.selectbox(f"I-R2", options=opts5, index=None, format_func=f5, placeholder="Pilih Impact R2", key=f"ir2_{df_code}_{i}", label_visibility="collapsed")
                        with c_lr1:
                            l_r1 = st.selectbox(f"L-R1", options=opts5, index=None, format_func=f5, placeholder="Pilih Likelihood R1", key=f"lr1_{df_code}_{i}", label_visibility="collapsed")
                        with c_lr2:
                            l_r2 = st.selectbox(f"L-R2", options=opts5, index=None, format_func=f5, placeholder="Pilih Likelihood R2", key=f"lr2_{df_code}_{i}", label_visibility="collapsed")

                        if any(v is None for v in [i_r1, i_r2, l_r1, l_r2]):
                            rows.append({"indicator": item, "method": "Risk Profile (Fuzzy TFN)", "r1": None, "r2": None, "final": None, "final_display": "Belum Terisi", "rounded_toolkit": "-", "ir1": i_r1, "ir2": i_r2, "lr1": l_r1, "lr2": l_r2, "impact_val": None, "likelihood_val": None, "risk_rating": None})
                        else:
                            res = calc_risk_profile(i_r1, i_r2, l_r1, l_r2)
                            rows.append({"indicator": item, "method": "Risk Profile (Fuzzy TFN)", "r1": res["impact_val"], "r2": res["likelihood_val"], "final": float(res["risk_rating"]), "final_display": str(res["risk_rating"]), "rounded_toolkit": str(res["risk_rating"]), "ir1": i_r1, "ir2": i_r2, "lr1": l_r1, "lr2": l_r2, "impact_val": res["impact_val"], "likelihood_val": res["likelihood_val"], "risk_rating": res["risk_rating"]})

                    temp_results[df_code] = rows

                    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                    if any(r["final"] is None for r in rows):
                        st.info(f"Pertanyaan pada **{df_code}** belum lengkap terisi.")
                    else:
                        st.success(f"Penilaian **{df_code}** lengkap terisi! Hasil kalkulasi Risk Profile (Impact × Likelihood):")
                        df_prev_risk = pd.DataFrame([{
                            "Skenario Risiko": r["indicator"],
                            "I-R1": r["ir1"], "I-R2": r["ir2"], "Impact (Bulat)": r["impact_val"],
                            "L-R1": r["lr1"], "L-R2": r["lr2"], "Likelihood (Bulat)": r["likelihood_val"],
                            "Risk Rating": r["risk_rating"]
                        } for r in rows])
                        st.dataframe(df_prev_risk, use_container_width=True)

                elif is_fuzzy:
                    scale_m = df_info["scale"]
                    opts = list(range(1, scale_m + 1))
                    labels = ["1 - Sangat Rendah", "2 - Rendah", "3 - Sedang", "4 - Tinggi", "5 - Sangat Tinggi"] if scale_m == 5 else ["1 - No Issue", "2 - Issue", "3 - Serious Issue"]
                    f_lbl = lambda x: labels[x-1] if x else ""

                    col_head_a, col_head_b = st.columns(2)
                    with col_head_a:
                        st.markdown("""<div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#4338CA; font-size:0.82rem;">Responden 1 (Dept. SIU / Accountable)</strong></div>""", unsafe_allow_html=True)
                    with col_head_b:
                        st.markdown("""<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#15803D; font-size:0.82rem;">Responden 2 (Dept. IT / Responsible)</strong></div>""", unsafe_allow_html=True)

                    rows = []
                    for i, item in enumerate(items):
                        c1, c2 = st.columns(2)
                        with c1:
                            r1 = st.selectbox(f"{item} (R1)", options=opts, index=None, format_func=f_lbl, placeholder="-- Pilih Nilai R1 --", key=f"r1_{df_code}_{i}")
                        with c2:
                            r2 = st.selectbox(f"{item} (R2)", options=opts, index=None, format_func=f_lbl, placeholder="-- Pilih Nilai R2 --", key=f"r2_{df_code}_{i}")

                        if r1 is None or r2 is None:
                            rows.append({"indicator": item, "method": "Fuzzy Logic TFN", "r1": r1, "r2": r2, "final": None, "final_display": "Belum Terisi", "rounded_toolkit": "-"})
                        else:
                            final_sc = calc_fuzzy_5(r1, r2) if scale_m == 5 else calc_fuzzy_3(r1, r2)
                            rows.append({"indicator": item, "method": "Fuzzy Logic TFN", "r1": r1, "r2": r2, "final": final_sc, "final_display": f"{final_sc:.2f}", "rounded_toolkit": str(int(round(final_sc)))})

                    temp_results[df_code] = rows

                    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                    if any(r["final"] is None for r in rows):
                        st.info(f"Indikator pada **{df_code}** masih kosong. Silakan lengkapi seluruh pertanyaan di atas.")
                    else:
                        st.success(f"Penilaian **{df_code}** lengkap terisi! Hasil kalkulasi agregat:")
                        df_prev_fuz = pd.DataFrame([{
                            "Indikator": r["indicator"], "R1": r["r1"], "R2": r["r2"],
                            "Nilai Akhir Agregat": r["final_display"], "Input Toolkit (Dibulatkan)": r["rounded_toolkit"]
                        } for r in rows])
                        st.dataframe(df_prev_fuz, use_container_width=True)

                else: # percentage
                    col_head_a, col_head_b = st.columns(2)
                    with col_head_a:
                        st.markdown("""<div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#4338CA; font-size:0.82rem;">Responden 1 (Dept. SIU)</strong></div>""", unsafe_allow_html=True)
                    with col_head_b:
                        st.markdown("""<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:8px 12px; margin-bottom:10px; text-align:center;"><strong style="color:#15803D; font-size:0.82rem;">Responden 2 (Dept. IT)</strong></div>""", unsafe_allow_html=True)

                    rows = []
                    for i, item in enumerate(items):
                        c1, c2 = st.columns(2)
                        with c1:
                            r1 = st.number_input(f"{item} - R1", min_value=0.0, max_value=100.0, value=None, step=5.0, placeholder="Persentase R1 (0-100%)...", key=f"r1_{df_code}_{i}")
                        with c2:
                            r2 = st.number_input(f"{item} - R2", min_value=0.0, max_value=100.0, value=None, step=5.0, placeholder="Persentase R2 (0-100%)...", key=f"r2_{df_code}_{i}")

                        if r1 is None or r2 is None:
                            rows.append({"indicator": item, "method": "Direct Percentage (%)", "r1": r1, "r2": r2, "final": None, "final_display": "Belum Terisi", "rounded_toolkit": "-"})
                        else:
                            final_sc = calc_percentage_avg(r1, r2)
                            rows.append({"indicator": item, "method": "Direct Percentage (%)", "r1": r1, "r2": r2, "final": final_sc, "final_display": f"{final_sc:.1f}%", "rounded_toolkit": f"{int(round(final_sc))}%"})

                    temp_results[df_code] = rows

                    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                    if any(r["final"] is None for r in rows):
                        st.info(f"Indikator pada **{df_code}** masih kosong.")
                    else:
                        st.success(f"Penilaian **{df_code}** lengkap terisi! Hasil kalkulasi agregat:")
                        df_prev_pct = pd.DataFrame([{
                            "Indikator": r["indicator"], "R1": r["r1"], "R2": r["r2"],
                            "Nilai Akhir Agregat": r["final_display"], "Input Toolkit (Dibulatkan)": r["rounded_toolkit"]
                        } for r in rows])
                        st.dataframe(df_prev_pct, use_container_width=True)

        st.session_state.calculated_results = temp_results

        st.markdown("<br>", unsafe_allow_html=True)
        col_save, col_info_box = st.columns([1.2, 2])
        with col_save:
            if st.button("Simpan Penilaian ke Database SQLite", type="primary", use_container_width=True):
                st.session_state.calculated_results = temp_results
                incomplete_dfs = [
                    code for code, r_list in temp_results.items()
                    if any(r["final"] is None for r in r_list)
                ]
                if resp_name.strip() == "":
                    st.error("Silakan isi nama penilai terlebih dahulu.")
                elif incomplete_dfs:
                    st.warning(f"Penilaian belum lengkap! Terdapat {len(incomplete_dfs)} Design Factor yang masih memiliki nilai kosong: {', '.join(incomplete_dfs)}.")
                else:
                    r_id = save_respondent_data(resp_name, resp_pos, temp_results)
                    st.success(f"Penilaian lengkap berhasil direkam ke database dengan Respondent ID #{r_id}!")
        with col_info_box:
            st.info(" Data yang telah lengkap diisi di atas langsung terhubung ke menu **Visualisasi & Rekapitulasi**.")

# ----------------------------------------------------
# MODUL 2: REKAPITULASI & VISUALISASI DESIGN FACTOR
# ----------------------------------------------------
elif "2. Rekapitulasi" in menu:
    if not is_admin:
        st.error(" Akses Terbatas: Modul ini dikhususkan bagi Administrator.")
        st.stop()
        
    st.markdown("""
    <div style="margin-bottom:16px;">
        <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">Rekapitulasi Agregat & Analisis Visual Design Factor</h2>
        <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Visualisasi polar radar untuk skor Fuzzy Logic dan bar horizontal untuk persentase faktor tata kelola</p>
    </div>
    """, unsafe_allow_html=True)

    
    # Auto-load data paling baru dari database jika session_state masih kosong/belum lengkap
    is_ready_session = bool(st.session_state.calculated_results) and all(
        all(r.get('final') is not None for r in rows) for rows in st.session_state.calculated_results.values()
    ) and len(st.session_state.calculated_results) == 10

    if not is_ready_session:
        db_data = load_latest_respondent_data()
        if db_data and len(db_data) == 10 and all(all(r.get('final') is not None for r in rows) for rows in db_data.values()):
            st.session_state.calculated_results = db_data
            is_ready_session = True

    if not is_ready_session:
        st.warning("Data penilaian kuesioner DF1–DF10 masih kosong atau belum terisi lengkap di Menu 1. Silakan buka Menu 1 dan lengkapi seluruh kuesioner terlebih dahulu untuk melihat rekapitulasi.")
    else:
        summary_rows = []
        fuzzy_scores = {}
        pct_scores = {}
        
        for df_code, rows in st.session_state.calculated_results.items():
            avg_r1 = np.mean([r['r1'] for r in rows])
            avg_r2 = np.mean([r['r2'] for r in rows])
            avg_final = np.mean([r['final'] for r in rows])
            method = rows[0]['method']
            
            if df_definitions[df_code]["type"] == "fuzzy":
                fuzzy_scores[df_code] = round(avg_final, 2)
            else:
                pct_scores[df_code] = round(avg_final, 2)

            unit = "%" if "Percentage" in method else " / 5.0"
            summary_rows.append({
                "Kode DF": df_code, 
                "Nama Design Factor": df_definitions[df_code]["title"],
                "Metode": method, 
                "Rata-rata R1": round(avg_r1, 2), 
                "Rata-rata R2": round(avg_r2, 2),
                "Skor Agregat": f"{round(avg_final, 2)}{unit}"
            })
            
        avg_fuzzy_core = np.mean(list(fuzzy_scores.values())[:4]) if fuzzy_scores else 0
        df7_score = fuzzy_scores.get('DF7', 0)
        avg_pct_all = np.mean(list(pct_scores.values())) if pct_scores else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="kpi-card kpi-card-cobit">
                <div class="kpi-title">Rata-Rata Fuzzy DF1–DF4</div>
                <div class="kpi-value">{avg_fuzzy_core:.2f} <span style="font-size:0.85rem; font-weight:500; color:#64748B;">/ 5.0</span></div>
                <div class="kpi-desc">Strategi & Sasaran Utama</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
            <div class="kpi-card kpi-card-fuzzy">
                <div class="kpi-title">Peran Strategis TI (DF7)</div>
                <div class="kpi-value">{df7_score:.2f} <span style="font-size:0.85rem; font-weight:500; color:#64748B;">/ 5.0</span></div>
                <div class="kpi-desc">Postur Peranan TI Kampus</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m3:
            st.markdown(f"""
            <div class="kpi-card kpi-card-teal">
                <div class="kpi-title">Persentase DF5–DF10</div>
                <div class="kpi-value">{avg_pct_all:.1f}%</div>
                <div class="kpi-desc">Landscape & Metodologi</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m4:
            st.markdown(f"""
            <div class="kpi-card kpi-card-gold">
                <div class="kpi-title">Cakupan Design Factor</div>
                <div class="kpi-value">10 / 10</div>
                <div class="kpi-desc">Lengkap Standar ISACA</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_chart1, col_chart2 = st.columns(2)
        
        plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
        plt.rcParams['axes.edgecolor'] = '#CBD5E1'
        plt.rcParams['axes.linewidth'] = 0.8
        
        with col_chart1:
            st.markdown("""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:14px 16px; margin-bottom:12px; box-shadow: 0 4px 14px -2px rgba(15,23,42,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong style="color:#0F172A; font-size:0.95rem;">🕸️ Skor Fuzzy (DF1-DF4, DF7)</strong>
                    <span style="font-size:0.72rem; background:#EEF2FF; color:#4338CA; padding:2px 7px; border-radius:4px; font-weight:600;">Skala 1 - 5</span>
                </div>
            """, unsafe_allow_html=True)
            
            categories = list(fuzzy_scores.keys())
            values = list(fuzzy_scores.values())
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            
            fig, ax = plt.subplots(figsize=(5.5, 4.2), subplot_kw=dict(polar=True), dpi=150)
            fig.patch.set_facecolor('#FFFFFF')
            ax.set_facecolor('#F8FAFC')
            
            ax.plot(angles + [angles[0]], values + [values[0]], color='#1E3A8A', linewidth=2.4, marker='o', markersize=5, markerfacecolor='#38BDF8')
            ax.fill(angles + [angles[0]], values + [values[0]], color='#0284C7', alpha=0.25)
            
            ax.set_xticks(angles)
            ax.set_xticklabels(categories, fontweight='bold', fontsize=8.5, color='#0F172A')
            ax.set_ylim(0, 5)
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=7, color='#64748B')
            ax.grid(color='#E2E8F0', linestyle='--', linewidth=0.7)
            fig.tight_layout()
            
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_chart2:
            st.markdown("""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:14px 16px; margin-bottom:12px; box-shadow: 0 4px 14px -2px rgba(15,23,42,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong style="color:#0F172A; font-size:0.95rem;"> Persentase DF (DF5-DF10)</strong>
                    <span style="font-size:0.72rem; background:#F0FDF4; color:#15803D; padding:2px 7px; border-radius:4px; font-weight:600;">Skala 0 - 100%</span>
                </div>
            """, unsafe_allow_html=True)
            
            fig2, ax2 = plt.subplots(figsize=(5.5, 4.2), dpi=150)
            fig2.patch.set_facecolor('#FFFFFF')
            ax2.set_facecolor('#FFFFFF')
            
            pct_keys = list(pct_scores.keys())
            pct_vals = list(pct_scores.values())
            
            bar_colors = ['#0D9488', '#0284C7', '#6366F1', '#D97706', '#059669'][:len(pct_keys)]
            bars = ax2.barh(pct_keys, pct_vals, color=bar_colors, height=0.55, edgecolor='none')
            
            for bar in bars:
                w = bar.get_width()
                ax2.text(w + 2, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', ha='left', fontsize=8, fontweight='bold', color='#1E293B')
                
            ax2.set_xlim(0, 115)
            ax2.grid(axis='x', linestyle='--', alpha=0.5, color='#E2E8F0')
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_color('#E2E8F0')
            ax2.spines['bottom'].set_color('#E2E8F0')
            ax2.tick_params(axis='y', labelsize=8.5, colors='#0F172A')
            ax2.tick_params(axis='x', labelsize=7.5, colors='#64748B')
            fig2.tight_layout()
            
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:1.1rem; font-weight:700; color:#0F172A; margin-bottom:10px;'> Tabel Detail Agregasi 10 Design Factors</h3>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

        # ══════════════════════════════════════════════════════════════════════
        # DF MAP — Kalkulasi Otomatis Skor Domain Prioritas dari Design Factors
        # Berdasarkan bobot resmi ISACA COBIT 2019 Design Toolkit
        # ══════════════════════════════════════════════════════════════════════
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1E3A8A,#0284C7); border-radius:14px; padding:18px 22px; margin-bottom:18px;">
            <h2 style="margin:0; color:#FFFFFF; font-size:1.2rem; font-weight:800;">🗺️ Design Factor Map — Skor Domain Prioritas COBIT 2019</h2>
            <p style="margin:6px 0 0 0; color:#BAE6FD; font-size:0.85rem;">Kalkulasi otomatis bobot kontribusi setiap Design Factor terhadap 4 domain prioritas UNKLAB (sesuai tabel resmi ISACA)</p>
        </div>
        """, unsafe_allow_html=True)

        # ─── Ambil hasil DF dari session state ───
        df_results = st.session_state.calculated_results

        # ─── Ambil nilai dominan per DF ───
        df1_rows = df_results.get("DF1", [])
        df1_scores = {r["indicator"]: r["final"] for r in df1_rows if r["final"] is not None}

        df2_avg = np.mean([r["final"] for r in df_results.get("DF2",[]) if r["final"] is not None]) if df_results.get("DF2") else 0
        df3_ratings = {r["indicator"]: (r["final"] if r["final"] else 0) for r in df_results.get("DF3", [])}
        df4_vals = {r["indicator"]: (r["final"] if r["final"] else 0) for r in df_results.get("DF4", [])}

        df5_rows = df_results.get("DF5", [])
        df5_high   = next((r["final"] for r in df5_rows if "High" in r["indicator"]), 0) or 0
        df5_normal = next((r["final"] for r in df5_rows if "Normal" in r["indicator"]), 0) or 0

        df6_rows = df_results.get("DF6", [])
        df6_high   = next((r["final"] for r in df6_rows if "High" in r["indicator"]), 0) or 0
        df6_normal = next((r["final"] for r in df6_rows if "Normal" in r["indicator"]), 0) or 0
        df6_low    = next((r["final"] for r in df6_rows if "Low" in r["indicator"]), 0) or 0

        df7_rows = df_results.get("DF7", [])
        df7_support    = next((r["final"] for r in df7_rows if "Support" in r["indicator"]), 0) or 0
        df7_factory    = next((r["final"] for r in df7_rows if "Factory" in r["indicator"]), 0) or 0
        df7_turnaround = next((r["final"] for r in df7_rows if "Turnaround" in r["indicator"]), 0) or 0
        df7_strategic  = next((r["final"] for r in df7_rows if "Strategic" in r["indicator"]), 0) or 0

        df8_rows = df_results.get("DF8", [])
        df8_out  = next((r["final"] for r in df8_rows if "Outsourc" in r["indicator"] or "out" in r["indicator"].lower()), 0) or 0
        df8_cloud= next((r["final"] for r in df8_rows if "Cloud" in r["indicator"]), 0) or 0
        df8_in   = next((r["final"] for r in df8_rows if "In-sourced" in r["indicator"] or "nsourc" in r["indicator"]), 0) or 0

        df9_rows = df_results.get("DF9", [])
        df9_agile = next((r["final"] for r in df9_rows if "Agile" in r["indicator"]), 0) or 0
        df9_devops= next((r["final"] for r in df9_rows if "DevOps" in r["indicator"]), 0) or 0
        df9_trad  = next((r["final"] for r in df9_rows if "Traditional" in r["indicator"] or "Waterfall" in r["indicator"]), 0) or 0

        df10_rows = df_results.get("DF10", [])
        df10_first  = next((r["final"] for r in df10_rows if "First" in r["indicator"]), 0) or 0
        df10_follow = next((r["final"] for r in df10_rows if "Follower" in r["indicator"]), 0) or 0
        df10_slow   = next((r["final"] for r in df10_rows if "Slow" in r["indicator"]), 0) or 0

        DOMAINS = {
            "APO12": "Managed Risk",
            "APO13": "Managed Security",
            "DSS05": "Managed Security Services",
            "MEA03": "Managed Compliance"
        }

        DF1_CATS = ["Growth / Acquisition", "Innovation / Differentiation", "Cost Leadership", "Client Service / Stability"]
        DF1_W = {
            "APO12": [1.0, 1.5, 1.0, 2.5],
            "APO13": [1.0, 1.0, 1.0, 2.5],
            "DSS05": [1.0, 1.0, 1.0, 2.5],
            "MEA03": [1.0, 1.0, 1.0, 1.0],
        }

        DF3_ITEMS = ["IT Investment Decision Making", "Program & Project Life Cycle", "IT Cost & Oversight",
                     "IT Expertise & Skills", "Enterprise/IT Architecture", "IT Infrastructure Incidents",
                     "Unauthorized Actions", "Software Adoption Problems", "Hardware Incidents",
                     "Software Failures", "Logical Attacks (Hacking/Malware)", "Third-Party / Supplier Incidents",
                     "Noncompliance", "Geopolitical Issues", "Industrial Action", "Acts of Nature",
                     "Technology-Based Innovation", "Environmental", "Data & Information Management"]
        DF3_W = {
            "APO12": [0,0,0,0,0,0,3,0,0,2,3,0,0,0,0,2,0,0,0],
            "APO13": [0,0,0,0,0,0,4,0,0,0,4,0,3,0,0,0,0,0,0],
            "DSS05": [0,0,0,0,0,3,4,0,2,0,4,0,3,0,3,2,0,0,3],
            "MEA03": [0,1,0,0,0,1,2,0,0,0,3,2,4,2,0,0,0,0,2],
        }

        DF4_ITEMS = ["Frustration antara entitas TI", "Frustration antara dept bisnis & TI",
                     "Insiden TI serius (kehilangan data, keamanan)", "Masalah pengiriman layanan outsourcer",
                     "Kegagalan memenuhi regulasi TI", "Temuan audit kinerja TI buruk",
                     "Pengeluaran TI tidak resmi / tersembunyi", "Duplikasi & tumpang tindih inisiatif TI",
                     "SDM TI tidak mencukupi / kurang keahlian", "Perubahan TI gagal memenuhi bisnis",
                     "Eksekutif enggan terlibat keputusan TI", "Model operasi TI terlalu rumit",
                     "Biaya TI dinilai terlalu tinggi", "Arsitektur TI menghambat inisiatif baru",
                     "Kesenjangan pengetahuan bisnis & teknis", "Masalah kualitas & integrasi data",
                     "End-user computing tinggi tanpa pengawasan", "Dept bisnis bangun solusi TI sendiri",
                     "Pengabaian regulasi privasi", "Ketidakmampuan manfaatkan teknologi baru"]
        DF4_W = {
            "APO12": [1,0.5,2.5,1.5,2,2,1,1,0.5,1,1,1,1,1,1,2,1,1.5,2.5,1],
            "APO13": [0,0,3.5,1,2,1,0,1,0,0.5,0,0,0,0,0,1.5,2,1,2,1],
            "DSS05": [0,0,4,2,2,0,0,0,0,0,0,0,0,0,0,1.5,1,2,2,0],
            "MEA03": [0,0,2,2,4,0.5,0,0,0,0,0,0,0,0,0,2,0,0,4,0],
        }

        DF5_W = {"APO12": [4,1], "APO13": [4,1], "DSS05": [3,1], "MEA03": [3,1]}
        DF6_W = {"APO12": [4,2,1], "APO13": [1.5,1,1], "DSS05": [2,1,1], "MEA03": [4,2,1]}
        DF7_W = {"APO12": [1,2.5,1,3], "APO13": [1,2,1.5,3], "DSS05": [1.5,2.5,1.5,3.5], "MEA03": [1,1,1,1.5]}
        DF8_W = {"APO12": [2,2,1], "APO13": [1,1,1], "DSS05": [1,1,1], "MEA03": [1,1,1]}
        DF9_W = {"APO12": [1,1.5,1], "APO13": [1,1,1], "DSS05": [1,1,1], "MEA03": [1,1,1]}
        DF10_W = {"APO12": [2,1.5,1], "APO13": [1,1,1], "DSS05": [1.5,1,1], "MEA03": [1,1,1]}

        def calc_df_map_score(domain):
            score = 0.0

            if df1_scores:
                dom_cat = max(df1_scores, key=df1_scores.get)
                matched_idx = 0
                for ci, cat in enumerate(DF1_CATS):
                    if any(w.lower() in dom_cat.lower() for w in cat.split()[:2]):
                        matched_idx = ci
                        break
                score += DF1_W[domain][matched_idx]

            df2_norm = (df2_avg - 1) / 4.0 if df2_avg > 1 else 0
            df2_domain_max = {"APO12": 4, "APO13": 3, "DSS05": 4, "MEA03": 3}
            score += round(df2_norm * df2_domain_max.get(domain, 2), 2)

            for i, item_name in enumerate(DF3_ITEMS):
                w = DF3_W[domain][i]
                if w == 0:
                    continue
                matched_rating = 0
                for key, val in df3_ratings.items():
                    if any(kw.lower() in key.lower() for kw in item_name.split()[:2]):
                        matched_rating = val
                        break
                score += round((matched_rating / 25.0) * w, 4)

            for i, item_name in enumerate(DF4_ITEMS):
                w = DF4_W[domain][i]
                if w == 0:
                    continue
                matched_val = 0
                for key, val in df4_vals.items():
                    if any(kw.lower() in key.lower() for kw in item_name.split()[:3]):
                        matched_val = val
                        break
                norm = (matched_val - 1) / 2.0 if matched_val > 1 else 0
                score += round(norm * w, 4)

            df5_pct_norm = [df5_high/100.0, df5_normal/100.0]
            score += sum(df5_pct_norm[i] * DF5_W[domain][i] for i in range(2))

            df6_pct_norm = [df6_high/100.0, df6_normal/100.0, df6_low/100.0]
            score += sum(df6_pct_norm[i] * DF6_W[domain][i] for i in range(3))

            df7_vals_norm = [(v-1)/4.0 if v and v > 1 else 0 for v in [df7_support, df7_factory, df7_turnaround, df7_strategic]]
            score += sum(df7_vals_norm[i] * DF7_W[domain][i] for i in range(4))

            df8_pct_norm = [df8_out/100.0, df8_cloud/100.0, df8_in/100.0]
            score += sum(df8_pct_norm[i] * DF8_W[domain][i] for i in range(3))

            df9_pct_norm = [df9_agile/100.0, df9_devops/100.0, df9_trad/100.0]
            score += sum(df9_pct_norm[i] * DF9_W[domain][i] for i in range(3))

            df10_pct_norm = [df10_first/100.0, df10_follow/100.0, df10_slow/100.0]
            score += sum(df10_pct_norm[i] * DF10_W[domain][i] for i in range(3))

            return round(score, 2)

        domain_scores = {d: calc_df_map_score(d) for d in DOMAINS}
        max_score = max(domain_scores.values()) if domain_scores and max(domain_scores.values()) > 0 else 1
        domain_scores_pct = {d: round((s / max_score) * 100, 1) for d, s in domain_scores.items()}
        ranked = sorted(domain_scores_pct.items(), key=lambda x: x[1], reverse=True)

        dcols = st.columns(4)
        domain_colors = {
            "APO12": ("kpi-card-cobit", "🔵"),
            "APO13": ("kpi-card-fuzzy", "🟣"),
            "DSS05": ("kpi-card-teal", "🟢"),
            "MEA03": ("kpi-card-gold", "🟡"),
        }
        for i, (dom, pct) in enumerate(ranked):
            cls, emoji = domain_colors.get(dom, ("kpi-card-cobit", "⚫"))
            with dcols[i]:
                rank_label = ["🥇 #1", "🥈 #2", "🥉 #3", "  #4"][i]
                st.markdown(f"""
                <div class="kpi-card {cls}">
                    <div class="kpi-title">{emoji} {dom} — {DOMAINS[dom]}</div>
                    <div class="kpi-value">{pct}</div>
                    <div class="kpi-desc">{rank_label} Prioritas  |  Skor Raw: {domain_scores[dom]:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<h3 style='font-size:1.05rem; font-weight:700; color:#0F172A; margin-bottom:10px;'>📊 Tabel Skor Domain — Design Factor Map</h3>", unsafe_allow_html=True)
        df_map_table = pd.DataFrame([
            {
                "Prioritas": ["1","2","3",][i],
                "Domain": dom,
                "Nama Domain": DOMAINS[dom],
                "Skor Total (Raw)": domain_scores[dom],
                "Skor Relatif (%)": domain_scores_pct[dom],
            }
            for i, (dom, _) in enumerate(ranked)
        ])
        st.dataframe(df_map_table, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_map1, col_map2 = st.columns([1.4, 1])

        with col_map1:
            st.markdown("""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:14px 16px; margin-bottom:12px;">
                <strong style="color:#0F172A; font-size:0.95rem;">🏆 Ranking Skor Domain Berdasarkan DF Map</strong>
            </div>
            """, unsafe_allow_html=True)
            fig_map, ax_map = plt.subplots(figsize=(6, 3.5), dpi=150)
            fig_map.patch.set_facecolor('#FFFFFF')
            ax_map.set_facecolor('#F8FAFC')
            dom_names = [f"{d}\n{DOMAINS[d]}" for d, _ in ranked]
            dom_pcts  = [p for _, p in ranked]
            bar_cols  = ['#1E3A8A', '#0284C7', '#0D9488', '#D97706']
            bars_map  = ax_map.barh(dom_names, dom_pcts, color=bar_cols, height=0.5, edgecolor='none')
            for bar in bars_map:
                w = bar.get_width()
                ax_map.text(w + 1.5, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', ha='left', fontsize=9, fontweight='bold', color='#0F172A')
            ax_map.set_xlim(0, 120)
            ax_map.set_xlabel("Skor Relatif (%)", fontsize=8, color='#64748B')
            ax_map.grid(axis='x', linestyle='--', alpha=0.4, color='#CBD5E1')
            ax_map.spines['top'].set_visible(False)
            ax_map.spines['right'].set_visible(False)
            ax_map.spines['left'].set_color('#E2E8F0')
            ax_map.spines['bottom'].set_color('#E2E8F0')
            ax_map.tick_params(axis='y', labelsize=7.5, colors='#0F172A')
            ax_map.tick_params(axis='x', labelsize=7, colors='#64748B')
            fig_map.tight_layout()
            st.pyplot(fig_map, use_container_width=True)
            plt.close(fig_map)

        with col_map2:
            st.markdown("""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:16px 18px;">
                <strong style="color:#0F172A; font-size:0.95rem;"> Rekomendasi Prioritas Domain</strong>
                <hr style="margin:10px 0; border-color:#E2E8F0;">
            """, unsafe_allow_html=True)
            interp = {
                "APO12": "Manajemen Risiko TI membutuhkan perhatian khusus sesuai profil risiko institusi.",
                "APO13": "Keamanan Informasi harus diperkuat seiring ancaman siber yang tinggi.",
                "DSS05": "Operasional Layanan Keamanan perlu distandarisasi dan dimonitor rutin.",
                "MEA03": "Kepatuhan Regulasi Eksternal wajib dipenuhi sesuai persyaratan akreditasi.",
            }
            for i, (dom, pct) in enumerate(ranked):
                medal = ["1","2","3","  "][i]
                st.markdown(f"""
                <div style="margin-bottom:10px; padding:8px 10px; background:#F8FAFC; border-left:3px solid {'#1E3A8A' if i==0 else '#0284C7' if i==1 else '#0D9488' if i==2 else '#D97706'}; border-radius:0 6px 6px 0;">
                    <div style="font-size:0.8rem; font-weight:700; color:#0F172A;">{medal} {dom} — Skor: {pct}%</div>
                    <div style="font-size:0.75rem; color:#64748B; margin-top:3px;">{interp.get(dom,'')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# MODUL 3: RIWAYAT DATABASE SQLITE
# ----------------------------------------------------
elif "3. Riwayat" in menu:
    if not is_admin:
        st.error(" Akses Terbatas: Modul ini dikhususkan bagi Administrator.")
        st.stop()
        
    st.markdown("""
    <div style="margin-bottom:16px;">
        <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">Penyimpanan & Riwayat Data Audit (SQLite)</h2>
        <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Pemeriksaan riwayat responden kuesioner dan data akun auditor terdaftar</p>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_FILE)
    df_resps = pd.read_sql_query("SELECT id, name, position, created_at FROM respondents ORDER BY id DESC", conn)
    df_users = pd.read_sql_query("SELECT id, username, fullname, position, role, created_at FROM users ORDER BY id DESC", conn)
    df_cap_history = pd.read_sql_query("SELECT id, domain_code, as_is_level, to_be_level, gap, achievement_pct, rating_scale, created_at FROM capability_assessments ORDER BY id DESC", conn)
    conn.close()
    
    tab_db1, tab_db2, tab_db3, tab_db4, tab_db5 = st.tabs([
        "📋 Jawaban DF1–DF10", 
        "👥 Riwayat Agregat Responden", 
        "👤 Akun Auditor & Pengguna", 
        "📈 Riwayat Kapabilitas",
        "📑 Checklist Wawancara 2"
    ])
    
    with tab_db1:
        df_indiv = pd.read_sql_query("SELECT id, username, fullname, position, df_code, indicator_name, score_val, impact_val, likelihood_val, submitted_at FROM individual_responses ORDER BY id DESC", conn)
        if df_indiv.empty:
            st.info("Belum ada jawaban individual responden di database.")
        else:
            resp_list = ["Semua Responden"] + sorted(list(df_indiv["fullname"].unique()))
            sel_resp = st.selectbox("Filter Tampilan Responden:", options=resp_list)
            if sel_resp != "Semua Responden":
                st.dataframe(df_indiv[df_indiv["fullname"] == sel_resp], use_container_width=True)
            else:
                st.dataframe(df_indiv, use_container_width=True)

    with tab_db2:
        if df_resps.empty:
            st.info("Belum ada data agregat responden yang tersimpan di basis data.")
        else:
            st.dataframe(df_resps, use_container_width=True)
            
    with tab_db3:
        st.dataframe(df_users, use_container_width=True)
        
    with tab_db4:
        if df_cap_history.empty:
            st.info("Belum ada riwayat evaluasi capability level di database.")
        else:
            st.dataframe(df_cap_history, use_container_width=True)

    with tab_db5:
        conn_chk = sqlite3.connect(DB_FILE)
        df_chk_db = pd.read_sql_query("SELECT id, username, fullname, position, domain_code, question_num, answer_val, submitted_at FROM individual_checklist_responses ORDER BY id DESC", conn_chk)
        conn_chk.close()
        if df_chk_db.empty:
            st.info("Belum ada data jawaban checklist Wawancara 2 di database.")
        else:
            df_chk_db['Status Jawaban'] = df_chk_db['answer_val'].apply(lambda x: '✅ Ya (Terpenuhi)' if x == 1 else '❌ Tidak (Belum Terpenuhi)')
            st.dataframe(df_chk_db, use_container_width=True)

# ----------------------------------------------------
# MODUL 4: CAPABILITY LEVEL & EXPORT PDF
# ----------------------------------------------------
elif "4. Capability" in menu:
    if not is_admin:
        st.error(" Akses Terbatas: Modul Capability Level & Export PDF hanya dapat diakses oleh Administrator.")
        st.stop()
        
    st.markdown("""
    <div style="margin-bottom:16px;">
        <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">Penilaian Capability Level & Analisis Gap</h2>
        <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Evaluasi 4 domain prioritas Universitas Klabat beserta penerbitan laporan resmi (PDF)</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Metadata Evaluator / Lead Auditor", expanded=True):
        col_e1, col_e2 = st.columns(2)
        eval_name = col_e1.text_input("Nama Lead Evaluator:", value=user_p['fullname'])
        eval_pos = col_e2.text_input("Jabatan Evaluator:", value=user_p['position'])
    
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px 18px; margin-bottom:16px;">
        <h3 style="margin:0 0 6px 0; font-size:1.05rem; font-weight:700; color:#0F172A;">📊 Sumber Data Penilaian Kapabilitas (Capability Level)</h3>
        <p style="margin:0 0 12px 0; font-size:0.82rem; color:#64748B;">Pilih metode penentuan persentase pencapaian proses dari Wawancara 2 (Checklist Biner) atau preset data skripsi</p>
    """, unsafe_allow_html=True)
    
    cap_mode = st.radio(
        "Metode Penentuan Nilai Kapabilitas:",
        [
            "📋 Integrasi Otomatis dari Checklist Wawancara 2 (Data Responden)",
            "⚡ Preset Data Aktual Skripsi UNKLAB (Novanca Tulende)",
            "✍️ Simulasi Manual (Slider Bebas)"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Inisialisasi dictionary hasil capaian 4 domain
    domain_scores = {}
    checklist_full_questions = load_checklist_questions()
    selected_evidence_answers = {}

    if "Integrasi Otomatis" in cap_mode:
        all_chk_resps = get_all_checklist_submitted_respondents()
        col_src1, col_src2 = st.columns([1.5, 2])
        with col_src1:
            resp_options = ["Konsensus Gabungan (Rata-rata Responden)"]
            if all_chk_resps:
                resp_options += [f"{r['fullname']} ({r['username']}) - {r['q_count']} butir" for r in all_chk_resps]
            sel_chk_source = st.selectbox("Pilih Sumber Jawaban Responden:", resp_options)

        with col_src2:
            st.info("💡 **Metode Wawancara 2:** Menggunakan rasio biner murni tanpa Fuzzy Logic: $\\text{Pencapaian (\\%)} = \\frac{\\sum \\text{Ya}}{\\text{Total Pertanyaan}} \\times 100\\%$.")

        # Hitung skor berdasarkan sumber yang dipilih
        if "Konsensus" in sel_chk_source:
            # Ambil jawaban responden1 & responden2
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT id, username FROM users WHERE username IN ('responden1', 'responden2')")
            u_rows = cur.fetchall()
            conn.close()
            
            all_u_answers = [get_user_checklist_answers(uid) for uid, _ in u_rows]
            selected_evidence_answers = all_u_answers[0] if all_u_answers else {}
            
            for d_code in ["APO12", "APO13", "DSS05", "MEA03"]:
                q_list = checklist_full_questions.get(d_code, [])
                total_q = len(q_list)
                if total_q == 0:
                    domain_scores[d_code] = {"ya": 0, "total": 0, "pct": 0.0, "rating": "N - Not Achieved (0-14%)", "as_is": 0}
                    continue
                
                # Rata-rata persentase antar responden
                pct_sum = 0.0
                for u_ans in all_u_answers:
                    d_ans = u_ans.get(d_code, {})
                    ya_c = sum(1 for q in q_list if d_ans.get(q['num']) == 1)
                    pct_sum += (ya_c / total_q) * 100.0
                
                avg_pct = round(pct_sum / len(all_u_answers), 2) if all_u_answers else 0.0
                rating_str, as_is_val = get_rating_level_cobit(avg_pct)
                domain_scores[d_code] = {
                    "ya": int(round((avg_pct / 100.0) * total_q)),
                    "total": total_q,
                    "pct": avg_pct,
                    "rating": rating_str,
                    "as_is": as_is_val
                }
        else:
            # Responden spesifik
            target_username = sel_chk_source.split("(")[1].split(")")[0].strip()
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = ?", (target_username,))
            r_row = cur.fetchone()
            conn.close()
            
            target_uid = r_row[0] if r_row else None
            user_chk_ans = get_user_checklist_answers(target_uid) if target_uid else {}
            selected_evidence_answers = user_chk_ans
            
            for d_code in ["APO12", "APO13", "DSS05", "MEA03"]:
                calc_res = calculate_domain_checklist_score(d_code, user_chk_ans, checklist_full_questions)
                domain_scores[d_code] = {
                    "ya": calc_res["ya"],
                    "total": calc_res["total"],
                    "pct": calc_res["pct"],
                    "rating": calc_res["rating"],
                    "as_is": calc_res["as_is_lvl"]
                }

    elif "Preset Data Aktual" in cap_mode:
        preset_data = get_preset_skripsi_capability()
        for d_code in ["APO12", "APO13", "DSS05", "MEA03"]:
            domain_scores[d_code] = {
                "ya": preset_data[d_code]["ya"],
                "total": preset_data[d_code]["total"],
                "pct": preset_data[d_code]["pct"],
                "rating": preset_data[d_code]["rating"],
                "as_is": preset_data[d_code]["as_is"]
            }
        # Gunakan jawaban responden1 sebagai referensi bukti
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = 'responden1'")
        r_row = cur.fetchone()
        conn.close()
        selected_evidence_answers = get_user_checklist_answers(r_row[0]) if r_row else {}

    else: # Simulasi Manual Slider
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; margin-bottom:14px;">
            <span style="font-size:0.83rem; color:#475569;">Sesuaikan persentase capaian pemenuhan proses secara manual di bawah ini:</span>
        </div>
        """, unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            p_apo12 = st.slider("1. APO12 — Managed Risk (%)", 0.0, 100.0, 8.0, step=0.5)
            p_apo13 = st.slider("2. APO13 — Managed Security (%)", 0.0, 100.0, 42.0, step=0.5)
        with col_s2:
            p_dss05 = st.slider("3. DSS05 — Security Services (%)", 0.0, 100.0, 75.0, step=0.5)
            p_mea03 = st.slider("4. MEA03 — Managed Compliance (%)", 0.0, 100.0, 31.0, step=0.5)

        for d_code, p_val, tot_val in [("APO12", p_apo12, 36), ("APO13", p_apo13, 19), ("DSS05", p_dss05, 49), ("MEA03", p_mea03, 20)]:
            r_str, as_is_val = get_rating_level_cobit(p_val)
            domain_scores[d_code] = {
                "ya": int(round((p_val / 100.0) * tot_val)),
                "total": tot_val,
                "pct": p_val,
                "rating": r_str,
                "as_is": as_is_val
            }

    # Pilihan Target Level To-Be
    col_tgt1, col_tgt2 = st.columns([1.2, 2.8])
    with col_tgt1:
        target_lvl = st.selectbox(
            "🎯 Target Capability Level (To-Be):",
            options=[1, 2, 3, 4, 5],
            index=3, # Default Level 4 (sesuai target skripsi UNKLAB)
            help="Sesuai target standar skripsi UNKLAB: Level 4 (Quantitative / Predictable)"
        )
    with col_tgt2:
        st.caption(f"Target yang ditetapkan: **Level {target_lvl}** &bull; Skripsi UNKLAB menargetkan Level 4 pada 4 Domain Prioritas Tata Kelola TI.")

    # Susun cap_list untuk visualisasi & tabel gap
    domain_display_names = {
        "APO12": "APO12 — Managed Risk",
        "APO13": "APO13 — Managed Security",
        "DSS05": "DSS05 — Security Services",
        "MEA03": "MEA03 — Compliance"
    }

    cap_list = []
    for d_code in ["APO12", "APO13", "DSS05", "MEA03"]:
        d_info = domain_scores[d_code]
        as_is_lvl = d_info["as_is"]
        cap_list.append({
            "domain_code": d_code,
            "domain": domain_display_names[d_code],
            "ya": d_info["ya"],
            "total": d_info["total"],
            "as_is": as_is_lvl,
            "to_be": target_lvl,
            "gap": max(0, target_lvl - as_is_lvl),
            "pct": d_info["pct"],
            "rating": d_info["rating"]
        })

    # KPI Summary Cards (4 Domain + Rata-rata Institusi)
    avg_inst_pct = round(sum(item['pct'] for item in cap_list) / 4.0, 2)
    avg_inst_as_is = int(round(sum(item['as_is'] for item in cap_list) / 4.0))
    avg_inst_gap = max(0, target_lvl - avg_inst_as_is)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    c_k1, c_k2, c_k3, c_k4, c_k5 = st.columns(5)
    with c_k1:
        st.markdown(f"""
        <div class="kpi-card kpi-card-cobit">
            <div class="kpi-title">APO12 — Risk</div>
            <div class="kpi-value">{cap_list[0]['pct']:.1f}%</div>
            <div class="kpi-desc">Level {cap_list[0]['as_is']} &bull; {cap_list[0]['ya']}/{cap_list[0]['total']} Ya</div>
        </div>
        """, unsafe_allow_html=True)
    with c_k2:
        st.markdown(f"""
        <div class="kpi-card kpi-card-cobit">
            <div class="kpi-title">APO13 — Security</div>
            <div class="kpi-value">{cap_list[1]['pct']:.1f}%</div>
            <div class="kpi-desc">Level {cap_list[1]['as_is']} &bull; {cap_list[1]['ya']}/{cap_list[1]['total']} Ya</div>
        </div>
        """, unsafe_allow_html=True)
    with c_k3:
        st.markdown(f"""
        <div class="kpi-card kpi-card-cobit">
            <div class="kpi-title">DSS05 — Services</div>
            <div class="kpi-value">{cap_list[2]['pct']:.1f}%</div>
            <div class="kpi-desc">Level {cap_list[2]['as_is']} &bull; {cap_list[2]['ya']}/{cap_list[2]['total']} Ya</div>
        </div>
        """, unsafe_allow_html=True)
    with c_k4:
        st.markdown(f"""
        <div class="kpi-card kpi-card-cobit">
            <div class="kpi-title">MEA03 — Compliance</div>
            <div class="kpi-value">{cap_list[3]['pct']:.1f}%</div>
            <div class="kpi-desc">Level {cap_list[3]['as_is']} &bull; {cap_list[3]['ya']}/{cap_list[3]['total']} Ya</div>
        </div>
        """, unsafe_allow_html=True)
    with c_k5:
        st.markdown(f"""
        <div class="kpi-card kpi-card-gold">
            <div class="kpi-title">Rata-rata Institusi</div>
            <div class="kpi-value">{avg_inst_pct:.1f}%</div>
            <div class="kpi-desc">Level {avg_inst_as_is} (Gap: {avg_inst_gap} Level)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================================
    # AUDIT TRAIL / EVIDENCE EXPLORER (124 BUTIR CHECKLIST)
    # ========================================================
    with st.expander("🔍 Audit Trail & Tinjauan Bukti: 124 Butir Checklist Wawancara 2", expanded=False):
        st.markdown("""
        <p style="font-size:0.83rem; color:#64748B; margin-bottom:12px;">
            Daftar lengkap 124 butir checklist dari 4 domain prioritas UNKLAB berdasarkan dokumen wawancara resmi.
        </p>
        """, unsafe_allow_html=True)
        
        col_flt1, col_flt2 = st.columns(2)
        with col_flt1:
            flt_dom = st.selectbox("Filter Domain:", ["Semua Domain", "APO12", "APO13", "DSS05", "MEA03"])
        with col_flt2:
            flt_st = st.selectbox("Filter Status Jawaban:", ["Semua Status", "Hanya Belum Terpenuhi (Tidak)", "Hanya Terpenuhi (Ya)"])
        
        evidence_rows = []
        for d_code in ["APO12", "APO13", "DSS05", "MEA03"]:
            if flt_dom != "Semua Domain" and flt_dom != d_code:
                continue
            q_list = checklist_full_questions.get(d_code, [])
            d_ans = selected_evidence_answers.get(d_code, {})
            for q in q_list:
                ans_val = d_ans.get(q['num'], 0)
                if flt_st == "Hanya Terpenuhi (Ya)" and ans_val != 1:
                    continue
                if flt_st == "Hanya Belum Terpenuhi (Tidak)" and ans_val != 0:
                    continue
                evidence_rows.append({
                    "Domain": d_code,
                    "Praktik": q['practice'],
                    "No": q['num'],
                    "Pertanyaan Wawancara": q['question'],
                    "Status": "✅ Ya" if ans_val == 1 else "❌ Tidak",
                    "Referensi ISACA COBIT 2019": q['desc_en']
                })
        
        if evidence_rows:
            df_evidence = pd.DataFrame(evidence_rows)
            st.dataframe(df_evidence, use_container_width=True)
        else:
            st.info("Tidak ada butir checklist yang cocok dengan filter yang dipilih.")

    # ========================================================
    # REKOMENDASI PERBAIKAN BERDASARKAN TEMUAN CHECKLIST
    # ========================================================
    with st.expander("📋 Rekomendasi Strategis Berdasarkan Temuan Gap Wawancara 2", expanded=True):
        st.markdown("""
        <div style="font-size:0.85rem; color:#1E293B; line-height:1.6;">
            <b>Rekomendasi Berdasarkan Analisis Temuan Lapangan:</b><br>
            • <b>APO12 (Managed Risk — 8.00% / Level 0):</b> Institusi belum memiliki Register Risiko TI formal dan metodologi asesmen risiko berkala. Disarankan menyusun panduan manajemen risiko TI dan menetapkan batas toleransi risiko institusi.<br>
            • <b>APO13 (Managed Security — 42.00% / Level 1):</b> Perlu memformalkan dokumen Kebijakan Sistem Manajemen Keamanan Informasi (SMKI), menunjuk Tim Tanggap Insiden Keamanan Siber (CSIRT), serta mengadakan sosialisasi berkala mengenai keamanan data bagi civitas akademika.<br>
            • <b>DSS05 (Security Services — 75.00% / Level 2):</b> Sebagian besar kontrol malware dan pengamanan endpoint telah berjalan baik. Perlu ditingkatkan peninjauan rutin hak akses istimewa pimpinan/staf (access privilege review) dan monitoring log audit berkala.<br>
            • <b>MEA03 (Managed Compliance — 31.00% / Level 1):</b> Disarankan membentuk matriks kepatuhan terpadu untuk memastikan keselarasan operasional TI terhadap regulasi eksternal (UU Pelindungan Data Pribadi / PDP dan standar akreditasi BAN-PT/Kemendikbudristek).
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # VISUALISASI GRAFIK
    # ========================================================
    col_cap_chart1, col_cap_chart2 = st.columns(2)
    
    with col_cap_chart1:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:14px 16px; margin-bottom:12px; box-shadow: 0 4px 14px -2px rgba(15,23,42,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <strong style="color:#0F172A; font-size:0.95rem;">📊 Tingkat Kapabilitas: As-Is vs To-Be</strong>
                <span style="font-size:0.72rem; background:#FEF3C7; color:#92400E; padding:2px 7px; border-radius:4px; font-weight:600;">Target: Level {target_lvl}</span>
            </div>
        """, unsafe_allow_html=True)
        
        domains_short = [x['domain_code'] for x in cap_list]
        fig_cap, ax_cap = plt.subplots(figsize=(5.5, 4.0), dpi=150)
        fig_cap.patch.set_facecolor('#FFFFFF')
        ax_cap.set_facecolor('#FFFFFF')
        
        x = np.arange(len(domains_short))
        width = 0.32
        
        rects1 = ax_cap.bar(x - width/2, [x['as_is'] for x in cap_list], width, label='Level As-Is (Saat Ini)', color='#D97706', edgecolor='none')
        rects2 = ax_cap.bar(x + width/2, [x['to_be'] for x in cap_list], width, label=f'Level To-Be (Target {target_lvl})', color='#1E3A8A', edgecolor='none')
        
        ax_cap.set_xticks(x)
        ax_cap.set_xticklabels(domains_short, fontweight='bold', fontsize=9, color='#0F172A')
        ax_cap.set_ylim(0, 5.2)
        ax_cap.set_yticks([0, 1, 2, 3, 4, 5])
        ax_cap.set_ylabel("Capability Level", fontsize=8, color='#64748B')
        ax_cap.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#E2E8F0', fontsize=8)
        ax_cap.grid(axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')
        ax_cap.spines['top'].set_visible(False)
        ax_cap.spines['right'].set_visible(False)
        ax_cap.spines['left'].set_color('#E2E8F0')
        ax_cap.spines['bottom'].set_color('#E2E8F0')
        fig_cap.tight_layout()
        
        st.pyplot(fig_cap, use_container_width=True)
        plt.close(fig_cap)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cap_chart2:
        st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:14px 16px; margin-bottom:12px; box-shadow: 0 4px 14px -2px rgba(15,23,42,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <strong style="color:#0F172A; font-size:0.95rem;">🎯 Capaian Persentase 4 Domain Prioritas</strong>
                <span style="font-size:0.72rem; background:#ECFDF5; color:#065F46; padding:2px 7px; border-radius:4px; font-weight:600;">Persentase (%)</span>
            </div>
        """, unsafe_allow_html=True)
        
        fig_donut, ax_donut = plt.subplots(figsize=(5.5, 4.0), dpi=150)
        fig_donut.patch.set_facecolor('#FFFFFF')
        
        pct_values = [x['pct'] for x in cap_list]
        total_pct = sum(pct_values)
        
        if total_pct == 0:
            ax_donut.pie([1], colors=['#E2E8F0'], wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2))
            ax_donut.text(0, 0, 'Persentase: 0%\n(Belum Terisi)', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#64748B')
        else:
            donut_colors = ['#EF4444', '#F59E0B', '#10B981', '#6366F1']
            wedges, texts, autotexts = ax_donut.pie(
                pct_values, 
                labels=domains_short, 
                autopct='%1.1f%%', 
                startangle=120, 
                colors=donut_colors, 
                wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2),
                pctdistance=0.75
            )
            for t in texts:
                t.set_fontsize(8.5)
                t.set_fontweight('bold')
                t.set_color('#0F172A')
            for at in autotexts:
                at.set_fontsize(7.5)
                at.set_color('#FFFFFF')
                at.set_fontweight('bold')
                
            ax_donut.text(0, 0, f'UNKLAB\n{avg_inst_pct:.1f}%', ha='center', va='center', fontsize=9, fontweight='bold', color='#1E3A8A')
        fig_donut.tight_layout()
        
        st.pyplot(fig_donut, use_container_width=True)
        plt.close(fig_donut)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.1rem; font-weight:700; color:#0F172A; margin-bottom:10px;'>📊 Tabel Evaluasi Kesenjangan (Gap Analysis)</h3>", unsafe_allow_html=True)
    
    df_cap_display = pd.DataFrame([
        {
            "Domain Evaluasi": item['domain'],
            "Butir Terpenuhi": f"{item['ya']} / {item['total']}",
            "Pencapaian (%)": f"{item['pct']:.2f}%",
            "Level As-Is": f"Level {item['as_is']}",
            "Target To-Be": f"Level {item['to_be']}",
            "Gap (Level)": f"{item['gap']} Level",
            "COBIT Rating Scale": item['rating']
        }
        for item in cap_list
    ])
    st.dataframe(df_cap_display, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn_db, col_btn_pdf = st.columns(2)
    
    with col_btn_db:
        if st.button("💾 Simpan Hasil Evaluasi ke Database SQLite", type="secondary", use_container_width=True):
            for item in cap_list:
                save_capability_data(item['domain'], item['as_is'], item['to_be'], item['gap'], item['pct'], item['rating'])
            st.success("🎉 Seluruh data capability level & gap analysis berhasil disimpan ke database SQLite!")

    with col_btn_pdf:
        pdf_buf = generate_pdf_report(eval_name, eval_pos, cap_list)
        st.download_button(
            label="📄 Unduh Laporan Resmi Audit COBIT 2019 (PDF)",
            data=pdf_buf, 
            file_name=f"Laporan_Audit_COBIT2019_UNKLAB_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf", 
            type="primary", 
            use_container_width=True
        )