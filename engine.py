import sqlite3
import hashlib
import io
import os
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Simpan database di folder home pengguna agar tidak kena error 'unable to open database file'
DB_FILE = os.path.join(os.path.expanduser("~"), "cobit2019_unklab.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            fullname TEXT NOT NULL,
            position TEXT NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Responden'")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respondents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS df_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respondent_id INTEGER,
            df_code TEXT NOT NULL,
            indicator_name TEXT NOT NULL,
            calc_method TEXT NOT NULL,
            score_r1 REAL NOT NULL,
            score_r2 REAL NOT NULL,
            final_result REAL NOT NULL,
            FOREIGN KEY (respondent_id) REFERENCES respondents (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS capability_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_code TEXT NOT NULL,
            as_is_level INTEGER NOT NULL,
            to_be_level INTEGER NOT NULL,
            gap INTEGER NOT NULL,
            achievement_pct REAL NOT NULL,
            rating_scale TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, fullname, position, role, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, fullname, position, role, password_hash) VALUES (?, ?, ?, ?, ?)",
            (username.strip().lower(), fullname.strip(), position.strip(), role, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Akun berhasil dibuat! Silahkan login."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username sudah digunakan!"

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, fullname, position, role, password_hash FROM users WHERE username = ?",
        (username.strip().lower(),)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user and user[5] == hash_password(password):
        return True, {"id": user[0], "username": user[1], "fullname": user[2], "position": user[3], "role": user[4]}
    return False, None

def save_respondent_data(name, position, df_results_dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO respondents (name, position) VALUES (?, ?)", (name, position))
    respondent_id = cursor.lastrowid
    
    for df_code, items in df_results_dict.items():
        for row in items:
            cursor.execute(
                '''INSERT INTO df_responses 
                   (respondent_id, df_code, indicator_name, calc_method, score_r1, score_r2, final_result) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (respondent_id, df_code, row['indicator'], row['method'], row['r1'], row['r2'], row['final'])
            )
    conn.commit()
    conn.close()
    return respondent_id

def save_capability_data(domain_code, as_is, to_be, gap, pct, rating):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO capability_assessments (domain_code, as_is_level, to_be_level, gap, achievement_pct, rating_scale) VALUES (?, ?, ?, ?, ?, ?)",
        (domain_code, as_is, to_be, gap, pct, rating)
    )
    conn.commit()
    conn.close()

# --- Engine Fuzzy & Percentage ---
def get_tfn_5(skor):
    tfn_map = {1: (0.00, 0.00, 0.25), 2: (0.00, 0.25, 0.50), 3: (0.25, 0.50, 0.75), 4: (0.50, 0.75, 1.00), 5: (0.75, 1.00, 1.00)}
    return tfn_map.get(skor, (0.00, 0.00, 0.00))

def get_tfn_3(skor):
    tfn_map = {1: (0.00, 0.00, 0.50), 2: (0.25, 0.50, 0.75), 3: (0.50, 1.00, 1.00)}
    return tfn_map.get(skor, (0.00, 0.00, 0.00))

def calc_fuzzy_5(r1, r2):
    t1, t2 = get_tfn_5(r1), get_tfn_5(r2)
    a_avg, b_avg, c_avg = (t1[0] + t2[0])/2.0, (t1[1] + t2[1])/2.0, (t1[2] + t2[2])/2.0
    z_star = (a_avg + b_avg + c_avg) / 3.0
    return round(1 + (z_star * 4), 2)

def calc_fuzzy_3(r1, r2):
    t1, t2 = get_tfn_3(r1), get_tfn_3(r2)
    a_avg, b_avg, c_avg = (t1[0] + t2[0])/2.0, (t1[1] + t2[1])/2.0, (t1[2] + t2[2])/2.0
    z_star = (a_avg + b_avg + c_avg) / 3.0
    return round(1 + (z_star * 2), 2)

def calc_percentage_avg(r1_pct, r2_pct):
    return round((r1_pct + r2_pct) / 2.0, 2)

def get_rating_level_cobit(pct):
    if pct < 15: return "N - Not Achieved (0-14%)", 1
    elif pct < 50: return "P - Partially Achieved (15-49%)", 1
    elif pct < 85: return "L - Largely Achieved (50-84%)", 1
    else: return "F - Fully Achieved (85-100%)", 2

def generate_pdf_report(evaluator_name, evaluator_pos, capability_data_list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    cobit_navy = colors.HexColor('#0B192C')
    cobit_blue = colors.HexColor('#1E3A8A')
    cobit_gold = colors.HexColor('#D97706')
    slate_bg = colors.HexColor('#F8FAFC')
    border_grey = colors.HexColor('#CBD5E1')
    
    title_style = ParagraphStyle(
        'CobitTitle', 
        parent=styles['Heading1'], 
        fontSize=15, 
        alignment=1, 
        textColor=cobit_navy,
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'CobitSubtitle', 
        parent=styles['Normal'], 
        alignment=1, 
        fontSize=10.5, 
        textColor=cobit_blue,
        fontName='Helvetica-Bold',
        spaceAfter=14
    )
    section_heading = ParagraphStyle(
        'SectionHeading', 
        parent=styles['Heading2'], 
        fontSize=10, 
        textColor=cobit_navy, 
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )
    
    story.append(Paragraph("LAPORAN RESMI AUDIT TATA KELOLA TEKNOLOGI INFORMASI", title_style))
    story.append(Paragraph("ISACA COBIT 2019 & FUZZY MULTI-CRITERIA &bull; UNIVERSITAS KLABAT", subtitle_style))
    story.append(Spacer(1, 4))
    
    info_data = [
        ["Lead Evaluator / Auditor:", evaluator_name, "Tanggal Dokumen:", datetime.now().strftime("%d %B %Y, %H:%M WITA")],
        ["Jabatan / Unit Kerja:", evaluator_pos, "Metodologi:", "Triangular Fuzzy Number (TFN) & Agregasi Langsung"]
    ]
    t_info = Table(info_data, colWidths=[120, 160, 100, 160])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), slate_bg),
        ('GRID', (0,0), (-1,-1), 0.5, border_grey),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>I. Evaluasi Tingkat Kemampuan (Capability Level) & Analisis Kesenjangan (Gap)</b>", section_heading))
    table_headers = [["Domain Prioritas", "Level As-Is", "Target To-Be", "Gap", "% Capaian", "Rating Scale COBIT"]]
    
    for item in capability_data_list:
        table_headers.append([
            item['domain'], 
            f"Level {item['as_is']}", 
            f"Level {item['to_be']}", 
            f"{item['gap']} Level", 
            f"{item['pct']:.1f}%", 
            item['rating']
        ])
        
    t_cap = Table(table_headers, colWidths=[160, 65, 65, 60, 75, 115])
    t_cap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), cobit_navy),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, border_grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, slate_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cap)
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("<b>II. Rekomendasi Strategis Perbaikan Tata Kelola TI:</b>", section_heading))
    recoms = [
        "1. <b>APO12 (Managed Risk):</b> Memformalkan dokumen Kebijakan Manajemen Risiko TI dan menyusun Register Risiko berkala di lingkungan Universitas Klabat.",
        "2. <b>APO13 (Managed Security):</b> Mengembangkan Kebijakan Sistem Manajemen Keamanan Informasi (SMKI) dan menetapkan tim tanggap insiden siber kampus.",
        "3. <b>DSS05 (Security Services):</b> Menetapkan SOP penanganan akses dan kerahasiaan data mahasiswa/dosen serta melaksanakan audit log secara periodik.",
        "4. <b>MEA03 (Managed Compliance):</b> Membentuk matriks kepatuhan terpadu untuk memastikan keselarasan terhadap regulasi Kemendikbudristek dan UU PDP."
    ]
    for rec in recoms:
        story.append(Paragraph(rec, normal_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 18))
    
    # Signature / Legal Block
    sig_data = [
        ["Diverifikasi oleh:", "Disetujui oleh:"],
        ["\n\n\n__________________________", "\n\n\n__________________________"],
        [f"<b>{evaluator_name}</b>", "<b>Pimpinan / Direktur SIU UNKLAB</b>"],
        [evaluator_pos, "Universitas Klabat"]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_sig)
        
    doc.build(story)
    buffer.seek(0)
    return buffer