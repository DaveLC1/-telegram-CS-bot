from telegram import Update
import os
from telegram.ext import ContextTypes

from config import ADMIN_ID
from keyboards.courses import get_courses_keyboard

from db.queries import (
    add_note, add_category, update_note,
    get_all_users, add_report, get_report, close_report, delete_category
    )


# -------- ADD COURSE --------
async def add_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("𝙎𝙚𝙣𝙙 𝘾𝙖𝙩𝙚𝙜𝙤𝙧𝙮 𝙉𝙖𝙢𝙚:")
    context.user_data["state"] = "ADDING_CATEGORY"


# -------- ADD NOTE --------
async def add_note_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "Select category:",
        reply_markup=get_courses_keyboard()
    )
    context.user_data["state"] = "WAITING_COURSE"


# -------- CANCEL --------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "𝘾𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙.",
        reply_markup=get_courses_keyboard()
    )


# -------- BROADCAST --------
async def send_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("Send broadcast:")
    context.user_data["state"] = "BROADCAST"


#__________Report/ Feedback__________

async def report_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "REPORT"
    await update.message.reply_text("𝙎𝙚𝙣𝙙 𝙮𝙤𝙪𝙧 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙤𝙧 𝙞𝙨𝙨𝙪𝙚:")
    
# -------- REPLY TO FEEDBACK --------
async def reply_to_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        report_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Usage: /reply <id> message")
        return

    report = get_report(report_id)
    if not report:
        await update.message.reply_text("Not found")
        return

    user_id, _ = report
    await context.bot.send_message(user_id, f"Response𓅄:\n{reply_text}")
    close_report(report_id)
    await update.message.reply_text("𝙍𝙚𝙥𝙡𝙞𝙚𝙙")


# -------- MANUAL BACKUP --------
async def backup_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not os.path.exists("bot.db"):
        await update.message.reply_text("DB not found")
        return

    # Delete previous backup if exists
    last_msg_id = context.bot_data.get("last_backup_msg_id")
    if last_msg_id:
        try:
            await context.bot.delete_message(chat_id=ADMIN_ID, message_id=last_msg_id)
        except:
            pass

    # Send new backup
    with open("bot.db", "rb") as f:
        msg = await update.message.reply_document(document=f, filename="bot_backup.db")

    # Pin it for future restore
    try:
        await msg.pin()
    except:
        pass

    context.bot_data["last_backup_msg_id"] = msg.message_id


# -------- AUTO BACKUP --------
async def auto_backup(context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("bot.db"):
        return

    last_msg_id = context.bot_data.get("last_backup_msg_id")
    if last_msg_id:
        try:
            await context.bot.delete_message(chat_id=ADMIN_ID, message_id=last_msg_id)
        except:
            pass

    with open("bot.db", "rb") as f:
        msg = await context.bot.send_document(chat_id=ADMIN_ID, document=f, filename="bot_backup.db")

    # Pin automatically
    try:
        await msg.pin()
    except:
        pass

    context.bot_data["last_backup_msg_id"] = msg.message_id


# -------- RESTORE FROM PINNED BACKUP --------
async def restore_db_from_chat(app):
    DB_PATH = "bot.db"
    EXPECTED_FILENAME = "bot_backup.db"

    # Treat empty or tiny DB as non-existent
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 1024:
        print("Local bot.db exists → skipping restore")
        return

    try:
        chat = await app.bot.get_chat(ADMIN_ID)
        pinned = chat.pinned_message

        if not pinned or not pinned.document:
            print("No pinned backup found")
            return

        if pinned.document.file_name != EXPECTED_FILENAME:
            print(f"Filename mismatch: expected {EXPECTED_FILENAME}, got {pinned.document.file_name}")
            return

        print(f"Restoring DB from pinned: {pinned.document.file_name}")
        file = await pinned.document.get_file()
        await file.download_to_drive(DB_PATH)

        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1 FROM sqlite_master")
        conn.close()

        print("✅ Database restored and validated")

        # Track pinned message ID for future auto-backups
        app.bot_data["last_backup_msg_id"] = pinned.message_id

    except Exception as e:
        print(f"Restore failed: {type(e).__name__}: {e}")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

# ---------------- DELETE CATEGORY ----------------
async def delete_category_command(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /delete_course <category_name>")
        return

    category_name = " ".join(context.args)
    delete_category(category_name)
    await update.message.reply_text(f"Category '{category_name}' deleted along with its notes.")
    
# -------- MESSAGE HANDLER --------
async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    # Feedback from anyone
    if state == "REPORT":
        report_id = add_report(user_id, update.message.text)
        await context.bot.send_message(
            ADMIN_ID,
            f"𝙍𝙚𝙥𝙤𝙧𝙩 #{report_id}\n{update.message.text}\n/reply {report_id}"
        )
        await update.message.reply_text("𝙎𝙚𝙣𝙩 𓅯")
        context.user_data.clear()
        return

    if user_id != ADMIN_ID:
        return

    # Add category
    if state == "ADDING_CATEGORY":
        add_category(update.message.text.strip())
        await update.message.reply_text("Added", reply_markup=get_courses_keyboard())
        context.user_data.clear()

    # Add note
    elif state == "WAITING_TITLE":
        context.user_data["title"] = update.message.text
        await update.message.reply_text("Send file")
        context.user_data["state"] = "WAITING_FILE"

    elif state == "WAITING_FILE":
        doc = update.message.document
        if not doc:
            await update.message.reply_text("Send file ❌")
            return
        add_note(context.user_data["category"], context.user_data["title"], doc.file_id)
        await update.message.reply_text("Saved")
        context.user_data.clear()

    # Edit note
    elif state == "EDIT_TITLE":
        context.user_data["new_title"] = update.message.text
        await update.message.reply_text("Send new file")
        context.user_data["state"] = "EDIT_FILE"

    elif state == "EDIT_FILE":
        doc = update.message.document
        if not doc:
            await update.message.reply_text("Send file ❌")
            return
        update_note(context.user_data["edit_note_id"], context.user_data["new_title"], doc.file_id)
        await update.message.reply_text("Updated")
        context.user_data.clear()

    # Broadcast
    elif state == "BROADCAST":
        users = get_all_users()
        for u in users:
            try:
                if update.message.text:
                    await context.bot.send_message(u, update.message.text)
                elif update.message.photo:
                    await context.bot.send_photo(u, update.message.photo[-1].file_id)
                elif update.message.document:
                    await context.bot.send_document(u, update.message.document.file_id)
            except:
                pass
        await update.message.reply_text("𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩 𝙨𝙚𝙣𝙩 𓅃")
        context.user_data.clear()
