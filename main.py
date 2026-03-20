import asyncio
import threading
import os
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from db.queries import create_tables
from handlers.start import start, courses_command
from handlers.buttons import button_click
from handlers.admin import (
    add_course,
    add_note_start,
    handle_admin_messages,
    cancel,
    send_notification,
    reply_to_report,
    backup_db,
    auto_backup
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

# -------- DATABASE SYNC (RESTORE & DELETE) --------
async def sync_db(bot):
    try:
        chat = await bot.get_chat(ADMIN_ID)
        pinned = chat.pinned_message
        # Matches the filename 'bot_backup.db' from your admin.py
        if pinned and pinned.document:
            file = await bot.get_file(pinned.document.file_id)
            await file.download_to_drive("bot.db")
            # Delete the old pinned message so the chat stays clean
            await bot.delete_message(ADMIN_ID, pinned.message_id)
            print("Database restored and old pin deleted.")
    except Exception as e:
        print(f"Sync skipped: {e}")

# -------- MAIN BOT --------
def main():
    # 1. Create tables if they don't exist
    create_tables()

    app = Application.builder().token(TOKEN).build()

    # 2. Run the Restore/Delete logic before starting
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sync_db(app.bot))

    # -------- COMMANDS --------
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", courses_command))
    app.add_handler(CommandHandler("add_course", add_course))
    app.add_handler(CommandHandler("add_note", add_note_start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("noti", send_notification))
    app.add_handler(CommandHandler("reply", reply_to_report))
    app.add_handler(CommandHandler("backup", backup_db))

    # -------- BUTTONS --------
    app.add_handler(CallbackQueryHandler(button_click))

    # -------- MESSAGES --------
    app.add_handler(MessageHandler(filters.ALL, handle_admin_messages))

    # -------- AUTO BACKUP --------
    if app.job_queue:
        app.job_queue.run_repeating(auto_backup, interval=7200, first=10)

    # -------- START WEB SERVER THREAD --------
    threading.Thread(target=run_web, daemon=True).start()

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
