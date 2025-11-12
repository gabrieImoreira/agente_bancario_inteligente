"""Exceções customizadas do sistema."""


class BankingException(Exception):
    """Exceção base para todas as exceções do sistema bancário."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BankingException):
    """Erro durante autenticação do cliente."""

    def __init__(self, message: str = "Falha na autenticação", attempts: int = 0):
        super().__init__(
            message=message,
            details={"attempts": attempts}
        )


class DataAccessError(BankingException):
    """Erro ao acessar dados (CSV, banco, etc)."""

    def __init__(self, message: str, filepath: str = None):
        super().__init__(
            message=message,
            details={"filepath": filepath}
        )


class ValidationError(BankingException):
    """Erro de validação de dados."""

    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(
            message=message,
            details={"field": field, "value": value}
        )


class ScoreCalculationError(BankingException):
    """Erro ao calcular score de crédito."""

    def __init__(self, message: str = "Erro no cálculo de score"):
        super().__init__(message=message)


class LimitRequestError(BankingException):
    """Erro ao processar solicitação de aumento de limite."""

    def __init__(self, message: str, score: int = None, limite_solicitado: float = None):
        super().__init__(
            message=message,
            details={"score": score, "limite_solicitado": limite_solicitado}
        )


class ExchangeAPIError(BankingException):
    """Erro ao consultar API de câmbio."""

    def __init__(self, message: str = "Erro ao consultar cotação", moeda: str = None):
        super().__init__(
            message=message,
            details={"moeda": moeda}
        )


class AgentError(BankingException):
    """Erro durante execução de um agente."""

    def __init__(self, message: str, agent_name: str = None):
        super().__init__(
            message=message,
            details={"agent": agent_name}
        )
