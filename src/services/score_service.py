"""Serviço de cálculo de score de crédito."""

from typing import Dict
from src.models.schemas import DadosFinanceiros
from src.utils.exceptions import ScoreCalculationError


class ScoreService:
    """
    Serviço para cálculo de score de crédito baseado em dados financeiros.

    Fórmula:
        score = (
            (renda_mensal / (despesas_fixas + 1)) * PESO_RENDA +
            PESO_EMPREGO[tipo_emprego] +
            PESO_DEPENDENTES[num_dependentes] +
            PESO_DIVIDAS[tem_dividas]
        )
    """

    # Pesos da fórmula (reajustados para melhor balance renda vs dívidas)
    PESO_RENDA = 200  # Aumentado para priorizar capacidade de pagamento
    PESO_EMPREGO: Dict[str, int] = {
        "formal": 200,      # Reduzido para equilibrar
        "autonomo": 150,    # Reduzido para equilibrar
        "desempregado": 0
    }
    PESO_DEPENDENTES: Dict[int, int] = {
        0: 50,    # Reduzido - menos impacto
        1: 35,    # Reduzido - menos impacto
        2: 20,    # Reduzido - menos impacto
    }
    PESO_DEPENDENTES_3_OU_MAIS = 10  # Reduzido

    PESO_DIVIDAS: Dict[bool, int] = {
        True: -50,    # Reduzido - penalização menos severa
        False: 50     # Reduzido - bônus moderado
    }

    @classmethod
    def calculate_score(cls, dados: DadosFinanceiros) -> int:
        """
        Calcula o score de crédito baseado nos dados financeiros.

        Args:
            dados: Dados financeiros do cliente

        Returns:
            Score calculado (0-1000)

        Raises:
            ScoreCalculationError: Se houver erro no cálculo

        Example:
            >>> dados = DadosFinanceiros(
            ...     renda_mensal=5000,
            ...     tipo_emprego="formal",
            ...     despesas_fixas=2000,
            ...     num_dependentes=2,
            ...     tem_dividas=False
            ... )
            >>> ScoreService.calculate_score(dados)
            635
        """
        try:
            # Componente: Relação renda/despesas
            if dados.despesas_fixas >= dados.renda_mensal:
                # Despesas maiores que renda = score muito baixo
                componente_renda = 0
            else:
                componente_renda = (
                    dados.renda_mensal / (dados.despesas_fixas + 1)
                ) * cls.PESO_RENDA

            # Componente: Tipo de emprego
            componente_emprego = cls.PESO_EMPREGO.get(
                dados.tipo_emprego,
                0
            )

            # Componente: Número de dependentes
            if dados.num_dependentes >= 3:
                componente_dependentes = cls.PESO_DEPENDENTES_3_OU_MAIS
            else:
                componente_dependentes = cls.PESO_DEPENDENTES.get(
                    dados.num_dependentes,
                    cls.PESO_DEPENDENTES_3_OU_MAIS
                )

            # Componente: Dívidas
            componente_dividas = cls.PESO_DIVIDAS.get(dados.tem_dividas, 0)

            # Score total
            score_bruto = (
                componente_renda +
                componente_emprego +
                componente_dependentes +
                componente_dividas
            )

            # Normalizar para faixa 0-1000
            score_final = max(0, min(1000, int(score_bruto)))

            return score_final

        except Exception as e:
            raise ScoreCalculationError(f"Erro ao calcular score: {str(e)}")

    @classmethod
    def validate_limit_for_score(
        cls,
        score: int,
        limite_solicitado: float,
        limite_maximo_score: float
    ) -> bool:
        """
        Valida se um limite solicitado é permitido para um score.

        Args:
            score: Score de crédito do cliente
            limite_solicitado: Limite que o cliente deseja
            limite_maximo_score: Limite máximo permitido para o score

        Returns:
            True se o limite solicitado é válido
        """
        return limite_solicitado <= limite_maximo_score

    @classmethod
    def get_score_classification(cls, score: int) -> str:
        """
        Retorna a classificação textual de um score.

        Args:
            score: Score de crédito (0-1000)

        Returns:
            Classificação ("Muito Baixo", "Baixo", etc)
        """
        if score < 300:
            return "Muito Baixo"
        elif score < 500:
            return "Baixo"
        elif score < 700:
            return "Regular"
        elif score < 850:
            return "Bom"
        else:
            return "Excelente"

    @classmethod
    def get_recommendations(cls, dados: DadosFinanceiros, score_atual: int) -> list[str]:
        """
        Gera recomendações para melhorar o score.

        Args:
            dados: Dados financeiros atuais
            score_atual: Score atual do cliente

        Returns:
            Lista de recomendações
        """
        recomendacoes = []

        # Analisar relação renda/despesas
        if dados.despesas_fixas >= dados.renda_mensal * 0.7:
            recomendacoes.append(
                "Reduza suas despesas fixas. Elas representam mais de 70% da sua renda."
            )

        # Analisar tipo de emprego
        if dados.tipo_emprego != "formal":
            recomendacoes.append(
                "Buscar um emprego formal (CLT) pode melhorar significativamente seu score."
            )

        # Analisar dívidas
        if dados.tem_dividas:
            recomendacoes.append(
                "Quite suas dividas ativas. Isso pode aumentar seu score em ate 200 pontos."
            )

        # Analisar dependentes
        if dados.num_dependentes >= 3:
            recomendacoes.append(
                "O numero de dependentes impacta negativamente seu score."
            )

        # Se não houver recomendações específicas
        if not recomendacoes:
            if score_atual < 850:
                recomendacoes.append(
                    "Continue mantendo suas financas organizadas para melhorar ainda mais seu score."
                )
            else:
                recomendacoes.append(
                    "Parabens! Seu score esta excelente. Continue assim!"
                )

        return recomendacoes
