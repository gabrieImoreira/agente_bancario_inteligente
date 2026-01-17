"""Tools de entrevista de credito para o Agente de Entrevista."""

from langchain.tools import tool
from typing import Dict, Any, Annotated

from src.services.data_service import DataService
from src.services.score_service import ScoreService
from src.models.schemas import DadosFinanceiros
from src.utils.validators import limpar_cpf
from src.utils.formatters import formatar_moeda_br
from src.utils.observability import observe_tool


#@observe_tool("calculate_new_score")
@tool
def calculate_new_score(
    cpf: str,
    renda_mensal: float,
    tipo_emprego: str,
    despesas_fixas: float,
    num_dependentes: int,
    tem_dividas: str
) -> Dict[str, Any]:
    """
    Calcula um novo score de credito baseado nos dados financeiros coletados na entrevista.

    Esta ferramenta:
    1. Valida os dados fornecidos
    2. Calcula o novo score usando a formula ponderada
    3. Compara com o score anterior
    4. Retorna o novo score e recomendacoes

    IMPORTANTE: Esta ferramenta NAO atualiza o score na base de dados.
    Use update_client_score para persistir o novo score.

    Args:
        cpf: CPF do cliente
        renda_mensal: Renda mensal em reais (deve ser > 0)
        tipo_emprego: Tipo de emprego - DEVE SER UM DOS VALORES: "formal", "autonomo", "desempregado"
        despesas_fixas: Despesas fixas mensais em reais (>= 0)
        num_dependentes: Numero de dependentes (>= 0)
        tem_dividas: Possui dividas ativas - DEVE SER: "sim" ou "nao"

    Returns:
        Dict com:
        - success (bool): Se o calculo foi bem-sucedido
        - message (str): Mensagem descritiva
        - data (dict): Score anterior, novo score, diferenca, classificacao

    Example:
        >>> calculate_new_score(
        ...     "12345678900",
        ...     5000.00,
        ...     "formal",
        ...     2000.00,
        ...     2,
        ...     "nao"
        ... )
        {
            "success": True,
            "message": "Novo score calculado com sucesso!",
            "data": {
                "score_anterior": 650,
                "score_novo": 735,
                "diferenca": +85,
                "classificacao": "Bom",
                "recomendacoes": [...]
            }
        }
    """
    try:
        cpf_limpo = limpar_cpf(cpf)

        # Buscar cliente
        data_service = DataService()
        cliente = data_service.get_client_by_cpf(cpf_limpo)

        if cliente is None:
            return {
                "success": False,
                "message": "Cliente nao encontrado.",
                "data": None
            }

        # Converter tem_dividas para boolean
        tem_dividas_bool = tem_dividas.lower() in ["sim", "s", "true", "1", "yes"]

        # Normalizar tipo_emprego
        tipo_emprego_normalizado = tipo_emprego.lower()
        if tipo_emprego_normalizado not in ["formal", "autonomo", "desempregado"]:
            return {
                "success": False,
                "message": f"Tipo de emprego invalido: '{tipo_emprego}'. Use: 'formal', 'autonomo' ou 'desempregado'.",
                "data": None
            }

        # Criar modelo de dados financeiros
        try:
            dados = DadosFinanceiros(
                renda_mensal=renda_mensal,
                tipo_emprego=tipo_emprego_normalizado,
                despesas_fixas=despesas_fixas,
                num_dependentes=num_dependentes,
                tem_dividas=tem_dividas_bool
            )
        except Exception as validation_error:
            return {
                "success": False,
                "message": f"Dados financeiros invalidos: {str(validation_error)}",
                "data": None
            }

        # Calcular novo score
        score_service = ScoreService()
        novo_score = score_service.calculate_score(dados)

        # Calcular diferença
        score_anterior = cliente.score_credito
        diferenca = novo_score - score_anterior

        # Obter classificação
        classificacao = score_service.get_score_classification(novo_score)

        # Obter recomendações
        recomendacoes = score_service.get_recommendations(dados, novo_score)

        # Mensagem descritiva
        if diferenca > 0:
            mensagem = f"Otima noticia! Seu score aumentou de {score_anterior} para {novo_score} (+{diferenca} pontos)."
        elif diferenca < 0:
            mensagem = f"Seu score diminuiu de {score_anterior} para {novo_score} ({diferenca} pontos)."
        else:
            mensagem = f"Seu score permaneceu o mesmo: {novo_score}."

        return {
            "success": True,
            "message": mensagem,
            "data": {
                "score_anterior": score_anterior,
                "score_novo": novo_score,
                "diferenca": diferenca,
                "classificacao": classificacao,
                "recomendacoes": recomendacoes,
                "dados_financeiros": {
                    "renda_mensal": formatar_moeda_br(renda_mensal),
                    "tipo_emprego": tipo_emprego_normalizado,
                    "despesas_fixas": formatar_moeda_br(despesas_fixas),
                    "num_dependentes": num_dependentes,
                    "tem_dividas": tem_dividas_bool
                }
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao calcular score: {str(e)}",
            "data": None
        }


#@observe_tool("update_client_score")
@tool
def update_client_score(cpf: str, novo_score: int) -> Dict[str, Any]:
    """
    Atualiza o score de credito de um cliente na base de dados.

    Use esta ferramenta APOS calcular o novo score com calculate_new_score.
    Esta ferramenta persiste o novo score no arquivo CSV de clientes.

    Args:
        cpf: CPF do cliente
        novo_score: Novo score de credito (0-1000)

    Returns:
        Dict com:
        - success (bool): Se a atualizacao foi bem-sucedida
        - message (str): Mensagem descritiva
        - data (dict): Score anterior e novo

    Example:
        >>> update_client_score("12345678900", 735)
        {
            "success": True,
            "message": "Score atualizado com sucesso!",
            "data": {
                "score_anterior": 650,
                "score_novo": 735
            }
        }
    """
    try:
        cpf_limpo = limpar_cpf(cpf)

        # Buscar cliente para pegar score anterior
        data_service = DataService()
        cliente = data_service.get_client_by_cpf(cpf_limpo)

        if cliente is None:
            return {
                "success": False,
                "message": "Cliente nao encontrado.",
                "data": None
            }

        score_anterior = cliente.score_credito

        # Atualizar score
        data_service.update_client_score(cpf_limpo, novo_score)

        # Calcular diferença
        diferenca = novo_score - score_anterior

        # Mensagem baseada na diferença
        if diferenca > 0:
            mensagem = f"Score atualizado com sucesso! Aumentou de {score_anterior} para {novo_score}."
        elif diferenca < 0:
            mensagem = f"Score atualizado de {score_anterior} para {novo_score}."
        else:
            mensagem = f"Score atualizado: {novo_score}."

        return {
            "success": True,
            "message": mensagem,
            "data": {
                "score_anterior": score_anterior,
                "score_novo": novo_score,
                "diferenca": diferenca
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao atualizar score: {str(e)}",
            "data": None
        }
