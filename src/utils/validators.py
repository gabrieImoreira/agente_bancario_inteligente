"""Funções de validação de dados."""

import re
from datetime import datetime
from typing import Optional


def validar_cpf(cpf: str) -> bool:
    """
    Valida formato de CPF (apenas formato, não dígitos verificadores).

    Args:
        cpf: CPF para validar (apenas números)

    Returns:
        True se o formato é válido
    """
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'\D', '', cpf)

    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return False

    # Verifica se não é uma sequência repetida (ex: 11111111111)
    if cpf_limpo == cpf_limpo[0] * 11:
        return False

    return True


def validar_data_nascimento(data: str) -> bool:
    """
    Valida formato de data de nascimento (DD/MM/AAAA).

    Args:
        data: Data no formato DD/MM/AAAA

    Returns:
        True se o formato é válido e a data é coerente
    """
    # Verifica formato
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', data):
        return False

    try:
        # Tenta fazer o parse
        dia, mes, ano = map(int, data.split('/'))
        data_obj = datetime(ano, mes, dia)

        # Verifica se a data não é futura
        if data_obj > datetime.now():
            return False

        # Verifica se a pessoa tem entre 18 e 120 anos
        idade = (datetime.now() - data_obj).days // 365
        if idade < 18 or idade > 120:
            return False

        return True

    except ValueError:
        return False


def limpar_cpf(cpf: str) -> str:
    """
    Remove formatação do CPF, deixando apenas números.

    Args:
        cpf: CPF com ou sem formatação

    Returns:
        CPF apenas com números
    """
    return re.sub(r'\D', '', cpf)


def formatar_cpf(cpf: str) -> str:
    """
    Formata CPF no padrão XXX.XXX.XXX-XX.

    Args:
        cpf: CPF apenas com números

    Returns:
        CPF formatado
    """
    cpf_limpo = limpar_cpf(cpf)
    if len(cpf_limpo) != 11:
        return cpf

    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"


def formatar_moeda(valor: float) -> str:
    """
    Formata valor em reais (R$ X.XXX,XX).

    Args:
        valor: Valor numérico

    Returns:
        String formatada
    """
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def validar_valor_positivo(valor: float, nome_campo: str = "valor") -> bool:
    """
    Valida se um valor é positivo.

    Args:
        valor: Valor a validar
        nome_campo: Nome do campo (para mensagem de erro)

    Returns:
        True se válido

    Raises:
        ValueError se inválido
    """
    if valor <= 0:
        raise ValueError(f"{nome_campo} deve ser maior que zero")
    return True


def validar_score(score: int) -> bool:
    """
    Valida se um score está no range válido (0-1000).

    Args:
        score: Score a validar

    Returns:
        True se válido

    Raises:
        ValueError se inválido
    """
    if not 0 <= score <= 1000:
        raise ValueError("Score deve estar entre 0 e 1000")
    return True


def extrair_numeros(texto: str) -> Optional[str]:
    """
    Extrai apenas números de um texto.

    Args:
        texto: Texto de entrada

    Returns:
        String com apenas números ou None se não houver
    """
    numeros = re.sub(r'\D', '', texto)
    return numeros if numeros else None
