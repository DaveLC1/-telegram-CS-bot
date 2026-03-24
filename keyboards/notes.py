from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_ID


def get_notes_keyboard(notes, user_id):
    keyboard = []

    for note_id, title in notes:
        row = [
            InlineKeyboardButton(title, callback_data=f"note_{note_id}")
        ]

        if user_id == ADMIN_ID:
            row.append(InlineKeyboardButton("🗑", callback_data=f"delete_{note_id}"))
            row.append(InlineKeyboardButton("✏️", callback_data=f"edit_{note_id}"))

        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅︎ Back", callback_data="back_courses")
    ])

    return InlineKeyboardMarkup(keyboard)
