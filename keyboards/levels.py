from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_levels_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 100 Level", callback_data="level_100")],
        [InlineKeyboardButton("🎓 200 Level", callback_data="level_200")],
        [InlineKeyboardButton("🎓 300 Level", callback_data="level_300")],
        [InlineKeyboardButton("🎓 400 Level", callback_data="level_400")]
    ])
