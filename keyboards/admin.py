from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ==========================================================
# PRE-EXISTING STRUCTURAL KEYBOARDS (UNTOUCHED)
# ==========================================================

def admin_level_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("100 Level", callback_data="admin_level_100")],
        [InlineKeyboardButton("200 Level", callback_data="admin_level_200")],
        [InlineKeyboardButton("300 Level", callback_data="admin_level_300")],
        [InlineKeyboardButton("400 Level", callback_data="admin_level_400")]
    ])

def semester_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 First Semester", callback_data="semester_1")],
        [InlineKeyboardButton("📙 Second Semester", callback_data="semester_2")]
    ])

def broadcast_keyboard(levels_with_users):
    keyboard = []
    for level in levels_with_users:
        keyboard.append([InlineKeyboardButton(f"{level} Level", callback_data=f"broadcast_{level}")])
    keyboard.append([InlineKeyboardButton("🌍 Everyone", callback_data="broadcast_all")])
    return InlineKeyboardMarkup(keyboard)

def confirm_keyboard(prefix):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes", callback_data=f"{prefix}_yes"),
            InlineKeyboardButton("❌ No", callback_data=f"{prefix}_no")
        ]
    ])

def back_keyboard(callback="back"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=callback)]])


# ==========================================================
# ADDED FOR DYNAMIC NOTE MANAGEMENT & UPLOADS
# ==========================================================

def admin_main_hub_keyboard():
    """Main dashboard menu panel."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Manage Content (Dynamic)", callback_data="adm_manage_hub")],
        [InlineKeyboardButton("📊 System Analytics", callback_data="adm_stats_panel")],
        [InlineKeyboardButton("📢 Global Notification", callback_data="adm_notify_panel")]
    ])

def admin_level_select_keyboard(action_prefix: str):
    """Level step for the dynamic selection flow."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 100 Level", callback_data=f"{action_prefix}_100")],
        [InlineKeyboardButton("🎓 200 Level", callback_data=f"{action_prefix}_200")],
        [InlineKeyboardButton("🎓 300 Level", callback_data=f"{action_prefix}_300")],
        [InlineKeyboardButton("🎓 400 Level", callback_data=f"{action_prefix}_400")],
        [InlineKeyboardButton("⇦ Admin Menu", callback_data="adm_main_back")]
    ])

def admin_semester_select_keyboard(action_prefix: str, level: str):
    """Semester step for the dynamic selection flow."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 First Semester", callback_data=f"{action_prefix}_{level}_1")],
        [InlineKeyboardButton("📙 Second Semester", callback_data=f"{action_prefix}_{level}_2")],
        [InlineKeyboardButton("⇦ Back to Levels", callback_data="adm_manage_hub")]
    ])

def admin_course_action_keyboard(level: str, semester: str, courses_list):
    """Displays existing courses at this location and adding options."""
    keyboard = []
    for course in courses_list:
        keyboard.append([InlineKeyboardButton(f"📖 {course['course_name']} (Edit)", callback_data=f"adm_editc_{course['id']}")])
        
    keyboard.extend([
        [InlineKeyboardButton("➕ Add Course Here", callback_data=f"adm_addc_{level}_{semester}")],
        [InlineKeyboardButton("➕ Upload Note Here", callback_data=f"adm_addn_{level}_{semester}")],
        [InlineKeyboardButton("⇦ Back to Semesters", callback_data=f"admnav_{level}")]
    ])
    return InlineKeyboardMarkup(keyboard)

def admin_notes_management_keyboard(course_id: int, notes_list):
    """Allows deleting notes, editing titles, or replacing files."""
    keyboard = []
    for note in notes_list:
        n_id = note[0] if isinstance(note, tuple) else note["id"]
        title = note[1] if isinstance(note, tuple) else note["title"]
        keyboard.append([
            InlineKeyboardButton(f"📝 Title: {title[:12]}...", callback_data=f"adm_entit_{n_id}"),
            InlineKeyboardButton("↻ File", callback_data=f"adm_enfile_{n_id}"),
            InlineKeyboardButton("🗑️", callback_data=f"adm_deln_{n_id}_{course_id}")
        ])
    keyboard.append([InlineKeyboardButton("⇦ Back to Hub", callback_data="adm_manage_hub")])
    return InlineKeyboardMarkup(keyboard)
