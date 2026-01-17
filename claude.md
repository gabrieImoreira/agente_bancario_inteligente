# Arquitetura do Agente Bancário Inteligente

Este documento descreve a arquitetura completa do **Agente Bancário Inteligente**, um sistema de atendimento bancário automatizado usando IA (LLM) e arquitetura multi-agente.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura de Diretórios](#estrutura-de-diretórios)
4. [Componentes Principais](#componentes-principais)
5. [Fluxo de Dados](#fluxo-de-dados)
6. [Padrões de Design](#padrões-de-design)
7. [Stack Tecnológica](#stack-tecnológica)
8. [Decisões de Design](#decisões-de-design)

---

## Visão Geral

O **Agente Bancário Inteligente** é um assistente virtual que utiliza Large Language Models (LLMs) para automatizar operações bancárias através de uma arquitetura multi-agente especializada.

### Funcionalidades Principais

- **Autenticação de Clientes**: Validação por CPF + data de nascimento
- **Gestão de Crédito**: Consulta e solicitação de aumento de limite
- **Atualização de Score**: Entrevista financeira para recálculo de score de crédito
- **Cotações de Moedas**: Consulta de cotações em tempo real e conversão de valores

### Características Técnicas

- **4 Agentes Especializados**: Triagem, Crédito, Entrevista e Câmbio
- **Transições Transparentes**: O usuário sente que está conversando com um único atendente
- **Function Calling**: LLM invoca funções Python dinamicamente
- **Gerenciamento de Estado**: Estado da conversa mantido entre interações

---

## Arquitetura do Sistema

### Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Streamlit (app/main.py)                │    │
│  │  - Interface web interativa                         │    │
│  │  - Chat UI                                          │    │
│  │  - Sidebar com dados do cliente                     │    │
│  │  - Gerenciamento de sessão                          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA DE ORQUESTRAÇÃO                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │    OrquestradorBancoAgil (orchestrator_agents.py)  │    │
│  │  - Gerencia estado global da conversa              │    │
│  │  - Decide qual agente deve processar a mensagem    │    │
│  │  - Controla transições entre agentes               │    │
│  │  - Atualiza estado após cada interação             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAMADA DE AGENTES                        │
│                                                              │
│  ┌────────┐  ┌────────┐  ┌───────────┐  ┌────────┐        │
│  │Triagem │  │Crédito │  │Entrevista │  │Câmbio  │        │
│  │        │  │        │  │           │  │        │        │
│  │- Auth  │  │- Limit │  │- Score    │  │- Rates │        │
│  │- Route │  │- Incr. │  │- Update   │  │- Conv. │        │
│  └────────┘  └────────┘  └───────────┘  └────────┘        │
│                                                              │
│  Cada agente é uma instância de AgentePadrao (agentes.py)  │
│  - LLM (OpenAI ChatGPT)                                     │
│  - Tools específicas                                        │
│  - System prompt dinâmico                                   │
│  - AgentExecutor (LangChain)                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAMADA DE TOOLS                         │
│             (Function Calling - LangChain Tools)             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Auth Tools  │  │ Credit Tools │  │Interview Tools│    │
│  │              │  │              │  │              │     │
│  │- authenticate│  │- get_limit   │  │- calc_score  │     │
│  │- get_info    │  │- request_inc │  │- update_score│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │Exchange Tools│  │ Common Tools │                        │
│  │              │  │              │                        │
│  │- get_rate    │  │- end_conv    │                        │
│  │- convert     │  │- get_help    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE SERVIÇOS                         │
│                   (Lógica de Negócio)                        │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  DataService (data_service.py)                   │      │
│  │  - Acesso aos dados CSV                          │      │
│  │  - CRUD de clientes                              │      │
│  │  - Registro de solicitações                      │      │
│  │  - Consulta de regras score/limite               │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  ScoreService (score_service.py)                 │      │
│  │  - Cálculo de score baseado em fórmula ponderada│      │
│  │  - Análise de elegibilidade para aumento         │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  ExchangeService (exchange_service.py)           │      │
│  │  - Integração com API externa de câmbio         │      │
│  │  - Cache de cotações                             │      │
│  │  - Conversão de moedas                           │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE DADOS                            │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  CSV Files (data/)                               │      │
│  │                                                   │      │
│  │  - clientes.csv                                  │      │
│  │    └─ CPF, nome, data_nasc, limite, score        │      │
│  │                                                   │      │
│  │  - score_limite.csv                              │      │
│  │    └─ Faixas de score e limites máximos          │      │
│  │                                                   │      │
│  │  - solicitacoes_aumento_limite.csv               │      │
│  │    └─ Histórico de solicitações                  │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Diretórios

```
agente_bancario_inteligente/
│
├── app/                          # Interface Streamlit
│   ├── main.py                   # Aplicação principal (ponto de entrada)
│   └── components/               # Componentes reutilizáveis (futuro)
│
├── src/                          # Código fonte principal
│   │
│   ├── agentes.py                # Definição dos agentes (AgentePadrao)
│   │                             # Factory functions para criar agentes
│   │
│   ├── orchestrator_agents.py   # Orquestrador multi-agente
│   │                             # - OrquestradorBancoAgil
│   │                             # - criar_estado_inicial()
│   │                             # - Lógica de transição entre agentes
│   │
│   ├── tools/                    # Tools para function calling
│   │   ├── __init__.py
│   │   ├── auth_tools.py         # authenticate_client, get_client_info
│   │   ├── credit_tools.py       # get_credit_limit, request_limit_increase
│   │   ├── interview_tools.py    # calculate_new_score, update_client_score
│   │   ├── exchange_tools.py     # get_exchange_rate, convert_currency
│   │   └── common_tools.py       # end_conversation, get_help
│   │
│   ├── services/                 # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── data_service.py       # DataService (acesso a CSV)
│   │   ├── score_service.py      # ScoreService (cálculo de score)
│   │   └── exchange_service.py   # ExchangeService (API de câmbio)
│   │
│   ├── config/                   # Configurações
│   │   ├── __init__.py
│   │   ├── settings.py           # Settings (Pydantic BaseSettings)
│   │   │                         # - Variáveis de ambiente (.env)
│   │   │                         # - get_llm() factory
│   │   │
│   │   └── prompts.py            # System prompts dos agentes
│   │                             # - TRIAGEM_SYSTEM_PROMPT
│   │                             # - CREDITO_SYSTEM_PROMPT
│   │                             # - ENTREVISTA_SYSTEM_PROMPT
│   │                             # - CAMBIO_SYSTEM_PROMPT
│   │                             # - format_*_prompt() helpers
│   │
│   ├── models/                   # Schemas Pydantic
│   │   ├── __init__.py
│   │   └── schemas.py            # Cliente, SolicitacaoAumento,
│   │                             # DadosFinanceiros, ScoreLimite,
│   │                             # CotacaoMoeda
│   │
│   └── utils/                    # Utilitários
│       ├── __init__.py
│       ├── validators.py         # validar_cpf, validar_data_nascimento
│       ├── formatters.py         # formatar_moeda_br, formatar_score
│       └── exceptions.py         # DataAccessError, AuthenticationError
│
├── data/                         # Dados (CSV)
│   ├── clientes.csv              # Cadastro de clientes
│   ├── score_limite.csv          # Faixas de score e limites
│   └── solicitacoes_aumento_limite.csv  # Histórico de solicitações
│
├── scripts/                      # Scripts auxiliares
│   └── setup_data.py             # Criação dos dados de teste
│
├── .env                          # Variáveis de ambiente (não versionado)
├── .env.example                  # Exemplo de variáveis de ambiente
├── .gitignore
├── Pipfile                       # Dependências (pipenv)
├── Pipfile.lock
├── requirements.txt              # Dependências (pip)
├── README.md                     # Documentação do usuário
└── claude.md                     # Este arquivo - Arquitetura
```

---

## Componentes Principais

### 1. Orquestrador (`orchestrator_agents.py`)

**Responsabilidade**: Coordenar a execução dos agentes e gerenciar o estado da conversa.

**Classe Principal**: `OrquestradorBancoAgil`

**Métodos Principais**:
- `__init__(verbose)`: Inicializa os 4 agentes com suas tools e prompts
- `processar(mensagem, estado)`: Processa mensagem com o agente apropriado
- `_atualizar_estado_triagem()`: Detecta autenticação e redireciona
- `_atualizar_estado_credito()`: Detecta solicitações de entrevista ou câmbio
- `_atualizar_estado_entrevista()`: Detecta conclusão de entrevista
- `_atualizar_estado_cambio()`: Detecta mudança para crédito

**Estado Global** (dicionário simples):
```python
{
    "agente_atual": str,          # triagem|credito|entrevista|cambio
    "autenticado": bool,
    "cpf": str | None,
    "nome": str | None,
    "limite": float | None,
    "score": int | None,
    "historico": List[tuple],     # [(role, content), ...]
    "ultima_mensagem": str,
    "tentativas_auth": int,
    "voltou_da_entrevista": bool, # Flag de transição
    "vindo_de_credito": bool      # Flag de transição
}
```

**Lógica de Transição**:
- **Triagem → Crédito**: Palavras-chave relacionadas a crédito/limite
- **Triagem → Câmbio**: Palavras-chave relacionadas a moedas/cotação
- **Crédito → Entrevista**: Cliente aceita fazer entrevista
- **Entrevista → Crédito**: Após atualizar score no sistema
- **Qualquer → Câmbio/Crédito**: Detecção de palavras-chave

---

### 2. Agentes (`agentes.py`)

**Classe Base**: `AgentePadrao`

Todos os agentes compartilham a mesma estrutura simples:
- LLM (OpenAI ChatGPT)
- Lista de Tools (LangChain)
- System Prompt dinâmico
- AgentExecutor (LangChain)

**Método Principal**: `processar(mensagem, historico)`
- Recria o executor com prompt atualizado
- Invoca o LangChain AgentExecutor
- Retorna `{sucesso, resposta, steps}`

**Factory Functions**:
```python
criar_agente_triagem(llm, tools, prompt, verbose)
criar_agente_credito(llm, tools, prompt, verbose)
criar_agente_entrevista(llm, tools, prompt, verbose)
criar_agente_cambio(llm, tools, prompt, verbose)
```

#### 2.1 Agente de Triagem

**Responsabilidades**:
- Recepção e saudação
- Coleta de CPF e data de nascimento (um por vez)
- Autenticação via tool `authenticate_client`
- Controle de tentativas (máximo 3)
- Identificação inicial da necessidade

**Tools Disponíveis**:
- `authenticate_client(cpf, data_nascimento)`
- `get_client_info(cpf)`
- `end_conversation(motivo)`
- `get_help()`

**Transições**:
- Se autenticado + palavra-chave "limite/crédito" → Crédito
- Se autenticado + palavra-chave "cotação/câmbio" → Câmbio

---

#### 2.2 Agente de Crédito

**Responsabilidades**:
- Consultar limite de crédito atual
- Processar solicitações de aumento de limite
- Aprovar/rejeitar baseado em score
- Oferecer entrevista de crédito em caso de rejeição

**Tools Disponíveis**:
- `get_credit_limit(cpf)`
- `request_limit_increase(cpf, novo_limite)`
- `check_max_limit_for_score(score)`
- `end_conversation(motivo)`
- `get_help()`

**Lógica de Aprovação**:
1. Consulta limite máximo permitido para o score do cliente
2. Compara com o valor solicitado
3. Se aprovado: atualiza limite no sistema
4. Se rejeitado: oferece entrevista de crédito

**Transições**:
- Se cliente aceita entrevista → Entrevista
- Se palavra-chave "cotação/câmbio" → Câmbio

---

#### 2.3 Agente de Entrevista

**Responsabilidades**:
- Conduzir entrevista financeira estruturada (5 perguntas)
- Calcular novo score baseado em fórmula ponderada
- Atualizar score no sistema
- Retornar para análise de crédito

**Perguntas da Entrevista**:
1. Renda mensal (float)
2. Tipo de emprego (formal|autônomo|desempregado)
3. Despesas fixas mensais (float)
4. Número de dependentes (int)
5. Dívidas ativas (sim|não)

**Tools Disponíveis**:
- `calculate_new_score(cpf, renda, tipo_emprego, despesas, dependentes, dividas)`
- `update_client_score(cpf, novo_score)`
- `end_conversation(motivo)`

**Fórmula de Score**:
```python
score = (renda_mensal / (despesas_fixas + 1)) * 100 +
        PESO_EMPREGO[tipo] +
        PESO_DEPENDENTES[num] +
        PESO_DIVIDAS[tem_dividas]

Onde:
- PESO_EMPREGO: formal=250, autônomo=180, desempregado=0
- PESO_DEPENDENTES: 0=80, 1=60, 2=40, 3+=20
- PESO_DIVIDAS: sem=-150, com=100
```

**Transições**:
- Após `update_client_score` → Crédito (automático)

---

#### 2.4 Agente de Câmbio

**Responsabilidades**:
- Consultar cotações de moedas em tempo real
- Converter valores entre moedas
- Suportar múltiplas moedas

**Tools Disponíveis**:
- `get_exchange_rate(moeda)` - Ex: "USD", "EUR"
- `get_multiple_exchange_rates(moedas)` - Ex: "USD,EUR,GBP"
- `convert_currency(valor, moeda_origem)`
- `end_conversation(motivo)`

**API Externa**: https://economia.awesomeapi.com.br/json/last

**Transições**:
- Se palavra-chave "limite/crédito" → Crédito

---

### 3. Tools (`src/tools/`)

As tools são funções decoradas com `@tool` do LangChain que podem ser invocadas pelo LLM via function calling.

#### Estrutura de uma Tool

```python
from langchain_core.tools import tool

@tool
def nome_da_tool(parametro: tipo) -> dict:
    """
    Descrição clara para o LLM entender quando usar.

    Args:
        parametro: Descrição do parâmetro

    Returns:
        dict: {"success": bool, "data": Any, "message": str}
    """
    # Lógica
    return {"success": True, "data": resultado, "message": ""}
```

#### Tools por Categoria

**Auth Tools** (`auth_tools.py`):
- `authenticate_client(cpf, data_nascimento)`
- `get_client_info(cpf)`

**Credit Tools** (`credit_tools.py`):
- `get_credit_limit(cpf)`
- `request_limit_increase(cpf, novo_limite)`
- `check_max_limit_for_score(score)`

**Interview Tools** (`interview_tools.py`):
- `calculate_new_score(cpf, renda_mensal, tipo_emprego, despesas_fixas, num_dependentes, tem_dividas)`
- `update_client_score(cpf, novo_score)`

**Exchange Tools** (`exchange_tools.py`):
- `get_exchange_rate(moeda)`
- `get_multiple_exchange_rates(moedas)`
- `convert_currency(valor, moeda_origem)`

**Common Tools** (`common_tools.py`):
- `end_conversation(motivo)`
- `get_help()`

---

### 4. Services (`src/services/`)

#### 4.1 DataService (`data_service.py`)

**Responsabilidade**: Abstrair acesso aos dados em CSV.

**Métodos Principais**:
```python
authenticate_client(cpf, data_nascimento) -> Optional[Cliente]
get_client_by_cpf(cpf) -> Optional[Cliente]
update_client_score(cpf, novo_score) -> bool
update_client_limit(cpf, novo_limite) -> bool
create_limit_request(solicitacao: SolicitacaoAumento) -> bool
get_max_limit_for_score(score) -> float
get_all_score_limits() -> List[ScoreLimite]
```

**Arquivos Gerenciados**:
- `data/clientes.csv`
- `data/solicitacoes_aumento_limite.csv`
- `data/score_limite.csv`

---

#### 4.2 ScoreService (`score_service.py`)

**Responsabilidade**: Cálculo de score e análise de elegibilidade.

**Métodos Principais**:
```python
calcular_score(dados_financeiros: DadosFinanceiros) -> int
analisar_elegibilidade(score_atual, novo_limite_solicitado, limite_atual) -> dict
```

**Lógica de Elegibilidade**:
1. Consulta limite máximo permitido pelo score
2. Verifica se novo limite solicitado está dentro do permitido
3. Retorna aprovação/rejeição com justificativa

---

#### 4.3 ExchangeService (`exchange_service.py`)

**Responsabilidade**: Integração com API de câmbio.

**Métodos Principais**:
```python
get_exchange_rate(moeda: str) -> CotacaoMoeda
get_multiple_rates(moedas: List[str]) -> List[CotacaoMoeda]
convert_currency(valor: float, moeda_origem: str, moeda_destino: str = "BRL") -> float
```

**API Externa**: AwesomeAPI (economia.awesomeapi.com.br)

**Moedas Suportadas**: USD, EUR, GBP, JPY, CHF, CAD, AUD

---

### 5. Models (`src/models/schemas.py`)

Schemas Pydantic para validação de dados:

```python
class Cliente(BaseModel):
    cpf: str                    # Pattern: ^\d{11}$
    nome: str
    data_nascimento: str        # Pattern: DD/MM/AAAA
    limite_credito: float       # >= 0
    score_credito: int          # 0-1000

class SolicitacaoAumento(BaseModel):
    cpf_cliente: str
    data_hora_solicitacao: datetime
    limite_atual: float
    novo_limite_solicitado: float  # > limite_atual
    status_pedido: Literal["pendente", "aprovado", "rejeitado"]

class DadosFinanceiros(BaseModel):
    renda_mensal: float         # > 0
    tipo_emprego: Literal["formal", "autonomo", "desempregado"]
    despesas_fixas: float       # >= 0
    num_dependentes: int        # >= 0
    tem_dividas: bool

class ScoreLimite(BaseModel):
    score_minimo: int           # 0-1000
    score_maximo: int           # 0-1000, > score_minimo
    limite_maximo: float        # >= 0

class CotacaoMoeda(BaseModel):
    moeda: str                  # 3 chars
    taxa: float                 # > 0
    data_hora: datetime
```

---

### 6. Config (`src/config/`)

#### 6.1 Settings (`settings.py`)

**Classe**: `Settings(BaseSettings)` - Pydantic Settings

**Configurações**:
```python
# OpenAI
openai_api_key: str
openai_model: str = "gpt-4o-mini"
openai_temperature: float = 0.4

# Application
max_auth_attempts: int = 3
csv_data_path: str = "./data"

# Exchange API
exchange_api_url: str = "https://economia.awesomeapi.com.br/json/last"

# LangSmith (Opcional)
langchain_tracing_v2: bool = False
langchain_api_key: Optional[str] = None
langchain_project: str = "agente-bancario"
```

**Factory Functions**:
```python
get_llm(temperature, streaming, model) -> ChatOpenAI
get_deterministic_llm() -> ChatOpenAI  # temperature=0
get_creative_llm() -> ChatOpenAI       # temperature=0.9
```

---

#### 6.2 Prompts (`prompts.py`)

Contém os system prompts de cada agente:

**Constantes**:
- `TRIAGEM_SYSTEM_PROMPT`
- `CREDITO_SYSTEM_PROMPT`
- `ENTREVISTA_SYSTEM_PROMPT`
- `CAMBIO_SYSTEM_PROMPT`

**Helper Functions** (formatação dinâmica):
```python
format_triagem_prompt(state: dict) -> str
format_credito_prompt(state: dict) -> str
format_entrevista_prompt(state: dict) -> str
format_cambio_prompt(state: dict) -> str
```

Os prompts são dinâmicos e incluem informações do estado atual:
- Nome do cliente
- CPF
- Limite de crédito
- Score
- Flags de transição (voltou_da_entrevista, vindo_de_credito)

---

### 7. Interface Streamlit (`app/main.py`)

**Responsabilidades**:
- Renderizar UI de chat
- Gerenciar sessão do Streamlit
- Exibir dados do cliente na sidebar
- Processar input do usuário
- Lidar com auto-continuação de conversas

**Session State**:
```python
st.session_state.messages = []        # Histórico de mensagens
st.session_state.estado = {...}       # Estado do orquestrador
st.session_state.authenticated = False
st.session_state.client_data = {}
```

**Fluxo de Processamento**:
1. Usuário envia mensagem
2. Adiciona ao histórico
3. Chama `orquestrador.processar(mensagem, estado)`
4. Atualiza estado
5. Exibe resposta
6. Se mudou agente e não tem pergunta: auto-continua

**Auto-Continuação**:
Quando o agente muda e a resposta não contém "?", o sistema automaticamente envia `[CONTINUACAO]` para o próximo agente processar.

---

## Fluxo de Dados

### Fluxo Completo de uma Mensagem

```
1. USUÁRIO digita mensagem
   │
   ▼
2. STREAMLIT (main.py)
   │  - Adiciona ao session_state.messages
   │  - Exibe mensagem do usuário
   │
   ▼
3. ORQUESTRADOR (orchestrator_agents.py)
   │  - Recebe: mensagem + estado atual
   │  - Identifica agente_atual no estado
   │  - Formata system prompt com dados do estado
   │
   ▼
4. AGENTE ESPECÍFICO (agentes.py)
   │  - AgentePadrao.processar(mensagem, historico)
   │  - Cria ChatPromptTemplate com:
   │    * System prompt dinâmico
   │    * Histórico de mensagens
   │    * Mensagem atual
   │    * Scratchpad para raciocínio
   │  - Invoca AgentExecutor (LangChain)
   │
   ▼
5. LLM (OpenAI GPT-4o-mini)
   │  - Analisa mensagem e histórico
   │  - Decide:
   │    a) Chamar uma tool (function calling)
   │    b) Responder diretamente
   │
   ▼ (se chamou tool)
6. TOOL (src/tools/*.py)
   │  - Executa lógica
   │  - Acessa SERVICE
   │
   ▼
7. SERVICE (src/services/*.py)
   │  - Lógica de negócio
   │  - Acessa DATA
   │
   ▼
8. DATA (data/*.csv)
   │  - Leitura/escrita via pandas
   │
   ▼
9. TOOL retorna resultado
   │  - {"success": bool, "data": Any, "message": str}
   │
   ▼
10. LLM recebe resultado da tool
    │  - Processa resultado
    │  - Gera resposta em linguagem natural
    │
    ▼
11. AGENTE retorna
    │  - {"sucesso": bool, "resposta": str, "steps": list}
    │
    ▼
12. ORQUESTRADOR analisa resultado
    │  - Extrai informações dos intermediate_steps
    │  - Atualiza estado:
    │    * Se autenticou: cpf, nome, limite, score
    │    * Se mudou limite: atualiza limite
    │    * Se atualizou score: atualiza score
    │  - Detecta palavras-chave para transição
    │  - Define próximo agente_atual
    │  - Adiciona ao histórico
    │
    ▼
13. ORQUESTRADOR retorna
    │  - (resposta: str, novo_estado: dict)
    │
    ▼
14. STREAMLIT
    │  - Atualiza session_state.estado
    │  - Atualiza client_data (sidebar)
    │  - Exibe resposta
    │  - Se mudou agente e não tem "?": auto-continua
    │
    ▼
15. USUÁRIO vê resposta
```

---

### Exemplo Concreto: Aumento de Limite Rejeitado → Entrevista

```
USUÁRIO: "Quero aumentar meu limite para R$ 10.000"
│
▼
ORQUESTRADOR: estado["agente_atual"] = "credito"
│
▼
AGENTE CRÉDITO:
│  System Prompt: "CPF: 12345678900, Score: 650, Limite: R$ 5000"
│
▼
LLM: "Vou processar a solicitação"
│  → Chama tool: request_limit_increase("12345678900", 10000)
│
▼
TOOL (credit_tools.py):
│  → Consulta ScoreService.analisar_elegibilidade(650, 10000, 5000)
│  → Score 650 permite até R$ 8.000
│  → Novo limite solicitado: R$ 10.000
│  → REJEITADO
│  → Retorna: {"success": False, "message": "Rejeitado: score insuficiente"}
│
▼
LLM recebe: "Rejeitado: score insuficiente"
│  → Gera resposta: "Infelizmente sua solicitação foi rejeitada.
│                    Gostaria de fazer uma entrevista de crédito?"
│
▼
ORQUESTRADOR:
│  - Analisa resposta: contém "entrevista"
│  - Não atualiza agente ainda (aguarda aceitação do cliente)
│  - Retorna resposta
│
▼
USUÁRIO: "Sim, quero fazer"
│
▼
ORQUESTRADOR: estado["agente_atual"] = "credito"
│  - Detecta palavras-chave: "sim", "quero" + contexto de "entrevista"
│  - ATUALIZA: estado["agente_atual"] = "entrevista"
│  - ATUALIZA: estado["vindo_de_credito"] = True
│
▼
AGENTE ENTREVISTA:
│  System Prompt: "CPF: 12345678900, Score: 650, vindo_de_credito: True"
│  - Como vindo_de_credito=True, vai DIRETO para primeira pergunta
│  → Resposta: "Qual é sua renda mensal em reais?"
│
▼
[Cliente responde 5 perguntas...]
│
▼
AGENTE ENTREVISTA:
│  → Chama: calculate_new_score(cpf, 5000, "formal", 2000, 0, False)
│  → Resultado: 735
│  → Chama: update_client_score(cpf, 735)
│  → Resposta: "Seu score aumentou de 650 para 735!"
│
▼
ORQUESTRADOR:
│  - Detecta tool "update_client_score" nos steps
│  - ATUALIZA: estado["agente_atual"] = "credito"
│  - ATUALIZA: estado["voltou_da_entrevista"] = True
│  - ATUALIZA: estado["score"] = 735
│
▼
STREAMLIT:
│  - Detecta mudança de agente e sem "?"
│  - AUTO-CONTINUA com mensagem "[CONTINUACAO]"
│
▼
AGENTE CRÉDITO:
│  System Prompt: "Score: 735, voltou_da_entrevista: True"
│  → Resposta: "Seu score foi atualizado! Posso ajudar em mais alguma coisa?"
```

---

## Padrões de Design

### 1. Multi-Agent Orchestration

**Padrão**: Múltiplos agentes especializados coordenados por um orquestrador central.

**Implementação**:
- Orquestrador mantém instâncias dos 4 agentes
- Estado global compartilhado (dict simples)
- Transições baseadas em:
  - Palavras-chave
  - Resultado de tools
  - Flags de estado

**Vantagens**:
- Separação de responsabilidades
- Prompts especializados e concisos
- Escalável (fácil adicionar novos agentes)

---

### 2. Function Calling (Tool Use)

**Padrão**: LLM decide dinamicamente quais funções chamar baseado no contexto.

**Implementação**:
- Tools decoradas com `@tool` do LangChain
- LLM recebe lista de tools disponíveis
- LLM invoca tools via JSON
- Tools retornam resultados estruturados

**Vantagens**:
- LLM não precisa "adivinhar" dados
- Integração com sistemas externos
- Resultados determinísticos

---

### 3. Repository Pattern

**Padrão**: Abstrair acesso aos dados através de uma camada de serviço.

**Implementação**:
- `DataService`: Encapsula operações de CSV
- Tools chamam DataService, nunca acessam CSV diretamente
- DataService usa Pydantic models para validação

**Vantagens**:
- Fácil migração para banco de dados real
- Validação centralizada
- Tratamento de erros consistente

---

### 4. Service Layer

**Padrão**: Lógica de negócio separada da infraestrutura.

**Implementação**:
- `ScoreService`: Cálculo de score e elegibilidade
- `ExchangeService`: Integração com API externa
- Tools chamam Services, nunca implementam lógica

**Vantagens**:
- Lógica testável independentemente
- Reutilização entre tools
- Separação de concerns

---

### 5. Stateful Conversation

**Padrão**: Estado mantido entre interações.

**Implementação**:
- Estado global como dict simples
- Atualizado após cada processamento
- Inclui dados do cliente e flags de transição

**Vantagens**:
- Conversação contextual
- Transições suaves entre agentes
- Histórico mantido

---

### 6. Dynamic System Prompts

**Padrão**: System prompts formatados dinamicamente com dados do estado.

**Implementação**:
- Prompts base com placeholders
- `format_*_prompt(state)` injeta dados
- Recriado a cada mensagem

**Vantagens**:
- LLM sempre tem contexto atualizado
- Comportamento adaptativo
- Menos confusão sobre estado

---

## Stack Tecnológica

### Core

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| **Python** | 3.11+ | Linguagem principal |
| **LangChain** | 0.3.27 | Framework para LLMs |
| **LangChain OpenAI** | 0.2.14 | Integração OpenAI |
| **OpenAI** | GPT-4o-mini | Modelo de linguagem |
| **Streamlit** | latest | Interface web |

### Bibliotecas

| Biblioteca | Uso |
|-----------|-----|
| **pandas** | Manipulação de dados CSV |
| **pydantic** | Validação de dados e schemas |
| **pydantic-settings** | Gerenciamento de configurações |
| **python-dotenv** | Variáveis de ambiente |
| **requests** | Chamadas HTTP (API de câmbio) |
| **httpx** | Cliente HTTP assíncrono |

### Ferramentas

| Ferramenta | Uso |
|-----------|-----|
| **pipenv** | Gerenciamento de dependências |
| **git** | Controle de versão |

### APIs Externas

| API | Uso |
|-----|-----|
| **OpenAI API** | Inferência de LLM |
| **AwesomeAPI** | Cotações de moedas em tempo real |
| **LangSmith** | Observabilidade (opcional) |

---

## Decisões de Design

### 1. Por que NÃO usar LangGraph?

**Decisão**: Usar orquestrador simples ao invés de LangGraph.

**Justificativa**:
- LangGraph adiciona complexidade desnecessária
- Graph-based routing é overkill para 4 agentes
- Estado simples (dict) é suficiente
- Transições são determinísticas (palavras-chave + flags)
- Mais fácil de entender e debugar

**Trade-off**:
- ❌ Menos "framework magic"
- ✅ Mais controle sobre fluxo
- ✅ Código mais simples

---

### 2. Transições Transparentes

**Decisão**: Transições entre agentes invisíveis ao usuário.

**Implementação**:
- System prompts instruem agentes a NÃO mencionar "transferência"
- Orquestrador detecta contexto automaticamente
- Auto-continuação quando apropriado

**Exemplo**:
```
❌ MAU: "Vou transferir você para o agente de crédito."
✅ BOM: "Perfeito! Vou verificar suas opções de aumento de limite."
```

**Justificativa**:
- Experiência mais natural
- Cliente sente que fala com UM atendente
- Reduz friç ão na conversa

---

### 3. System Prompts Dinâmicos

**Decisão**: Recriar prompts com dados do estado a cada mensagem.

**Implementação**:
```python
self.credito.system_prompt = format_credito_prompt(estado)
resultado = self.credito.processar(mensagem, historico)
```

**Justificativa**:
- LLM sempre tem dados atualizados
- Evita "alucinações" sobre limite/score
- Permite comportamento condicional (ex: vindo_de_credito)

**Trade-off**:
- ❌ Overhead mínimo de formatação
- ✅ Precisão máxima

---

### 4. CSV para Persistência

**Decisão**: Usar CSV ao invés de banco de dados.

**Justificativa**:
- Projeto de demonstração/POC
- Fácil inspeção manual
- Sem dependências externas
- Simples de configurar

**Limitações**:
- ❌ Não thread-safe
- ❌ Performance limitada
- ❌ Sem transações

**Migração Futura**:
- Substituir `DataService` por implementação com SQLAlchemy
- Manter mesma interface
- Zero mudanças em tools/agentes

---

### 5. Controle de Tentativas de Autenticação

**Decisão**: Máximo 3 tentativas de login.

**Implementação**:
- Estado rastreia `tentativas_auth`
- Agente de triagem monitora falhas
- Após 3 falhas: chama `end_conversation`

**Justificativa**:
- Previne brute force
- Alinhado com práticas bancárias
- Melhora UX (não fica em loop infinito)

---

### 6. Auto-Continuação de Conversas

**Decisão**: Enviar `[CONTINUACAO]` automaticamente após transições.

**Implementação** (main.py):
```python
if mudou_agente and "?" not in resposta:
    resposta_cont, estado_cont = orquestrador.processar(
        "[CONTINUACAO]",
        estado
    )
```

**Justificativa**:
- Evita mensagens vazias do agente
- Garante continuidade natural
- Exemplo: Após entrevista, agente de crédito automaticamente oferece ajuda

**Trade-off**:
- ❌ Uma chamada extra ao LLM
- ✅ UX muito melhor

---

### 7. Flags de Transição

**Decisão**: Usar flags `voltou_da_entrevista` e `vindo_de_credito`.

**Justificativa**:
- **`vindo_de_credito`**: Entrevista pula introdução e vai direto às perguntas
- **`voltou_da_entrevista`**: Crédito cumprimento retorno ("Seu score foi atualizado!")

**Comportamento**:
- Flags são setadas durante transição
- Flags são limpas no próximo processamento
- System prompt as recebe e ajusta comportamento

**Exemplo**:
```python
# Prompt da entrevista
if vindo_de_credito:
    "Qual é sua renda mensal?"  # Direto ao ponto
else:
    "Vou fazer algumas perguntas..."  # Introdução completa
```

---

### 8. Validação com Pydantic

**Decisão**: Usar Pydantic para todos os schemas.

**Justificativa**:
- Validação automática em runtime
- Type hints nativos
- Documentação auto-gerada
- Serialização JSON fácil

**Exemplo**:
```python
class Cliente(BaseModel):
    cpf: str = Field(..., pattern=r"^\d{11}$")
    score_credito: int = Field(..., ge=0, le=1000)
```

**Vantagens**:
- ✅ Erros detectados cedo
- ✅ Código auto-documentado
- ✅ Menos bugs

---

### 9. Formatação de Respostas

**Decisão**: Formatadores específicos para valores monetários e scores.

**Implementação** (`utils/formatters.py`):
```python
formatar_moeda_br(5000.00)  # "R$ 5.000,00"
formatar_score(735)          # "735 (Bom)"
```

**Justificativa**:
- Consistência visual
- Experiência mais profissional
- Reutilização

---

### 10. Temperature do LLM

**Decisão**: Temperature padrão de 0.4.

**Justificativa**:
- Não muito determinístico (0.0) - respostas robóticas
- Não muito criativo (1.0) - respostas imprevisíveis
- 0.4 é equilíbrio: natural mas consistente

**Variações**:
- `get_deterministic_llm()`: 0.0 para extrações
- `get_creative_llm()`: 0.9 para conversação

---

## Conclusão

O **Agente Bancário Inteligente** demonstra uma arquitetura multi-agente simples e eficaz para automação de atendimento bancário usando LLMs.

### Pontos Fortes

✅ **Simplicidade**: Sem abstrações desnecessárias
✅ **Modularidade**: Fácil adicionar novos agentes ou tools
✅ **Transparência**: Transições invisíveis ao usuário
✅ **Escalabilidade**: Fácil migrar de CSV para banco real
✅ **Manutenibilidade**: Código organizado e bem documentado

### Próximos Passos Possíveis

1. **Banco de Dados**: Migrar de CSV para PostgreSQL/MongoDB
2. **Autenticação Real**: Integrar com sistema de auth existente
3. **Mais Agentes**: Investimentos, seguros, cartões
4. **Histórico Persistente**: Salvar conversas completas
5. **Analytics**: Dashboard com métricas de uso
6. **Testes**: Suite de testes unitários e de integração
7. **Deploy**: Containerização (Docker) e deploy em nuvem

---

**Última atualização**: 2025-01-14
**Versão da Arquitetura**: 1.1
