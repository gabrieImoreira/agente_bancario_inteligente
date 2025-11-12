"""Tools de cambio para o Agente de Cambio."""

from langchain.tools import tool
from typing import Dict, Any

from src.services.exchange_service import ExchangeService
from src.utils.exceptions import ExchangeAPIError
from src.utils.formatters import formatar_data_br


@tool
def get_exchange_rate(moeda: str = "USD") -> Dict[str, Any]:
    """
    Consulta a cotacao atual de uma moeda estrangeira em relacao ao Real (BRL).

    Use esta ferramenta para obter a cotacao em tempo real de moedas como:
    - USD (Dolar Americano)
    - EUR (Euro)
    - GBP (Libra Esterlina)
    - JPY (Iene Japones)
    - CHF (Franco Suico)
    - CAD (Dolar Canadense)
    - AUD (Dolar Australiano)

    Args:
        moeda: Codigo da moeda (3 letras). Padrao: "USD"

    Returns:
        Dict com:
        - success (bool): Se a consulta foi bem-sucedida
        - message (str): Mensagem descritiva
        - data (dict): Taxa de cambio e informacoes

    Example:
        >>> get_exchange_rate("USD")
        {
            "success": True,
            "message": "Cotacao obtida com sucesso.",
            "data": {
                "moeda": "USD",
                "taxa": 5.25,
                "data_hora": "09/01/2025 10:30:45",
                "descricao": "1 USD = R$ 5,25"
            }
        }
    """
    try:
        # Normalizar moeda para uppercase
        moeda_upper = moeda.upper().strip()

        # Consultar API
        exchange_service = ExchangeService()
        cotacao = exchange_service.get_rate(moeda_upper)

        # Formatar taxa em reais
        taxa_formatada = f"R$ {cotacao.taxa:.2f}".replace(".", ",")

        return {
            "success": True,
            "message": f"Cotacao atual: 1 {cotacao.moeda} = {taxa_formatada}",
            "data": {
                "moeda": cotacao.moeda,
                "taxa": cotacao.taxa,
                "taxa_formatada": taxa_formatada,
                "data_hora": formatar_data_br(cotacao.data_hora),
                "descricao": f"1 {cotacao.moeda} = {taxa_formatada}"
            }
        }

    except ExchangeAPIError as e:
        return {
            "success": False,
            "message": f"Erro ao consultar cotacao: {e.message}",
            "data": None
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro inesperado: {str(e)}",
            "data": None
        }


@tool
def get_multiple_exchange_rates(moedas: str) -> Dict[str, Any]:
    """
    Consulta cotacoes de multiplas moedas simultaneamente.

    Args:
        moedas: String com codigos de moedas separados por virgula.
                Exemplo: "USD,EUR,GBP"

    Returns:
        Dict com cotacoes de todas as moedas solicitadas

    Example:
        >>> get_multiple_exchange_rates("USD,EUR,GBP")
        {
            "success": True,
            "message": "3 cotacoes obtidas com sucesso.",
            "data": {
                "USD": {"taxa": 5.25, ...},
                "EUR": {"taxa": 5.80, ...},
                "GBP": {"taxa": 6.50, ...}
            }
        }
    """
    try:
        # Parsear moedas
        lista_moedas = [m.strip().upper() for m in moedas.split(",")]

        # Consultar API
        exchange_service = ExchangeService()
        cotacoes = exchange_service.get_multiple_rates(lista_moedas)

        # Formatar resultado
        resultado = {}
        for moeda_code, cotacao in cotacoes.items():
            taxa_formatada = f"R$ {cotacao.taxa:.2f}".replace(".", ",")
            resultado[moeda_code] = {
                "taxa": cotacao.taxa,
                "taxa_formatada": taxa_formatada,
                "descricao": f"1 {moeda_code} = {taxa_formatada}"
            }

        return {
            "success": True,
            "message": f"{len(resultado)} cotacoes obtidas com sucesso.",
            "data": resultado
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao consultar cotacoes: {str(e)}",
            "data": None
        }


@tool
def convert_currency(valor: float, moeda_origem: str = "USD") -> Dict[str, Any]:
    """
    Converte um valor de moeda estrangeira para Reais (BRL).

    Args:
        valor: Valor em moeda estrangeira
        moeda_origem: Codigo da moeda (padrao: USD)

    Returns:
        Dict com valor convertido

    Example:
        >>> convert_currency(100, "USD")
        {
            "success": True,
            "message": "100 USD = R$ 525,00",
            "data": {
                "valor_origem": 100,
                "moeda_origem": "USD",
                "valor_brl": 525.00,
                "taxa": 5.25
            }
        }
    """
    try:
        moeda_upper = moeda_origem.upper().strip()

        # Obter taxa
        exchange_service = ExchangeService()
        cotacao = exchange_service.get_rate(moeda_upper)

        # Calcular conversão
        valor_brl = valor * cotacao.taxa

        # Formatar valores
        valor_brl_formatado = f"R$ {valor_brl:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

        return {
            "success": True,
            "message": f"{valor} {moeda_upper} = {valor_brl_formatado}",
            "data": {
                "valor_origem": valor,
                "moeda_origem": moeda_upper,
                "valor_brl": valor_brl,
                "valor_brl_formatado": valor_brl_formatado,
                "taxa": cotacao.taxa
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao converter: {str(e)}",
            "data": None
        }
