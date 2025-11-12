"""Serviço de acesso a dados (CSV)."""

import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.models.schemas import Cliente, SolicitacaoAumento, ScoreLimite
from src.utils.exceptions import DataAccessError, AuthenticationError
from src.utils.validators import validar_cpf, validar_data_nascimento
from src.config.settings import settings


class DataService:
    """Serviço para manipulação de dados em CSV."""

    def __init__(self, data_path: Optional[Path] = None):
        """
        Inicializa o serviço de dados.

        Args:
            data_path: Caminho para o diretório de dados.
                      Se None, usa settings.data_path
        """
        self.data_path = data_path or settings.data_path
        self.clientes_file = self.data_path / "clientes.csv"
        self.solicitacoes_file = self.data_path / "solicitacoes_aumento_limite.csv"
        self.score_limite_file = self.data_path / "score_limite.csv"

    def _carregar_clientes(self) -> pd.DataFrame:
        """Carrega o DataFrame de clientes."""
        try:
            return pd.read_csv(self.clientes_file, dtype={"cpf": str})
        except FileNotFoundError:
            raise DataAccessError(
                f"Arquivo de clientes nao encontrado",
                filepath=str(self.clientes_file)
            )
        except Exception as e:
            raise DataAccessError(
                f"Erro ao ler arquivo de clientes: {str(e)}",
                filepath=str(self.clientes_file)
            )

    def _salvar_clientes(self, df: pd.DataFrame) -> None:
        """Salva o DataFrame de clientes."""
        try:
            df.to_csv(self.clientes_file, index=False)
        except Exception as e:
            raise DataAccessError(
                f"Erro ao salvar arquivo de clientes: {str(e)}",
                filepath=str(self.clientes_file)
            )

    def authenticate_client(self, cpf: str, data_nascimento: str) -> Optional[Cliente]:
        """
        Autentica um cliente usando CPF e data de nascimento.

        Args:
            cpf: CPF do cliente (11 dígitos)
            data_nascimento: Data de nascimento no formato DD/MM/AAAA

        Returns:
            Cliente se autenticado, None caso contrário

        Raises:
            DataAccessError: Se houver erro ao acessar dados
            AuthenticationError: Se os dados forem inválidos
        """
        # Validar formato
        if not validar_cpf(cpf):
            raise AuthenticationError("CPF invalido")

        if not validar_data_nascimento(data_nascimento):
            raise AuthenticationError("Data de nascimento invalida")

        # Buscar no CSV
        df = self._carregar_clientes()

        cliente_row = df[
            (df["cpf"] == cpf) &
            (df["data_nascimento"] == data_nascimento)
        ]

        if cliente_row.empty:
            return None

        # Converter para modelo Pydantic
        row_dict = cliente_row.iloc[0].to_dict()
        return Cliente(**row_dict)

    def get_client_by_cpf(self, cpf: str) -> Optional[Cliente]:
        """
        Busca cliente apenas por CPF.

        Args:
            cpf: CPF do cliente

        Returns:
            Cliente se encontrado, None caso contrário
        """
        if not validar_cpf(cpf):
            return None

        df = self._carregar_clientes()
        cliente_row = df[df["cpf"] == cpf]

        if cliente_row.empty:
            return None

        row_dict = cliente_row.iloc[0].to_dict()
        return Cliente(**row_dict)

    def update_client_score(self, cpf: str, novo_score: int) -> bool:
        """
        Atualiza o score de crédito de um cliente.

        Args:
            cpf: CPF do cliente
            novo_score: Novo score (0-1000)

        Returns:
            True se atualizado com sucesso

        Raises:
            DataAccessError: Se houver erro ao acessar/salvar dados
        """
        df = self._carregar_clientes()

        # Verificar se cliente existe
        if cpf not in df["cpf"].values:
            raise DataAccessError(f"Cliente com CPF {cpf} nao encontrado")

        # Validar score
        if not 0 <= novo_score <= 1000:
            raise ValueError("Score deve estar entre 0 e 1000")

        # Atualizar
        df.loc[df["cpf"] == cpf, "score_credito"] = novo_score

        # Salvar
        self._salvar_clientes(df)

        return True

    def update_client_limit(self, cpf: str, novo_limite: float) -> bool:
        """
        Atualiza o limite de crédito de um cliente.

        Args:
            cpf: CPF do cliente
            novo_limite: Novo limite de crédito

        Returns:
            True se atualizado com sucesso
        """
        df = self._carregar_clientes()

        if cpf not in df["cpf"].values:
            raise DataAccessError(f"Cliente com CPF {cpf} nao encontrado")

        if novo_limite < 0:
            raise ValueError("Limite deve ser maior ou igual a zero")

        df.loc[df["cpf"] == cpf, "limite_credito"] = novo_limite
        self._salvar_clientes(df)

        return True

    def create_limit_request(self, solicitacao: SolicitacaoAumento) -> bool:
        """
        Cria uma solicitação de aumento de limite.

        Args:
            solicitacao: Dados da solicitação

        Returns:
            True se criada com sucesso
        """
        try:
            # Carregar solicitações existentes
            try:
                df = pd.read_csv(self.solicitacoes_file, dtype={"cpf_cliente": str})
            except FileNotFoundError:
                # Se arquivo não existe, criar um vazio
                df = pd.DataFrame(columns=[
                    "cpf_cliente",
                    "data_hora_solicitacao",
                    "limite_atual",
                    "novo_limite_solicitado",
                    "status_pedido"
                ])

            # Adicionar nova solicitação
            nova_linha = {
                "cpf_cliente": solicitacao.cpf_cliente,
                "data_hora_solicitacao": solicitacao.data_hora_solicitacao.isoformat(),
                "limite_atual": solicitacao.limite_atual,
                "novo_limite_solicitado": solicitacao.novo_limite_solicitado,
                "status_pedido": solicitacao.status_pedido
            }

            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)

            # Salvar
            df.to_csv(self.solicitacoes_file, index=False)

            return True

        except Exception as e:
            raise DataAccessError(
                f"Erro ao criar solicitacao: {str(e)}",
                filepath=str(self.solicitacoes_file)
            )

    def get_max_limit_for_score(self, score: int) -> float:
        """
        Retorna o limite máximo permitido para um score.

        Args:
            score: Score de crédito (0-1000)

        Returns:
            Limite máximo em reais

        Raises:
            DataAccessError: Se houver erro ao acessar dados
        """
        try:
            df = pd.read_csv(self.score_limite_file)

            # Encontrar a faixa correspondente
            faixa = df[
                (df["score_minimo"] <= score) &
                (df["score_maximo"] >= score)
            ]

            if faixa.empty:
                raise ValueError(f"Nenhuma faixa encontrada para score {score}")

            return float(faixa.iloc[0]["limite_maximo"])

        except FileNotFoundError:
            raise DataAccessError(
                "Arquivo score_limite.csv nao encontrado",
                filepath=str(self.score_limite_file)
            )
        except Exception as e:
            raise DataAccessError(
                f"Erro ao consultar score_limite: {str(e)}",
                filepath=str(self.score_limite_file)
            )

    def get_all_score_limits(self) -> list[ScoreLimite]:
        """
        Retorna todas as faixas de score e limite.

        Returns:
            Lista de ScoreLimite
        """
        try:
            df = pd.read_csv(self.score_limite_file)
            return [ScoreLimite(**row) for row in df.to_dict(orient="records")]
        except Exception as e:
            raise DataAccessError(
                f"Erro ao carregar faixas de score: {str(e)}",
                filepath=str(self.score_limite_file)
            )
