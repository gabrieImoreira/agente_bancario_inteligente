"""Utilitários para observabilidade com Langfuse SDK v3."""

from functools import wraps
from typing import Any, Dict, Optional, Callable

from src.config.settings import settings

# Re-exportar APIs nativas do Langfuse para uso em outros módulos
try:
    from langfuse import observe, get_client
except ImportError:
    observe = None
    get_client = None


def get_langfuse_client():
    """
    Retorna instância do cliente Langfuse (ou None se desabilitado).

    Usa get_client() nativo do SDK que gerencia singleton automaticamente.
    """
    if not settings.langfuse_enabled:
        return None

    if get_client is None:
        return None

    try:
        return get_client()
    except Exception as e:
        print(f"AVISO: Falha ao obter cliente Langfuse: {e}")
        return None


def shutdown_langfuse():
    """
    Realiza flush e shutdown do Langfuse.

    Deve ser chamado no encerramento da aplicação para garantir
    que todos os dados sejam enviados.
    """
    client = get_langfuse_client()
    if client:
        try:
            client.flush()
            client.shutdown()
        except Exception as e:
            print(f"AVISO: Erro ao encerrar Langfuse: {e}")


def sanitize_cpf(cpf: str) -> str:
    """Mascara CPF para mostrar apenas últimos 4 dígitos."""
    if not cpf or len(cpf) < 11:
        return "***"
    return f"***.***.{cpf[-4:]}"


def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove/mascara dados sensíveis de dicionários."""
    if not isinstance(data, dict):
        return data

    sanitized = data.copy()

    # Mascarar CPF
    if "cpf" in sanitized and sanitized["cpf"]:
        sanitized["cpf"] = sanitize_cpf(str(sanitized["cpf"]))
    if "cpf_cliente" in sanitized and sanitized["cpf_cliente"]:
        sanitized["cpf_cliente"] = sanitize_cpf(str(sanitized["cpf_cliente"]))

    # Mascarar data de nascimento
    if "data_nascimento" in sanitized:
        sanitized["data_nascimento"] = "**/**/****"

    return sanitized


def observed_tool(name: str = None):
    """
    Decorator que combina @observe(as_type="tool") com sanitização de dados.

    Usage:
        @observed_tool("authenticate_client")
        @tool
        def authenticate_client(cpf: str, data_nascimento: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            langfuse = get_langfuse_client()

            # Atualizar span com input sanitizado
            if langfuse and kwargs:
                try:
                    langfuse.update_current_span(input=sanitize_data(kwargs))
                except Exception:
                    pass  # Ignora erros de observabilidade

            # Executar função
            result = func(*args, **kwargs)

            # Atualizar span com output sanitizado
            if langfuse and isinstance(result, dict):
                try:
                    langfuse.update_current_span(
                        output=sanitize_data(result),
                        metadata={"success": result.get("success", False)}
                    )
                except Exception:
                    pass

            return result

        # Preservar annotations para o LangChain/Pydantic
        wrapper.__annotations__ = func.__annotations__

        # Aplicar @observe se disponível
        if observe is not None:
            tool_name = f"tool_{name or func.__name__}"
            wrapper = observe(as_type="tool", name=tool_name)(wrapper)

        return wrapper
    return decorator


# Alias para compatibilidade retroativa
observe_tool = observed_tool
