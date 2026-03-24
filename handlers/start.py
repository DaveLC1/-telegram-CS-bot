from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from keyboards.courses import get_courses_keyboard


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚𝙇𝙞𝙨𝙩 𝙤𝙛 𝘾𝙤𝙪𝙧𝙨𝙚𝙨", callback_data="show_courses")],
        [InlineKeyboardButton("💬 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠", callback_data="feedback")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𓉳", reply_markup=main_menu())


async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ད𝙎𝙚𝙡𝙚𝙘𝙩 𝙖 𝙘𝙤𝙪𝙧𝙨𝙚:ད",
        reply_markup=get_courses_keyboard()
    )


async def report_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "REPORT"
    await update.message.reply_text("𝙎𝙚𝙣𝙙 𝙮𝙤𝙪𝙧 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙤𝙧 𝙦𝙪𝙚𝙧𝙧𝙮(𝚃𝚎𝚡𝚝 𝚘𝚗𝚕𝚢)𓅭:")
