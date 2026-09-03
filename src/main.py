import json

from src.agents.evidence_agent import evidence_agent
from src.loaders.files import load_files

from dotenv import load_dotenv

load_dotenv()

UPLOADS_DIR = "uploads"
OUTPUT_FILE = "out/analise.json"


def main():
    documents = load_files(UPLOADS_DIR)

    prompt = f"""
        Analise as evidências abaixo.

        Extraia os dados do processo e construa uma linha do tempo
        dos acontecimentos relevantes.

        EVIDÊNCIAS:

        {documents}
    """

    response = evidence_agent.run(prompt)

    analysis = response.content

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            analysis.model_dump(mode="json"),
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Análise salva em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
