"""Teste de integração completa do Langfuse com o sistema de agentes."""

from src.utils.observability import ObservabilityContext, LangfuseManager
from src.config.settings import settings

print("\n=== TESTE DE INTEGRACAO LANGFUSE ===\n")

langfuse = LangfuseManager.get_instance()

if not langfuse:
    print("ERRO: Langfuse não está habilitado ou falhou ao inicializar")
    exit(1)

print("Simulando uma interacao do usuario com o agente...")
print("-" * 50)

# Simular um trace completo (uma mensagem do usuario)
with ObservabilityContext(
    name="user_message",
    trace=True,
    user_id="test_user_1234",
    session_id="session_abc123",
    metadata={
        "authenticated": False,
        "agente_atual": "triagem"
    },
    input_data={"message": "Olá, gostaria de autenticar"}
) as trace_ctx:

    print("1. Trace criado (representa uma mensagem do usuario)")

    # Simular orquestrador processando
    with ObservabilityContext(
        name="orchestrator_process",
        metadata={
            "agente_atual": "triagem",
            "autenticado": False
        }
    ) as orch_ctx:

        print("2. Orquestrador processando...")

        # Simular agente de triagem processando
        with ObservabilityContext(
            name="agent_triagem",
            metadata={
                "prompt_size": 1500
            }
        ) as agent_ctx:

            print("3. Agente de triagem executando...")

            # Simular chamada de tool
            with ObservabilityContext(
                name="tool_authenticate_client",
                metadata={
                    "tool_type": "langchain_tool"
                },
                input_data={
                    "cpf": "***.***.***-34",
                    "data_nascimento": "**/**/****"
                }
            ) as tool_ctx:

                print("4. Tool de autenticacao executando...")

                # Simular resultado da tool
                tool_result = {
                    "success": True,
                    "data": {
                        "nome": "João Silva",
                        "limite": 5000.00,
                        "score": 650
                    }
                }

                tool_ctx.update(
                    output=tool_result,
                    metadata={"success": True}
                )

                print("5. Tool executada com sucesso")

            # Atualizar agente com resultado
            agent_ctx.update(
                output={"resposta": "Olá João Silva! Como posso ajudá-lo?"},
                metadata={"sucesso": True}
            )

            print("6. Agente finalizou processamento")

        # Atualizar orquestrador
        orch_ctx.update(
            metadata={
                "agente_proximo": "credito",
                "mudou_agente": False
            }
        )

        print("7. Orquestrador finalizou")

    # Atualizar trace com output final
    trace_ctx.update(
        output={"resposta": "Olá João Silva! Como posso ajudá-lo?"},
        metadata={
            "agente_final": "triagem",
            "auto_continuou": False
        }
    )

    print("8. Trace finalizado")

print("\n" + "-" * 50)
print("Enviando dados para o servidor Langfuse...")
langfuse.flush()
print("OK: Dados enviados!")

print("\n" + "=" * 50)
print("SUCESSO: Integracao completa funcionando!")
print("=" * 50)
print(f"\nAcesse o dashboard: {settings.langfuse_host}")
print("Voce deve ver:")
print("  - 1 trace (user_message)")
print("  - 3 spans (orchestrator, agent, tool)")
print("  - Metadados em cada nivel")
print("\nDica: Procure por user_id='test_user_1234'")
