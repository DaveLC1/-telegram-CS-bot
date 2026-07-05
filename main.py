from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading
import os
from db.database import create_tables
from config import TOKEN

# --- IMPORT SECURE ALIGNED PIPELINE MODULES ---
from handlers.start import start, courses_command
from handlers.buttons import button_click, handle_note_retrieval
from handlers.admin import (
    semester_command, 
    stats_command,
    level_reset_command, 
    broadcast_command, cancel,
    handle_semester_callback,
    handle_broadcast_callback, 
    handle_global_messages,
    backup_db,
    restore_db_from_chat,
    admin_panel_command,
    handle_admin_dynamic_callbacks
)

from flask import Flask
web_app = Flask(__name__)

@web_app.route("/")
def home(): 
    return "Deployment Active"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port, use_reloader=False)

# UNTOUCHED: Kept exactly as structured to safeguard database snapshot restoration mechanisms
async def startup(app: Application):
    print(" Restoring DB from pinned backup (if exists)...")
    await restore_db_from_chat(app)
    create_tables()
    print("✅ Database ready")

def main():
    app = Application.builder().token(TOKEN).post_init(startup).build()
    
    # --- COMMAND RECEPTORS ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("courses", courses_command))
    app.add_handler(CommandHandler("semester", semester_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("backup", backup_db))
    app.add_handler(CommandHandler("level_reset", level_reset_command))
    app.add_handler(CommandHandler("notify", broadcast_command))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("admin", admin_panel_command))
    
    # Catch dynamic text commands like /get_5 (for search results)
    app.add_handler(MessageHandler(filters.Regex(r"^/get_\d+$"), handle_note_retrieval))

    # --- CALLBACK DELEGATIONS ---
    app.add_handler(CallbackQueryHandler(handle_semester_callback, pattern="^semester_"))
    app.add_handler(CallbackQueryHandler(handle_broadcast_callback, pattern="^(broadcast_|notify_)"))
    app.add_handler(CallbackQueryHandler(handle_note_retrieval, pattern="^note_"))
    app.add_handler(CallbackQueryHandler(handle_admin_dynamic_callbacks, pattern="^(adm_|admnav_|admsem_|admdestn_)"))
    app.add_handler(CallbackQueryHandler(button_click))

    # --- MONOLITHIC MESSAGE MULTIPLEXER ---
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_global_messages))

    # RUN KEEPALIVE ENGINE
    threading.Thread(target=run_web, daemon=True).start()

    print("🚀 Bot Engine Online.")
    app.run_polling()

if __name__ == "__main__":
    main()
