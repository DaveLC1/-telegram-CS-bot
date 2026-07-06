from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_levels_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 𝟭𝟬𝟬 𝙻𝚎𝚟𝚎𝚕", callback_data="level_100")],
        [InlineKeyboardButton("🎓 𝟮𝟬𝟬 𝙻𝚎𝚟𝚎𝚕", callback_data="level_200")],
        [InlineKeyboardButton("🎓 𝟯𝟬𝟬 𝙻𝚎𝚟𝚎𝚕", callback_data="level_300")],
        [InlineKeyboardButton("🎓 𝟰𝟬𝟬 𝙻𝚎𝚟𝚎𝚕", callback_data="level_400")]
    ])
