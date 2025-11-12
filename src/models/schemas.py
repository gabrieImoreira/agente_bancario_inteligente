"""Schemas Pydantic para validação de dados."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal


class Cliente(BaseModel):
    """Modelo de dados de um cliente."""

    cpf: str = Field(..., pattern=r"^\d{11}$", description="CPF com 11 dígitos")
    nome: str = Field(..., min_length=3, description="Nome completo do cliente")
    data_nascimento: str = Field(..., pattern=r"^\d{2}/\d{2}/\d{4}$", description="Data no formato DD/MM/AAAA")
    limite_credito: float = Field(..., ge=0, description="Limite de crédito em reais")
    score_credito: int = Field(..., ge=0, le=1000, description="Score de crédito (0-1000)")

    class Config:
        json_schema_extra = {
            "example": {
                "cpf": "12345678900",
                "nome": "João Silva",
                "data_nascimento": "15/03/1985",
                "limite_credito": 5000.00,
                "score_credito": 650
            }
        }


class SolicitacaoAumento(BaseModel):
    """Modelo de solicitação de aumento de limite."""

    cpf_cliente: str = Field(..., pattern=r"^\d{11}$")
    data_hora_solicitacao: datetime = Field(default_factory=datetime.now)
    limite_atual: float = Field(..., ge=0)
    novo_limite_solicitado: float = Field(..., ge=0)
    status_pedido: Literal["pendente", "aprovado", "rejeitado"] = Field(default="pendente")

    @field_validator("novo_limite_solicitado")
    @classmethod
    def validar_novo_limite(cls, v: float, info) -> float:
        """Valida que o novo limite é maior que o atual."""
        limite_atual = info.data.get("limite_atual", 0)
        if v <= limite_atual:
            raise ValueError("Novo limite deve ser maior que o limite atual")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "cpf_cliente": "12345678900",
                "data_hora_solicitacao": "2025-01-09T10:30:00",
                "limite_atual": 5000.00,
                "novo_limite_solicitado": 8000.00,
                "status_pedido": "pendente"
            }
        }


class DadosFinanceiros(BaseModel):
    """Dados financeiros coletados na entrevista de crédito."""

    renda_mensal: float = Field(..., gt=0, description="Renda mensal em reais")
    tipo_emprego: Literal["formal", "autonomo", "desempregado"] = Field(..., description="Tipo de emprego")
    despesas_fixas: float = Field(..., ge=0, description="Despesas fixas mensais em reais")
    num_dependentes: int = Field(..., ge=0, description="Número de dependentes")
    tem_dividas: bool = Field(..., description="Possui dívidas ativas")

    class Config:
        json_schema_extra = {
            "example": {
                "renda_mensal": 5000.00,
                "tipo_emprego": "formal",
                "despesas_fixas": 2000.00,
                "num_dependentes": 2,
                "tem_dividas": False
            }
        }


class ScoreLimite(BaseModel):
    """Regra de limite máximo por faixa de score."""

    score_minimo: int = Field(..., ge=0, le=1000)
    score_maximo: int = Field(..., ge=0, le=1000)
    limite_maximo: float = Field(..., ge=0)

    @field_validator("score_maximo")
    @classmethod
    def validar_score_maximo(cls, v: int, info) -> int:
        """Valida que score_maximo é maior que score_minimo."""
        score_minimo = info.data.get("score_minimo", 0)
        if v <= score_minimo:
            raise ValueError("Score máximo deve ser maior que score mínimo")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "score_minimo": 700,
                "score_maximo": 849,
                "limite_maximo": 15000.00
            }
        }


class CotacaoMoeda(BaseModel):
    """Cotação de uma moeda."""

    moeda: str = Field(..., min_length=3, max_length=3, description="Código da moeda (USD, EUR, etc)")
    taxa: float = Field(..., gt=0, description="Taxa de câmbio")
    data_hora: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "moeda": "USD",
                "taxa": 5.25,
                "data_hora": "2025-01-09T10:30:00"
            }
        }
