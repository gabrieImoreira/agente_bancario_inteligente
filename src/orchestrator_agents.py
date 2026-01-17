from typing import Dict, Any, Tuple
from src.agentes import (
    criar_agente_triagem,
    criar_agente_credito,
    criar_agente_entrevista,
    criar_agente_cambio
)
from src.config.settings import get_llm
from src.config.prompts import (
    TRIAGEM_SYSTEM_PROMPT,
    CREDITO_SYSTEM_PROMPT,
    ENTREVISTA_SYSTEM_PROMPT,
    CAMBIO_SYSTEM_PROMPT,
    format_triagem_prompt,
    format_credito_prompt,
    format_entrevista_prompt,
    format_cambio_prompt
)
from src.utils.observability import (
    observe,
    get_langfuse_client,
    sanitize_data,
    sanitize_cpf
)

# Import tools
from src.tools.auth_tools import authenticate_client, get_client_info
from src.tools.credit_tools import get_credit_limit, request_limit_increase, check_max_limit_for_score
from src.tools.interview_tools import calculate_new_score, update_client_score
from src.tools.exchange_tools import get_exchange_rate, get_multiple_exchange_rates, convert_currency
from src.tools.common_tools import end_conversation, get_help


class OrquestradorBancoAgil:
    """
    Mantém instâncias dos 4 agentes e decide qual usar baseado no estado.
    """

    def __init__(self, verbose: bool = False):
        """
        Inicializa orquestrador e cria os 4 agentes.

        Args:
            verbose: Se True, agentes mostram logs detalhados
        """
        self.verbose = verbose
        llm = get_llm()

        # Criar agentes com suas tools específicas
        self.triagem = criar_agente_triagem(
            llm=llm,
            tools=[authenticate_client, get_client_info, end_conversation, get_help],
            prompt=TRIAGEM_SYSTEM_PROMPT,
            verbose=verbose
        )

        self.credito = criar_agente_credito(
            llm=llm,
            tools=[get_credit_limit, request_limit_increase, check_max_limit_for_score, end_conversation, get_help],
            prompt=CREDITO_SYSTEM_PROMPT,
            verbose=verbose
        )

        self.entrevista = criar_agente_entrevista(
            llm=llm,
            tools=[calculate_new_score, update_client_score, end_conversation],
            prompt=ENTREVISTA_SYSTEM_PROMPT,
            verbose=verbose
        )

        self.cambio = criar_agente_cambio(
            llm=llm,
            tools=[get_exchange_rate, get_multiple_exchange_rates, convert_currency, end_conversation],
            prompt=CAMBIO_SYSTEM_PROMPT,
            verbose=verbose
        )

    def processar(self, mensagem: str, estado: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Processa mensagem com o agente apropriado.

        Args:
            mensagem: Mensagem do usuário
            estado: Estado atual da conversa (dict simples):
                {
                    "agente_atual": str,
                    "autenticado": bool,
                    "cpf": str | None,
                    "nome": str | None,
                    "limite": float | None,
                    "score": int | None,
                    "historico": List[tuple],
                    "ultima_mensagem": str
                }

        Returns:
            Tuple (resposta_str, novo_estado_dict)
        """
        # Salvar última mensagem para análise
        estado["ultima_mensagem"] = mensagem

        # Determinar agente atual
        agente_atual = estado.get("agente_atual", "triagem")
        historico = estado.get("historico", [])

        # Atualizar trace do Langfuse com contexto da sessão
        langfuse = get_langfuse_client()
        if langfuse:
            try:
                langfuse.update_current_trace(
                    user_id=sanitize_cpf(estado.get("cpf")) if estado.get("cpf") else "anonymous",
                    session_id=estado.get("session_id"),
                    metadata={
                        "agente_atual": agente_atual,
                        "autenticado": estado.get("autenticado", False)
                    }
                )
                langfuse.update_current_span(
                    input={"mensagem": mensagem},
                    metadata={"historico_size": len(historico)}
                )
            except Exception:
                pass  # Ignora erros de observabilidade

        # Executar agente específico
        if agente_atual == "triagem":
            self.triagem.system_prompt = format_triagem_prompt(self._estado_para_dict(estado))
            resultado = self.triagem.processar(mensagem, historico)
            novo_estado = self._atualizar_estado_triagem(resultado, estado)

        elif agente_atual == "credito":
            self.credito.system_prompt = format_credito_prompt(self._estado_para_dict(estado))
            resultado = self.credito.processar(mensagem, historico)
            novo_estado = self._atualizar_estado_credito(resultado, estado)

        elif agente_atual == "entrevista":
            self.entrevista.system_prompt = format_entrevista_prompt(self._estado_para_dict(estado))
            resultado = self.entrevista.processar(mensagem, historico)
            novo_estado = self._atualizar_estado_entrevista(resultado, estado)

        elif agente_atual == "cambio":
            self.cambio.system_prompt = format_cambio_prompt(self._estado_para_dict(estado))
            resultado = self.cambio.processar(mensagem, historico)
            novo_estado = self._atualizar_estado_cambio(resultado, estado)

        else:
            # Fallback - voltar para triagem
            resultado = {"resposta": "Erro: agente desconhecido. Retornando para triagem..."}
            novo_estado = estado.copy()
            novo_estado["agente_atual"] = "triagem"

        # Atualizar histórico
        novo_estado["historico"] = historico + [
            ("user", mensagem),
            ("assistant", resultado["resposta"])
        ]

        # Atualizar span com resultado
        if langfuse:
            try:
                langfuse.update_current_span(
                    output={"resposta_length": len(resultado["resposta"])},
                    metadata={
                        "agente_usado": agente_atual,
                        "agente_proximo": novo_estado.get("agente_atual"),
                        "mudou_agente": agente_atual != novo_estado.get("agente_atual"),
                        "sucesso": resultado.get("sucesso", False)
                    }
                )
            except Exception:
                pass

        # Debug
        if self.verbose:
            print(f"\n[DEBUG] Agente: {agente_atual} -> {novo_estado['agente_atual']}")
            print(f"[DEBUG] Autenticado: {novo_estado.get('autenticado')}")

        return resultado["resposta"], novo_estado

    def _estado_para_dict(self, estado: Dict) -> Dict:
        """Converte estado para formato esperado pelos prompts."""
        return {
            "authenticated": estado.get("autenticado", False),
            "authentication_attempts": estado.get("tentativas_auth", 0),
            "cpf_cliente": estado.get("cpf"),
            "nome_cliente": estado.get("nome"),
            "limite_credito": estado.get("limite"),
            "score_credito": estado.get("score"),
            "voltou_da_entrevista": estado.get("voltou_da_entrevista", False),
            "vindo_de_credito": estado.get("vindo_de_credito", False),
            "messages": estado.get("historico", []),
            "current_agent": estado.get("agente_atual", "triagem")
        }

    def _atualizar_estado_triagem(self, resultado: Dict, estado: Dict) -> Dict:
        """
        Atualiza estado após processamento pelo Agente de Triagem.

        Detecta:
        - Autenticação bem-sucedida (via tool authenticate_client)
        - Palavras-chave para redirecionar para outros agentes
        """
        novo_estado = estado.copy()

        # Verificar se autenticou (olhando intermediate_steps)
        for step in resultado.get("steps", []):
            if len(step) >= 2:
                tool_output = step[1]

                # Autenticação bem-sucedida
                if isinstance(tool_output, dict) and tool_output.get("success"):
                    data = tool_output.get("data", {})
                    if "cpf" in data:
                        novo_estado["autenticado"] = True
                        novo_estado["cpf"] = data.get("cpf")
                        novo_estado["nome"] = data.get("nome")
                        novo_estado["limite"] = data.get("limite_credito")
                        novo_estado["score"] = data.get("score_credito")

        # Detectar próximo agente via palavras-chave (SE autenticado)
        if novo_estado.get("autenticado"):
            mensagem_lower = estado.get("ultima_mensagem", "").lower()

            # Palavras-chave de crédito
            credito_kw = ["limite", "credito", "aumentar", "aumento", "emprestimo", "score", "pontos"]
            cambio_kw = ["dolar", "euro", "cotacao", "cambio", "moeda", "taxa", "usd", "eur"]

            if any(k in mensagem_lower for k in credito_kw):
                novo_estado["agente_atual"] = "credito"
            elif any(k in mensagem_lower for k in cambio_kw):
                novo_estado["agente_atual"] = "cambio"

        return novo_estado

    def _atualizar_estado_credito(self, resultado: Dict, estado: Dict) -> Dict:
        """
        Atualiza estado após processamento pelo Agente de Crédito.

        Detecta:
        - Mudança de contexto para câmbio ou entrevista
        - Atualização de limite (via tool request_limit_increase)
        """
        novo_estado = estado.copy()
        mensagem_lower = estado.get("ultima_mensagem", "").lower()

        # Limpar flag de retorno da entrevista após primeiro uso
        if novo_estado.get("voltou_da_entrevista"):
            novo_estado["voltou_da_entrevista"] = False

        # Verificar se limite foi atualizado
        for step in resultado.get("steps", []):
            if len(step) >= 2:
                tool_output = step[1]
                if isinstance(tool_output, dict):
                    data = tool_output.get("data", {})
                    if "novo_limite" in data:
                        novo_estado["limite"] = data["novo_limite"]

        # Detectar mudança de contexto
        cambio_kw = ["dolar", "euro", "cotacao", "cambio", "moeda", "taxa", "usd", "eur", "conversao"]
        if any(k in mensagem_lower for k in cambio_kw):
            novo_estado["agente_atual"] = "cambio"

        # Detectar aceitação de entrevista
        entrevista_kw = ["entrevista", "atualizar score", "sim", "quero", "aceito"]
        resposta_lower = resultado.get("resposta", "").lower()

        if "entrevista" in resposta_lower and any(k in mensagem_lower for k in ["sim", "quero", "aceito", "gostaria"]):
            novo_estado["agente_atual"] = "entrevista"
            novo_estado["vindo_de_credito"] = True  # Flag para evitar repetição

        return novo_estado

    def _atualizar_estado_entrevista(self, resultado: Dict, estado: Dict) -> Dict:
        """
        Atualiza estado após processamento pelo Agente de Entrevista.

        Detecta:
        - Entrevista concluída (score atualizado)
        - Mudança de contexto para câmbio
        """
        novo_estado = estado.copy()

        # Limpar flag de transição após primeiro uso
        if novo_estado.get("vindo_de_credito"):
            novo_estado["vindo_de_credito"] = False

        # Verificar se concluiu entrevista (score atualizado)
        for step in resultado.get("steps", []):
            if len(step) >= 2:
                tool_name = getattr(step[0], "tool", None)

                if tool_name == "update_client_score":
                    # Entrevista concluída! Voltar para crédito
                    tool_output = step[1]
                    if isinstance(tool_output, dict):
                        data = tool_output.get("data", {})
                        if "score_novo" in data:
                            novo_estado["score"] = data["score_novo"]

                    novo_estado["agente_atual"] = "credito"
                    novo_estado["voltou_da_entrevista"] = True
                    break

        # Detectar mudança de contexto para câmbio
        mensagem_lower = estado.get("ultima_mensagem", "").lower()
        cambio_kw = ["dolar", "euro", "cotacao", "cambio", "moeda"]

        if any(k in mensagem_lower for k in cambio_kw):
            novo_estado["agente_atual"] = "cambio"

        return novo_estado

    def _atualizar_estado_cambio(self, resultado: Dict, estado: Dict) -> Dict:
        """
        Atualiza estado após processamento pelo Agente de Câmbio.

        Detecta:
        - Mudança de contexto para crédito
        """
        novo_estado = estado.copy()
        mensagem_lower = estado.get("ultima_mensagem", "").lower()

        # Detectar mudança de contexto para crédito
        credito_kw = ["limite", "credito", "aumentar", "aumento", "emprestimo", "score"]

        if any(k in mensagem_lower for k in credito_kw):
            novo_estado["agente_atual"] = "credito"

        return novo_estado


def criar_estado_inicial() -> Dict[str, Any]:
    """
    Cria estado inicial para nova conversa.

    Returns:
        Dict com estado inicial
    """
    return {
        "agente_atual": "triagem",
        "autenticado": False,
        "cpf": None,
        "nome": None,
        "limite": None,
        "score": None,
        "historico": [],
        "ultima_mensagem": "",
        "tentativas_auth": 0
    }
