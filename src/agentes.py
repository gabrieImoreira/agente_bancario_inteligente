# -*- coding: utf-8 -*-
"""
Agentes Simples - Versão simplificada sem abstrações desnecessárias.

Cada agente é uma instância simples de Agente com:
- LLM (OpenAI)
- Tools específicas
- Prompt específico

NÃO usa LangGraph, NÃO usa herança complexa.
"""

from typing import List, Dict, Any, Annotated
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

from src.config.settings import get_langfuse_callback


class AgentePadrao:
    """
    Classe base para agentes bancários simples.
    """

    def __init__(
        self,
        nome: str,
        llm: ChatOpenAI,
        tools: List[BaseTool],
        system_prompt: str,
        verbose: bool = False
    ):
        """
        Inicializa agente simples.

        Args:
            nome: Nome do agente (triagem, credito, entrevista, cambio)
            llm: Instância do ChatOpenAI
            tools: Lista de tools do LangChain
            system_prompt: Prompt do sistema
            verbose: Se True, mostra logs
        """
        self.nome = nome
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.verbose = verbose

        # Vamos criar executor dinamicamente em processar()
        self.executor = None

    def processar(self, mensagem: str, historico: List = None) -> Dict[str, Any]:
        """
        Processa uma mensagem e retorna resposta.

        Args:
            mensagem: Mensagem do usuário
            historico: Lista de tuplas (role, content) do histórico

        Returns:
            Dict com:
                - sucesso: bool
                - resposta: str (resposta do agente)
                - steps: list (intermediate_steps para debug)
        """
        if historico is None:
            historico = []

        try:
            # Recriar executor com prompt atualizado (pode ter mudado)
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="historico"),
                ("human", "{mensagem}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt_template
            )

            executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=self.verbose,
                return_intermediate_steps=True,
                max_iterations=10,
                handle_parsing_errors=True
            )

            # Preparar callbacks do Langfuse
            callbacks = []
            langfuse_cb = get_langfuse_callback()
            if langfuse_cb:
                callbacks.append(langfuse_cb)

            result = executor.invoke(
                {"mensagem": mensagem, "historico": historico},
                config={"callbacks": callbacks} if callbacks else None
            )

            return {
                "sucesso": True,
                "resposta": result.get("output", ""),
                "steps": result.get("intermediate_steps", [])
            }

        except Exception as e:
            import traceback
            traceback.print_exc()  # Ativar para ver o traceback completo
            return {
                "sucesso": False,
                "resposta": f"Desculpe, ocorreu um erro: {str(e)}",
                "steps": [],
                "erro": str(e)
            }


# ==============================================================================
# FACTORY FUNCTIONS - Criam agentes especializados
# ==============================================================================

def criar_agente_triagem(llm: ChatOpenAI, tools: List[BaseTool], prompt: str, verbose: bool = False) -> AgentePadrao:
    """
    Cria agente de Triagem.

    Responsável por:
    - Autenticação (CPF + data nascimento)
    - Direcionamento inicial
    """
    return AgentePadrao(
        nome="triagem",
        llm=llm,
        tools=tools,
        system_prompt=prompt,
        verbose=verbose
    )


def criar_agente_credito(llm: ChatOpenAI, tools: List[BaseTool], prompt: str, verbose: bool = False) -> AgentePadrao:
    """
    Cria agente de Crédito.

    Responsável por:
    - Consulta de limite
    - Solicitação de aumento de limite
    - Aprovação/rejeição automática
    """
    return AgentePadrao(
        nome="credito",
        llm=llm,
        tools=tools,
        system_prompt=prompt,
        verbose=verbose
    )


def criar_agente_entrevista(llm: ChatOpenAI, tools: List[BaseTool], prompt: str, verbose: bool = False) -> AgentePadrao:
    """
    Cria agente de Entrevista.

    Responsável por:
    - Coletar dados financeiros (5 perguntas)
    - Calcular novo score
    - Atualizar score no sistema
    """
    return AgentePadrao(
        nome="entrevista",
        llm=llm,
        tools=tools,
        system_prompt=prompt,
        verbose=verbose
    )


def criar_agente_cambio(llm: ChatOpenAI, tools: List[BaseTool], prompt: str, verbose: bool = False) -> AgentePadrao:
    """
    Cria agente de Câmbio.

    Responsável por:
    - Consulta de cotações de moedas
    - Conversão de valores
    """
    return AgentePadrao(
        nome="cambio",
        llm=llm,
        tools=tools,
        system_prompt=prompt,
        verbose=verbose
    )
