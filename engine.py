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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS individual_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            fullname TEXT NOT NULL,
            position TEXT NOT NULL,
            df_code TEXT NOT NULL,
            indicator_name TEXT NOT NULL,
            score_val REAL,
            impact_val REAL,
            likelihood_val REAL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, df_code, indicator_name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS individual_checklist_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            fullname TEXT NOT NULL,
            position TEXT NOT NULL,
            domain_code TEXT NOT NULL,
            question_num INTEGER NOT NULL,
            answer_val INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, domain_code, question_num)
        )
    ''')

    # Auto-seed akun sistem permanen agar tidak pernah hilang saat cloud reboot/redeploy
    system_accounts = [
        ("admin", "Novanca Tulende", "Kepala SIU UNKLAB", "Admin", hash_password("admin123")),
        ("admin1", "Novanca Tulende", "IT Supervisor UNKLAB", "Admin", hash_password("admin123")),
        ("responden1", "Douglas Rasuh", "Dept. SIU (Accountable)", "Responden", hash_password("responden123")),
        ("responden2", "Enrico Djimesha", "Dept. IT (Responsible)", "Responden", hash_password("responden123")),
        ("responden", "Myeclle Kaseger", "Auditor Internal UNKLAB", "Responden", hash_password("responden123")),
    ]
    for u, name, pos, role, pw_hash in system_accounts:
        cursor.execute(
            """INSERT INTO users (username, fullname, position, role, password_hash)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(username) DO UPDATE SET 
                   password_hash = excluded.password_hash,
                   fullname = excluded.fullname,
                   position = excluded.position,
                   role = excluded.role""",
            (u, name, pos, role, pw_hash)
        )
    conn.commit()

    # Pre-seed verified responses for responden1 & responden2 if table is empty
    cursor.execute("SELECT COUNT(*) FROM individual_responses")
    if cursor.fetchone()[0] == 0:
        seed_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
        if os.path.exists(seed_path):
            try:
                import json
                with open(seed_path, 'r', encoding='utf-8') as sf:
                    seed_payload = json.load(sf)
                
                cursor.execute("SELECT id, username, fullname, position FROM users WHERE username IN ('responden1', 'responden2')")
                u_map = {row[1]: (row[0], row[2], row[3]) for row in cursor.fetchall()}
                
                for key, user_key in [("R1", "responden1"), ("R2", "responden2")]:
                    if user_key in u_map and key in seed_payload:
                        uid, fname, pos = u_map[user_key]
                        for df_c, items_dict in seed_payload[key].items():
                            for ind_name, val in items_dict.items():
                                if isinstance(val, dict):
                                    imp = val.get("impact")
                                    lik = val.get("likelihood")
                                    sc = imp * lik if (imp is not None and lik is not None) else None
                                else:
                                    sc = val
                                    imp = None
                                    lik = None
                                cursor.execute('''
                                    INSERT INTO individual_responses 
                                    (user_id, username, fullname, position, df_code, indicator_name, score_val, impact_val, likelihood_val)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ON CONFLICT(user_id, df_code, indicator_name) DO NOTHING
                                ''', (uid, user_key, fname, pos, df_c, ind_name, sc, imp, lik))
                conn.commit()
            except Exception:
                pass

    # Pre-seed verified checklist responses for responden1 & responden2 if table is empty
    cursor.execute("SELECT COUNT(*) FROM individual_checklist_responses")
    if cursor.fetchone()[0] == 0:
        seed_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
        if os.path.exists(seed_path):
            try:
                import json
                with open(seed_path, 'r', encoding='utf-8') as sf:
                    seed_payload = json.load(sf)
                
                checklists = seed_payload.get("checklist_wawancara2", {})
                cursor.execute("SELECT id, username, fullname, position FROM users WHERE username IN ('responden1', 'responden2')")
                u_map = {row[1]: (row[0], row[2], row[3]) for row in cursor.fetchall()}
                
                for key, user_key in [("R1", "responden1"), ("R2", "responden2")]:
                    if user_key in u_map and key in checklists:
                        uid, fname, pos = u_map[user_key]
                        for d_code, q_dict in checklists[key].items():
                            for q_num_str, ans_val in q_dict.items():
                                q_num = int(q_num_str)
                                cursor.execute('''
                                    INSERT INTO individual_checklist_responses
                                    (user_id, username, fullname, position, domain_code, question_num, answer_val)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                    ON CONFLICT(user_id, domain_code, question_num) DO NOTHING
                                ''', (uid, user_key, fname, pos, d_code, q_num, int(ans_val)))
                conn.commit()
            except Exception:
                pass

    conn.close()

def register_user(username, fullname, position, role, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    clean_u = username.strip().lower()
    try:
        cursor.execute(
            "INSERT INTO users (username, fullname, position, role, password_hash) VALUES (?, ?, ?, ?, ?)",
            (clean_u, fullname.strip(), position.strip(), role, hash_password(password))
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
    clean_u = username.strip().lower()
    clean_no_space = clean_u.replace(" ", "")
    p_hash = hash_password(password)
    
    cursor.execute(
        """SELECT id, username, fullname, position, role 
           FROM users 
           WHERE (username = ? OR REPLACE(LOWER(username), ' ', '') = ?)
             AND password_hash = ?""",
        (clean_u, clean_no_space, p_hash)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
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

def load_latest_respondent_data():
    """Memuat data kuesioner DF1-DF10 paling baru dari database SQLite."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM respondents ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {}
    
    respondent_id = row[0]
    cursor.execute(
        "SELECT df_code, indicator_name, calc_method, score_r1, score_r2, final_result FROM df_responses WHERE respondent_id = ? ORDER BY id ASC",
        (respondent_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {}

    results = {}
    for df_code, indicator, method, r1, r2, final in rows:
        if df_code not in results:
            results[df_code] = []
        
        if final is None:
            final_display = "Belum Diisi"
            rounded_toolkit = "-"
        else:
            if "%" in str(method) or "Percentage" in str(method):
                final_display = f"{final:.1f}%"
                rounded_toolkit = f"{int(round(final))}%"
            else:
                final_display = f"{final:.2f}"
                rounded_toolkit = str(int(round(final)))
        
        results[df_code].append({
            "indicator": indicator,
            "method": method,
            "r1": r1,
            "r2": r2,
            "final": final,
            "final_display": final_display,
            "rounded_toolkit": rounded_toolkit
        })
    return results

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
    # Selaras dengan sheet TFN_REF pada file 'perhitungan fuzzy & average.xlsx' (Skala 1-5)
    tfn_map = {
        1: (0.00, 0.00, 0.25), 
        2: (0.00, 0.25, 0.50), 
        3: (0.25, 0.50, 0.75), 
        4: (0.50, 0.75, 1.00), 
        5: (0.75, 1.00, 1.00)
    }
    return tfn_map.get(skor, (0.00, 0.00, 0.00))

def get_tfn_3(skor):
    # Selaras dengan sheet TFN_REF pada file 'perhitungan fuzzy & average.xlsx' (Skala 1-3)
    tfn_map = {
        1: (0.00, 0.00, 0.50), 
        2: (0.00, 0.50, 1.00), 
        3: (0.50, 1.00, 1.00)
    }
    return tfn_map.get(skor, (0.00, 0.00, 0.00))

def calc_fuzzy_5(r1, r2):
    t1, t2 = get_tfn_5(r1), get_tfn_5(r2)
    a_avg = round((t1[0] + t2[0]) / 2.0, 2)
    b_avg = round((t1[1] + t2[1]) / 2.0, 2)
    c_avg = round((t1[2] + t2[2]) / 2.0, 2)
    z_star = round((a_avg + b_avg + c_avg) / 3.0, 2)
    return round(1 + (z_star * 4), 2)

def calc_fuzzy_3(r1, r2):
    t1, t2 = get_tfn_3(r1), get_tfn_3(r2)
    a_avg = round((t1[0] + t2[0]) / 2.0, 2)
    b_avg = round((t1[1] + t2[1]) / 2.0, 2)
    c_avg = round((t1[2] + t2[2]) / 2.0, 2)
    z_star = round((a_avg + b_avg + c_avg) / 3.0, 2)
    return round(1 + (z_star * 2), 2)

def calc_percentage_avg(r1_pct, r2_pct):
    return round((r1_pct + r2_pct) / 2.0, 2)

def calc_risk_profile(i_r1, i_r2, l_r1, l_r2):
    """
    Kalkulasi DF3 Risk Profile dengan 4 input terpisah:
    - i_r1, i_r2 : skor Impact dari Responden 1 & 2 (skala 1-5)
    - l_r1, l_r2 : skor Likelihood dari Responden 1 & 2 (skala 1-5)
    Return dict: impact_val, likelihood_val, risk_rating
    Sesuai toolkit: Impact = round(1 + z*_impact * 4), Likelihood = round(1 + z*_likelihood * 4)
    Risk Rating = Impact * Likelihood
    """
    # --- Impact ---
    ti1, ti2 = get_tfn_5(i_r1), get_tfn_5(i_r2)
    ai_avg = round((ti1[0] + ti2[0]) / 2.0, 2)
    bi_avg = round((ti1[1] + ti2[1]) / 2.0, 2)
    ci_avg = round((ti1[2] + ti2[2]) / 2.0, 2)
    zi_star = round((ai_avg + bi_avg + ci_avg) / 3.0, 2)
    impact_raw = round(1 + (zi_star * 4), 2)
    impact_val = int(round(impact_raw))          # dibulatkan seperti di toolkit

    # --- Likelihood ---
    tl1, tl2 = get_tfn_5(l_r1), get_tfn_5(l_r2)
    al_avg = round((tl1[0] + tl2[0]) / 2.0, 2)
    bl_avg = round((tl1[1] + tl2[1]) / 2.0, 2)
    cl_avg = round((tl1[2] + tl2[2]) / 2.0, 2)
    zl_star = round((al_avg + bl_avg + cl_avg) / 3.0, 2)
    likelihood_raw = round(1 + (zl_star * 4), 2)
    likelihood_val = int(round(likelihood_raw))  # dibulatkan seperti di toolkit

    # --- Risk Rating ---
    risk_rating = impact_val * likelihood_val

    return {
        "impact_raw": impact_raw,
        "impact_val": impact_val,
        "likelihood_raw": likelihood_raw,
        "likelihood_val": likelihood_val,
        "risk_rating": risk_rating
    }

def save_individual_answers(user_id, username, fullname, position, answers_dict):
    """Menyimpan seluruh jawaban kuesioner dari seorang responden ke database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for df_code, items in answers_dict.items():
        for item in items:
            indicator = item['indicator']
            score = item.get('score')
            impact = item.get('impact')
            likelihood = item.get('likelihood')
            cursor.execute('''
                INSERT INTO individual_responses 
                (user_id, username, fullname, position, df_code, indicator_name, score_val, impact_val, likelihood_val, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, df_code, indicator_name) DO UPDATE SET
                    fullname = excluded.fullname,
                    position = excluded.position,
                    score_val = excluded.score_val,
                    impact_val = excluded.impact_val,
                    likelihood_val = excluded.likelihood_val,
                    submitted_at = CURRENT_TIMESTAMP
            ''', (user_id, username, fullname, position, df_code, indicator, score, impact, likelihood))
    conn.commit()
    conn.close()
    return True

def get_user_submission_status(user_id):
    """Mengecek apakah responden tertentu sudah menyelesaikan seluruh DF1-DF10."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT df_code), MAX(submitted_at) FROM individual_responses WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] >= 10:
        return True, row[1]
    return False, None

def get_user_saved_answers(user_id):
    """Mengambil dictionary jawaban individual responden dari database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT df_code, indicator_name, score_val, impact_val, likelihood_val FROM individual_responses WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    saved = {}
    for df_code, ind, sc, imp, lik in rows:
        if df_code not in saved:
            saved[df_code] = {}
        saved[df_code][ind] = {"score": sc, "impact": imp, "likelihood": lik}
    return saved

def get_all_submitted_respondents():
    """Mengambil daftar seluruh responden yang telah mengisi kuesioner."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, fullname, position, COUNT(DISTINCT df_code) as df_count, MAX(submitted_at) as last_submit
        FROM individual_responses
        GROUP BY user_id, username, fullname, position
        ORDER BY last_submit DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "user_id": r[0],
            "username": r[1],
            "fullname": r[2],
            "position": r[3],
            "df_count": r[4],
            "submitted_at": r[5]
        }
        for r in rows
    ]

# ========================================================
# WAWANCARA 2: CHECKLIST CAPABILITY LEVEL (BINER YA / TIDAK)
# ========================================================

def load_checklist_questions():
    """Memuat daftar 124 butir checklist dari file parsed_checklist.json."""
    import json
    json_path = os.path.join(os.path.dirname(__file__), "parsed_checklist.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_individual_checklist(user_id, username, fullname, position, checklist_dict):
    """
    Menyimpan seluruh jawaban checklist Wawancara 2 (Ya=1, Tidak=0) dari seorang responden ke database.
    checklist_dict: {domain_code: {question_num: int(0 or 1)}}
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for domain_code, q_map in checklist_dict.items():
        for q_num, ans_val in q_map.items():
            cursor.execute('''
                INSERT INTO individual_checklist_responses 
                (user_id, username, fullname, position, domain_code, question_num, answer_val, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, domain_code, question_num) DO UPDATE SET
                    fullname = excluded.fullname,
                    position = excluded.position,
                    answer_val = excluded.answer_val,
                    submitted_at = CURRENT_TIMESTAMP
            ''', (user_id, username, fullname, position, domain_code, int(q_num), int(ans_val)))
    conn.commit()
    conn.close()
    return True

def get_user_checklist_answers(user_id):
    """Mengambil dictionary jawaban checklist Wawancara 2 dari seorang responden."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT domain_code, question_num, answer_val FROM individual_checklist_responses WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    res = {}
    for d_code, q_num, ans in rows:
        if d_code not in res:
            res[d_code] = {}
        res[d_code][q_num] = ans
    return res

def get_user_checklist_status(user_id):
    """Mengecek apakah responden telah menyelesaikan checklist Wawancara 2 (124 butir)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), MAX(submitted_at) FROM individual_checklist_responses WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    count = row[0] if row else 0
    max_time = row[1] if row else None
    return (count >= 124), count, max_time

def get_all_checklist_submitted_respondents():
    """Mengambil daftar seluruh responden yang telah mengisi checklist Wawancara 2."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, fullname, position, COUNT(*) as q_count, MAX(submitted_at) as last_submit
        FROM individual_checklist_responses
        GROUP BY user_id, username, fullname, position
        ORDER BY last_submit DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "user_id": r[0],
            "username": r[1],
            "fullname": r[2],
            "position": r[3],
            "q_count": r[4],
            "submitted_at": r[5]
        }
        for r in rows
    ]

def calculate_domain_checklist_score(domain_code, user_answers_dict, all_questions_dict=None):
    """
    Menghitung skor capability level suatu domain berdasarkan jawaban checklist Wawancara 2.
    Formula COBIT 2019 (Tanpa Fuzzy):
    Pencapaian (%) = (Total Jawaban 'Ya' / Total Pertanyaan) * 100%
    """
    if all_questions_dict is None:
        all_questions_dict = load_checklist_questions()
    questions = all_questions_dict.get(domain_code, [])
    total_q = len(questions)
    if total_q == 0:
        return {
            "domain_code": domain_code,
            "total": 0,
            "ya": 0,
            "tidak": 0,
            "pct": 0.0,
            "rating": "N - Not Achieved (0-14%)",
            "as_is_lvl": 0
        }
    
    domain_answers = user_answers_dict.get(domain_code, {})
    ya_count = sum(1 for q in questions if domain_answers.get(q['num']) == 1)
    tidak_count = total_q - ya_count
    pct = round((ya_count / total_q) * 100.0, 2)
    rating, as_is_lvl = get_rating_level_cobit(pct)
    return {
        "domain_code": domain_code,
        "total": total_q,
        "ya": ya_count,
        "tidak": tidak_count,
        "pct": pct,
        "rating": rating,
        "as_is_lvl": as_is_lvl
    }

def get_preset_skripsi_capability():
    """Mengembalikan data pencapaian capability level riil skripsi UNKLAB (Novanca Tulende)."""
    return {
        "APO12": {"ya": 3, "total": 36, "pct": 8.00, "rating": "N - Not Achieved (0-14%)", "as_is": 0},
        "APO13": {"ya": 8, "total": 19, "pct": 42.00, "rating": "P - Partially Achieved (15-49%)", "as_is": 1},
        "DSS05": {"ya": 37, "total": 49, "pct": 75.00, "rating": "L - Largely Achieved (50-84%)", "as_is": 2},
        "MEA03": {"ya": 6, "total": 20, "pct": 31.00, "rating": "P - Partially Achieved (15-49%)", "as_is": 1},
        "average_pct": 39.00,
        "overall_as_is": 1,
        "overall_target": 4,
        "overall_gap": 3
    }

def aggregate_two_respondents(user_id_1, user_id_2, df_definitions):
    """Menggabungkan data kuesioner dari dua responden menggunakan Fuzzy TFN & formula COBIT 2019."""
    ans1 = get_user_saved_answers(user_id_1)
    ans2 = get_user_saved_answers(user_id_2)
    
    aggregated = {}
    for df_code, df_info in df_definitions.items():
        is_risk = (df_info["type"] == "risk_profile")
        is_fuzzy = (df_info["type"] == "fuzzy")
        items = df_info["items"]
        rows = []
        
        for item in items:
            a1_item = ans1.get(df_code, {}).get(item, {})
            a2_item = ans2.get(df_code, {}).get(item, {})
            
            if is_risk:
                ir1 = a1_item.get("impact")
                lr1 = a1_item.get("likelihood")
                ir2 = a2_item.get("impact")
                lr2 = a2_item.get("likelihood")
                
                if any(v is None for v in [ir1, ir2, lr1, lr2]):
                    rows.append({
                        "indicator": item, "method": "Risk Profile (Fuzzy TFN)",
                        "r1": None, "r2": None, "final": None,
                        "final_display": "Belum Lengkap", "rounded_toolkit": "-",
                        "ir1": ir1, "ir2": ir2, "lr1": lr1, "lr2": lr2
                    })
                else:
                    res = calc_risk_profile(ir1, ir2, lr1, lr2)
                    rows.append({
                        "indicator": item, "method": "Risk Profile (Fuzzy TFN)",
                        "r1": res["impact_val"], "r2": res["likelihood_val"],
                        "final": float(res["risk_rating"]),
                        "final_display": str(res["risk_rating"]),
                        "rounded_toolkit": str(res["risk_rating"]),
                        "ir1": ir1, "ir2": ir2, "lr1": lr1, "lr2": lr2,
                        "impact_val": res["impact_val"], "likelihood_val": res["likelihood_val"],
                        "risk_rating": res["risk_rating"]
                    })
            elif is_fuzzy:
                r1 = a1_item.get("score")
                r2 = a2_item.get("score")
                if r1 is None or r2 is None:
                    rows.append({
                        "indicator": item, "method": "Fuzzy Logic TFN",
                        "r1": r1, "r2": r2, "final": None,
                        "final_display": "Belum Lengkap", "rounded_toolkit": "-"
                    })
                else:
                    final_sc = calc_fuzzy_5(r1, r2) if df_info["scale"] == 5 else calc_fuzzy_3(r1, r2)
                    rows.append({
                        "indicator": item, "method": "Fuzzy Logic TFN",
                        "r1": r1, "r2": r2, "final": final_sc,
                        "final_display": f"{final_sc:.2f}",
                        "rounded_toolkit": str(int(round(final_sc)))
                    })
            else:
                r1 = a1_item.get("score")
                r2 = a2_item.get("score")
                if r1 is None or r2 is None:
                    rows.append({
                        "indicator": item, "method": "Direct Percentage (%)",
                        "r1": r1, "r2": r2, "final": None,
                        "final_display": "Belum Lengkap", "rounded_toolkit": "-"
                    })
                else:
                    final_sc = calc_percentage_avg(r1, r2)
                    rows.append({
                        "indicator": item, "method": "Direct Percentage (%)",
                        "r1": r1, "r2": r2, "final": final_sc,
                        "final_display": f"{final_sc:.1f}%",
                        "rounded_toolkit": f"{int(round(final_sc))}%"
                    })
        aggregated[df_code] = rows
    return aggregated


def get_rating_level_cobit(pct):
    if pct < 15: return "N - Not Achieved (0-14%)", 0
    elif pct < 50: return "P - Partially Achieved (15-49%)", 1
    elif pct < 85: return "L - Largely Achieved (50-84%)", 2
    else: return "F - Fully Achieved (85-100%)", 3

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