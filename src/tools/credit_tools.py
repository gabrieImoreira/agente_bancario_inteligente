"""Tools de crédito para o Agente de Crédito."""

from langchain.tools import tool
from typing import Dict, Any, Annotated
from datetime import datetime

from src.services.data_service import DataService
from src.services.score_service import ScoreService
from src.models.schemas import SolicitacaoAumento
from src.utils.validators import limpar_cpf
from src.utils.formatters import formatar_moeda_br
from src.utils.observability import observe_tool


#@observe_tool("get_credit_limit")
@tool
def get_credit_limit(cpf: str) -> Dict[str, Any]:
    """
    Consulta o limite de credito atual de um cliente.

    Use esta ferramenta para verificar o limite de credito disponivel
    do cliente autenticado.

    Args:
        cpf: CPF do cliente

    Returns:
        Dict com:
        - success (bool): Se a consulta foi bem-sucedida
        - message (str): Mensagem descritiva
        - data (dict): Limite atual e score do cliente

    Example:
        >>> get_credit_limit("12345678900")
        {
            "success": True,
            "message": "Limite consultado com sucesso.",
            "data": {
                "limite_atual": 5000.00,
                "limite_formatado": "R$ 5.000,00",
                "score": 650
            }
        }
    """
    try:
        cpf_limpo = limpar_cpf(cpf)

        data_service = DataService()
        cliente = data_service.get_client_by_cpf(cpf_limpo)

        if cliente is None:
            return {
                "success": False,
                "message": "Cliente nao encontrado.",
                "data": None
            }

        return {
            "success": True,
            "message": f"Seu limite de credito atual e de {formatar_moeda_br(cliente.limite_credito)}.",
            "data": {
                "limite_atual": cliente.limite_credito,
                "limite_formatado": formatar_moeda_br(cliente.limite_credito),
                "score": cliente.score_credito
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao consultar limite: {str(e)}",
            "data": None
        }


#@observe_tool("request_limit_increase")
@tool
def request_limit_increase(cpf: str, novo_limite: float) -> Dict[str, Any]:
    """
    Processa uma solicitacao de aumento de limite de credito.

    Esta ferramenta:
    1. Verifica o score atual do cliente
    2. Consulta o limite maximo permitido para o score
    3. Valida se o novo limite solicitado e permitido
    4. Aprova ou rejeita automaticamente
    5. Registra a solicitacao em CSV
    6. Se aprovado, atualiza o limite do cliente

    Args:
        cpf: CPF do cliente
        novo_limite: Novo limite de credito desejado (em reais)

    Returns:
        Dict com:
        - success (bool): Se a solicitacao foi processada
        - approved (bool): Se a solicitacao foi aprovada
        - message (str): Mensagem descritiva
        - data (dict): Detalhes da solicitacao

    Example:
        >>> request_limit_increase("12345678900", 8000.00)
        {
            "success": True,
            "approved": True,
            "message": "Solicitacao aprovada! Seu novo limite e R$ 8.000,00",
            "data": {
                "limite_anterior": 5000.00,
                "novo_limite": 8000.00,
                "score": 650
            }
        }
    """
    try:
        cpf_limpo = limpar_cpf(cpf)

        # Buscar dados do cliente
        data_service = DataService()
        cliente = data_service.get_client_by_cpf(cpf_limpo)

        if cliente is None:
            return {
                "success": False,
                "approved": False,
                "message": "Cliente nao encontrado.",
                "data": None
            }

        # Validar que o novo limite é maior que o atual
        if novo_limite <= cliente.limite_credito:
            return {
                "success": False,
                "approved": False,
                "message": f"O novo limite deve ser maior que o limite atual ({formatar_moeda_br(cliente.limite_credito)}).",
                "data": None
            }

        # Obter limite máximo para o score
        limite_maximo_score = data_service.get_max_limit_for_score(cliente.score_credito)

        # Validar se o limite solicitado é permitido
        score_service = ScoreService()
        is_valid = score_service.validate_limit_for_score(
            cliente.score_credito,
            novo_limite,
            limite_maximo_score
        )

        # Determinar status
        status = "aprovado" if is_valid else "rejeitado"

        # Criar solicitação
        solicitacao = SolicitacaoAumento(
            cpf_cliente=cpf_limpo,
            data_hora_solicitacao=datetime.now(),
            limite_atual=cliente.limite_credito,
            novo_limite_solicitado=novo_limite,
            status_pedido=status
        )

        # Registrar no CSV
        data_service.create_limit_request(solicitacao)

        # Se aprovado, atualizar limite do cliente
        if is_valid:
            data_service.update_client_limit(cpf_limpo, novo_limite)

            return {
                "success": True,
                "approved": True,
                "message": f"Parabens! Sua solicitacao foi APROVADA. Seu novo limite e {formatar_moeda_br(novo_limite)}.",
                "data": {
                    "limite_anterior": cliente.limite_credito,
                    "novo_limite": novo_limite,
                    "score": cliente.score_credito
                }
            }
        else:
            return {
                "success": True,
                "approved": False,
                "message": "Solicitacao REJEITADA devido ao score insuficiente.",
                "data": {
                    "limite_anterior": cliente.limite_credito,
                    "novo_limite_solicitado": novo_limite,
                    "score": cliente.score_credito,
                    "pode_fazer_entrevista": True
                }
            }

    except Exception as e:
        return {
            "success": False,
            "approved": False,
            "message": f"Erro ao processar solicitacao: {str(e)}",
            "data": None
        }


#@observe_tool("check_max_limit_for_score")
@tool
def check_max_limit_for_score(score: int) -> Dict[str, Any]:
    """
    Consulta o limite maximo permitido para um determinado score.

    Use esta ferramenta para verificar qual o limite de credito maximo
    que um cliente pode ter baseado no score de credito.

    Args:
        score: Score de credito (0-1000)

    Returns:
        Dict com o limite maximo e classificacao do score

    Example:
        >>> check_max_limit_for_score(750)
        {
            "success": True,
            "data": {
                "score": 750,
                "classificacao": "Bom",
                "limite_maximo": 15000.00
            }
        }
    """
    try:
        data_service = DataService()
        limite_maximo = data_service.get_max_limit_for_score(score)

        classificacao = ScoreService.get_score_classification(score)

        return {
            "success": True,
            "message": f"Com score {score} ({classificacao}), o limite maximo e {formatar_moeda_br(limite_maximo)}.",
            "data": {
                "score": score,
                "classificacao": classificacao,
                "limite_maximo": limite_maximo,
                "limite_maximo_formatado": formatar_moeda_br(limite_maximo)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao consultar limite maximo: {str(e)}",
            "data": None
        }
