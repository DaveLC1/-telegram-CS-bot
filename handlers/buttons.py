# -------- MANUAL BACKUP --------
async def backup_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    # Use the filename actually present in your directory
    db_path = "bot.db" 
    if not os.path.exists(db_path):
        await update.message.reply_text("DB not found")
        return

    # 1. Find and delete the previous pinned backup to keep chat clean
    try:
        chat = await context.bot.get_chat(ADMIN_ID)
        if chat.pinned_message:
            await context.bot.delete_message(ADMIN_ID, chat.pinned_message.message_id)
    except:
        pass

    # 2. Send new backup
    with open(db_path, "rb") as f:
        msg = await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=f,
            filename="database.db" # Standardized name for easy restore
        )

    # 3. Pin it so main.py can find it after a restart
    await context.bot.pin_chat_message(ADMIN_ID, msg.message_id)
    await update.message.reply_text("Backup pinned and synced.")


# -------- AUTO BACKUP (EVERY 2 HOURS) --------
async def auto_backup(context: ContextTypes.DEFAULT_TYPE):
    db_path = "bot.db"
    if not os.path.exists(db_path):
        return

    # 1. Clean up old pinned message
    try:
        chat = await context.bot.get_chat(ADMIN_ID)
        if chat.pinned_message:
            await context.bot.delete_message(ADMIN_ID, chat.pinned_message.message_id)
    except:
        pass

    # 2. Send and Pin new backup
    with open(db_path, "rb") as f:
        msg = await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=f,
            filename="database.db"
        )
    
    await context.bot.pin_chat_message(ADMIN_ID, msg.message_id)
