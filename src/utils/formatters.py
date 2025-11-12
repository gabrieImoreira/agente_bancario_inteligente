"""Funções de formatação de dados para exibição."""

from datetime import datetime
from typing import Optional


def formatar_moeda_br(valor: float) -> str:
    """
    Formata valor em reais brasileiros.

    Args:
        valor: Valor numérico

    Returns:
        String no formato R$ X.XXX,XX

    Example:
        >>> formatar_moeda_br(1234.56)
        'R$ 1.234,56'
    """
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_cpf(cpf: str) -> str:
    """
    Formata CPF no padrão XXX.XXX.XXX-XX.

    Args:
        cpf: CPF com 11 dígitos

    Returns:
        CPF formatado

    Example:
        >>> formatar_cpf("12345678900")
        '123.456.789-00'
    """
    if len(cpf) != 11:
        return cpf

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_data_br(data: datetime) -> str:
    """
    Formata datetime para padrão brasileiro.

    Args:
        data: Objeto datetime

    Returns:
        String no formato DD/MM/AAAA HH:MM:SS

    Example:
        >>> formatar_data_br(datetime.now())
        '09/01/2025 10:30:45'
    """
    return data.strftime("%d/%m/%Y %H:%M:%S")


def formatar_data_br_curta(data: datetime) -> str:
    """
    Formata datetime para padrão brasileiro (apenas data).

    Args:
        data: Objeto datetime

    Returns:
        String no formato DD/MM/AAAA
    """
    return data.strftime("%d/%m/%Y")


def formatar_score(score: int) -> str:
    """
    Formata score com classificação.

    Args:
        score: Score de crédito (0-1000)

    Returns:
        String formatada com score e classificação

    Example:
        >>> formatar_score(750)
        '750 (Bom)'
    """
    if score < 300:
        classificacao = "Muito Baixo"
    elif score < 500:
        classificacao = "Baixo"
    elif score < 700:
        classificacao = "Regular"
    elif score < 850:
        classificacao = "Bom"
    else:
        classificacao = "Excelente"

    return f"{score} ({classificacao})"


def formatar_limite_credito(limite_atual: float, limite_maximo: Optional[float] = None) -> str:
    """
    Formata informações de limite de crédito.

    Args:
        limite_atual: Limite atual do cliente
        limite_maximo: Limite máximo permitido (opcional)

    Returns:
        String formatada

    Example:
        >>> formatar_limite_credito(5000.00, 8000.00)
        'R$ 5.000,00 (máximo permitido: R$ 8.000,00)'
    """
    texto = formatar_moeda_br(limite_atual)

    if limite_maximo:
        texto += f" (maximo permitido: {formatar_moeda_br(limite_maximo)})"

    return texto


def formatar_tipo_emprego(tipo: str) -> str:
    """
    Formata tipo de emprego para exibição.

    Args:
        tipo: Tipo de emprego ('formal', 'autonomo', 'desempregado')

    Returns:
        String formatada
    """
    mapeamento = {
        "formal": "Emprego Formal (CLT)",
        "autonomo": "Trabalhador Autonomo",
        "desempregado": "Desempregado"
    }

    return mapeamento.get(tipo, tipo)


def formatar_status_solicitacao(status: str) -> str:
    """
    Formata status de solicitação com emoji/indicador.

    Args:
        status: Status da solicitação

    Returns:
        String formatada

    Example:
        >>> formatar_status_solicitacao("aprovado")
        '[APROVADO]'
    """
    status_upper = status.upper()

    if status == "aprovado":
        return f"[{status_upper}]"
    elif status == "rejeitado":
        return f"[{status_upper}]"
    else:
        return f"[{status_upper}]"


def truncar_texto(texto: str, max_len: int = 50) -> str:
    """
    Trunca texto longo adicionando reticências.

    Args:
        texto: Texto a truncar
        max_len: Tamanho máximo

    Returns:
        Texto truncado

    Example:
        >>> truncar_texto("Texto muito longo aqui", 10)
        'Texto m...'
    """
    if len(texto) <= max_len:
        return texto

    return texto[:max_len - 3] + "..."
