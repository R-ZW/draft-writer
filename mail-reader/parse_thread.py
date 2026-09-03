import base64
import re
import json
from html import unescape


def decode_base64url(data: str) -> str:
    """
    Decodifica o formato Base64URL utilizado pela Gmail API.
    """
    if not data:
        return ""

    # Gmail usa Base64URL, que pode vir sem padding.
    data += "=" * (-len(data) % 4)

    decoded = base64.urlsafe_b64decode(data)

    return decoded.decode("utf-8", errors="replace")


def get_header(message: dict, header_name: str) -> str | None:
    """
    Obtém um header da mensagem.
    """
    headers = message.get("payload", {}).get("headers", [])

    for header in headers:
        if header.get("name", "").lower() == header_name.lower():
            return header.get("value")

    return None


def html_to_text(html: str) -> str:
    """
    Conversão simples de HTML para texto.

    Não é um parser HTML completo, mas funciona bem
    para o HTML típico retornado pelo Gmail.
    """

    # Remove scripts e styles
    html = re.sub(
        r"<(script|style).*?>.*?</\1>", "", html, flags=re.IGNORECASE | re.DOTALL
    )

    # Quebras de linha para algumas tags
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)

    html = re.sub(
        r"</(p|div|li|tr|blockquote|h[1-6])>", "\n", html, flags=re.IGNORECASE
    )

    # Remove tags
    text = re.sub(r"<[^>]+>", "", html)

    # Decodifica entidades HTML
    text = unescape(text)

    return text


def extract_text_from_payload(payload: dict) -> str:
    """
    Extrai o melhor conteúdo textual de um payload Gmail.

    Prioridade:
    1. text/plain
    2. text/html
    """

    if not payload:
        return ""

    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})

    # Caso a própria payload contenha texto
    if mime_type == "text/plain" and body.get("data"):
        return decode_base64url(body["data"])

    if mime_type == "text/html" and body.get("data"):
        html = decode_base64url(body["data"])
        return html_to_text(html)

    # Caso seja multipart/*
    parts = payload.get("parts", [])

    plain_text = None
    html_text = None

    for part in parts:

        part_mime = part.get("mimeType", "")
        part_body = part.get("body", {})

        # text/plain diretamente
        if part_mime == "text/plain":
            if part_body.get("data"):
                plain_text = decode_base64url(part_body["data"])

        # text/html diretamente
        elif part_mime == "text/html":
            if part_body.get("data"):
                html = decode_base64url(part_body["data"])
                html_text = html_to_text(html)

        # Multipart aninhado
        elif part_mime.startswith("multipart/"):
            nested_text = extract_text_from_payload(part)

            if nested_text:
                if plain_text is None:
                    plain_text = nested_text

    # Preferimos plain text
    if plain_text:
        return plain_text

    if html_text:
        return html_text

    return ""


def clean_text(text: str) -> str:
    """
    Limpeza básica do corpo do e-mail.
    """

    if not text:
        return ""

    # Normaliza quebras de linha
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove espaços no final das linhas
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Remove excesso de linhas vazias
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove espaços duplicados, mas preserva linhas
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def remove_quoted_text(text: str) -> str:
    """
    Remove mensagens anteriores citadas.

    Exemplos:

        > mensagem anterior

    e:

        Em qua., 2 de set. de 2026 às 21:37, Fulano escreveu:
        > mensagem anterior
    """

    if not text:
        return ""

    lines = text.splitlines()

    result = []

    for line in lines:

        stripped = line.strip()

        # Início típico de mensagem citada
        if re.match(r"^Em .+ escreveu:\s*$", stripped, flags=re.IGNORECASE):
            break

        # Outro formato comum
        if re.match(r"^On .+ wrote:\s*$", stripped, flags=re.IGNORECASE):
            break

        # Linha citada
        if stripped.startswith(">"):
            break

        result.append(line)

    return "\n".join(result).strip()


def normalize_message(message: dict) -> dict:
    """
    Transforma uma mensagem Gmail em uma estrutura simplificada.
    """

    body = extract_text_from_payload(message.get("payload", {}))

    body = clean_text(body)

    # Opcional: remover mensagens anteriores citadas
    body = remove_quoted_text(body)

    to = get_header(message, "To")

    # Transforma To em lista
    to_list = []

    if to:
        to_list = [item.strip() for item in to.split(",") if item.strip()]

    return {
        "id": message.get("id"),
        "thread_id": message.get("threadId"),
        "from": get_header(message, "From"),
        "to": to_list,
        "date": get_header(message, "Date"),
        "subject": get_header(message, "Subject"),
        "body": body,
    }


def normalize_thread(thread: dict) -> dict:
    """
    Transforma uma resposta completa de:

        GET /gmail/v1/users/me/threads/{threadId}

    em um JSON simplificado.
    """

    messages = thread.get("messages", [])

    return {
        "thread_id": thread.get("id"),
        "messages": [normalize_message(message) for message in messages],
    }


with open("./out/thread.json", "r", encoding="utf-8") as file:
    thread = json.load(file)

normalized = normalize_thread(thread)

with open("./out/normalized.json", "w", encoding="utf-8") as f:
    json.dump(normalized, f, indent=2, ensure_ascii=False)

print("Thread salva em ./out/normalized.json")
