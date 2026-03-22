from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading
import os

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
    auto_backup,
    restore_db_from_chat,
    delete_category_command
)
from config import TOKEN

# -------- KEEP ALIVE SERVER --------
from flask import Flask

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port, use_reloader=False)


# -------- MAIN BOT --------
def main():
    app = Application.builder().token(TOKEN).build()

    # -------- STARTUP --------
    async def startup(app):
        print(" Restoring DB from pinned backup (if exists)...")

        # ? RESTORE FIRST
        await restore_db_from_chat(app)

        # THEN create tables if needed
        create_tables()

        print("✅ Database ready")

    app.post_init = startup

    # -------- COMMANDS --------
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", courses_command))
    app.add_handler(CommandHandler("add_course", add_course))
    app.add_handler(CommandHandler("add_note", add_note_start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("noti", send_notification))
    app.add_handler(CommandHandler("reply", reply_to_report))
    app.add_handler(CommandHandler("backup", backup_db))
    app.add_handler(CommandHandler("delete_course", delete_category_command))
    app.add_handler(CommandHandler("report", report_start))

    # -------- BUTTONS --------
    app.add_handler(CallbackQueryHandler(button_click))

    # -------- MESSAGES --------
    app.add_handler(MessageHandler(filters.ALL, handle_admin_messages))

    # -------- AUTO BACKUP --------
    if app.job_queue:
        app.job_queue.run_repeating(auto_backup, interval=7200, first=10)

    # -------- START WEB SERVER --------
    threading.Thread(target=run_web, daemon=True).start()

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
