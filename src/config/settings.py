"""Configurações da aplicação."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_openai import ChatOpenAI


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    # =========================================================================
    # OpenAI
    # =========================================================================
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.4

    # =========================================================================
    # Exchange Rate API
    # =========================================================================
    exchange_api_url: str = "https://api.exchangerate-api.com/v4/latest/"

    # =========================================================================
    # Application
    # =========================================================================
    max_auth_attempts: int = 3
    csv_data_path: str = "./data"

    # =========================================================================
    # LangSmith (Opcional)
    # =========================================================================
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "agente-bancario"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @property
    def data_path(self) -> Path:
        """Retorna o Path do diretório de dados."""
        return Path(self.csv_data_path)

    def get_csv_path(self, filename: str) -> Path:
        """Retorna o Path completo para um arquivo CSV."""
        return self.data_path / filename


# Instância global de configurações
settings = Settings()


def get_llm(
    temperature: Optional[float] = None,
    streaming: bool = True,
    model: Optional[str] = None
) -> ChatOpenAI:
    """
    Factory para criar instância do ChatOpenAI.

    Args:
        temperature: Temperatura para o modelo (0.0-2.0).
                    Default: settings.openai_temperature
        streaming: Habilitar streaming de respostas. Default: True
        model: Modelo a ser usado. Default: settings.openai_model

    Returns:
        ChatOpenAI configurado e pronto para uso.

    Example:
        >>> llm = get_llm(temperature=0.5)
        >>> response = llm.invoke("Olá!")
    """
    return ChatOpenAI(
        model=model or settings.openai_model,
        temperature=temperature if temperature is not None else settings.openai_temperature,
        api_key=settings.openai_api_key,
        streaming=streaming,
        top_p=0.9  # Nucleus sampling
    )


def get_deterministic_llm() -> ChatOpenAI:
    """
    Retorna um LLM com temperatura 0 (determinístico).

    Útil para extrações de dados e operações que requerem consistência.

    Returns:
        ChatOpenAI com temperature=0
    """
    return get_llm(temperature=0.0, streaming=False)


def get_creative_llm() -> ChatOpenAI:
    """
    Retorna um LLM com temperatura alta (criativo).

    Útil para geração de texto mais natural e variado.

    Returns:
        ChatOpenAI com temperature=0.9
    """
    return get_llm(temperature=0.9, streaming=True)
