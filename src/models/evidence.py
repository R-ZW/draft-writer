from datetime import date as datetime_date, time as datetime_time
from enum import Enum

from pydantic import BaseModel, Field


class Participant(str, Enum):
    ADMINISTRACAO = "ADMINISTRACAO"
    EMPRESA = "EMPRESA"
    TERCEIRO = "TERCEIRO"
    DESCONHECIDO = "DESCONHECIDO"


class EventType(str, Enum):
    ENVIO_EMPENHO = "ENVIO_EMPENHO"
    ALERTA_PRAZO = "ALERTA_PRAZO"
    COMUNICACAO_ATRASO = "COMUNICACAO_ATRASO"

    MANIFESTACAO_EMPRESA = "MANIFESTACAO_EMPRESA"
    COMUNICACAO_ADMINISTRACAO = "COMUNICACAO_ADMINISTRACAO"

    SOLICITACAO = "SOLICITACAO"
    RESPOSTA = "RESPOSTA"

    ENTREGA = "ENTREGA"
    DEVOLUCAO = "DEVOLUCAO"

    CANCELAMENTO = "CANCELAMENTO"
    OUTRO = "OUTRO"


class EvidenceReference(BaseModel):
    file: str = Field(description="Nome do arquivo que sustenta o fato.")

    reference: str | None = Field(
        default=None,
        description=(
            "Referência adicional à evidência, como horário da mensagem, "
            "assunto do e-mail ou outro identificador."
        ),
    )


class Event(BaseModel):
    date: datetime_date = Field(description="Data em que o evento ocorreu.")

    time: datetime_time | None = Field(
        default=None,
        description="Horário do evento, se disponível.",
    )

    participant: Participant = Field(description="Quem realizou ou informou o evento.")

    type: EventType = Field(description="Tipo do evento.")

    description: str = Field(
        description=(
            "Descrição objetiva do fato, sem adicionar informações "
            "que não estejam presentes na evidência."
        )
    )

    evidence: list[EvidenceReference] = Field(
        default_factory=list,
        description="Evidências que sustentam este evento.",
    )


class EvidenceAnalysis(BaseModel):
    empenho: str | None = Field(
        default=None,
        description="Número do empenho identificado nas evidências.",
    )

    fornecedor: str | None = Field(
        default=None,
        description="Nome da empresa fornecedora, se identificado.",
    )

    cnpj: str | None = Field(
        default=None,
        description="CNPJ do fornecedor, se identificado.",
    )

    data_emissao_empenho: datetime_date | None = Field(
        default=None,
        description="Data de emissão do empenho, se identificada.",
    )

    prazo_entrega_dias: int | None = Field(
        default=None,
        description="Prazo de entrega informado nas evidências, se identificado.",
    )

    data_envio_empenho: datetime_date | None = Field(
        default=None,
        description=(
            "Data em que o empenho foi efetivamente encaminhado à empresa. "
            "Não confundir com a data de emissão."
        ),
    )

    events: list[Event] = Field(
        default_factory=list,
        description="Eventos relevantes organizados cronologicamente.",
    )

    pending_issues: list[str] = Field(
        default_factory=list,
        description=(
            "Questões ou pendências que permanecem sem solução "
            "de acordo com as evidências."
        ),
    )

    ambiguities: list[str] = Field(
        default_factory=list,
        description=(
            "Informações ambíguas, conflitantes ou insuficientes "
            "encontradas nas evidências."
        ),
    )
