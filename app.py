import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# Mengimpor modul dari engine.py
from engine import (
    init_db, register_user, authenticate_user, 
    save_respondent_data, save_capability_data,
    calc_fuzzy_5, calc_fuzzy_3, calc_percentage_avg,
    get_rating_level_cobit, generate_pdf_report, DB_FILE
)

# Inisialisasi Database
init_db()

# ==========================================
# PAGE CONFIGURATION & METADATA
# ==========================================
st.set_page_config(
    page_title="COBIT 2019 Governance & Fuzzy Logic - UNKLAB",
    page_icon="🏛️",
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

    /* User Profile Card on Sidebar */
    .user-profile-badge {
        background: linear-gradient(135deg, #0A2540 0%, #1E3A8A 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 16px;
        color: #FFFFFF;
        margin-bottom: 16px;
        box-shadow: 0 6px 18px -4px rgba(10, 37, 64, 0.35);
    }

    .user-role-pill {
        display: inline-block;
        background: #F59E0B;
        color: #1E293B;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .user-role-pill.respondent {
        background: #38BDF8;
        color: #0C4A6E;
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
        "type": "fuzzy", 
        "scale": 5, 
        "desc": "Profil dan mitigasi risiko Teknologi Informasi kampus",
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
            <span>🏛️ ISACA COBIT 2019 & FUZZY LOGIC ENGINE</span>
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
        
        tab_login, tab_register = st.tabs(["🔑 Masuk (Sign In)", "📝 Daftar Akun Baru"])
        
        with tab_login:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            login_user = st.text_input("Username Auditor / Responden:", placeholder="cth: admin / auditor", key="login_username")
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
            <span>🛡️ Enkripsi Kata Sandi SHA-256</span> • <span>Algoritma Agregasi TFN Defuzzifikasi</span>
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
st.sidebar.markdown(f"""
<div class="user-profile-badge">
    <div class="user-role-pill {role_class}">{role_label}</div>
    <div style="font-size: 1.05rem; font-weight: 700; line-height: 1.3;">{user_p['fullname']}</div>
    <div style="font-size: 0.78rem; opacity: 0.85; margin-top: 2px;">{user_p['position']}</div>
    <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.15); font-size: 0.72rem; color: #93C5FD; display: flex; align-items: center; gap: 6px;">
        <span style="display:inline-block; width:7px; height:7px; background:#10B981; border-radius:50%;"></span>
        Sesi Aktif di SQLite
    </div>
</div>
""", unsafe_allow_html=True)

if is_admin:
    menu = st.sidebar.radio(
        "NAVIGASI MODUL UTAMA:",
        [
            "1. Input Penilaian Design Factor (DF1-DF10)", 
            "2. Rekapitulasi & Visualisasi Design Factor", 
            "3. Riwayat Responden & Database", 
            "4. Capability Level & Export PDF"
        ]
    )
else:
    menu = st.sidebar.radio(
        "NAVIGASI MODUL UTAMA:",
        [
            "1. Input Penilaian Design Factor (DF1-DF10)", 
            "4. Capability Level & Export PDF"
        ]
    )

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px; font-size:0.75rem; color:#475569;">
    <strong style="color:#0F172A;">📐 Landasan Analisis:</strong><br>
    • <b>COBIT 2019:</b> 10 Design Factors & 4 Domain Prioritas UNKLAB (APO12, APO13, DSS05, MEA03).<br>
    • <b>Fuzzy Logic:</b> Triangular Fuzzy Number (TFN) & Bobot Defuzzifikasi Rata-Rata ($z^*$).
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.calculated_results = {}
    st.rerun()

# HERO HEADER AT TOP OF MAIN DASHBOARD
st.markdown("""
<div class="cobit-hero-header">
    <div class="cobit-badge-ribbon">
        <span>🏛️ ISACA COBIT 2019</span>
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
# MODUL 1: INPUT PENILAIAN DF1 - DF10
# ----------------------------------------------------
if menu == "1. Input Penilaian Design Factor (DF1-DF10)":
    st.markdown("""
    <div style="margin-bottom:14px;">
        <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">Formulir Pengisian Kuesioner (DF1 - DF10)</h2>
        <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Evaluasi penilaian ganda (Responden 1 & 2) dengan kalkulasi otomatis Fuzzy TFN / Persentase Agregat</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("👤 Identitas Penilai & Metadata Audit", expanded=True):
        col_resp_a, col_resp_b = st.columns(2)
        resp_name = col_resp_a.text_input("Nama Penilai / Lead Auditor:", value=user_p['fullname'])
        resp_pos = col_resp_b.text_input("Jabatan / Unit Kerja Evaluasi:", value=user_p['position'])

    tab_labels = [f"📊 {code}" for code in df_definitions.keys()]
    tabs = st.tabs(tab_labels)
    temp_results = {}

    for idx, (df_code, df_info) in enumerate(df_definitions.items()):
        with tabs[idx]:
            is_fuzzy = (df_info["type"] == "fuzzy")
            method_badge = "📐 Fuzzy TFN" if is_fuzzy else "📈 Direct Percentage"
            scale_badge = f"Skala 1-{df_info['scale']}" if is_fuzzy else "Skala 0-100%"
            
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
            col_r1, col_r2 = st.columns(2)
            
            r1_vals, r2_vals = [], []
            
            with col_r1:
                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; margin-bottom:10px;">
                    <strong style="color:#1E3A8A; font-size:0.85rem;">👤 Responden 1 (Cth: Douglas Rasuh)</strong>
                </div>
                """, unsafe_allow_html=True)
                for i, item in enumerate(items):
                    if is_fuzzy:
                        val = st.slider(f"[R1] {item}", 1, df_info["scale"], 3, key=f"r1_{df_code}_{i}")
                    else:
                        val = st.slider(f"[R1] {item}", 0, 100, 50, step=5, key=f"r1_{df_code}_{i}")
                    r1_vals.append(val)

            with col_r2:
                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; margin-bottom:10px;">
                    <strong style="color:#0284C7; font-size:0.85rem;">👤 Responden 2 (Cth: Enrico Djimesha)</strong>
                </div>
                """, unsafe_allow_html=True)
                for i, item in enumerate(items):
                    if is_fuzzy:
                        val = st.slider(f"[R2] {item}", 1, df_info["scale"], 3, key=f"r2_{df_code}_{i}")
                    else:
                        val = st.slider(f"[R2] {item}", 0, 100, 50, step=5, key=f"r2_{df_code}_{i}")
                    r2_vals.append(val)
            
            rows = []
            for item, r1, r2 in zip(items, r1_vals, r2_vals):
                if is_fuzzy:
                    scale_max = df_info["scale"]
                    final_sc = calc_fuzzy_5(r1, r2) if scale_max == 5 else calc_fuzzy_3(r1, r2)
                else:
                    final_sc = calc_percentage_avg(r1, r2)
                    
                rows.append({
                    "indicator": item, 
                    "method": "Fuzzy Logic TFN" if is_fuzzy else "Direct Percentage (%)", 
                    "r1": r1, 
                    "r2": r2, 
                    "final": final_sc
                })
            temp_results[df_code] = rows

    st.session_state.calculated_results = temp_results

    st.markdown("<br>", unsafe_allow_html=True)
    col_save, col_info_box = st.columns([1.2, 2])
    with col_save:
        if st.button("💾 Simpan Penilaian ke Database SQLite", type="primary", use_container_width=True):
            if resp_name.strip() == "":
                st.error("Silakan isi nama penilai terlebih dahulu.")
            else:
                r_id = save_respondent_data(resp_name, resp_pos, temp_results)
                st.success(f"✅ Penilaian berhasil direkam ke database dengan Respondent ID #{r_id}!")
    with col_info_box:
        st.info("💡 Data yang dihitung secara *live* di atas langsung tersedia di menu **Visualisasi & Rekapitulasi**.")

# ----------------------------------------------------
# MODUL 2: REKAPITULASI & VISUALISASI DESIGN FACTOR
# ----------------------------------------------------
elif menu == "2. Rekapitulasi & Visualisasi Design Factor":
    if not is_admin:
        st.error("⛔ Akses Terbatas: Modul ini dikhususkan bagi Administrator.")
        st.stop()
        
    st.markdown("""
    <div style="margin-bottom:16px;">
        <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">Rekapitulasi Agregat & Analisis Visual Design Factor</h2>
        <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Visualisasi polar radar untuk skor Fuzzy Logic dan bar horizontal untuk persentase faktor tata kelola</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.calculated_results:
        st.warning("⚠️ Belum ada data penilaian aktif. Harap buka Menu 1 untuk mengisi kuesioner terlebih dahulu.")
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
                    <strong style="color:#0F172A; font-size:0.95rem;">📊 Persentase DF (DF5-DF10)</strong>
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
        st.markdown("<h3 style='font-size:1.1rem; font-weight:700; color:#0F172A; margin-bottom:10px;'>📋 Tabel Detail Agregasi 10 Design Factors</h3>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

# ----------------------------------------------------
# MODUL 3: RIWAYAT DATABASE SQLITE
# ----------------------------------------------------
elif menu == "3. Riwayat Responden & Database":
    if not is_admin:
        st.error("⛔ Akses Terbatas: Modul ini dikhususkan bagi Administrator.")
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
    
    tab_db1, tab_db2, tab_db3 = st.tabs(["👥 Riwayat Responden", "🛡️ Akun Auditor", "📈 Riwayat Kapabilitas"])
    
    with tab_db1:
        if df_resps.empty:
            st.info("ℹ️ Belum ada data responden yang tersimpan di basis data.")
        else:
            st.dataframe(df_resps, use_container_width=True)
            
    with tab_db2:
        st.dataframe(df_users, use_container_width=True)
        
    with tab_db3:
        if df_cap_history.empty:
            st.info("ℹ️ Belum ada riwayat evaluasi capability level di database.")
        else:
            st.dataframe(df_cap_history, use_container_width=True)

# ----------------------------------------------------
# MODUL 4: CAPABILITY LEVEL & EXPORT PDF
# ----------------------------------------------------
elif menu == "4. Capability Level & Export PDF":
    st.markdown("""
    <div style="margin-bottom:16px;">
        <h2 style="margin:0; font-size:clamp(1.15rem, 2.5vw, 1.45rem); font-weight:800; color:#0F172A;">Penilaian Capability Level & Analisis Gap</h2>
        <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">Evaluasi 4 domain prioritas Universitas Klabat beserta penerbitan laporan resmi (PDF)</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Metadata Evaluator / Lead Auditor", expanded=True):
        col_e1, col_e2 = st.columns(2)
        eval_name = col_e1.text_input("Nama Lead Evaluator:", value=user_p['fullname'])
        eval_pos = col_e2.text_input("Jabatan Evaluator:", value=user_p['position'])
    
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px 18px; margin-bottom:16px;">
        <h3 style="margin:0 0 4px 0; font-size:1.05rem; font-weight:700; color:#0F172A;">🎛️ Input Persentase Pencapaian (4 Domain Prioritas UNKLAB)</h3>
        <p style="margin:0 0 12px 0; font-size:0.82rem; color:#64748B;">Geser slider untuk menentukan persentase pemenuhan pada masing-masing domain audit</p>
    """, unsafe_allow_html=True)
    
    col_cap1, col_cap2 = st.columns(2)
    with col_cap1:
        p_apo12 = st.slider("📌 APO12 — Managed Risk (%)", 0, 100, 8, help="Manajemen Risiko TI Institusi")
        p_apo13 = st.slider("📌 APO13 — Managed Security (%)", 0, 100, 42, help="Sistem Manajemen Keamanan Informasi")
    with col_cap2:
        p_dss05 = st.slider("📌 DSS05 — Security Services (%)", 0, 100, 75, help="Operasional Layanan Keamanan Jaringan & Data")
        p_mea03 = st.slider("📌 MEA03 — Managed Compliance (%)", 0, 100, 31, help="Kepatuhan terhadap Regulasi Eksternal & Internal")
        
    st.markdown("</div>", unsafe_allow_html=True)

    domain_inputs = [
        ("APO12 - Managed Risk", p_apo12),
        ("APO13 - Managed Security", p_apo13),
        ("DSS05 - Security Services", p_dss05),
        ("MEA03 - Compliance", p_mea03)
    ]

    cap_list = []
    for d_code, pct in domain_inputs:
        rating, as_is_lvl = get_rating_level_cobit(pct)
        target_lvl = 3
        cap_list.append({
            "domain": d_code, 
            "as_is": as_is_lvl, 
            "to_be": target_lvl, 
            "gap": target_lvl - as_is_lvl, 
            "pct": pct, 
            "rating": rating
        })

    col_cap_chart1, col_cap_chart2 = st.columns(2)
    
    with col_cap_chart1:
        st.markdown("""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:14px 16px; margin-bottom:12px; box-shadow: 0 4px 14px -2px rgba(15,23,42,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <strong style="color:#0F172A; font-size:0.95rem;">📊 Tingkat Kapabilitas: As-Is vs To-Be</strong>
                <span style="font-size:0.72rem; background:#FEF3C7; color:#92400E; padding:2px 7px; border-radius:4px; font-weight:600;">Target: Level 3</span>
            </div>
        """, unsafe_allow_html=True)
        
        domains_short = [x['domain'].split()[0] for x in cap_list]
        fig_cap, ax_cap = plt.subplots(figsize=(5.5, 4.0), dpi=150)
        fig_cap.patch.set_facecolor('#FFFFFF')
        ax_cap.set_facecolor('#FFFFFF')
        
        x = np.arange(len(domains_short))
        width = 0.32
        
        rects1 = ax_cap.bar(x - width/2, [x['as_is'] for x in cap_list], width, label='Level As-Is (Saat Ini)', color='#D97706', edgecolor='none')
        rects2 = ax_cap.bar(x + width/2, [x['to_be'] for x in cap_list], width, label='Level To-Be (Target)', color='#1E3A8A', edgecolor='none')
        
        ax_cap.set_xticks(x)
        ax_cap.set_xticklabels(domains_short, fontweight='bold', fontsize=9, color='#0F172A')
        ax_cap.set_ylim(0, 4.2)
        ax_cap.set_yticks([0, 1, 2, 3, 4])
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
                <strong style="color:#0F172A; font-size:0.95rem;">🍩 Capaian Proses Domain Prioritas</strong>
                <span style="font-size:0.72rem; background:#ECFDF5; color:#065F46; padding:2px 7px; border-radius:4px; font-weight:600;">Persentase (%)</span>
            </div>
        """, unsafe_allow_html=True)
        
        fig_donut, ax_donut = plt.subplots(figsize=(5.5, 4.0), dpi=150)
        fig_donut.patch.set_facecolor('#FFFFFF')
        
        donut_colors = ['#BE123C', '#F59E0B', '#10B981', '#6366F1']
        wedges, texts, autotexts = ax_donut.pie(
            [x['pct'] for x in cap_list], 
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
            
        ax_donut.text(0, 0, 'COBIT 2019\nUNKLAB', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E3A8A')
        fig_donut.tight_layout()
        
        st.pyplot(fig_donut, use_container_width=True)
        plt.close(fig_donut)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.1rem; font-weight:700; color:#0F172A; margin-bottom:10px;'>📋 Tabel Evaluasi Kesenjangan (Gap Analysis)</h3>", unsafe_allow_html=True)
    
    df_cap_display = pd.DataFrame(cap_list)
    df_cap_display.columns = ["Domain Evaluasi", "Level As-Is", "Target To-Be", "Gap (Level)", "Pencapaian (%)", "COBIT Rating Scale"]
    st.dataframe(df_cap_display, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn_db, col_btn_pdf = st.columns(2)
    
    with col_btn_db:
        if st.button("💾 Simpan Hasil Evaluasi ke Database SQLite", type="secondary", use_container_width=True):
            for item in cap_list:
                save_capability_data(item['domain'], item['as_is'], item['to_be'], item['gap'], item['pct'], item['rating'])
            st.success("✅ Seluruh data assessment kapabilitas berhasil direkam ke database!")

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