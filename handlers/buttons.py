from telegram import Update
from telegram.ext import ContextTypes
from db.queries import (
    set_user_level, get_user_level, get_current_semester, 
    get_notes_by_course, get_note_by_id
)
from keyboards.courses import get_courses_keyboard
from keyboards.notes import get_notes_keyboard
from handlers.start import main_menu

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    semester = get_current_semester()
    
    # Track the active query message ID as our current menu reference point
    context.user_data["last_menu_id"] = query.message.message_id

    if data.startswith("level_"):
        level = data.split("_")[1]
        set_user_level(user_id, level)
        keyboard = get_courses_keyboard(level, semester)
        
        if keyboard is None:
            await query.edit_message_text(
                f"✅ 𝚁𝚎𝚐𝚒𝚜𝚝𝚎𝚛𝚎𝚍 {level} 𝙻𝚎𝚟𝚎𝚕.\n📂 No courses active for Semester {semester}.", 
                reply_markup=main_menu()
            )
            return
        await query.edit_message_text(
            f"🎓 Level: {level} | Semester: {semester}\nSelect a course:", 
            reply_markup=keyboard
        )

    elif data == "my_courses":
        level = get_user_level(user_id)
        if not level:
            await query.edit_message_text("Use /start to configure your level setting.")
            return
        keyboard = get_courses_keyboard(level, semester)
        if keyboard is None:
            await query.edit_message_text(
                f"📂 No active course structure found for Semester {semester}.", 
                reply_markup=main_menu()
            )
            return
        await query.edit_message_text("📚 Select a course path:", reply_markup=keyboard)

    elif data.startswith("course_"):
        course_name = data.split("_")[1]
        level = get_user_level(user_id)
        notes = get_notes_by_course(level, semester, course_name)
        
        if not notes:
            await query.edit_message_text(
                f"📂 𝙽𝚘 𝚛𝚎𝚌𝚘𝚛𝚍 𝚏𝚘𝚞𝚗𝚍 𝚞𝚗𝚍𝚎𝚛 {course_name} 𝚢𝚎𝚝.", 
                reply_markup=get_notes_keyboard([], user_id)
            )
            return
        await query.edit_message_text(
            f"📚 𝙽𝚘𝚝𝚎𝚜 𝚞𝚗𝚍𝚎𝚛 {course_name}:", 
            reply_markup=get_notes_keyboard(notes, user_id)
        )

    elif data == "search_notes":
        context.user_data["state"] = "SEARCH_PROMPT"
        await query.edit_message_text("🔍 Send the keyword or target string to match courses/files:")

    elif data == "feedback":
        context.user_data["state"] = "FEEDBACK_PROMPT"
        await query.edit_message_text("💬 Send your textual report, suggestion, or query directly below:")


async def handle_note_retrieval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if query:
        await query.answer()
        note_id = query.data.split("_")[1]
        try:
            # If they tapped the file button, remove the menu interface entirely
            await query.message.delete()
            if "last_menu_id" in context.user_data:
                del context.user_data["last_menu_id"]
        except Exception:
            pass
    else:
        note_id = update.message.text.replace("/get_", "")
        # If they used a textual command route, delete any open button layout first
        old_menu_id = context.user_data.get("last_menu_id")
        if old_menu_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=old_menu_id)
                del context.user_data["last_menu_id"]
            except Exception:
                pass
        
    note = get_note_by_id(note_id)
    if not note:
        msg_obj = query.message if query else update.message
        await msg_obj.reply_text("❌ Resource item vanished or index broken.")
        return
        
    target_chat = update.effective_chat.id
    await context.bot.send_document(
        chat_id=target_chat, 
        document=note["file_id"], 
        caption=f"📄 Document Reference: {note['title']}"
    )
