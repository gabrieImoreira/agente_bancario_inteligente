"""LangChain Tools"""

# Garantir que Annotated e outras classes Pydantic estão disponíveis globalmente
from typing import Annotated
from pydantic import BaseModel, Field
import builtins

builtins.Annotated = Annotated
builtins.BaseModel = BaseModel
builtins.Field = Field
