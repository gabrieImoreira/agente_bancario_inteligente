"""Script de teste para verificar se o Langfuse está funcionando."""

from src.utils.observability import LangfuseManager
from src.config.settings import settings

print("\n=== TESTE DE CONEXAO LANGFUSE ===\n")

print("Configuracao:")
print(f"  - Habilitado: {settings.langfuse_enabled}")
print(f"  - Host: {settings.langfuse_host}")
print(f"  - Public Key: {'Configurado' if settings.langfuse_public_key else 'NAO configurado'}")
print(f"  - Secret Key: {'Configurado' if settings.langfuse_secret_key else 'NAO configurado'}")

print("\nTestando conexao...")

try:
    langfuse = LangfuseManager.get_instance()

    if langfuse is None:
        print("ERRO: Langfuse desabilitado ou falhou ao inicializar")
    else:
        print("OK: Langfuse inicializado com sucesso!")

        print("\nTestando criacao de trace com decorator @observe...")
        from langfuse import observe

        @observe()
        def test_function():
            return {"status": "success", "message": "Teste de observabilidade"}

        result = test_function()
        print(f"OK: Funcao instrumentada executada: {result}")

        print("\nTestando context manager start_as_current_span...")
        with langfuse.start_as_current_span(name="test_span") as span:
            span.update(metadata={"test": True})
            print("OK: Span criado usando context manager!")

        # Flush para garantir que os dados sejam enviados
        print("\nEnviando dados para o servidor...")
        langfuse.flush()
        print("OK: Dados enviados com sucesso!")

        print("\n" + "="*50)
        print("RESULTADO: Langfuse esta FUNCIONANDO corretamente!")
        print("="*50)
        print("\nAcesse o dashboard em:", settings.langfuse_host)

except Exception as e:
    print(f"\nERRO: Falha ao conectar com Langfuse:")
    print(f"  {type(e).__name__}: {e}")
    print("\nVerifique:")
    print("  1. Se as chaves estao corretas no .env")
    print("  2. Se o host esta acessivel (para self-hosted)")
    print("  3. Se ha conexao com internet (para cloud)")
