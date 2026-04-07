import os
from dotenv import load_dotenv

load_dotenv()

# TOKEN
TOKEN = os.getenv("TOKEN", "")

# BASIC CONFIG
No_Prefix = [int(os.getenv("NP", "0"))] if os.getenv("NP") else []
NAME = os.getenv("BOT_NAME", "Cypher")
BotName = os.getenv("BOT_NAME", "Cypher")

# SERVER
server = os.getenv("SERVER_LINK", "")
serverLink = os.getenv("SERVER_LINK", "")

# OWNER IDS
OWNER_IDS = [int(os.getenv("OWNER_IDS", "0"))] if os.getenv("OWNER_IDS") else []

# WEBHOOKS
whCL = os.getenv("WH_CL", "")
whBL = os.getenv("WH_BL", "")

# STATUS
statusText = os.getenv("STATUS_TEXT", ".help")

# STATIC (same as before)
ch = "https://discord.com/channels/699587669059174461/1271825678710476911"