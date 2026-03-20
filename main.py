import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from db.queries import create_tables
from handlers.start import start, courses_command
from handlers.buttons import button_click
from handlers.admin import (
    add_course, add_note_start, handle_admin_messages,
    cancel, send_notification, reply_to_report,
    backup_db, auto_backup
)
from config import TOKEN, ADMIN_ID # Assuming ADMIN_ID is in your config

from flask import Flask
import threading
import os

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

async def sync_db(bot):
    try:
        chat = await bot.get_chat(ADMIN_ID)
        pinned = chat.pinned_message
        if pinned and pinned.document and pinned.document.file_name == 'database.db':
            file = await bot.get_file(pinned.document.file_id)
            await file.download_to_drive("database.db")
            await bot.delete_message(ADMIN_ID, pinned.message_id)
            print("DB restored and old backup deleted.")
    except Exception as e:
        print(f"Sync skip: {e}")

def main():
    # 1. Ensure tables exist
    create_tables()

    app = Application.builder().token(TOKEN).build()

    # 2. Run the Restore/Delete logic
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sync_db(app.bot))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", courses_command))
    app.add_handler(CommandHandler("add_course", add_course))
    app.add_handler(CommandHandler("add_note", add_note_start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("noti", send_notification))
    app.add_handler(CommandHandler("reply", reply_to_report))
    app.add_handler(CommandHandler("backup", backup_db))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL, handle_admin_messages))

    if app.job_queue:
        app.job_queue.run_repeating(auto_backup, interval=7200, first=10)

    threading.Thread(target=run_web, daemon=True).start()

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
