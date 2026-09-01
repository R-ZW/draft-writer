from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()


def main():
    agente_teste = Agent(name="Agente de Teste", model=Groq(id="openai/gpt-oss-120b"))

    agente_teste.print_response("Qual é o clima hoje em Uruguaiana-RS Brasil?")


if __name__ == "__main__":
    main()
