import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from baseclass import BaseClass
from models import Categoria, Produto


@pytest.fixture(scope='session')
def engine():
    """
    Cria uma engine de banco de dados SQLite em memória para a sessão de testes.
    Retorna a engine para que possa ser usada em outros fixtures.
    """
    return create_engine('sqlite:///:memory:')


@pytest.fixture(scope='session')
def tables(engine):
    """
    Cria todas as tabelas do modelo no banco de dados de teste antes da execução
    dos testes e as remove ao final.
    """
    BaseClass.metadata.create_all(engine)
    yield
    BaseClass.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """
    Fornece uma sessão de banco de dados transacional para cada teste.

    Cria uma conexão, inicia uma transação e fornece a sessão. Ao final do
    teste, faz o rollback da transação para isolar os testes.
    """
    connection = engine.connect()
    # Inicia uma transação que pode ser revertida
    transaction = connection.begin()
    # Cria uma sessão vinculada à conexão transacional
    session = Session(bind=connection)

    yield session

    # Fecha a sessão e reverte a transação para limpar os dados do teste
    session.close()
    transaction.rollback()
    connection.close()