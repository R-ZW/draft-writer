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
# PEGA O ASSUNTO INFORMADO PELA LINHA DE COMANDO
# ============================================================

if len(sys.argv) != 2:
    print("Uso:")
    print('  python gmail_thread.py "ASSUNTO DO EMAIL"')
    sys.exit(1)

subject = sys.argv[1]


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
# INICIALIZA O SERVIÇO DA GMAIL API
# ============================================================

service = build("gmail", "v1", credentials=credentials)


# ============================================================
# PROCURA O EMAIL PELO ASSUNTO
# ============================================================

try:
    query = f'subject:"{subject}"'

    response = service.users().messages().list(userId="me", q=query).execute()

    messages = response.get("messages", [])

    if not messages:
        print(f'Nenhum email encontrado com o assunto: "{subject}"')
        sys.exit(1)

    # Pega a primeira mensagem encontrada
    message_id = messages[0]["id"]

    # Obtém os detalhes da mensagem para pegar o threadId
    message = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="metadata")
        .execute()
    )

    thread_id = message["threadId"]

    print(f"Assunto: {subject}")
    print(f"Message ID: {message_id}")
    print(f"Thread ID: {thread_id}")

except HttpError as error:
    print(f"Erro na API do Gmail: {error}")
    sys.exit(1)
