from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_ID

def get_notes_keyboard(notes, user_id):
    keyboard = []
    for note in notes:
        note_id = note["id"]
        title = note["title"]
        
        if user_id == ADMIN_ID:
            keyboard.append([
                InlineKeyboardButton(f"📄 {title}", callback_data=f"note_{note_id}"),
                InlineKeyboardButton("🗑️", callback_data=f"delnote_{note_id}")
            ])
        else:
            keyboard.append([InlineKeyboardButton(f"📄 {title}", callback_data=f"note_{note_id}")])
            
    keyboard.append([InlineKeyboardButton("⬅️ Back to Courses", callback_data="my_courses")])
    return InlineKeyboardMarkup(keyboard)
