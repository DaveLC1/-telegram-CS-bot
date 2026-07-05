from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db.queries import get_courses_by_level_and_semester

def get_courses_keyboard(level, semester):
    courses = get_courses_by_level_and_semester(level, semester)
    if not courses:
        return None
        
    keyboard = []
    row = []
    
    for course in courses:
        # Build button configuration
        btn = InlineKeyboardButton(f"📖 {course}", callback_data=f"course_{course}")
        row.append(btn)
        
        # Once we have 2 side buttons, pack the row and clear it for the next one
        if len(row) == 2:
            keyboard.append(row)
            row = []
            
    # If there's an odd number of courses left over, append the remaining single button row
    if row:
        keyboard.append(row)
        
    return InlineKeyboardMarkup(keyboard)
