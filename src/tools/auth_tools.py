"""Tools de autenticação para o Agente de Triagem."""

from langchain.tools import tool
from typing import Dict, Any, Annotated

from src.services.data_service import DataService
from src.utils.exceptions import AuthenticationError, DataAccessError
from src.utils.validators import limpar_cpf
from src.utils.observability import observe_tool


@tool
def authenticate_client(cpf: str, data_nascimento: str) -> Dict[str, Any]:
    """
    Autentica um cliente usando CPF e data de nascimento.

    Use esta ferramenta para validar as credenciais do cliente contra
    a base de dados. O cliente precisa fornecer CPF (11 digitos) e
    data de nascimento no formato DD/MM/AAAA.

    Args:
        cpf: CPF do cliente (pode conter formatacao, sera limpo automaticamente)
        data_nascimento: Data de nascimento no formato DD/MM/AAAA

    Returns:
        Dict com:
        - success (bool): Se a autenticacao foi bem-sucedida
        - message (str): Mensagem descritiva
        - data (dict): Dados do cliente se autenticado (cpf, nome, limite, score)

    Example:
        >>> authenticate_client("123.456.789-00", "15/03/1985")
        {
            "success": True,
            "message": "Cliente autenticado com sucesso!",
            "data": {
                "cpf": "12345678900",
                "nome": "Joao Silva",
                "limite_credito": 5000.00,
                "score_credito": 650
            }
        }
    """
    try:
        # Limpar CPF (remover formatação)
        cpf_limpo = limpar_cpf(cpf)

        # Tentar autenticar
        data_service = DataService()
        cliente = data_service.authenticate_client(cpf_limpo, data_nascimento)

        if cliente is None:
            return {
                "success": False,
                "message": "CPF ou data de nascimento incorretos.",
                "data": None
            }

        # Sucesso!
        return {
            "success": True,
            "message": f"Cliente autenticado com sucesso! Bem-vindo(a), {cliente.nome}.",
            "data": {
                "cpf": cliente.cpf,
                "nome": cliente.nome,
                "limite_credito": cliente.limite_credito,
                "score_credito": cliente.score_credito
            }
        }

    except AuthenticationError as e:
        return {
            "success": False,
            "message": f"Erro de autenticacao: {e.message}",
            "data": None
        }

    except DataAccessError as e:
        return {
            "success": False,
            "message": "Erro ao acessar base de dados. Tente novamente mais tarde.",
            "data": None
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro inesperado: {str(e)}",
            "data": None
        }


@tool
def get_client_info(cpf: str) -> Dict[str, Any]:
    """
    Busca informacoes de um cliente ja autenticado.

    Use esta ferramenta para obter dados atualizados de um cliente
    que ja foi autenticado previamente.

    Args:
        cpf: CPF do cliente

    Returns:
        Dict com dados do cliente ou erro
    """
    try:
        cpf_limpo = limpar_cpf(cpf)

        data_service = DataService()
        cliente = data_service.get_client_by_cpf(cpf_limpo)

        if cliente is None:
            return {
                "success": False,
                "message": "Cliente nao encontrado.",
                "data": None
            }

        return {
            "success": True,
            "message": "Dados do cliente obtidos com sucesso.",
            "data": {
                "cpf": cliente.cpf,
                "nome": cliente.nome,
                "limite_credito": cliente.limite_credito,
                "score_credito": cliente.score_credito
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao buscar dados: {str(e)}",
            "data": None
        }
