# -*- coding: utf-8 -*-
"""Interface Streamlit para o Banco Agil."""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretorio raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# ==============================================================================
# 1. CONFIGURACAO DA INTERFACE E CARREGAMENTO DO BACKEND
# ==============================================================================

st.set_page_config(
    page_title="Banco Ágil - Atendimento Inteligente",
    page_icon="🏦",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        text-align: left !important;
        border-radius: 8px;
        transition: background-color 0.2s, color 0.2s;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stButton>button:hover {
        background-color: #4A4A4A;
        color: white;
    }
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Carregamento do orquestrador com cache
@st.cache_resource
def load_orchestrator():
    try:
        from src.orchestrator_agents import OrquestradorBancoAgil
        return OrquestradorBancoAgil(verbose=False)
    except FileNotFoundError as e:
        st.error(f"Arquivo nao encontrado: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Erro ao inicializar sistema: {str(e)}")
        st.info("Verifique se:\n1. OPENAI_API_KEY esta configurada no .env\n2. Arquivos CSV foram criados (execute: pipenv run python scripts/setup_data.py)")
        st.stop()

orquestrador = load_orchestrator()

# Inicializar estado da sessao
if "messages" not in st.session_state:
    st.session_state.messages = []
if "estado" not in st.session_state:
    from src.orchestrator_agents import criar_estado_inicial
    st.session_state.estado = criar_estado_inicial()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "client_data" not in st.session_state:
    st.session_state.client_data = {}

# ==============================================================================
# 2. FUNCOES AUXILIARES
# ==============================================================================

def nova_conversa():
    from src.orchestrator_agents import criar_estado_inicial
    st.session_state.messages = []
    st.session_state.estado = criar_estado_inicial()
    st.session_state.authenticated = False
    st.session_state.client_data = {}

# ==============================================================================
# 3. LAYOUT DA APLICACAO
# ==============================================================================

# SIDEBAR com informacoes do cliente
with st.sidebar:
    st.markdown("### 🏦 Banco Ágil")

    if st.button("➕ Nova Conversa", use_container_width=True, type="primary"):
        nova_conversa()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Informações do Cliente")

    if st.session_state.authenticated and st.session_state.client_data:
        data = st.session_state.client_data
        st.success("✅ Autenticado")
        st.markdown(f"**Nome:** {data.get('nome', 'N/A')}")

        # CPF parcialmente oculto
        cpf = data.get('cpf', '')
        if len(cpf) == 11:
            cpf_masked = f"***.**{cpf[5:8]}.{cpf[8:11]}"
            st.markdown(f"**CPF:** {cpf_masked}")

        st.markdown("---")

        # Metricas
        from src.utils.formatters import formatar_moeda_br, formatar_score
        limite = data.get('limite_credito', 0)
        score = data.get('score_credito', 0)

        st.metric("💳 Limite de Crédito", formatar_moeda_br(limite))
        st.metric("⭐ Score de Crédito", formatar_score(score))
    else:
        st.info("Não autenticado")
        st.markdown("Inicie uma conversa para fazer login.")

    st.markdown("---")

    # Serviços disponíveis
    with st.expander("ℹ️ Serviços"):
        st.markdown("""
        - Consulta de Limite
        - Aumento de Limite
        - Entrevista de Crédito
        - Cotação de Moedas
        """)

    # Dados de teste
    with st.expander("🔑 Dados de teste"):
        st.code("""
CPF: 12345678900
Data: 15/03/1985
Score: 650

CPF: 98765432100
Data: 22/07/1990
Score: 820

CPF: 99988877766
Data: 18/01/1982
Score: 320
        """)

# CABECALHO principal
col1, col2 = st.columns([1, 10])
with col1:
    st.markdown("# 🏦")
with col2:
    st.markdown("<h2 style='vertical-align: middle; margin-bottom: 0px;'>Banco Agil - Atendimento Inteligente</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6E6E6E; margin-top: 0px;'>Seu assistente virtual bancário com IA</p>", unsafe_allow_html=True)

st.markdown("---")

# EXIBIR historico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.container(border=True).markdown(msg["content"])

# MENSAGEM inicial (se nao houver mensagens)
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.container(border=True).markdown("""
**Olá! Bem-vindo ao Banco Ágil!** 👋

Sou seu assistente virtual e posso ajudar com:
- 💳 Consulta e aumento de limite de crédito
- ⭐ Atualização de score de crédito
- 💱 Cotações de moedas em tempo real

Para começar, preciso autenticar sua identidade.

Digite **"Olá"** para iniciar o atendimento!
        """)

# INPUT do usuario
user_input = st.chat_input("Digite sua mensagem...")

if user_input:
    # Adicionar mensagem do usuario
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.container(border=True).markdown(user_input)

    # Processar com o orquestrador simples
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            try:
                # Processar mensagem
                resposta, novo_estado = orquestrador.processar(
                    user_input,
                    st.session_state.estado
                )

                # Verificar se agente mudou
                agente_anterior = st.session_state.estado.get("agente_atual")
                agente_novo = novo_estado.get("agente_atual")
                mudou_agente = (agente_anterior != agente_novo)

                # Atualizar estado
                st.session_state.estado = novo_estado

                # Exibir resposta
                st.container(border=True).markdown(resposta)

                # Salvar no histórico
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": resposta
                })

                # Atualizar dados do cliente se autenticado
                if novo_estado.get("autenticado"):
                    st.session_state.authenticated = True
                    st.session_state.client_data = {
                        "nome": novo_estado.get("nome"),
                        "cpf": novo_estado.get("cpf"),
                        "limite_credito": novo_estado.get("limite"),
                        "score_credito": novo_estado.get("score")
                    }

                # AUTO-CONTINUAR se mudou de agente E não tem pergunta
                if mudou_agente and "?" not in resposta:
                    # Processar continuação automática
                    with st.spinner("Continuando..."):
                        resposta_cont, novo_estado_cont = orquestrador.processar(
                            "[CONTINUACAO]",  # Mensagem interna
                            st.session_state.estado
                        )

                        # Atualizar estado novamente
                        st.session_state.estado = novo_estado_cont

                        # Exibir resposta de continuação
                        st.container(border=True).markdown(resposta_cont)

                        # Salvar no histórico
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": resposta_cont
                        })

                        # Atualizar dados do cliente
                        if novo_estado_cont.get("autenticado"):
                            st.session_state.client_data = {
                                "nome": novo_estado_cont.get("nome"),
                                "cpf": novo_estado_cont.get("cpf"),
                                "limite_credito": novo_estado_cont.get("limite"),
                                "score_credito": novo_estado_cont.get("score")
                            }

            except Exception as e:
                import traceback
                error_msg = f"Erro ao processar: {str(e)}"
                st.container(border=True).error(error_msg)
                st.code(traceback.format_exc())  # Debug
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Desculpe, ocorreu um erro. Tente novamente."
                })

    # Rerun para atualizar
    st.rerun()
