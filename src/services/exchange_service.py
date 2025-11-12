"""Serviço de consulta de cotação de moedas."""

import requests
from typing import Optional, Dict
from datetime import datetime

from src.models.schemas import CotacaoMoeda
from src.utils.exceptions import ExchangeAPIError
from src.config.settings import settings


class ExchangeService:
    """
    Serviço para consultar cotação de moedas via API externa.

    Usa a AwesomeAPI (API brasileira gratuita):
    https://docs.awesomeapi.com.br/api-de-moedas
    """

    def __init__(self, api_url: Optional[str] = None):
        """
        Inicializa o serviço de câmbio.

        Args:
            api_url: URL base da API (não usado com AwesomeAPI)
        """
        # AwesomeAPI - API brasileira com valores corretos
        self.api_base = "https://economia.awesomeapi.com.br/json/last"
        self.timeout = 10  # Timeout em segundos

    def get_rate(self, moeda: str = "USD", base: str = "BRL") -> CotacaoMoeda:
        """
        Obtém a cotação de uma moeda em relação ao Real (BRL).

        Args:
            moeda: Código da moeda a consultar (USD, EUR, GBP, etc)
            base: Sempre BRL (Real Brasileiro)

        Returns:
            CotacaoMoeda com os dados da cotação

        Raises:
            ExchangeAPIError: Se houver erro na consulta

        Example:
            >>> service = ExchangeService()
            >>> cotacao = service.get_rate("USD")
            >>> print(f"1 {cotacao.moeda} = R$ {cotacao.taxa:.2f}")
            1 USD = R$ 5.25
        """
        try:
            # AwesomeAPI: formato USD-BRL, EUR-BRL, etc
            par = f"{moeda}-{base}"
            url = f"{self.api_base}/{par}"

            # Fazer requisição
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse JSON
            data = response.json()

            # AwesomeAPI retorna formato: {"USDBRL": {"bid": "5.25", ...}}
            chave = par.replace("-", "")  # USD-BRL -> USDBRL

            if chave not in data:
                raise ExchangeAPIError(
                    f"Moeda {moeda} nao encontrada na API",
                    moeda=moeda
                )

            # Pegar taxa de compra (bid)
            taxa_str = data[chave].get("bid")
            if not taxa_str:
                raise ExchangeAPIError(
                    "Taxa nao encontrada na resposta da API",
                    moeda=moeda
                )

            taxa = float(taxa_str)

            # Criar modelo
            cotacao = CotacaoMoeda(
                moeda=moeda,
                taxa=taxa,
                data_hora=datetime.now()
            )

            return cotacao

        except requests.exceptions.Timeout:
            raise ExchangeAPIError(
                "Timeout ao consultar API de cambio",
                moeda=moeda
            )

        except requests.exceptions.ConnectionError:
            raise ExchangeAPIError(
                "Erro de conexao ao consultar API de cambio",
                moeda=moeda
            )

        except requests.exceptions.HTTPError as e:
            raise ExchangeAPIError(
                f"Erro HTTP ao consultar API: {e.response.status_code}",
                moeda=moeda
            )

        except Exception as e:
            raise ExchangeAPIError(
                f"Erro inesperado ao consultar cotacao: {str(e)}",
                moeda=moeda
            )

    def get_multiple_rates(self, moedas: list[str], base: str = "BRL") -> Dict[str, CotacaoMoeda]:
        """
        Obtém cotações de múltiplas moedas.

        Args:
            moedas: Lista de códigos de moedas (ex: ["USD", "EUR", "GBP"])
            base: Moeda base (padrão: BRL)

        Returns:
            Dict mapeando código da moeda -> CotacaoMoeda

        Example:
            >>> service = ExchangeService()
            >>> cotacoes = service.get_multiple_rates(["USD", "EUR"])
            >>> for moeda, cotacao in cotacoes.items():
            ...     print(f"{moeda}: R$ {cotacao.taxa:.2f}")
            USD: R$ 5.25
            EUR: R$ 5.80
        """
        resultado = {}

        try:
            # AwesomeAPI aceita múltiplas moedas: USD-BRL,EUR-BRL,GBP-BRL
            pares = [f"{moeda}-{base}" for moeda in moedas]
            pares_str = ",".join(pares)
            url = f"{self.api_base}/{pares_str}"

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Processar cada moeda
            for moeda in moedas:
                chave = f"{moeda}{base}"  # USD-BRL -> USDBRL
                if chave in data:
                    taxa_str = data[chave].get("bid")
                    if taxa_str:
                        resultado[moeda] = CotacaoMoeda(
                            moeda=moeda,
                            taxa=float(taxa_str),
                            data_hora=datetime.now()
                        )

            return resultado

        except Exception as e:
            raise ExchangeAPIError(
                f"Erro ao consultar multiplas cotacoes: {str(e)}"
            )

    def is_api_available(self) -> bool:
        """
        Verifica se a API está disponível.

        Returns:
            True se a API está respondendo
        """
        try:
            response = requests.get(
                f"{self.api_base}/USD-BRL",
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False

    def get_available_currencies(self, base: str = "BRL") -> list[str]:
        """
        Retorna lista de moedas disponíveis na AwesomeAPI.

        Args:
            base: Moeda base (não usado, sempre BRL)

        Returns:
            Lista de códigos de moedas disponíveis
        """
        # AwesomeAPI suporta moedas principais
        return ["USD", "EUR", "GBP", "ARS", "BTC", "CAD", "CHF", "JPY"]
