import os

# ---- Telegram ----
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID  = int(os.environ["ADMIN_ID"])

# ---- Channels ----
CHANNELS = [
    {"username": "@Gaurav_beni_0001",    "url": "https://t.me/Gaurav_beni_0001",    "id": int(os.getenv("CH1_ID", "0"))},
    {"username": "@beniwalmods",         "url": "https://t.me/beniwalmods",         "id": int(os.getenv("CH2_ID", "0"))},
    {"username": "@BeniwalzonYT",        "url": "https://t.me/BeniwalzonYT",        "id": int(os.getenv("CH3_ID", "0"))},
    {"username": "@gauravbeniwalhacker", "url": "https://t.me/gauravbeniwalhacker", "id": int(os.getenv("CH4_ID", "0"))},
]

# ---- GitHub (USER bots store karne ke liye) ----
GITHUB_TOKEN  = os.environ["GITHUB_TOKEN"]
GITHUB_REPO   = os.environ["GITHUB_REPO"]     # ex: "gauravbeniwal3003-prog/bot-storage"
GITHUB_BRANCH = "main"

# ---- Storage ----
DB_PATH       = "hosting.db"
TEMP_DIR      = "bots"
MAX_FILE_SIZE = 1 * 1024 * 1024

# ---- Render URL (webhook service ka URL) ----
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "https://your-webhook.onrender.com")
