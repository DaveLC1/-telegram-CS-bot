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

from config import TOKEN


def main():
    # ✅ 1. Create DB first
    create_tables()

    # ✅ 2. Create app
    app = Application.builder().token(TOKEN).build()

    # ✅ 3. Start auto backup AFTER app exists
    app.job_queue.run_repeating(auto_backup, interval=7200, first=10)

    # ✅ 4. Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", courses_command))
    app.add_handler(CommandHandler("add_course", add_course))
    app.add_handler(CommandHandler("add_note", add_note_start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("noti", send_notification))
    app.add_handler(CommandHandler("reply", reply_to_report))
    app.add_handler(CommandHandler("backup", backup_db))

    # ✅ 5. Buttons
    app.add_handler(CallbackQueryHandler(button_click))

    # ✅ 6. Messages (state system)
    app.add_handler(MessageHandler(filters.ALL, handle_admin_messages))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()