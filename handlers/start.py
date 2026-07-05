from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.queries import add_user, get_user_level
from keyboards.levels import get_levels_keyboard

# Telegram Confetti/Celebration Effect
MESSAGE_EFFECT_ID = "5104841245755180586"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 My Courses", callback_data="my_courses")],
        [InlineKeyboardButton("🔍 Search Notes", callback_data="search_notes")],
        [InlineKeyboardButton("💬 Feedback", callback_data="feedback")]
    ])

async def clear_old_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper function to delete the previously tracked menu message."""
    old_menu_id = context.user_data.get("last_menu_id")
    if old_menu_id:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=old_menu_id
            )
        except Exception:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)

    # Delete any lingering keyboard menu before printing the new start window
    await clear_old_menu(update, context)

    level = get_user_level(user.id)

    if level is None:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👋 𝚆𝚎𝚕𝚌𝚘𝚖𝚎! 𝚜𝚎𝚕𝚎𝚌𝚝 𝚢𝚘𝚞𝚛 𝙰𝚌𝚊𝚍𝚎𝚖𝚒𝚌 𝙻𝚎𝚟𝚎𝚕 𝚋𝚎𝚕𝚘𝚠 𝚝𝚘 𝚌𝚘𝚗𝚝𝚒𝚗𝚞𝚎:",
            reply_markup=get_levels_keyboard(),
            message_effect_id=MESSAGE_EFFECT_ID
        )
        context.user_data["last_menu_id"] = msg.message_id
        return

    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗯𝗮𝗰𝗸! \n🎓 𝙲𝚞𝚛𝚛𝚎𝚗𝚝 𝙻𝚎𝚟𝚎𝚕: {level} Level",
        reply_markup=main_menu(),
        message_effect_id=MESSAGE_EFFECT_ID
    )
    context.user_data["last_menu_id"] = msg.message_id

async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    level = get_user_level(update.effective_user.id)
    if level is None:
        await update.message.reply_text("Please set your level using /start first.")
        return

    await clear_old_menu(update, context)

    msg = await update.message.reply_text(
        "📚༼𝙲𝚘𝚞𝚛𝚜𝚎 𝙼𝚎𝚗𝚞 𝚘𝚙𝚝𝚒𝚘𝚗𝚜༽",
        reply_markup=main_menu()
    )

    context.user_data["last_menu_id"] = msg.message_id
