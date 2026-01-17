# Agente Bancário Inteligente

Sistema de atendimento bancário automatizado usando IA (LLM) e arquitetura multi-agente. O projeto simula um assistente virtual capaz de realizar autenticação, consultas de crédito, análise de score e cotações de moedas.

## Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Como Testar](#como-testar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Decisões de Design](#decisões-de-design)
- [Observabilidade (Langfuse)](#observabilidade-langfuse)

---

## Visão Geral

O **Agente Bancário Inteligente** é um assistente virtual que usa modelos de linguagem (LLMs) para automatizar operações bancárias. O sistema implementa uma arquitetura multi-agente onde diferentes agentes especializados lidam com tarefas específicas:

- **Triagem:** Autenticação de clientes
- **Crédito:** Operações de limite de crédito
- **Entrevista:** Atualização de score baseada em dados financeiros
- **Câmbio:** Cotações de moedas em tempo real

A transição entre agentes é transparente para o usuário, criando uma experiência de conversa natural e contínua.

---

## Funcionalidades

### 1. Autenticação de Clientes
- Validação por CPF + data de nascimento
- Controle de tentativas de login
- Acesso seguro aos dados do cliente

### 2. Consulta de Limite de Crédito
- Verificação de limite atual
- Consulta de score de crédito
- Interface amigável com formatação monetária

### 3. Solicitação de Aumento de Limite
- Análise automática baseada em score
- Aprovação/rejeição instantânea
- Registro de solicitações para auditoria

### 4. Entrevista de Crédito
- Coleta de dados financeiros (5 perguntas)
- Recálculo de score baseado em fórmula ponderada
- Recomendações para melhoria do score

### 5. Cotações de Moedas
- Consulta de cotações em tempo real (API externa)
- Conversão de valores
- Suporte a múltiplas moedas (USD, EUR, GBP, etc)

---

## Arquitetura

### Visão Geral

```
┌─────────────────┐
│   STREAMLIT     │  Interface web interativa
│    (UI)         │
└────────┬────────┘
         │
┌────────▼────────────────────────────────────────┐
│          ORQUESTRADOR                           │  Gerencia estado e transições
│                                                 │
│  ┌───────┐  ┌────────┐  ┌──────────┐  ┌──────┐│
│  │Triagem│→ │Crédito │→ │Entrevista│  │Câmbio││  4 agentes especializados
│  └───────┘  └────────┘  └──────────┘  └──────┘│
└────────┬────────────────────────────────────────┘
         │
┌────────▼────────┐
│   LANGCHAIN     │  Framework de IA
│   AGENT         │  Function calling
│   EXECUTOR      │
└────────┬────────┘
         │
┌────────▼────────┐
│   OPENAI GPT    │  Modelo de linguagem
│   (gpt-4o-mini) │
└─────────────────┘
         │
┌────────▼────────┐
│     TOOLS       │  Funções que o LLM pode chamar
│  - Auth         │
│  - Credit       │
│  - Score        │
│  - Exchange     │
└────────┬────────┘
         │
┌────────▼────────┐
│   SERVICES      │  Lógica de negócio
│  - DataService  │
│  - ScoreService │
└────────┬────────┘
         │
┌────────▼────────┐
│   CSV FILES     │  Persistência de dados
│  - clientes.csv │
│  - score_limite │
│  - solicitacoes │
└─────────────────┘
```

### Fluxo de Conversação

1. **Usuário** envia mensagem via Streamlit
2. **Orquestrador** identifica qual agente deve processar
3. **Agente** (LangChain) interpreta mensagem e decide:
   - Chamar uma tool (function calling)
   - Responder diretamente
4. **Tool** acessa serviços e dados
5. **Resposta** é formatada pelo LLM e enviada ao usuário
6. **Estado** é atualizado (autenticação, score, etc)
7. **Transição** para outro agente se necessário

### Padrões Utilizados

- **Multi-Agent Orchestration:** Múltiplos agentes especializados coordenados por orquestrador central
- **Function Calling:** LLM invoca funções Python dinamicamente
- **Stateful Conversation:** Estado da conversa mantido entre interações
- **Repository Pattern:** DataService abstrai acesso aos dados
- **Service Layer:** Lógica de negócio separada da infraestrutura

---

## Tecnologias

### Core
- **Python 3.11+**
- **LangChain** - Framework para aplicações com LLMs
- **OpenAI GPT-4o-mini** - Modelo de linguagem
- **Streamlit** - Interface web interativa

### Bibliotecas
- **pandas** - Manipulação de dados (CSV)
- **pydantic** - Validação de dados e schemas
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **requests** - Chamadas HTTP (API de câmbio)

### Ferramentas
- **pipenv** - Gerenciamento de dependências
- **black** - Formatação de código (opcional)
- **pytest** - Testes (estrutura preparada)

---

## Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip e pipenv instalados
- Chave de API da OpenAI

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd agente_bancario_inteligente
```

2. **Instale as dependências:**
```bash
pipenv install
```

3. **Configure as variáveis de ambiente:**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env e adicione sua chave da OpenAI
# OPENAI_API_KEY=sk-...
```

4. **Crie os dados de teste:**
```bash
pipenv run python scripts/setup_data.py
```

5. **Execute a aplicação:**
```bash
pipenv run streamlit run app/main.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

---

## Como Usar

### 1. Autenticação

Ao iniciar a conversa, o sistema solicitará:
- **CPF** (11 dígitos)
- **Data de nascimento** (DD/MM/AAAA)

Após autenticação bem-sucedida, seus dados aparecerão na sidebar:
- Nome do cliente
- CPF (parcialmente mascarado)
- Limite de crédito
- Score de crédito

### 2. Consultar Limite

```
Você: "Qual é meu limite de crédito?"
Agente: "Seu limite de crédito atual é de R$ 5.000,00. Gostaria de solicitar um aumento?"
```

### 3. Solicitar Aumento de Limite

```
Você: "Sim, quero aumentar para R$ 10.000"
Agente: [Analisa seu score]
        "Infelizmente sua solicitação foi rejeitada devido ao score insuficiente.
         Gostaria de fazer uma entrevista de crédito para atualizar seu score?"
```

### 4. Fazer Entrevista de Crédito

```
Você: "Sim, quero fazer a entrevista"
Agente: "Ótimo! Vou fazer 5 perguntas sobre sua situação financeira.
         Qual é a sua renda mensal em reais?"

[Responda as 5 perguntas:]
1. Renda mensal
2. Tipo de emprego (formal/autônomo/desempregado)
3. Despesas fixas mensais
4. Número de dependentes
5. Possui dívidas ativas? (sim/não)

Agente: "Seu score aumentou de 650 para 735 (+85 pontos)!
         Seu score foi atualizado. Posso ajudar em mais alguma coisa?"
```

### 5. Consultar Cotações

```
Você: "Qual a cotação do dólar?"
Agente: "A cotação atual do dólar é: 1 USD = R$ 5,25"

Você: "Quanto é 100 dólares em reais?"
Agente: "100 dólares equivalem a R$ 525,00 na cotação atual."
```

---

## Como Testar

### Dados de Teste Disponíveis

O sistema vem com 3 clientes pré-cadastrados:

| CPF | Data de Nascimento | Score | Limite Atual |
|-----|-------------------|-------|--------------|
| 12345678900 | 15/03/1985 | 650 | R$ 5.000 |
| 98765432100 | 22/07/1990 | 820 | R$ 8.000 |
| 99988877766 | 18/01/1982 | 320 | R$ 1.000 |

### Cenários de Teste

#### Cenário 1: Aumento Aprovado
1. Autentique com CPF `98765432100` (score alto: 820)
2. Solicite aumento para R$ 12.000
3. **Resultado:** ✅ Aprovado (score 820 permite até R$ 15.000)

#### Cenário 2: Aumento Rejeitado → Entrevista
1. Autentique com CPF `12345678900` (score médio: 650)
2. Solicite aumento para R$ 10.000
3. **Resultado:** ❌ Rejeitado (score 650 permite até R$ 8.000)
4. Aceite fazer entrevista de crédito
5. Informe dados financeiros positivos:
   - Renda: R$ 8.000
   - Emprego: formal
   - Despesas: R$ 2.000
   - Dependentes: 0
   - Dívidas: não
6. **Resultado:** Score aumenta para ~900
7. Solicite aumento novamente → ✅ Aprovado

#### Cenário 3: Score Baixo
1. Autentique com CPF `99988877766` (score baixo: 320)
2. Solicite aumento para R$ 5.000
3. **Resultado:** ❌ Rejeitado (score 320 permite apenas R$ 3.000)
4. Faça entrevista de crédito com dados negativos:
   - Renda: R$ 2.000
   - Emprego: desempregado
   - Despesas: R$ 1.500
   - Dependentes: 3
   - Dívidas: sim
5. **Resultado:** Score diminui ou se mantém baixo

#### Cenário 4: Cotações
1. Autentique normalmente
2. Pergunte: "Qual a cotação do dólar e do euro?"
3. Pergunte: "Quanto é 500 libras em reais?"
4. **Resultado:** Respostas com valores em tempo real

### Verificar Dados Persistidos

Após usar o sistema, verifique os arquivos CSV:

```bash
# Ver solicitações registradas
cat data/solicitacoes_aumento_limite.csv

# Ver scores atualizados
cat data/clientes.csv
```

---

## Estrutura do Projeto

```
agente_bancario_inteligente/
│
├── app/                          # Interface Streamlit
│   ├── main.py                   # Aplicação principal
│   └── components/               # Componentes reutilizáveis (futuro)
│
├── src/                          # Código fonte principal
│   ├── agentes.py                 # Definição dos agentes (LangChain)
│   ├── orchestrator_agents.py    # Orquestrador multi-agente
│   │
│   ├── tools/                    # Tools para function calling
│   │   ├── auth_tools.py         # Autenticação
│   │   ├── credit_tools.py       # Operações de crédito
│   │   ├── interview_tools.py    # Cálculo de score
│   │   ├── exchange_tools.py     # Cotações de moedas
│   │   └── common_tools.py       # Ferramentas comuns
│   │
│   ├── services/                 # Lógica de negócio
│   │   ├── data_service.py       # Acesso aos dados (CSV)
│   │   ├── score_service.py      # Cálculo de score
│   │   └── exchange_service.py   # API de câmbio
│   │
│   ├── config/                   # Configurações
│   │   ├── settings.py           # Variáveis de ambiente
│   │   └── prompts.py            # System prompts dos agentes
│   │
│   ├── models/                   # Schemas Pydantic
│   │   └── schemas.py            # Cliente, SolicitacaoAumento, etc
│   │
│   └── utils/                    # Utilitários
│       ├── validators.py         # Validação de CPF, data, etc
│       ├── formatters.py         # Formatação de moeda, data
│       └── exceptions.py         # Exceções customizadas
│
├── data/                         # Dados (CSV)
│   ├── clientes.csv              # Cadastro de clientes
│   ├── score_limite.csv          # Faixas de score e limites
│   └── solicitacoes_aumento_limite.csv  # Histórico de solicitações
│
├── scripts/                      # Scripts auxiliares
│   └── setup_data.py             # Criação dos dados de teste
│
├── .env.example                  # Exemplo de variáveis de ambiente
├── Pipfile                       # Dependências (pipenv)
└── README.md                # Guia rápido de início
```

---

### Fórmula de Score de Crédito

**Fórmula ponderada:**
```
score = (renda_mensal / (despesas_fixas + 1)) * 100 +
        PESO_EMPREGO[tipo] +
        PESO_DEPENDENTES[num] +
        PESO_DIVIDAS[tem_dividas]
```

**Pesos ajustados:**
- Renda/Despesas: peso 100 (capacidade de pagamento)
- Emprego formal: +250, autônomo: +180, desempregado: 0
- Dependentes: 0 deps = +80, 1 dep = +60, 2 deps = +40, 3+ deps = +20
- Dívidas: sem dívidas = +100, com dívidas = -150

**Faixas de score:**
| Score | Classificação | Limite Máximo |
|-------|--------------|---------------|
| 0-299 | Muito Baixo | R$ 1.000 |
| 300-499 | Baixo | R$ 3.000 |
| 500-699 | Regular | R$ 8.000 |
| 700-849 | Bom | R$ 15.000 |
| 850-1000 | Excelente | R$ 50.000 |

**Justificativa:**
- Peso maior na relação renda/despesas (indica capacidade real)
- Emprego formal valorizado (menor risco)
- Penalização significativa para dívidas ativas

---

## Observabilidade (Langfuse)

O projeto possui integração **opcional** com o [Langfuse](https://langfuse.com) para monitoramento e observabilidade das interações com o LLM.

> **IMPORTANTE:** O Langfuse é completamente **opcional**. O sistema funciona normalmente sem ele.

### Funcionalidades do Langfuse

Quando habilitado, você pode:
- Rastrear cada conversa (traces completos)
- Monitorar chamadas de tools e agentes
- Acompanhar custos e tokens utilizados
- Analisar latência por componente
- Debugar problemas com visibilidade total do fluxo

### Como Ativar o Langfuse

#### Opção 1: Langfuse Cloud (Mais Simples)

**1. Obtenha suas chaves gratuitas:**
- Acesse https://cloud.langfuse.com
- Crie uma conta (gratuita)
- Copie as chaves `Public Key` e `Secret Key`

**2. Configure o arquivo `.env`:**

```bash
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

**3. Reinicie a aplicação**

#### Opção 2: Self-Hosting com Docker

Se preferir rodar localmente:

```bash
# Clonar e iniciar
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d

# Acesse http://localhost:3000
```

Configure o `.env` apontando para localhost:

```bash
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx  # Chave do projeto local
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=http://localhost:3000
```

Veja instruções detalhadas em [LANGFUSE_GUIDE.md](./LANGFUSE_GUIDE.md#self-hosting-com-docker)

### Como Desativar o Langfuse

Para desativar, basta definir no `.env`:

```bash
LANGFUSE_ENABLED=false
```

Ou simplesmente não definir as variáveis `LANGFUSE_*` - o sistema detecta automaticamente e funciona sem observabilidade.

### Onde Está a Configuração no Código

| Arquivo | Descrição |
|---------|-----------|
| `src/config/settings.py` | Configurações (`langfuse_enabled`, chaves) |
| `src/utils/observability.py` | Utilitários de observabilidade |
| `.env` | Variáveis de ambiente (ativação) |

### Documentação Completa

Para mais detalhes sobre a integração Langfuse (hierarquia de traces, métricas disponíveis, troubleshooting), consulte:

**[LANGFUSE_GUIDE.md](./LANGFUSE_GUIDE.md)**

---

**Desenvolvido com:**
- 🤖 LangChain & OpenAI
- 🐍 Python 3.11
- 🎨 Streamlit
- 📊 Pandas

**Última atualização:** 2025-11-12
