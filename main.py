import asyncio
import threading
import os
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from db.queries import create_tables
from handlers.start import start, courses_command
from handlers.buttons import button_click
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

# -------- THE FIX: PROPER ASYNC RESTORE --------
async def restore_and_run(app):
    # This block 'wakes up' the bot so we can use app.bot
    async with app:
        try:
            chat = await app.bot.get_chat(ADMIN_ID)
            pinned = chat.pinned_message
            if pinned and pinned.document:
                print("Found backup! Restoring...")
                file = await app.bot.get_file(pinned.document.file_id)
                # Ensure this filename matches what you use in your queries
                await file.download_to_drive("bot.db")
                await app.bot.delete_message(ADMIN_ID, pinned.message_id)
                print("Restore complete.")
        except Exception as e:
            print(f"Sync skipped/failed: {e}")
        
        # Now that we've restored (or skipped), start the bot
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # Keep it running
        while True:
            await asyncio.sleep(3600)

def main():
    create_tables()

    app = Application.builder().token(TOKEN).build()

    # Handlers
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

    # Web Server Thread
    threading.Thread(target=run_web, daemon=True).start()

    print("Starting restoration and polling...")
    # Use asyncio to run the restoration AND the bot logic
    asyncio.run(restore_and_run(app))

if __name__ == "__main__":
    main()
