import os

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "YOUR_TELEGRAM_USER_ID"))

# Mandatory channels (bot must be admin in these)
CHANNELS = [
    {"username": "@Gaurav_beni_0001", "url": "https://t.me/Gaurav_beni_0001", "id": -1000000000001},
    {"username": "@beniwalmods",      "url": "https://t.me/beniwalmods",      "id": -1000000000002},
    {"username": "@BeniwalzonYT",     "url": "https://t.me/BeniwalzonYT",     "id": -1000000000003},
    {"username": "@gauravbeniwalhacker","url": "https://t.me/gauravbeniwalhacker","id": -1000000000004},
]

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_REPO  = os.getenv("GITHUB_REPO", "yourusername/bot-hosting-storage")
GITHUB_BRANCH = "main"

# Storage
DB_PATH   = "hosting.db"
TEMP_DIR  = "bots"
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

# Public URL of this Flask server (used to build ping links)
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://your-server.example.com")
