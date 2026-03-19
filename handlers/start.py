from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from keyboards.courses import get_courses_keyboard


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚𝙇𝙞𝙨𝙩 𝙤𝙛 𝘾𝙤𝙪𝙧𝙨𝙚𝙨", callback_data="show_courses")],
        [InlineKeyboardButton("💬 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠", callback_data="feedback")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𓉳 𓀽", reply_markup=main_menu())


async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ད𝙎𝙚𝙡𝙚𝙘𝙩 𝙖 𝙘𝙤𝙪𝙧𝙨𝙚:ད",
        reply_markup=get_courses_keyboard()
    )