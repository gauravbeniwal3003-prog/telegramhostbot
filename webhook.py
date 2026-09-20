import os
from flask import Flask, jsonify, request, Response
from database import get_bot
from datetime import datetime

app = Flask(__name__)

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
    if u: return u
    return jsonify({
        "bot_id":   bot["id"],
        "bot_name": bot["bot_name"],
        "owner":    bot["username"],
        "status":   bot["status"],
        "healthy":  bot["status"] == "running",
        "github":   bot["github_links"],
        "checked_at": datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route("/", methods=["GET"])
def index():
    return jsonify({"service": "Telegram Bot Hosting", "ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
