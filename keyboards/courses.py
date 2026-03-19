from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db.queries import get_categories


def get_courses_keyboard():
    categories = get_categories()
    buttons = []

    row = []
    for i, c in enumerate(categories, 1):
        row.append(InlineKeyboardButton(c, callback_data=f"course_{c}"))

        if i % 2 == 0:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)