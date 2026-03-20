import asyncio
import threading
import os
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from db.queries import create_tables
from handlers.start import start, courses_command
# FIXED IMPORT: Changed button_click to handle_buttons
from handlers.buttons import handle_buttons 
from handlers.admin import (
    add_course, add_note_start, handle_admin_messages,
    cancel, send_notification, reply_to_report,
    backup_db, auto_backup
)
from config import TOKEN, ADMIN_ID

# -------- KEEP ALIVE SERVER --------
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# -------- SYNC LOGIC --------
async def post_init(application: Application):
    try:
        chat = await application.bot.get_chat(ADMIN_ID)
        pinned = chat.pinned_message
        if pinned and pinned.document:
            print("Restoring database...")
            file = await application.bot.get_file(pinned.document.file_id)
            await file.download_to_drive("bot.db")
            await application.bot.delete_message(ADMIN_ID, pinned.message_id)
            print("Sync complete.")
    except Exception as e:
        print(f"Sync skipped: {e}")

# -------- MAIN --------
def main():
    create_tables()

    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # COMMANDS
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", courses_command))
    app.add_handler(CommandHandler("add_course", add_course))
    app.add_handler(CommandHandler("add_note", add_note_start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("noti", send_notification))
    app.add_handler(CommandHandler("reply", reply_to_report))
    app.add_handler(CommandHandler("backup", backup_db))

    # BUTTONS - Updated to match the imported function name
    app.add_handler(CallbackQueryHandler(handle_buttons))

    # MESSAGES
    app.add_handler(MessageHandler(filters.ALL, handle_admin_messages))

    if app.job_queue:
        app.job_queue.run_repeating(auto_backup, interval=7200, first=10)

    threading.Thread(target=run_web, daemon=True).start()

    print("Bot is starting on Render...")
    app.run_polling()

if __name__ == "__main__":
    main()
