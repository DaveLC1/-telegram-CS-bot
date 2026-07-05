from db.database import get_connection
from datetime import datetime

# --- FONTS NORMALIZATION TRANSLATOR ---
def normalize_text(text: str) -> str:
    """Converts mathematical alphanumeric styled fonts back into standard plain text."""
    if not text:
        return ""
    
    # Map for Monospace (𝚃𝚑𝚒𝚜) and Sans-Serif Bold (𝘁𝗵𝗶𝘀) + standard blocks
    font_map = str.maketrans(
        # Styled Capitals
        "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝗔𝗕𝗖𝗗Ｅ𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠加𝗡𝗢𝗣𝗤𝗦𝗧𝗨做𝗩𝗪𝗫𝗬𝗭",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ",
        # Styled Lowercase
        "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
    )
    return text.translate(font_map)

# --- SETTINGS ---
def get_current_semester():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT current_semester FROM settings WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return row["current_semester"] if row else 1

def set_current_semester(semester):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET current_semester=? WHERE id=1", (int(semester),))
    conn.commit()
    conn.close()

# --- USERS ---
def add_user(user_id, username=None, first_name=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?,?,?)
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()

def update_last_active(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_active=? WHERE user_id=?", (datetime.now(), user_id))
    conn.commit()
    conn.close()

def set_user_level(user_id, level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET level=? WHERE user_id=?", (str(level), user_id))
    conn.commit()
    conn.close()

def get_user_level(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT level FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["level"] if row else None

def clear_all_levels():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET level=NULL")
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    rows = [row["user_id"] for row in cur.fetchall()]
    conn.close()
    return rows

def get_users_by_level(level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE level=?", (str(level),))
    rows = [row["user_id"] for row in cur.fetchall()]
    conn.close()
    return rows

def get_levels_with_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT level FROM users WHERE level IS NOT NULL ORDER BY level")
    rows = [row["level"] for row in cur.fetchall()]
    conn.close()
    return rows

def get_level_counts():
    conn = get_connection()
    cur = conn.cursor()
    counts = {}
    for lvl in ["100", "200", "300", "400"]:
        cur.execute("SELECT COUNT(*) AS total FROM users WHERE level=?", (lvl,))
        counts[lvl] = cur.fetchone()["total"]
    conn.close()
    return counts

# --- COURSES & NOTES ---
def add_course(level, semester, course_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO courses (level, semester, course_name)
        VALUES (?,?,?)
    """, (str(level), int(semester), course_name.strip().upper()))
    conn.commit()
    conn.close()

def delete_course(level, semester, course_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM courses WHERE level=? AND semester=? AND course_name=?", 
                (str(level), int(semester), course_name.strip().upper()))
    conn.commit()
    conn.close()

def get_courses_by_level_and_semester(level, semester):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_name FROM courses WHERE level=? AND semester=?", (str(level), int(semester)))
    rows = [row["course_name"] for row in cur.fetchall()]
    conn.close()
    return rows

def get_course_id(level, semester, course_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM courses WHERE level=? AND semester=? AND course_name=?", 
                (str(level), int(semester), course_name.strip().upper()))
    row = cur.fetchone()
    conn.close()
    return row["id"] if row else None

def add_note(course_id, title, file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (course_id, title, file_id) VALUES (?,?,?)", (course_id, title, file_id))
    conn.commit()
    conn.close()

def get_notes_by_course(level, semester, course_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT n.id, n.title, n.file_id FROM notes n
        JOIN courses c ON n.course_id = c.id
        WHERE c.level=? AND c.semester=? AND c.course_name=?
    """, (str(level), int(semester), course_name.upper()))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_note_by_id(note_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, file_id FROM notes WHERE id=?", (note_id,))
    row = cur.fetchone()
    conn.close()
    return row

def search_notes_global(keyword):
    # Convert whatever the user searched for into flat lowercase text
    clean_keyword = normalize_text(keyword).strip().lower()
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Grab all data nodes from tables to execute clean matches in python runtime memory
    cur.execute("""
        SELECT n.id, n.title, c.course_name 
        FROM notes n
        JOIN courses c ON n.course_id = c.id
    """)
    all_rows = cur.fetchall()
    conn.close()
    
    matched_rows = []
    for row in all_rows:
        # Normalize row strings dynamically right before comparing strings
        norm_title = normalize_text(row["title"]).lower()
        norm_course = normalize_text(row["course_name"]).lower()
        
        if clean_keyword in norm_title or clean_keyword in norm_course:
            matched_rows.append(row)
            
    return matched_rows

# --- STATISTICS ---
def get_global_stats():
    conn = get_connection()
    cur = conn.cursor()
    stats = {}
    cur.execute("SELECT COUNT(*) AS total FROM users")
    stats["users"] = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM courses")
    stats["courses"] = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM notes")
    stats["notes"] = cur.fetchone()["total"]
    conn.close()
    return stats

def add_log(action):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO admin_logs(action) VALUES(?)", (action,))
    conn.commit()
    conn.close()

# --- ADMIN HELPERS ---
def get_courses_admin(level, semester):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, course_name
        FROM courses
        WHERE level=? AND semester=?
        ORDER BY course_name
    """, (str(level), int(semester)))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_notes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT n.id, n.title, c.course_name, c.level, c.semester
        FROM notes n
        JOIN courses c ON n.course_id=c.id
        ORDER BY c.level, c.semester, c.course_name
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_note(note_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
    
