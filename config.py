"""
Módulo de configuração para a aplicação.

Este módulo é responsável por ler as configurações da aplicação,
como a URL do banco de dados, a partir de um arquivo de configuração.
"""
import configparser
from dataclasses import dataclass


@dataclass
class AppConfig:
    """
    DataClass para armazenar as configurações da aplicação.

    Attributes:
        url_bd (str): A URL de conexão com o banco de dados SQLAlchemy.
    """
    url_bd: str


def read_config() -> AppConfig:
    """
    Lê o arquivo de configuração e retorna um objeto AppConfig.

    A função lê a URL do banco de dados da seção [alembic] do arquivo
    `alembic.ini`.

    Returns:
        AppConfig: Um objeto com as configurações da aplicação.

    Raises:
        FileNotFoundError: Se o arquivo 'alembic.ini' não for encontrado.
        KeyError: Se a seção 'alembic' ou a chave 'sqlalchemy.url' não
                  forem encontradas no arquivo de configuração.
    """
    app_config = configparser.ConfigParser()
    try:
        files_read = app_config.read("alembic.ini")
        if not files_read:
            raise FileNotFoundError("Arquivo de configuração não encontrado.")
        try:
            sqlalchemy_url = app_config.get("alembic", "sqlalchemy.url")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise KeyError(f"Falta a seção/chave no arquivo de configuração: {e}")
        return AppConfig(url_bd=sqlalchemy_url)
    except Exception as e:
        print(f"Erro lendo o arquivo de configuração: {e}")
        raise