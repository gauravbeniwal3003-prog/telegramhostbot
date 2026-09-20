import os, asyncio, logging
from flask import Flask, request, jsonify, Response
from telegram import Update
from datetime import datetime

from config import BOT_TOKEN, PUBLIC_BASE_URL, WEBHOOK_SECRET
from main import build_application
from database import get_bot, init_db
from github_handler import test_connection

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)

# ---------- Telegram bot init ----------
ptb_app = build_application()
loop = asyncio.new_event_loop()

# Build absolute webhook URL (safety: no double slashes, no double secret)
WEBHOOK_PATH = f"/telegram/{WEBHOOK_SECRET}"
WEBHOOK_URL  = f"{PUBLIC_BASE_URL.rstrip('/')}{WEBHOOK_PATH}"


async def _init_bot():
    await ptb_app.initialize()

    # Delete any old webhook first (clears cached bad URLs)
    try:
        await ptb_app.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        log.warning("delete_webhook failed: %s", e)

    log.info("Setting webhook to: %s", WEBHOOK_URL)
    await ptb_app.bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
    await ptb_app.start()
    log.info("✅ Telegram webhook set → %s", WEBHOOK_URL)


def init_telegram():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_init_bot())


# ---------- Telegram webhook endpoint ----------
@app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, ptb_app.bot)
    asyncio.run_coroutine_threadsafe(ptb_app.process_update(update), loop)
    return "ok", 200


# ---------- Ping endpoints ----------
def _check_auth(bot):
    auth = request.authorization
    if not auth or auth.username != bot["ping_user"] or auth.password != bot["ping_pass"]:
        return Response(
            '{"status":"unauthorized"}', 401,
            {"WWW-Authenticate": 'Basic realm="Ping"', "Content-Type": "application/json"}
        )
    return None


@app.route("/ping/<int:bot_id>", methods=["GET"])
def ping(bot_id):
    bot = get_bot(bot_id)
    if not bot:
        return jsonify({"status": "not_found", "bot_id": bot_id}), 404
    u = _check_auth(bot)
    if u:
        return u
    return jsonify({
        "bot_id":     bot["id"],
        "bot_name":   bot["bot_name"],
        "owner":      bot["username"],
        "status":     bot["status"],
        "healthy":    bot["status"] == "running",
        "github":     bot["github_links"],
        "checked_at": datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route("/", methods=["GET"])
def index():
    return jsonify({"service": "Telegram Bot Hosting", "ok": True,
                    "bot": "running" if ptb_app.running else "starting"})


@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200


# ---------- Startup ----------
init_db()
try:
    init_telegram()
    ok, msg = test_connection()
    if ok:
        log.info("✅ GitHub connected: %s", msg)
    else:
        log.error("❌ GitHub connection FAILED: %s", msg)
    log.info("✅ All systems ready")
except Exception as e:
    log.exception("Startup failed: %s", e)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
