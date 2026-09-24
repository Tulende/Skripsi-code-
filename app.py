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
# CONFIGURATION & CUSTOM STYLING (CSS)
# ==========================================
st.set_page_config(
    page_title="Audit COBIT 2019 - UNKLAB",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .header-banner {
        background: linear-gradient(90deg, #1E3C72 0%, #2A5298 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .user-card {
        background-color: #e3f2fd;
        border-left: 4px solid #1e88e5;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Struktur Data Design Factor (DF1 - DF10)
df_definitions = {
    "DF1": {"title": "DF1: Enterprise Strategy", "type": "fuzzy", "scale": 5, "items": ["Growth / Acquisition", "Innovation / Differentiation", "Cost Leadership", "Client Service / Operational Stability"]},
    "DF2": {"title": "DF2: Enterprise Goals", "type": "fuzzy", "scale": 5, "items": ["EG01: Portfolio of products", "EG02: Financial risk", "EG03: Compliance laws", "EG04: Quality of financial info", "EG05: Customer-Oriented culture", "EG06: Business continuity", "EG07: Quality of management info", "EG08: Internal business process", "EG09: Optimization of process costs", "EG10: Staff skills & productivity", "EG11: Compliance with internal policies", "EG12: Managed digital transformation", "EG13: Product & business innovation"]},
    "DF3": {"title": "DF3: Risk Profile", "type": "fuzzy", "scale": 5, "items": ["IT Investment Decision Making", "Program & Project Life Cycle", "IT Cost & Oversight", "IT Expertise & Skills", "Enterprise/IT Architecture", "IT Infrastructure Incidents", "Unauthorized Actions", "Software Adoption Problems", "Hardware Incidents", "Software Failures", "Logical Attacks (Hacking/Malware)", "Third-Party / Supplier Incidents", "Noncompliance", "Geopolitical Issues", "Industrial Action", "Acts of Nature", "Technology-Based Innovation", "Environmental", "Data & Information Management"]},
    "DF4": {"title": "DF4: I&T Related Issues", "type": "fuzzy", "scale": 3, "items": ["Frustration antara entitas TI", "Frustration antara dept bisnis & TI", "Insiden TI serius (kehilangan data, keamanan)", "Masalah pengiriman layanan outsourcer", "Kegagalan memenuhi regulasi TI", "Temuan audit kinerja TI buruk", "Pengeluaran TI tidak resmi / tersembunyi", "Duplikasi & tumpang tindih inisiatif TI", "SDM TI tidak mencukupi / kurang keahlian", "Perubahan TI gagal memenuhi bisnis", "Eksekutif enggan terlibat keputusan TI", "Model operasi TI terlalu rumit", "Biaya TI dinilai terlalu tinggi", "Arsitektur TI menghambat inisiatif baru", "Kesenjangan pengetahuan bisnis & teknis", "Masalah kualitas & integrasi data", "End-user computing tinggi tanpa pengawasan", "Dept bisnis bangun solusi TI sendiri", "Pengabaian regulasi privasi", "Ketidakmampuan manfaatkan teknologi baru"]},
    "DF5": {"title": "DF5: Threat Landscape", "type": "percentage", "scale": 100, "items": ["High Threat Landscape (%)", "Normal Threat Landscape (%)"]},
    "DF6": {"title": "DF6: Compliance Requirements", "type": "percentage", "scale": 100, "items": ["High Compliance (%)", "Normal Compliance (%)", "Low Compliance (%)"]},
    "DF7": {"title": "DF7: Role of IT", "type": "fuzzy", "scale": 5, "items": ["Support Role", "Factory Role", "Turnaround Role", "Strategic Role"]},
    "DF8": {"title": "DF8: Sourcing Model for IT", "type": "percentage", "scale": 100, "items": ["In-sourced (%)", "Outsourcing (%)", "Cloud Services (%)"]},
    "DF9": {"title": "DF9: IT Implementation Methods", "type": "percentage", "scale": 100, "items": ["Agile (%)", "DevOps (%)", "Traditional / Waterfall (%)"]},
    "DF10": {"title": "DF10: Tech Adoption Strategy", "type": "percentage", "scale": 100, "items": ["First Mover (%)", "Follower (%)", "Slow Adopter (%)"]}
}

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "calculated_results" not in st.session_state:
    st.session_state.calculated_results = {}

# ==========================================
# PAGE 1: AUTHENTICATION
# ==========================================
if not st.session_state.authenticated:
    st.markdown("""
    <div class="header-banner" style="text-align: center;">
        <h2>Sistem Audit COBIT 2019 - Universitas Klabat</h2>
        <p>Silahkan Sign In atau Registrasi Akun Baru untuk Memulai</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        auth_tab1, auth_tab2 = st.tabs(["Sign In (Masuk)", "Sign Up (Pendaftaran)"])
        
        with auth_tab1:
            st.subheader("Sign In")
            login_user = st.text_input("Username:", key="login_username")
            login_pass = st.text_input("Password:", type="password", key="login_password")
            
            if st.button("Sign In", type="primary", use_container_width=True):
                if not login_user or not login_pass:
                    st.error("Silakan isi Username dan Password!")
                else:
                    success, user_data = authenticate_user(login_user, login_pass)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_data
                        st.success(f"Selamat datang, {user_data['fullname']} ({user_data['role']})!")
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")

        with auth_tab2:
            st.subheader("Sign Up Akun Baru")
            reg_user = st.text_input("Username Baru:", key="reg_username")
            reg_name = st.text_input("Nama Lengkap:", key="reg_fullname")
            reg_pos = st.selectbox("Jabatan / Unit Kerja:", ["IT Supervisor UNKLAB", "NOC Engineer", "Kepala SIU UNKLAB", "Staf IT", "Auditor Internal"], key="reg_position")
            reg_role = st.selectbox("Pilih Peran (Role):", ["Responden", "Admin"], key="reg_role_select")
            reg_pass1 = st.text_input("Password:", type="password", key="reg_pass1")
            reg_pass2 = st.text_input("Konfirmasi Password:", type="password", key="reg_pass2")
            
            if st.button("Daftarkan Akun", type="primary", use_container_width=True):
                if not reg_user or not reg_name or not reg_pass1:
                    st.error("Harap isi semua kolom!")
                elif reg_pass1 != reg_pass2:
                    st.error("Password tidak cocok!")
                else:
                    ok, msg = register_user(reg_user, reg_name, reg_pos, reg_role, reg_pass1)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
    st.stop()

# ==========================================
# PAGE 2: MAIN DASHBOARD
# ==========================================
user_p = st.session_state.user_info
role_badge = "ADMIN" if user_p['role'] == "Admin" else " RESPONDEN"

st.sidebar.markdown(f"""
<div class="user-card">
    <b> Login Sebagai:</b> {role_badge}<br>
    <strong>{user_p['fullname']}</strong><br>
    <small>{user_p['position']}</small>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Logout / Sign Out", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.calculated_results = {}
    st.rerun()

st.sidebar.markdown("---")

st.markdown("""
<div class="header-banner">
    <h2 style="margin:0; color:white;"> Dashboard Evaluasi Tata Kelola TI COBIT 2019</h2>
    <p style="margin:5px 0 0 0; opacity:0.9;">Universitas Klabat (UNKLAB) | Fuzzy Logic & Percentage Engine</p>
</div>
""", unsafe_allow_html=True)

if user_p['role'] == "Admin":
    menu = st.sidebar.radio(
        "Navigasi Menu (Admin):",
        ["1. Input Penilaian Design Factor (DF1-DF10)", "2. Rekapitulasi & Visualisasi Design Factor", "3. Riwayat Responden di Database", "4. Capability Level & Export PDF"]
    )
else:
    menu = st.sidebar.radio(
        "Navigasi Menu (Responden):",
        ["1. Input Penilaian Design Factor (DF1-DF10)", "4. Capability Level & Export PDF"]
    )
    st.sidebar.info(" Anda login sebagai **Responden**.")

# ------------------------------------------
# MODUL 1: INPUT PENILAIAN DF1 - DF10
# ------------------------------------------
if menu == "1. Input Penilaian Design Factor (DF1-DF10)":
    st.header("Input Kuesioner Responden")
    
    with st.expander("Data Responden / Penilai", expanded=True):
        c_a, c_b = st.columns(2)
        resp_name = c_a.text_input("Nama Penilai / Auditor:", value=user_p['fullname'])
        resp_pos = c_b.text_input("Jabatan / Unit Work:", value=user_p['position'])

    tabs = st.tabs([f"DF{i}" for i in range(1, 11)])
    temp_results = {}

    for idx, (df_code, df_info) in enumerate(df_definitions.items()):
        with tabs[idx]:
            st.subheader(df_info["title"])
            method_label = "Fuzzy Logic TFN" if df_info["type"] == "fuzzy" else "Direct Percentage (%) Average"
            
            col_info1, col_info2 = st.columns([3, 1])
            col_info1.caption(f"Metode: **{method_label}**")
            col_info2.metric("Skala Penilaian", f"1 - {df_info['scale']}" if df_info["type"] == "fuzzy" else "0 - 100%")
            
            items = df_info["items"]
            col_r1, col_r2 = st.columns(2)
            
            r1_vals, r2_vals = [], []
            
            with col_r1:
                st.markdown("**Responden 1 (R1 - Cth: Douglas Rasuh)**")
                for i, item in enumerate(items):
                    if df_info["type"] == "fuzzy":
                        val = st.slider(f"[R1] {item}", 1, df_info["scale"], 3, key=f"r1_{df_code}_{i}")
                    else:
                        val = st.slider(f"[R1] {item}", 0, 100, 50, step=5, key=f"r1_{df_code}_{i}")
                    r1_vals.append(val)

            with col_r2:
                st.markdown(" **Responden 2 (R2 - Cth: Enrico Djimesha)**")
                for i, item in enumerate(items):
                    if df_info["type"] == "fuzzy":
                        val = st.slider(f"[R2] {item}", 1, df_info["scale"], 3, key=f"r2_{df_code}_{i}")
                    else:
                        val = st.slider(f"[R2] {item}", 0, 100, 50, step=5, key=f"r2_{df_code}_{i}")
                    r2_vals.append(val)
            
            rows = []
            for item, r1, r2 in zip(items, r1_vals, r2_vals):
                if df_info["type"] == "fuzzy":
                    scale_max = df_info["scale"]
                    final_sc = calc_fuzzy_5(r1, r2) if scale_max == 5 else calc_fuzzy_3(r1, r2)
                else:
                    final_sc = calc_percentage_avg(r1, r2)
                    
                rows.append({"indicator": item, "method": method_label, "r1": r1, "r2": r2, "final": final_sc})
            temp_results[df_code] = rows

    st.session_state.calculated_results = temp_results

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Simpan Seluruh Data Penilaian ke Database SQLite", type="primary", use_container_width=True):
        if resp_name.strip() == "":
            st.error("Silahkan isi Nama Penilai terlebih dahulu!")
        else:
            r_id = save_respondent_data(resp_name, resp_pos, temp_results)
            st.success(f"Data Penilaian berhasil disimpan ke Database dengan ID Responden #{r_id}!")

# ------------------------------------------
# MODUL 2: REKAPITULASI & VISUALISASI
# ------------------------------------------
elif menu == "2. Rekapitulasi & Visualisasi Design Factor":
    if user_p['role'] != "Admin":
        st.error("Akses ditolak! Menu ini khusus untuk Admin.")
        st.stop()
        
    st.header("Rekapitulasi & Visualisasi Grafik DF1 - DF10")
    
    if not st.session_state.calculated_results:
        st.warning("Silahkan isi dan hitung kuesioner pada Menu 1 terlebih dahulu.")
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
                "Design Factor": df_code, "Nama DF": df_definitions[df_code]["title"],
                "Metode": method, "Avg R1": round(avg_r1, 2), "Avg R2": round(avg_r2, 2),
                "Hasil Akhir Agregat": f"{round(avg_final, 2)}{unit}"
            })
            
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rata-rata Fuzzy DF1-4", f"{np.mean(list(fuzzy_scores.values())[:4]):.2f} / 5.0")
        m2.metric("Fuzzy DF7", f"{fuzzy_scores.get('DF7', 0):.2f} / 5.0")
        m3.metric("Rata-rata Persentase DF5-10", f"{np.mean(list(pct_scores.values())):.1f}%")
        m4.metric("Total DF", "10 Factor")

        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Radar Chart: Skor Fuzzy DF")
            categories = list(fuzzy_scores.keys())
            values = list(fuzzy_scores.values())
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            fig, ax = plt.subplots(figsize=(6, 5), subplot_kw=dict(polar=True))
            ax.plot(angles + [angles[0]], values + [values[0]], color='#1E88E5', linewidth=2.5)
            ax.fill(angles + [angles[0]], values + [values[0]], color='#1E88E5', alpha=0.3)
            ax.set_xticks(angles)
            ax.set_xticklabels(categories, fontweight='bold')
            ax.set_ylim(0, 5)
            st.pyplot(fig)

        with col_chart2:
            st.subheader("Bar Chart: Persentase DF")
            fig2, ax2 = plt.subplots(figsize=(6, 4.3))
            ax2.barh(list(pct_scores.keys()), list(pct_scores.values()), color='#26A69A', height=0.55)
            ax2.set_xlim(0, 100)
            st.pyplot(fig2)

        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

# ------------------------------------------
# MODUL 3: RIWAYAT DATABASE
# ------------------------------------------
elif menu == "3. Riwayat Responden di Database":
    if user_p['role'] != "Admin":
        st.error("Akses ditolak! Menu ini khusus untuk Admin.")
        st.stop()
        
    st.header(" Riwayat Data di Database SQLite")
    conn = sqlite3.connect(DB_FILE)
    df_resps = pd.read_sql_query("SELECT * FROM respondents ORDER BY id DESC", conn)
    df_users = pd.read_sql_query("SELECT id, username, fullname, position, role, created_at FROM users ORDER BY id DESC", conn)
    conn.close()
    
    tab_db1, tab_db2 = st.tabs(["Riwayat Penilaian Responden", "Data Akun Auditor"])
    with tab_db1:
        if df_resps.empty: st.info("Belum ada data.")
        else: st.dataframe(df_resps, use_container_width=True)
    with tab_db2:
        st.dataframe(df_users, use_container_width=True)

# ------------------------------------------
# MODUL 4: CAPABILITY LEVEL & EXPORT PDF
# ------------------------------------------
elif menu == "4. Capability Level & Export PDF":
    st.header("Assessment Capability Level & Analisis Gap (COBIT 2019)")
    
    col_e1, col_e2 = st.columns(2)
    eval_name = col_e1.text_input("Nama Evaluator Audit:", value=user_p['fullname'])
    eval_pos = col_e2.text_input("Jabatan Evaluator:", value=user_p['position'])
    
    st.subheader("Input Persentase Pencapaian (4 Domain Prioritas UNKLAB)")
    c1, c2 = st.columns(2)
    p_apo12 = c1.slider("% Pencapaian APO12 (Managed Risk)", 0, 100, 8)
    p_apo13 = c2.slider("% Pencapaian APO13 (Managed Security)", 0, 100, 42)
    
    c3, c4 = st.columns(2)
    p_dss05 = c3.slider("% Pencapaian DSS05 (Security Services)", 0, 100, 75)
    p_mea03 = c4.slider("% Pencapaian MEA03 (Managed Compliance)", 0, 100, 31)

    cap_list = []
    for d_code, pct in [("APO12 - Managed Risk", p_apo12), ("APO13 - Managed Security", p_apo13), ("DSS05 - Security Services", p_dss05), ("MEA03 - Compliance", p_mea03)]:
        rating, as_is_lvl = get_rating_level_cobit(pct)
        target_lvl = 3
        cap_list.append({"domain": d_code, "as_is": as_is_lvl, "to_be": target_lvl, "gap": target_lvl - as_is_lvl, "pct": pct, "rating": rating})

    st.markdown("---")
    col_cap_chart1, col_cap_chart2 = st.columns(2)
    
    with col_cap_chart1:
        st.subheader("Perbandingan As-Is vs Target To-Be")
        domains = [x['domain'].split()[0] for x in cap_list]
        fig_cap, ax_cap = plt.subplots(figsize=(6, 4))
        x = np.arange(len(domains))
        ax_cap.bar(x - 0.175, [x['as_is'] for x in cap_list], 0.35, label='As-Is', color='#FFA726')
        ax_cap.bar(x + 0.175, [x['to_be'] for x in cap_list], 0.35, label='To-Be', color='#42A5F5')
        ax_cap.set_xticks(x)
        ax_cap.set_xticklabels(domains, fontweight='bold')
        ax_cap.set_ylim(0, 4)
        ax_cap.legend()
        st.pyplot(fig_cap)

    with col_cap_chart2:
        st.subheader("Donut Chart: Persentase Pencapaian")
        fig_donut, ax_donut = plt.subplots(figsize=(6, 4))
        ax_donut.pie([x['pct'] for x in cap_list], labels=domains, autopct='%1.1f%%', startangle=90, colors=['#5C6BC0', '#26A69A', '#EC407A', '#AB47BC'], wedgeprops=dict(width=0.4, edgecolor='w'))
        st.pyplot(fig_donut)

    st.subheader(" Tabel Detail Assessment Capability Level")
    st.dataframe(pd.DataFrame(cap_list), use_container_width=True)
    
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("Simpan Capability Assessment ke Database", use_container_width=True):
            for item in cap_list:
                save_capability_data(item['domain'], item['as_is'], item['to_be'], item['gap'], item['pct'], item['rating'])
            st.success("Berhasil disimpan ke database!")

    with c_btn2:
        pdf_buf = generate_pdf_report(eval_name, eval_pos, cap_list)
        st.download_button(
            label="Download Laporan Audit Resmi (PDF)",
            data=pdf_buf, file_name=f"Laporan_Audit_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf", type="primary", use_container_width=True
        )