"""Teste da nova estrutura de observabilidade: 1 trace por sessão, 1 span por mensagem."""

from src.utils.observability import SessionTrace, LangfuseManager
from src.config.settings import settings
import time

print("\n" + "="*70)
print("TESTE: Nova Estrutura de Observabilidade")
print("="*70)

langfuse = LangfuseManager.get_instance()

if not langfuse:
    print("\nERRO: Langfuse não habilitado")
    exit(1)

print("\nConfiguracao:")
print(f"  - Host: {settings.langfuse_host}")
print(f"  - Session agrupando mensagens: SIM")

# Simular uma sessão com múltiplas mensagens
session_id = "test_session_12345"
print(f"\n{'='*70}")
print(f"Simulando SESSAO: {session_id}")
print(f"{'='*70}\n")

# Criar gerenciador de trace da sessão
session_trace = SessionTrace.create(
    session_id=session_id,
    user_id="anonymous"
)

# Mensagem 1
print("1. Primeira mensagem (cria o TRACE da sessão)...")
with session_trace.message_span(
    user_message="Olá, gostaria de me autenticar",
    metadata={
        "authenticated": False,
        "agente_atual": "triagem"
    }
) as msg1_span:

    # Simular processamento
    time.sleep(0.1)

    msg1_span.update(
        output={"response": "Olá! Vou precisar do seu CPF."},
        metadata={
            "agente_usado": "triagem",
            "agente_final": "triagem"
        }
    )
    print("   OK: Trace da mensagem 1 criado")

# Mensagem 2 (outro trace com mesmo session_id)
print("\n2. Segunda mensagem (outro TRACE com mesmo session_id)...")

# Simular autenticação
session_trace.user_id = "***.***.***-34"

with session_trace.message_span(
    user_message="12345678900",
    metadata={
        "authenticated": False,
        "agente_atual": "triagem"
    }
) as msg2_span:

    time.sleep(0.1)

    msg2_span.update(
        output={"response": "Perfeito! Agora sua data de nascimento."},
        metadata={
            "agente_usado": "triagem",
            "agente_final": "triagem"
        }
    )
    print("   OK: Trace da mensagem 2 criado")

# Mensagem 3
print("\n3. Terceira mensagem (outro TRACE com mesmo session_id)...")
with session_trace.message_span(
    user_message="15/03/1985",
    metadata={
        "authenticated": False,
        "agente_atual": "triagem"
    }
) as msg3_span:

    time.sleep(0.1)

    msg3_span.update(
        output={"response": "Autenticado com sucesso! Olá João Silva!"},
        metadata={
            "agente_usado": "triagem",
            "agente_final": "credito",
            "authenticated": True
        }
    )
    print("   OK: Trace da mensagem 3 criado")

# Mensagem 4
print("\n4. Quarta mensagem (mais um TRACE)...")
with session_trace.message_span(
    user_message="Quero aumentar meu limite",
    metadata={
        "authenticated": True,
        "agente_atual": "credito"
    }
) as msg4_span:

    time.sleep(0.1)

    msg4_span.update(
        output={"response": "Seu limite atual é R$ 5.000. Qual valor deseja?"},
        metadata={
            "agente_usado": "credito",
            "agente_final": "credito"
        }
    )
    print("   OK: Trace da mensagem 4 criado")

# Mensagem 5
print("\n5. Quinta mensagem (ultimo TRACE)...")
with session_trace.message_span(
    user_message="R$ 8.000",
    metadata={
        "authenticated": True,
        "agente_atual": "credito"
    }
) as msg5_span:

    time.sleep(0.1)

    msg5_span.update(
        output={"response": "Solicitação aprovada! Seu limite é agora R$ 8.000."},
        metadata={
            "agente_usado": "credito",
            "agente_final": "credito",
            "limite_atualizado": True
        }
    )
    print("   OK: Trace da mensagem 5 criado")

print("\n" + "="*70)
print("Enviando dados para Langfuse...")
langfuse.flush()
print("OK: Dados enviados!")

print("\n" + "="*70)
print("RESULTADO ESPERADO NO DASHBOARD:")
print("="*70)
print(f"""
Voce deve ver NO LANGFUSE:

5 TRACES (uma para cada mensagem):
   - message_1: "Ola, gostaria de me autenticar"
   - message_2: "12345678900"
   - message_3: "15/03/1985"
   - message_4: "Quero aumentar meu limite"
   - message_5: "R$ 8.000"

Todos compartilham:
   - Session ID: {session_id}
   - User ID: ***.***.***-34 (apos autenticacao)

VANTAGENS desta estrutura:
   1. Filtrar por session_id mostra todas as mensagens da conversa
   2. Cada mensagem tem seus proprios spans (orchestrator, agent, tools)
   3. message_number permite ordenacao cronologica
   4. Metricas por mensagem E por sessao

COMO BUSCAR NO DASHBOARD:
   - Filtre por session_id: "{session_id}"
   - Ou por user_id: "***.***.***-34"
   - Ordene por timestamp ou message_number
""")

print("="*70)
print(f"Acesse: {settings.langfuse_host}")
print("="*70)
