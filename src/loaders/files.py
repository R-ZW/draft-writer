from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".json",
}


def load_files(directory: str) -> str:
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {directory}")

    files = sorted(
        file
        for file in path.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        raise ValueError(f"Nenhum arquivo suportado encontrado em: {directory}")

    documents = []

    for file in files:
        content = file.read_text(
            encoding="utf-8",
            errors="replace",
        )

        documents.append(f"""
==============================
ARQUIVO: {file.name}
==============================

{content}
""")

    return "\n".join(documents)
