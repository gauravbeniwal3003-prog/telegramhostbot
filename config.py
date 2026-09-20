# ============================================
#  HARDCODED CONFIG — Sab yahan bharo
# ============================================

# ---- Telegram ----
BOT_TOKEN = "7891234567:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # @BotFather se
ADMIN_ID  = 5123456789                                       # @userinfobot se

# ---- Channels (bot ko inme ADMIN banao) ----
CHANNELS = [
    {"username": "@Gaurav_beni_0001",    "url": "https://t.me/Gaurav_beni_0001",    "id": -1001234567890},
    {"username": "@beniwalmods",         "url": "https://t.me/beniwalmods",         "id": -1001234567891},
    {"username": "@BeniwalzonYT",        "url": "https://t.me/BeniwalzonYT",        "id": -1001234567892},
    {"username": "@gauravbeniwalhacker", "url": "https://t.me/gauravbeniwalhacker", "id": -1001234567893},
]

# ---- GitHub (user bots store karne ke liye ALAG repo) ----
GITHUB_TOKEN  = "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"       # Naya token (purana delete karo!)
GITHUB_REPO   = "gauravbeniwal3003-prog/bot-storage"         # Users ke files ka repo
GITHUB_BRANCH = "main"

# ---- Storage ----
DB_PATH       = "hosting.db"
TEMP_DIR      = "bots"
MAX_FILE_SIZE = 1 * 1024 * 1024   # 1 MB

# ---- Render URL (deploy ke baad yahan paste karo) ----
PUBLIC_BASE_URL = "https://telegramhostbot.onrender.com"

# ---- Telegram Webhook secret (random string, koi bhi daal do) ----
WEBHOOK_SECRET = "abc123xyz_secret_2024"
