import os
from datetime import datetime
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from db.database import get_connection
from db.queries import (
    get_current_semester, set_current_semester, get_level_counts, clear_all_levels,
    get_levels_with_users, get_all_users, get_users_by_level, add_course, delete_course,
    get_course_id, add_note, get_global_stats, add_log, search_notes_global,
    get_courses_admin, get_notes_by_course, delete_note
)
from keyboards.admin import (
    admin_main_hub_keyboard, admin_level_select_keyboard, admin_semester_select_keyboard,
    admin_course_action_keyboard, admin_notes_management_keyboard, admin_level_keyboard,
    semester_keyboard, broadcast_keyboard, back_keyboard
)

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    context.user_data.clear()
    await update.message.reply_text("𝙰放𝚝𝚒𝚟𝚎 𝚘𝚙𝚎𝚛𝚊𝚝𝚒𝚘𝚗 𝙲𝚊𝚗𝚌𝚎𝚕𝚕𝚎𝚍.")


# 💾 ROBUST INTERACTIVE & AUTOMATED BACKUP ENGINE 

# -------- MANUAL BACKUP --------
async def backup_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else ADMIN_ID
    if str(user_id) != str(ADMIN_ID):
        return

    if not os.path.exists("bot.db"):
        msg_obj = update.message if update.message else (update.callback_query.message if update.callback_query else None)
        if msg_obj:
            await msg_obj.reply_text("DB not found")
        return

    last_msg_id = context.bot_data.get("last_backup_msg_id")
    if last_msg_id:
        try:
            await context.bot.delete_message(chat_id=ADMIN_ID, message_id=last_msg_id)
        except:
            pass

    with open("bot.db", "rb") as f:
        msg = await context.bot.send_document(chat_id=ADMIN_ID, document=f, filename="bot_backup.db")

    try:
        await context.bot.pin_chat_message(chat_id=ADMIN_ID, message_id=msg.message_id, disable_notification=True)
    except Exception as e:
        print(f"Pin failed: {e}")

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

    try:
        await context.bot.pin_chat_message(chat_id=ADMIN_ID, message_id=msg.message_id, disable_notification=True)
    except Exception as e:
        print(f"Pin failed: {e}")

    context.bot_data["last_backup_msg_id"] = msg.message_id


# -------- RESTORE FROM PINNED BACKUP --------
async def restore_db_from_chat(app):
    DB_PATH = "bot.db"
    EXPECTED_FILENAME = "bot_backup.db"

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
        app.bot_data["last_backup_msg_id"] = pinned.message_id

    except Exception as e:
        print(f"Restore failed: {type(e).__name__}: {e}")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
 
 
# 🛠️ ADMINISTRATIVE UI WORKFLOW AND MATRIX COMMANDS


async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text(
        "🛠️ **𝙰𝚌𝚊𝚍𝚎𝚖𝚒𝚌 𝚋𝚘𝚝 𝙼𝚊𝚗𝚊げて𝚖𝚎𝚗𝚝 𝙲𝚘𝚗𝚜𝚘𝚕𝚎 𝙴𝚗𝚐𝚒𝚗𝚎**\n𝚂𝚎𝚕𝚎𝚌𝚝 𝚊𝚗 𝙴𝚗𝚝𝚛𝚢:",
        reply_markup=admin_main_hub_keyboard(),
        parse_mode="Markdown"
    )

async def handle_admin_dynamic_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(update.effective_user.id):
        await query.answer("𝕦𝕟𝕒𝕦𝕥𝕙𝕠𝕣𝕚𝕫𝕖𝕕 𝔸𝕔𝕔𝕖𝕤𝕤!!🚫.", show_alert=True)
        return
        
    await query.answer()
    data = query.data

    if data == "adm_main_back":
        await query.edit_message_text("🛠️ **Academic Bot Management Console Engine**", reply_markup=admin_main_hub_keyboard(), parse_mode="Markdown")

    elif data == "adm_manage_hub":
        await query.edit_message_text("📂 Choose structural tier level to configure content:", reply_markup=admin_level_select_keyboard("admnav"))

    elif data.startswith("admnav_"):
        level = data.split("_")[1]
        await query.edit_message_text(f"🎓 Level Focus: {level} Level\nSelect target semester:", reply_markup=admin_semester_select_keyboard("admsem", level))

    elif data.startswith("admsem_"):
        _, level, semester = data.split("_")
        courses = get_courses_admin(level, semester)
        await query.edit_message_text(
            f"🎯 **Context Target**: Level {level} | Semester {semester}\nChoose an action matrix branch or active course item:",
            reply_markup=admin_course_action_keyboard(level, semester, courses),
            parse_mode="Markdown"
        )

    elif data.startswith("adm_editc_"):
        course_id = int(data.split("_")[2])
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT level, semester, course_name FROM courses WHERE id=?", (course_id,))
        c_info = cur.fetchone()
        conn.close()
        
        if c_info:
            notes = get_notes_by_course(c_info["level"], c_info["semester"], c_info["course_name"])
            await query.edit_message_text(
                f"📝 **Configuring Course**: {c_info['course_name']} ({c_info['level']}L, S{c_info['semester']})\nModify properties or assets instantly:",
                reply_markup=admin_notes_management_keyboard(course_id, notes),
                parse_mode="Markdown"
            )

    elif data.startswith("adm_addc_"):
        _, _, level, semester = data.split("_")
        context.user_data["adm_state"] = "WAITING_CNAME"
        context.user_data["t_level"] = level
        context.user_data["t_sem"] = semester
        await query.edit_message_text(f"➕ Enter target name/code string for new **{level} Level - Semester {semester}** course:")

    elif data.startswith("adm_addn_"):
        _, _, level, semester = data.split("_")
        courses = get_courses_admin(level, semester)
        if not courses:
            await query.edit_message_text("❌ Create a course code at this configuration first.")
            return
        keyboard = [[InlineKeyboardButton(f"📥 Insert to {c['course_name']}", callback_data=f"admdestn_{c['id']}")] for c in courses]
        await query.edit_message_text("Select target course module path:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("admdestn_"):
        course_id = int(data.split("_")[1])
        context.user_data["adm_state"] = "WAITING_NFILE"
        context.user_data["t_cid"] = course_id
        await query.edit_message_text("📎 Upload or forward the document asset to bind into this path structure directly:")

    elif data.startswith("adm_entit_"):
        note_id = int(data.split("_")[2])
        context.user_data["adm_state"] = "WAITING_ETITLE"
        context.user_data["t_nid"] = note_id
        await query.edit_message_text("📝 Enter the **new alternative title** text:")

    elif data.startswith("adm_enfile_"):
        note_id = int(data.split("_")[2])
        context.user_data["adm_state"] = "WAITING_EFILE"
        context.user_data["t_nid"] = note_id
        await query.edit_message_text("🔄 Upload the **new document binary asset** to swap references:")

    elif data.startswith("adm_deln_"):
        _, _, note_id, course_id = data.split("_")
        delete_note(int(note_id))
        await query.edit_message_text("✅ Resource purged successfully from structural array configurations.", reply_markup=admin_main_hub_keyboard())

    elif data == "adm_stats_panel":
        await stats_command(update, context)

    elif data == "adm_notify_panel":
        await broadcast_command(update, context)

    elif data.startswith("adm_reply_tk_"):
        target_uid = int(data.split("_")[3])
        context.user_data["adm_state"] = f"REP_TICKET_{target_uid}"
        await query.edit_message_text(f"✉️ Type response text below to dispatch to user key `{target_uid}` directly:")

# ==========================================================
# 📊 UTILITY STATISTICS AND LIVE CHAT BROADCASTS
# ==========================================================

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    counts = get_level_counts()
    gstats = get_global_stats()
    text = (
        "📊 **𝕊𝕐𝕊𝕋𝕖𝕞 𝕒𝕟𝕒𝕝𝕪𝕥𝕚𝕔𝕒𝕝 𝕕𝕒𝕥𝕒𝕤**\n\n"
        f"👥 Overall Database Users: {gstats['users']}\n"
        f"📚 Valid Course Nodes: {gstats['courses']}\n"
        f"📄 Managed Binary Notes: {gstats['notes']}\n\n"
        f"🎓 Level 100 Breakdown: {counts['100']} users\n"
        f"🎓 Level 200 Breakdown: {counts['200']} users\n"
        f"🎓 Level 300 Breakdown: {counts['300']} users\n"
        f"🎓 Level 400 Breakdown: {counts['400']} users"
    )
    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text(text, reply_markup=back_keyboard("adm_main_back"), parse_mode="Markdown")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    lvls = get_levels_with_users()
    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text("📢 Select broadcast deployment parameters:", reply_markup=broadcast_keyboard(lvls))

async def handle_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    target = query.data.replace("broadcast_", "")
    if target == "cancel":
        await query.edit_message_text("❌ Broadcast sequence dropped.")
        return
    context.user_data["state"] = "AWAITING_BROADCAST_PAYLOAD"
    context.user_data["broadcast_target"] = target
    await query.edit_message_text(f"📥 Forward/Type payload contents intended for **{target} Target Cohort**:")

async def semester_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    sem = get_current_semester()
    await update.message.reply_text(f"📅 Current system configurations: Semester {sem}\nSelect switch path below:", reply_markup=semester_keyboard())

async def handle_semester_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sem = int(query.data.split("_")[1])
    set_current_semester(sem)
    await query.edit_message_text(f"✅ System processing switched dynamically to **Semester {sem}**.", parse_mode="Markdown")

async def level_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    clear_all_levels()
    await update.message.reply_text("🧹 Database structural user tier registration contexts wiped cleanly.")

# ==========================================================
# ⚙️ SYSTEM STATE MACHINE PIPELINES (MESSAGE CONTEXT SEPARATION)
# ==========================================================

async def handle_global_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = context.user_data.get("state")
    adm_state = context.user_data.get("adm_state")

    if is_admin(user_id) and adm_state:
        if adm_state == "WAITING_CNAME" and update.message.text:
            c_name = update.message.text.strip().upper()
            level = context.user_data.get("t_level")
            semester = context.user_data.get("t_sem")
            add_course(level, semester, c_name)
            context.user_data.clear()
            await update.message.reply_text(f"✅ Route provisioned: `{c_name}` within {level}L - Sem {semester} structure matrix.")
            return

        elif adm_state == "WAITING_NFILE" and (update.message.document or update.message.photo or update.message.audio or update.message.video):
            cid = context.user_data.get("t_cid")
            file_id = None
            title = "Attachment Entry Asset"
            
            if update.message.document:
                file_id = update.message.document.file_id
                title = update.message.document.file_name or title
            elif update.message.photo:
                file_id = update.message.photo[-1].file_id
            elif update.message.audio:
                file_id = update.message.audio.file_id
                title = update.message.audio.title or title
            elif update.message.video:
                file_id = update.message.video.file_id
                
            add_note(cid, title, file_id)
            context.user_data.clear()
            await update.message.reply_text(f"🚀 File record mapped successfully: `{title}` to target course container.")
            return

        elif adm_state == "WAITING_ETITLE" and update.message.text:
            n_title = update.message.text.strip()
            nid = context.user_data.get("t_nid")
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE notes SET title=? WHERE id=?", (n_title, nid))
            conn.commit()
            conn.close()
            context.user_data.clear()
            await update.message.reply_text("✅ Target structural layout title updated dynamically.")
            return

        elif adm_state == "WAITING_EFILE" and update.message.document:
            doc = update.message.document
            nid = context.user_data.get("t_nid")
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE notes SET file_id=?, title=? WHERE id=?", (doc.file_id, doc.file_name, nid))
            conn.commit()
            conn.close()
            context.user_data.clear()
            await update.message.reply_text("✅ Target runtime document file reference swapped successfully.")
            return

        elif adm_state.startswith("REP_TICKET_"):
            target_uid = int(adm_state.split("_")[2])
            reply_text = update.message.text
            try:
                await context.bot.send_message(
                    chat_id=target_uid,
                    text=f"✉️ **Support Feedback System Response Alert**:\n\n{reply_text}",
                    parse_mode="Markdown"
                )
                await update.message.reply_text(f"🚀 Response safely processed and relayed to user: `{target_uid}`.")
            except Exception as error:
                await update.message.reply_text(f"❌ Failed to reach recipient context cluster node endpoint structure: {error}")
            context.user_data.clear()
            return

    if is_admin(user_id) and state == "AWAITING_BROADCAST_PAYLOAD":
        target = context.user_data.get("broadcast_target")
        recipients = get_all_users() if target == "all" else get_users_by_level(target)
        context.user_data.clear()
        
        sent_count = 0
        for u in recipients:
            try:
                await update.message.copy(chat_id=u)
                sent_count += 1
            except Exception:
                continue
        await update.message.reply_text(f"📊 Broadcast execution processing complete. Pushed updates to {sent_count} endpoints.")
        return

    if state == "SEARCH_PROMPT" and update.message.text:
        keyword = update.message.text.strip()
        results = search_notes_global(keyword)
        context.user_data.clear()
        
        if not results:
            await update.message.reply_text("❌ No target configurations match the text string parameter.")
            return
            
        text = "🔍 **Matched Records Portfolio Query Output Matrix**:\n\n"
        for row in results:
            text += f"📄 `{row['title']}` (Course: {row['course_name']})\n👉 Pull link execution path: /get_{row['id']}\n\n"
        await update.message.reply_text(text, parse_mode="Markdown")
        return

    # UNIVERSAL MULTI-MEDIA REPORT ENGINE
    elif state == "FEEDBACK_PROMPT":
        uname = update.effective_user.username or "Anonymous Context Block"
        
        # 1. Inspect message blocks dynamically to catch all raw media formats
        media_type = "TEXT"
        if update.message.document: media_type = "DOCUMENT"
        elif update.message.photo: media_type = "PHOTO"
        elif update.message.sticker: media_type = "STICKER"
        elif update.message.voice or update.message.audio: media_type = "AUDIO"
        elif update.message.video or update.message.video_note: media_type = "VIDEO"

        # 2. Add structural tracking indexes to the sqlite catalog database
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reports(user_id, message_type, message_id) VALUES(?, ?, ?)", 
            (user_id, media_type, update.message.message_id)
        )
        report_ticket_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # 3. Create active callback links so the operator can reply directly
        reply_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✍️ Reply Ticket #{report_ticket_id}", callback_data=f"adm_reply_tk_{user_id}")]
        ])
        
        try:
            # Send notification header details packet first
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📥 **System Support Queue Event Ticket #{report_ticket_id}**\n👤 Identity Node: @{uname} (`{user_id}`)\n📦 Content Type: {media_type}",
                parse_mode="Markdown"
            )
            
            # Copy the raw content array seamlessly down to the operator's interface matrix
            await update.message.copy(chat_id=ADMIN_ID, reply_markup=reply_kb)
            await update.message.reply_text("✅ Your support request packet has been securely logged and dispatched to developers.")
        except Exception as e:
            print(f"Error copying package data over to developer console channel: {e}")
            await update.message.reply_text("✅ Core processing complete: Logged natively inside database schemas.")
            
        context.user_data.clear()
        return
            
