from telegram import Update
from telegram.ext import ContextTypes

from keyboards.courses import get_courses_keyboard
from keyboards.notes import get_notes_keyboard

from db.queries import get_notes_by_category, get_note_by_id, delete_note
from config import ADMIN_ID


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = update.effective_user.id

    # MENU
    if data == "show_courses":
        await query.edit_message_text("Choose a category:", reply_markup=get_courses_keyboard())

    elif data == "feedback":
        context.user_data["state"] = "REPORT"
        await query.message.reply_text("𝙎𝙚𝙣𝙙 𝙮𝙤𝙪𝙧 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠/𝙧𝙚𝙥𝙤𝙧𝙩:")

    # CATEGORY
    elif data.startswith("course_"):
        category = data.split("_", 1)[1]

        # ADMIN ADD NOTE FLOW
        if user_id == ADMIN_ID and context.user_data.get("state") == "WAITING_COURSE":
            context.user_data["category"] = category
            context.user_data["state"] = "WAITING_TITLE"
            await query.edit_message_text(f"** {category}** selected.\nSend title:")
            return

        context.user_data["category"] = category
        notes = get_notes_by_category(category)

        await query.edit_message_text(
            f"Notes for **{category}**:",
            reply_markup=get_notes_keyboard(notes, user_id)
        )

    # OPEN NOTE
    elif data.startswith("note_"):
        note_id = int(data.split("_")[1])
        note = get_note_by_id(note_id)

        if note:
            title, file_id = note
            await context.bot.send_document(update.effective_chat.id, file_id, caption=title)

    # DELETE
    elif data.startswith("delete_"):
        if user_id != ADMIN_ID:
            return

        note_id = int(data.split("_")[1])
        delete_note(note_id)

        category = context.user_data.get("category")
        notes = get_notes_by_category(category)

        await query.edit_message_text(
            f"𝙉𝙤𝙩𝙚𝙨 𝙛𝙤𝙧 **{category}**:",
            reply_markup=get_notes_keyboard(notes, user_id)
        )

    # EDIT
    elif data.startswith("edit_"):
        if user_id != ADMIN_ID:
            return

        context.user_data["edit_note_id"] = int(data.split("_")[1])
        context.user_data["state"] = "EDIT_TITLE"
        await query.message.reply_text("Send new title:")

    # BACK
    elif data == "back_courses":
        await query.edit_message_text("𝙎𝙚𝙡𝙚𝙘𝙩 𝙖 𝙘𝙤𝙪𝙧𝙨𝙚:", reply_markup=get_courses_keyboard())
