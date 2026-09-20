import json, secrets, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)
from config import BOT_TOKEN, ADMIN_ID, CHANNELS, MAX_FILE_SIZE, PUBLIC_BASE_URL
from database import init_db, add_bot, set_running, get_bot, get_user_bots
from github_handler import upload_files

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

WAIT_BOT_NAME, WAIT_FILES, WAIT_CONFIRM = range(3)


# ---------- helpers ----------
async def is_member(context, user_id):
    for ch in CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch["id"], user_id)
            if m.status in ("left", "kicked"):
                return False, ch
        except Exception:
            continue
    return True, None


async def require_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ok, ch = await is_member(context, user.id)
    if ok:
        return True
    kb = [[InlineKeyboardButton(f"Join {c['username']}", url=c["url"])] for c in CHANNELS]
    kb.append([InlineKeyboardButton("✅ I Joined", callback_data="check_join")])
    await update.effective_message.reply_text(
        "🚫 <b>Access Denied</b>\n\nJoin all channels to use this bot:\n"
        + "\n".join(f"• {c['username']}" for c in CHANNELS),
        reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML"
    )
    return False


# ---------- commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_join(update, context):
        return
    await update.message.reply_text(
        "👋 <b>Welcome to Free Telegram Bot Hosting</b>\n\n"
        "Upload any number of Python files (max <b>1 MB</b> each).\n\n"
        "<b>Commands</b>\n"
        "• /upload — submit a new bot\n"
        "• /mybots — list your bots\n"
        "• /status &lt;bot_id&gt; — check status\n"
        "• /cancel — cancel",
        parse_mode="HTML"
    )


async def mybots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_join(update, context):
        return
    bots = get_user_bots(update.effective_user.id)
    if not bots:
        await update.message.reply_text("📭 No bots yet. Use /upload")
        return
    lines = ["<b>🤖 Your Bots</b>"]
    for b in bots:
        lines.append(
            f"\n<b>#{b['id']} — {b['bot_name']}</b>\n"
            f"Status: <code>{b['status']}</code>"
            + (f"\nPing: <code>{b['ping_url']}</code>" if b['ping_url'] else "")
        )
    await update.message.reply_text("\n".join(lines), parse_mode="HTML",
                                    disable_web_page_preview=True)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_join(update, context):
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /status <bot_id>")
        return
    bot = get_bot(int(context.args[0]))
    if not bot or bot["user_id"] != update.effective_user.id:
        await update.message.reply_text("❌ Not found.")
        return
    text = f"<b>Bot #{bot['id']} — {bot['bot_name']}</b>\nStatus: <code>{bot['status']}</code>"
    if bot["ping_url"]:
        text += (
            f"\n\n<b>Ping URL:</b>\n<code>{bot['ping_url']}</code>\n"
            f"<b>Username:</b> <code>{bot['ping_user']}</code>\n"
            f"<b>Password:</b> <code>{bot['ping_pass']}</code>"
        )
    await update.message.reply_text(text, parse_mode="HTML",
                                    disable_web_page_preview=True)


# ---------- upload flow ----------
async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_join(update, context):
        return ConversationHandler.END
    context.user_data.clear()
    context.user_data["files"] = []
    await update.message.reply_text("📝 <b>Step 1/3</b>\nSend a short <b>name</b> for your bot:",
                                    parse_mode="HTML")
    return WAIT_BOT_NAME


async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) > 40:
        await update.message.reply_text("Name too long (max 40):")
        return WAIT_BOT_NAME
    context.user_data["bot_name"] = name
    await update.message.reply_text(
        "📤 <b>Step 2/3</b>\nSend your <b>.py files</b> (max 1 MB each).\n"
        "Send /done when finished.", parse_mode="HTML"
    )
    return WAIT_FILES


async def got_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.endswith(".py"):
        await update.message.reply_text("⚠️ Only .py files allowed.")
        return WAIT_FILES
    if doc.file_size and doc.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("⚠️ File > 1 MB.")
        return WAIT_FILES
    f = await doc.get_file()
    content = bytes(await f.download_as_bytearray())
    context.user_data["files"].append({"name": doc.file_name, "content": content})
    await update.message.reply_text(
        f"✅ Added <code>{doc.file_name}</code> ({len(context.user_data['files'])} total).\nSend more or /done.",
        parse_mode="HTML"
    )
    return WAIT_FILES


async def done_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = context.user_data.get("files", [])
    if not files:
        await update.message.reply_text("❌ No files. /upload to restart.")
        return ConversationHandler.END
    await update.message.reply_text(
        f"📦 <b>Step 3/3</b>\nBot: <b>{context.user_data['bot_name']}</b>\n"
        f"Files: {len(files)}\n\nConfirm?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Submit", callback_data="confirm_upload"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_upload")
        ]])
    )
    return WAIT_CONFIRM


async def confirm_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    if q.data == "cancel_upload":
        await q.edit_message_text("❌ Cancelled.")
        return ConversationHandler.END

    name  = context.user_data["bot_name"]
    files = context.user_data["files"]
    folder = f"bots/{user.id}_{secrets.token_hex(4)}_{name.replace(' ','_')}"

    await q.edit_message_text("⏳ Uploading to GitHub…")
    try:
        links = upload_files(folder, files)
    except Exception as e:
        log.exception("GitHub upload failed")
        await q.edit_message_text(f"❌ GitHub upload failed:\n<code>{e}</code>", parse_mode="HTML")
        return ConversationHandler.END

    bot_id = add_bot(
        user_id=user.id,
        username=user.username or user.full_name,
        bot_name=name,
        folder=folder,
        files_json=json.dumps([f["name"] for f in files]),
        github_links=json.dumps(links)
    )

    file_lines = "\n".join(f"• <a href='{l['url']}'>{l['name']}</a>" for l in links)
    admin_msg = (
        f"🆕 <b>NEW BOT SUBMISSION</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Bot ID:</b> <code>{bot_id}</code>\n"
        f"<b>Name:</b> {name}\n"
        f"<b>User:</b> @{user.username or '—'} (<code>{user.id}</code>)\n"
        f"<b>Folder:</b> <code>{folder}</code>\n"
        f"<b>Files:</b> {len(files)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>GitHub Links:</b>\n{file_lines}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    await context.bot.send_message(
        ADMIN_ID, admin_msg, parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(f"✅ Mark #{bot_id} RUNNING", callback_data=f"run_{bot_id}")
        ]])
    )

    await q.edit_message_text(
        f"✅ <b>Submitted!</b>\nBot ID: <code>{bot_id}</code>\n\n"
        f"Admin will host it soon. Use /status {bot_id}",
        parse_mode="HTML"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


# ---------- admin callback ----------
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID:
        await q.answer("Admin only.", show_alert=True)
        return
    if q.data.startswith("run_"):
        bot_id = int(q.data.split("_")[1])
        p_user = f"bot{bot_id}"
        p_pass = secrets.token_urlsafe(12)
        ping_url = f"{PUBLIC_BASE_URL}/ping/{bot_id}"
        set_running(bot_id, ping_url, p_user, p_pass)
        bot = get_bot(bot_id)

        user_msg = (
            f"🎉 <b>Your bot #{bot_id} is now RUNNING!</b>\n\n"
            f"<b>Ping URL:</b>\n<code>{ping_url}</code>\n\n"
            f"<b>Username:</b> <code>{p_user}</code>\n"
            f"<b>Password:</b> <code>{p_pass}</code>\n\n"
            "Open URL in Chrome → enter creds → JSON status milega."
        )
        try:
            await context.bot.send_message(bot["user_id"], user_msg,
                                           parse_mode="HTML",
                                           disable_web_page_preview=True)
        except Exception:
            log.warning("Could not DM user %s", bot["user_id"])

        await q.edit_message_text(
            f"✅ <b>Bot #{bot_id} RUNNING</b>\n\n"
            f"Ping URL: <code>{ping_url}</code>\n"
            f"User: <code>{p_user}</code>\n"
            f"Pass: <code>{p_pass}</code>",
            parse_mode="HTML"
        )


async def join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ok, ch = await is_member(context, q.from_user.id)
    if ok:
        await q.edit_message_text("✅ Verified! Send /start")
    else:
        await q.answer("Still not joined all channels.", show_alert=True)


# ---------- build application ----------
def build_application():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_start)],
        states={
            WAIT_BOT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
            WAIT_FILES:    [MessageHandler(filters.Document.ALL, got_file),
                            CommandHandler("done", done_files)],
            WAIT_CONFIRM:  [CallbackQueryHandler(confirm_upload, pattern="^(confirm|cancel)_upload$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True, per_chat=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mybots", mybots))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^run_"))
    app.add_handler(CallbackQueryHandler(join_check, pattern="^check_join$"))
    return app
