"""Tools comuns disponiveis para todos os agentes."""

from langchain.tools import tool
from typing import Dict, Any


@tool
def end_conversation(motivo: str = "Cliente solicitou encerramento") -> Dict[str, Any]:
    """
    Encerra a conversacao com o cliente.

    Use esta ferramenta quando:
    - O cliente pedir para encerrar o atendimento
    - O cliente disser "tchau", "ate logo", "obrigado, e so isso", etc
    - A conversa natural chegou ao fim
    - Nao ha mais acoes a realizar

    Args:
        motivo: Motivo do encerramento (opcional)

    Returns:
        Dict sinalizando encerramento

    Example:
        >>> end_conversation("Cliente solicitou encerramento")
        {
            "should_end": True,
            "message": "Atendimento encerrado. Obrigado por usar o Banco Agil!",
            "motivo": "Cliente solicitou encerramento"
        }
    """
    return {
        "should_end": True,
        "message": "Atendimento encerrado. Obrigado por usar o Banco Ágil! Até a próxima!",
        "motivo": motivo
    }


@tool
def transfer_to_agent(agente_destino: str, motivo: str) -> Dict[str, Any]:
    """
    Sinaliza transferencia para outro agente.

    IMPORTANTE: Esta tool NAO deve ser usada diretamente pelos agentes.
    As transicoes entre agentes sao gerenciadas automaticamente pelo sistema.

    Args:
        agente_destino: Nome do agente destino ('credito', 'entrevista', 'cambio')
        motivo: Motivo da transferencia

    Returns:
        Dict com informacoes de transferencia
    """
    agentes_validos = ["credito", "entrevista", "cambio", "triagem"]

    if agente_destino not in agentes_validos:
        return {
            "success": False,
            "message": f"Agente inválido: {agente_destino}. álidos: {', '.join(agentes_validos)}"
        }

    return {
        "success": True,
        "next_agent": agente_destino,
        "message": f"Transferindo para agente de {agente_destino}...",
        "motivo": motivo
    }


@tool
def get_help() -> Dict[str, Any]:
    """
    Fornece informacoes de ajuda sobre os servicos disponiveis.

    Use quando o cliente perguntar "o que voce pode fazer?", "quais servicos?", etc.

    Returns:
        Dict com lista de servicos disponiveis
    """
    return {
        "success": True,
        "message": "Servicos disponiveis no Banco Agil:",
        "data": {
            "servicos": [
                {
                    "nome": "Consulta de Limite de Credito",
                    "descricao": "Verifique seu limite de credito disponivel"
                },
                {
                    "nome": "Solicitacao de Aumento de Limite",
                    "descricao": "Solicite aumento do seu limite de credito (analise automatica baseada em score)"
                },
                {
                    "nome": "Entrevista de Credito",
                    "descricao": "Atualize seu score de credito respondendo perguntas sobre sua situacao financeira"
                },
                {
                    "nome": "Cotacao de Moedas",
                    "descricao": "Consulte a cotacao atual de moedas estrangeiras (USD, EUR, GBP, etc)"
                }
            ]
        }
    }
