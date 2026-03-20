import asyncio
import threading
import os
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from db.queries import create_tables
import handlers.buttons as btn_handlers
from handlers.start import start, courses_command
from handlers.admin import (
    add_course, add_note_start, handle_admin_messages,
    cancel, send_notification, reply_to_report,
    backup_db, auto_backup
)
from config import TOKEN, ADMIN_ID

# -------- KEEP ALIVE --------
web_app = Flask(__name__)
@web_app.route("/")
def home(): return "Bot is live and syncing."

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# -------- THE RESTORE & DELETE FEATURE --------
async def post_init(application: Application):
    print("Searching for last backup to restore...")
    try:
        # 1. Search last 50 messages for the DB file
        async for message in application.bot.get_chat_history(ADMIN_ID, limit=50):
            if message.document and message.document.file_name == "database.db":
                print(f"Found backup from {message.date}. Restoring...")
                
                # 2. Download and overwrite local bot.db
                file = await application.bot.get_file(message.document.file_id)
                await file.download_to_drive("bot.db")
                
                # 3. DELETE the old message so the chat stays clean
                await application.bot.delete_message(ADMIN_ID, message.message_id)
                print("Database restored and old backup message deleted.")
                return 
        
        print("No backup found in history.")
    except Exception as e:
        print(f"Sync failed: {e}")

# -------- MAIN --------
def main():
    create_tables() # Ensure file exists for handlers to import
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", courses_command))
    app.add_handler(CommandHandler("add_course", add_course))
    app.add_handler(CommandHandler("add_note", add_note_start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("noti", send_notification))
    app.add_handler(CommandHandler("reply", reply_to_report))
    app.add_handler(CommandHandler("backup", backup_db))
    app.add_handler(CallbackQueryHandler(btn_handlers.button_click))
    app.add_handler(MessageHandler(filters.ALL, handle_admin_messages))

    if app.job_queue:
        app.job_queue.run_repeating(auto_backup, interval=7200, first=10)

    threading.Thread(target=run_web, daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
