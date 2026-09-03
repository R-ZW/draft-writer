import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os

# ============================================================
# SUAS CREDENCIAIS
# ============================================================
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")


# ============================================================
# PEGA O THREAD ID INFORMADO PELA LINHA DE COMANDO
# ============================================================

if len(sys.argv) != 2:
    print("Uso:")
    print("  python gmail_thread.py THREAD_ID")
    sys.exit(1)

thread_id = sys.argv[1]


# ============================================================
# CRIA O OBJETO DE CREDENCIAIS DO GOOGLE
# ============================================================

credentials = Credentials(
    token=ACCESS_TOKEN,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)


# ============================================================
# INICIALIZA O SERVIÇO DA GMAIL API (RENOVA O TOKEN SE NECESSÁRIO)
# ============================================================

service = build("gmail", "v1", credentials=credentials)


# ============================================================
# FAZ A REQUISIÇÃO E SALVA O JSON
# ============================================================

try:
    thread = service.users().threads().get(userId="me", id=thread_id).execute()

    os.makedirs("./out", exist_ok=True)

    with open("./out/thread.json", "w", encoding="utf-8") as f:
        json.dump(thread, f, indent=2, ensure_ascii=False)

    print("Thread salva em ./out/thread.json")

except HttpError as error:
    print(f"Erro na API do Gmail: {error}")
    sys.exit(1)
