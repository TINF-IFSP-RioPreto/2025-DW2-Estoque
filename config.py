import configparser
from dataclasses import dataclass


@dataclass
class AppConfig:
    url_bd: str


def read_config() -> AppConfig:
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
