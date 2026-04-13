from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from keyboards.courses import get_courses_keyboard
from db.queries import add_user


# -------- DELETE OLD KEYBOARDS --------
async def delete_old_keyboards(context, chat_id):
    keyboard_msgs = context.user_data.get("keyboard_msgs", [])

    for msg_id in keyboard_msgs:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except:
            pass

    context.user_data["keyboard_msgs"] = []


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚𝙇𝙞𝙨𝙩 𝙤𝙛 𝘾𝙤𝙪𝙧𝙨𝙚𝙨", callback_data="show_courses")],
        [InlineKeyboardButton("💬 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠", callback_data="feedback")]
    ])


# -------- START --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)  # ✅ SAVE USER

    chat_id = update.effective_chat.id

    # 🧹 delete old keyboards
    await delete_old_keyboards(context, chat_id)

    msg = await update.message.reply_text(
        "𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𓉳",
        reply_markup=main_menu()
    )

    # 💾 save this keyboard message
    context.user_data.setdefault("keyboard_msgs", []).append(msg.message_id)


# -------- COURSES --------
async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)  # ✅ SAVE USER

    chat_id = update.effective_chat.id

    # 🧹 delete old keyboards
    await delete_old_keyboards(context, chat_id)

    msg = await update.message.reply_text(
        "ད𝙎𝙚𝙡𝙚𝙘𝙩 𝙖 𝙘𝙤𝙪𝙧𝙨𝙚:ད",
        reply_markup=get_courses_keyboard()
    )

    # 💾 save this keyboard message
    context.user_data.setdefault("keyboard_msgs", []).append(msg.message_id)


# -------- REPORT --------
async def report_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "REPORT"

    chat_id = update.effective_chat.id

    # 🧹 delete old keyboards
    await delete_old_keyboards(context, chat_id)

    await update.message.reply_text(
        "𝙎𝙚𝙣𝙙 𝙮𝙤𝙪𝙧 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙤𝙧 𝙦𝙪𝙚𝙧𝙧𝙮(𝚃𝚎𝚡𝚝 𝚘𝚗𝚕𝚢)𓅭:"
    )
