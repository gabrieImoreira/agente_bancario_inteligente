"""Script para criar arquivos CSV de exemplo com dados mock."""

import pandas as pd
from pathlib import Path


def create_clientes_csv(data_dir: Path):
    """Cria arquivo clientes.csv com dados de exemplo."""

    clientes_data = {
        "cpf": [
            "12345678900",
            "98765432100",
            "11122233344",
            "55566677788",
            "99988877766"
        ],
        "nome": [
            "João Silva",
            "Maria Santos",
            "Pedro Oliveira",
            "Ana Costa",
            "Carlos Souza"
        ],
        "data_nascimento": [
            "15/03/1985",
            "22/07/1990",
            "10/12/1978",
            "05/09/1995",
            "18/01/1982"
        ],
        "limite_credito": [
            5000.00,
            8000.00,
            3000.00,
            15000.00,
            2000.00
        ],
        "score_credito": [
            650,
            820,
            450,
            900,
            320
        ]
    }

    df = pd.DataFrame(clientes_data)
    filepath = data_dir / "clientes.csv"
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"[OK] Criado: {filepath}")
    print(f"     {len(df)} clientes cadastrados")


def create_score_limite_csv(data_dir: Path):
    """Cria arquivo score_limite.csv com regras de score."""

    score_limite_data = {
        "score_minimo": [0, 300, 500, 700, 850],
        "score_maximo": [299, 499, 699, 849, 1000],
        "limite_maximo": [1000.00, 3000.00, 8000.00, 15000.00, 50000.00]
    }

    df = pd.DataFrame(score_limite_data)
    filepath = data_dir / "score_limite.csv"
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"[OK] Criado: {filepath}")
    print(f"     {len(df)} faixas de score definidas")


def create_solicitacoes_csv(data_dir: Path):
    """Cria arquivo solicitacoes_aumento_limite.csv (vazio inicialmente)."""

    # Criar apenas com headers
    solicitacoes_data = {
        "cpf_cliente": [],
        "data_hora_solicitacao": [],
        "limite_atual": [],
        "novo_limite_solicitado": [],
        "status_pedido": []
    }

    df = pd.DataFrame(solicitacoes_data)
    filepath = data_dir / "solicitacoes_aumento_limite.csv"
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"[OK] Criado: {filepath}")
    print(f"     Arquivo vazio criado (sera preenchido durante uso)")


def setup_data():
    """Cria todos os arquivos CSV necessários."""

    print("Banco Agil - Setup de Dados\n")
    print("=" * 50)

    # Criar diretório data se não existir
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data"
    data_dir.mkdir(exist_ok=True)

    print(f"Diretorio de dados: {data_dir}\n")

    # Criar CSVs
    create_clientes_csv(data_dir)
    create_score_limite_csv(data_dir)
    create_solicitacoes_csv(data_dir)

    print("\n" + "=" * 50)
    print("Setup concluido com sucesso!")
    print("\nDados de teste disponiveis:")
    print("   - CPF: 12345678900 | Data: 15/03/1985 | Score: 650")
    print("   - CPF: 98765432100 | Data: 22/07/1990 | Score: 820")
    print("   - CPF: 11122233344 | Data: 10/12/1978 | Score: 450")
    print("   - CPF: 55566677788 | Data: 05/09/1995 | Score: 900")
    print("   - CPF: 99988877766 | Data: 18/01/1982 | Score: 320")


if __name__ == "__main__":
    setup_data()
