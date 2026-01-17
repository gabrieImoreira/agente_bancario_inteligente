# Guia de Uso do Langfuse - Agente Bancário Inteligente

> **IMPORTANTE:** O Langfuse é uma ferramenta **100% opcional**. O sistema funciona perfeitamente sem ele. Use apenas se desejar monitorar e analisar as interações com o LLM.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Como Ativar (Cloud)](#como-ativar-cloud)
- [Self-Hosting com Docker](#self-hosting-com-docker)
- [Como Desativar](#como-desativar)
- [Arquitetura da Integração](#arquitetura-da-integração)
- [Hierarquia de Observabilidade](#hierarquia-de-observabilidade)
- [Dashboard e Métricas](#dashboard-e-métricas)
- [Privacidade e Segurança](#privacidade-e-segurança)
- [Casos de Uso](#casos-de-uso)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

O **Langfuse** é uma plataforma de observabilidade para aplicações LLM. A integração com este projeto permite:

- ✅ Rastrear cada conversa do usuário (trace completo)
- ✅ Ver qual agente processou cada mensagem
- ✅ Monitorar todas as chamadas de tools (autenticação, crédito, entrevista, câmbio)
- ✅ Acompanhar custos e tokens utilizados
- ✅ Analisar latência por componente (orquestrador, agentes, tools, LLM)
- ✅ Debugar problemas com visibilidade total do fluxo
- Avaliar qualidade das respostas do LLM

---

## Como Ativar (Cloud)

A forma mais simples de usar o Langfuse é através do serviço cloud gratuito.

### Passo 1: Obter Chaves do Langfuse (Gratuito)

1. Acesse https://cloud.langfuse.com
2. Crie uma conta gratuita
3. Crie um novo projeto
4. Copie as chaves:
   - `Public Key` (pk-lf-...)
   - `Secret Key` (sk-lf-...)

### Passo 2: Configurar o `.env`

Edite seu arquivo `.env` e adicione:

```bash
# ============================================
# Langfuse (OPCIONAL - Observabilidade)
# ============================================
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Passo 3: Reiniciar a Aplicação

```bash
pipenv run streamlit run app/main.py
```

Pronto! Os traces começarão a aparecer no dashboard do Langfuse.

---

## Self-Hosting com Docker

Se preferir rodar o Langfuse localmente ou em seu próprio servidor, você pode usar Docker Compose.

### Pré-requisitos

- Git instalado
- Docker e Docker Compose instalados
  - Windows/Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Linux: `sudo apt install docker.io docker-compose`

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/langfuse/langfuse.git
cd langfuse
```

### Passo 2: Configurar Credenciais

Edite o arquivo `docker-compose.yml` e altere todas as linhas marcadas com `# CHANGEME`:

```yaml
# Principais variáveis para alterar:
NEXTAUTH_SECRET: "seu-secret-seguro-aqui"        # CHANGEME
SALT: "seu-salt-seguro-aqui"                      # CHANGEME
ENCRYPTION_KEY: "sua-chave-32-caracteres-aqui"   # CHANGEME (deve ter exatamente 32 caracteres)

# Credenciais do banco de dados
POSTGRES_PASSWORD: "sua-senha-postgres"           # CHANGEME
CLICKHOUSE_PASSWORD: "sua-senha-clickhouse"       # CHANGEME

# Credenciais do MinIO (S3)
MINIO_ROOT_USER: "minio-admin"                    # CHANGEME
MINIO_ROOT_PASSWORD: "sua-senha-minio"            # CHANGEME
```

### Passo 3: Iniciar os Containers

```bash
# Subir todos os serviços
docker compose up -d

# Verificar se está rodando
docker compose ps

# Ver logs (útil para debug)
docker compose logs -f
```

Aguarde 2-3 minutos para todos os serviços iniciarem.

### Passo 4: Acessar o Langfuse Local

1. Abra http://localhost:3000 no navegador
2. Crie uma conta (local)
3. Crie um novo projeto
4. Copie as chaves geradas (`Public Key` e `Secret Key`)

### Passo 5: Configurar o Projeto para Usar Langfuse Local

No arquivo `.env` do **Agente Bancário Inteligente**:

```bash
# ============================================
# Langfuse Self-Hosted (Docker)
# ============================================
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx    # Chave do seu projeto local
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx    # Chave do seu projeto local
LANGFUSE_HOST=http://localhost:3000   # Apontando para o Docker local
```

### Comandos Úteis do Docker

```bash
# Parar todos os containers
docker compose down

# Parar e remover volumes (APAGA TODOS OS DADOS)
docker compose down -v

# Reiniciar um serviço específico
docker compose restart langfuse-web

# Ver uso de recursos
docker stats

# Limpar containers parados e imagens não utilizadas
docker system prune
```

### Arquitetura do Self-Hosting

O docker-compose sobe os seguintes serviços:

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `langfuse-web` | 3000 | Interface web e APIs |
| `langfuse-worker` | - | Processamento assíncrono |
| `postgres` | 5432 (interno) | Banco de dados principal |
| `clickhouse` | 8123 (interno) | Banco de analytics |
| `redis` | 6379 (interno) | Cache |
| `minio` | 9000/9090 | Armazenamento S3 (console: 9090) |

> **Nota:** Apenas as portas 3000 (web) e 9090 (MinIO console) são expostas externamente por segurança.

### Atualizar o Langfuse

```bash
cd langfuse
git pull
docker compose pull
docker compose up -d
```

---

## Como Desativar

O Langfuse pode ser desativado de **duas formas**:

### Opção 1: Via variável de ambiente (Recomendado)

No arquivo `.env`, defina:

```bash
LANGFUSE_ENABLED=false
```

### Opção 2: Remover as variáveis

Simplesmente não defina as variáveis `LANGFUSE_*` no `.env`. O sistema detecta automaticamente e funciona normalmente sem observabilidade.

### Verificar Status

Para verificar se o Langfuse está ativo, você pode verificar no código:

```python
# src/config/settings.py
from src.config.settings import settings
print(f"Langfuse habilitado: {settings.langfuse_enabled}")
```

---

## Arquitetura da Integração

### Arquivos Envolvidos

| Arquivo | Responsabilidade |
|---------|------------------|
| `src/config/settings.py` | Configurações (`langfuse_enabled`, chaves, host) |
| `src/utils/observability.py` | Utilitários (decorators, sanitização, cliente) |
| `src/orchestrator_agents.py` | Instrumentação do orquestrador |
| `src/tools/*.py` | Instrumentação das tools |
| `app/main.py` | Criação de traces no Streamlit |

### Fluxo de Dados

```
Usuário envia mensagem
       │
       ▼
┌──────────────────┐
│  Streamlit       │ ─── Cria trace (se Langfuse habilitado)
│  (app/main.py)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Orquestrador    │ ─── Atualiza span com contexto
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Agente          │ ─── Registra execução do agente
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Tool            │ ─── Registra chamada de tool (dados sanitizados)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  LLM (OpenAI)    │ ─── Callback automático (tokens, custo)
└──────────────────┘
```

---

## Hierarquia de Observabilidade

O Langfuse rastreia tudo em uma estrutura hierárquica:

```
TRACE: streamlit_user_message (uma mensagem do usuário)
│
├─ SPAN: orchestrator_process (orquestrador decide qual agente usar)
│  │
│  ├─ SPAN: agent_triagem (agente de triagem processa)
│  │  │
│  │  ├─ GENERATION: LLM call (chamada ao ChatGPT - automática)
│  │  ├─ SPAN: tool_authenticate_client (tool de autenticação)
│  │  └─ GENERATION: LLM response (resposta do ChatGPT - automática)
│  │
│  ├─ SPAN: agent_credito (agente de crédito processa)
│  │  │
│  │  ├─ GENERATION: LLM call
│  │  ├─ SPAN: tool_get_credit_limit
│  │  ├─ SPAN: tool_request_limit_increase
│  │  └─ GENERATION: LLM response
│  │
│  └─ ... (outros agentes)
│
└─ Output: Resposta final do assistente
```

---

## Dashboard e Métricas

### **1. Traces (Conversas)**
Cada mensagem do usuário aparece como um **trace** individual com:
- **User ID**: CPF mascarado (últimos 4 dígitos) ou "anonymous"
- **Session ID**: UUID único da sessão Streamlit
- **Input**: Mensagem do usuário
- **Output**: Resposta do assistente
- **Metadata**:
  - `authenticated`: Se o usuário está autenticado
  - `message_count`: Número de mensagens na conversa
  - `agente_atual`: Qual agente está ativo
  - `agente_usado`: Qual agente processou a mensagem
  - `agente_final`: Qual agente ficou ativo após processamento
  - `auto_continuou`: Se houve auto-continuação entre agentes

### **2. Spans (Componentes)**

#### **Orquestrador (orchestrator_process)**
- `agente_atual`: Qual agente está processando
- `autenticado`: Status de autenticação
- `historico_size`: Tamanho do histórico de mensagens
- `agente_proximo`: Próximo agente
- `mudou_agente`: Se houve transição de agente

#### **Agentes (agent_triagem, agent_credito, agent_entrevista, agent_cambio)**
- `prompt_size`: Tamanho do prompt usado
- `score_cliente`: Score do cliente (para crédito)
- `vindo_de_credito`: Flag de transição (para entrevista)
- `sucesso`: Se o agente executou com sucesso
- `limite_atualizado`: Se houve mudança no limite
- `score_atualizado`: Se houve mudança no score

#### **Tools (tool_*)**
Cada tool rastreada mostra:
- **Input**: Parâmetros **sanitizados** (CPF mascarado, data nascimento oculta)
- **Output**: Resultado da tool (também sanitizado)
- **Metadata**:
  - `tool_type`: "langchain_tool"
  - `success`: Se a tool executou com sucesso
  - `args_sanitized`: Argumentos mascarados

### **3. Generations (Chamadas LLM)**
Rastreadas **automaticamente** via callback handler:
- **Model**: gpt-4o-mini
- **Prompt**: System prompt + mensagem
- **Completion**: Resposta do LLM
- **Tokens**: Input tokens, output tokens, total
- **Custo**: Calculado automaticamente
- **Latência**: Tempo de resposta
- **Temperature**: 0.4 (ou configurado)

---

## Privacidade e Segurança

O sistema **sanitiza dados sensíveis** antes de enviar ao Langfuse:

### Dados Mascarados

| Dado | Exemplo Original | Enviado ao Langfuse |
|------|------------------|---------------------|
| CPF | `12345678900` | `***.***.***00` |
| Data de Nascimento | `15/03/1985` | `**/**/****` |

### Dados Mantidos (para análise)

- Nome do cliente
- Score de crédito
- Limite de crédito

O código de sanitização está em `src/utils/observability.py` (funções `sanitize_cpf` e `sanitize_data`).

---

## Métricas Disponíveis

### Custos
- Custo por conversa
- Custo por agente
- Custo total do projeto
- Breakdown por modelo (gpt-4o-mini)

### Performance
- Latência total da conversa
- Latência por componente (orquestrador, agentes, tools, LLM)
- Tokens utilizados (input/output)

### Qualidade
- Taxa de sucesso de autenticações
- Taxa de aprovação de crédito
- Taxa de conclusão de entrevistas
- Erros e exceções

### Uso
- Mensagens por sessão
- Agentes mais utilizados
- Tools mais chamadas
- Transições entre agentes

---

## Casos de Uso

### 1. Debug de Problemas

**Cenário:** Cliente reclama que não conseguiu aumentar limite

**Como investigar:**
1. Busque pelo CPF (mascarado) no Langfuse
2. Veja o trace completo da conversa
3. Identifique qual tool falhou (`tool_request_limit_increase`)
4. Verifique os parâmetros enviados
5. Veja o erro retornado

### 2. Otimização de Custos

**Cenário:** Custos estão altos

**Como analisar:**
1. Vá em "Usage" no Langfuse
2. Filtre por agente
3. Identifique qual agente consome mais tokens
4. Otimize o prompt desse agente
5. Compare before/after

### 3. Melhoria de Qualidade

**Cenário:** Respostas não estão boas

**Como melhorar:**
1. Filtre traces com baixa avaliação
2. Veja os prompts usados
3. Identifique padrões de falha
4. Ajuste prompts em `src/config/prompts.py`
5. Monitore melhoria

### 4. Análise de Fluxo

**Cenário:** Entender jornada do usuário

**Como visualizar:**
1. Abra um trace no Langfuse
2. Veja a hierarquia visual de spans
3. Identifique transições entre agentes
4. Analise se o fluxo está correto
5. Otimize lógica de roteamento se necessário

---

## Troubleshooting

### Problema: Langfuse não está rastreando

**Soluções:**
1. Verifique se `LANGFUSE_ENABLED=true` no `.env`
2. Verifique se as chaves estão corretas
3. Verifique logs do console para erros de importação
4. Teste a conexão manualmente:

```python
from langfuse import Langfuse
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com"
)
print(langfuse.trace(name="test"))
```

### Problema: Dados sensíveis aparecem no Langfuse

**Solução:**
Verifique a função `sanitize_data()` em `src/utils/observability.py` e adicione campos adicionais para sanitizar.

### Problema: Muitos avisos no console

Avisos como `AVISO: Erro ao criar span...` são normais quando Langfuse está desabilitado ou há problemas de rede. O sistema continua funcionando normalmente.

---

## Recursos Adicionais

- **Langfuse Docs**: https://langfuse.com/docs
- **Langfuse Python SDK**: https://langfuse.com/docs/sdk/python
- **LangChain Integration**: https://langfuse.com/docs/integrations/langchain
- **Dashboard Tour**: https://langfuse.com/docs/dashboard

---

## Próximos Passos

Agora que o Langfuse está configurado, você pode:

1. **Explorar o Dashboard** - Faça alguns testes no Streamlit e veja os traces em tempo real

2. **Configurar Alertas** - Configure alertas no Langfuse para erros e custos

3. **Avaliar Respostas** - Use o sistema de scores do Langfuse para marcar respostas

4. **Criar Dashboards** - Use a API do Langfuse para visualizações customizadas

5. **Versionamento de Prompts** - Use o Prompt Management do Langfuse para A/B testing

---

**Última atualização:** 2025-01-17
