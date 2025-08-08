from abc import ABC, abstractmethod
from typing import Any, cast, Generic, Optional, TypeVar

from sqlalchemy import ColumnElement, Engine, func, select
from sqlalchemy.orm import Session

# Definição do tipo genérico T
T = TypeVar('T')


class IRepository(Generic[T], ABC):
    """
    Interface genérica para repositório de dados em Python.

    Esta interface define operações CRUD básicas e funcionalidades de consulta
    para qualquer tipo de entidade. Implementa o padrão Repository com suporte
    a generics através do módulo typing do Python.

    Type Parameters:
        T: O tipo da entidade que será gerenciada pelo repositório
    """

    @abstractmethod
    def get_all(self, load_options: Optional[list] = None) -> list[T]:
        """
        Recupera todas as entidades do repositório.

        Args:
            load_options (Optional[list]): Lista de opções de carregamento
               (ex: [joinedload(Model.relationship)]).
        Returns:
            list[T]: Uma lista contendo entidades do tipo T
        """
        pass

    @abstractmethod
    def get(self, predicate: Optional[ColumnElement[bool]] = None,
            load_options: Optional[list] = None) -> list[T]:
        """
        Recupera entidades baseadas em um predicado opcional.

        Args:
            predicate: Função que define o critério de filtragem.
                       Se None, retorna todas as entidades.
            load_options (Optional[list]): Lista de opções de carregamento
               (ex: [joinedload(Model.relationship)]).

        Returns:
            list[T]: Uma lista contendo entidades do tipo T que satisfazem o predicado
        """
        pass

    @abstractmethod
    def get_first(self, predicate: Optional[ColumnElement[bool]] = None,
                  load_options: Optional[list] = None) -> Optional[T]:
        """
        Recupera a primeira entidade que satisfaz o predicado.

        Args:
            predicate: Função que define o critério de busca.
                       Se None, retorna a primeira entidade disponível.
            load_options (Optional[list]): Lista de opções de carregamento
               (ex: [joinedload(Model.relationship)]).

        Returns:
            Optional[T]: A primeira entidade encontrada ou None se não encontrada
        """
        pass

    @abstractmethod
    def get_by_id(self, *key: Any) -> Optional[T]:
        """
        Recupera uma entidade pela sua chave primária.

        Args:
            *key: Valores da chave primária (suporta chaves compostas)

        Returns:
            Optional[T]: A entidade encontrada ou None se não encontrada
        """
        pass

    @abstractmethod
    def add(self, entity: T) -> None:
        """
        Adiciona uma nova entidade ao repositório.

        Args:
            entity: A entidade a ser adicionada
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        """
        Atualiza uma entidade existente no repositório.

        Args:
            entity: A entidade com os dados atualizados
        """
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        """
        Remove uma entidade do repositório.

        Args:
            entity: A entidade a ser removida
        """
        pass

    @abstractmethod
    def count(self, predicate: Optional[ColumnElement[bool]]) -> int:
        """
        Retorna o número total de entidades no repositório que satisfazem o predicado.

        Args:
            predicate: Função que define o critério de busca.
                       Se None, retorna todos

        Returns:
            int: Quantidade de entidades
        """
        pass


class ISQLAlchemyRepository(IRepository[T], ABC):
    """
    Implementação IRepository para SQLAlchemy.

    Esta classe fornece uma base para repositórios que utilizam SQLAlchemy como ORM.

    Type  Parameters:
        T: O tipo da entidade que será gerenciada pelo repositório

    Attributes:
        _engine (Engine): Instância do SQLAlchemy Engine para conexão com o banco de dados
        _model (Optional[Type[T]]): Classe do modelo ORM que este repositório gerencia
    """

    def __init__(self, engine: Engine = None, model: Optional[T] = None):
        """
        Inicializa o repositório com um engine SQLAlchemy e um modelo opcional.

        Args:
            engine (Engine, opcional): Instância do SQLAlchemy Engine para conexão com o banco de
            dados.
            model (Optional[T], opcional): Classe do modelo ORM que este repositório irá gerenciar.
        """
        self._engine = engine
        self._model = model

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @property
    def get_engine(self):
        return self._engine

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    def get_all(self, load_options: Optional[list] = None) -> list[T]:
        """
        Recupera todas as entidades do repositório.

        Args:
            load_options (Optional[list]): Lista de opções de carregamento (ex: [joinedload(
            Model.relationship)]).

        Returns:
             list[T]: Uma lista contendo entidades do tipo T
        """
        with Session(self._engine) as session:
            stmt = select(self._model)
            # Aplica as opções de carregamento se elas forem fornecidas
            if load_options:
                stmt = stmt.options(*load_options)
            result = session.execute(stmt).scalars().all()
            return cast(list[T], result)

    def get(self, predicate: Optional[ColumnElement[bool]] = None,
            load_options: Optional[list] = None) -> list[T]:
        """
        Recupera entidades do repositório com base em um predicado opcional.

        Args:
            predicate (Optional[ColumnElement[bool]]): Expressão booleana SQLAlchemy usada para
            filtrar os resultados.
                Se None, retorna todas as entidades.
            load_options (Optional[list]): Lista de opções de carregamento (ex: [joinedload(
            Model.relationship)]).

        Returns:
             list[T]: Uma lista contendo entidades do tipo T que satisfazem o predicado.
        """
        stmt = select(self._model)
        if predicate is not None:
            stmt = stmt.where(predicate)
            # Aplica as opções de carregamento se elas forem fornecidas
        if load_options:
            stmt = stmt.options(*load_options)

        with Session(self._engine) as session:
            # .scalars() retorna um iterador que produz instâncias do modelo (T)
            result = session.execute(stmt).scalars().all()
            return cast(list[T], result)

    def get_first(self, predicate: Optional[ColumnElement[bool]] = None,
                  load_options: Optional[list] = None) -> Optional[T]:
        """
        Recupera a primeira entidade que satisfaz o predicado.

        Args:
            predicate (Optional[ColumnElement[bool]]): Expressão booleana SQLAlchemy usada para
            filtrar os resultados.
                Se None, retorna a primeira entidade disponível.
            load_options (Optional[list]): Lista de opções de carregamento (ex: [joinedload(
            Model.relationship)]).

        Returns:
            Optional[T]: A primeira entidade encontrada ou None se não encontrada.
        """
        stmt = select(self._model)
        if predicate is not None:
            stmt = stmt.where(predicate)
        if load_options:
            stmt = stmt.options(*load_options)

        with Session(self._engine) as session:
            # .scalars().first() é a forma idiomática e eficiente de buscar
            # um único objeto ORM ou None se não for encontrado.
            result = session.execute(stmt).scalars().first()
            return result

    def get_by_id(self, *key: Any, load_options: Optional[list] = None) -> Optional[T]:
        """
        Busca uma única instância do modelo pela sua chave primária.

        Wrapper para `session.get()`, a forma mais eficiente de buscar por
         chave primária no SQLAlchemy.

        Args:
            *key (Any): Valores da chave primária. Pode ser um valor único para chave simples
                        ou múltiplos valores para chave composta.
            load_options (Optional[list]): Lista de opções de carregamento (ex: [joinedload(
            Model.relationship)]).

        Returns:
            Optional[T]: Instância do modelo encontrada ou None se não encontrada.
        """
        if not key:
            return None  # Retorna None se nenhuma chave for fornecida

        with Session(self._engine) as session:
            # `session.get()` espera a classe do modelo e a identidade.
            # A identidade pode ser um valor único ou uma tupla para chaves compostas.
            # O `*key` nos dá uma tupla. Precisamos tratar os dois casos.

            if len(key) == 1:
                # Chave primária simples (ex: id)
                identity = key[0]
            else:
                # Chave primária composta (ex: order_id, product_id)
                identity = key

            result = session.get(self._model, identity, options=load_options)
            return result

    def add(self, entity: T) -> None:
        """
        Adiciona uma nova entidade ao repositório e realiza o commit da transação.

        Args:
            entity (T): A entidade a ser adicionada ao banco de dados.
        """
        with Session(self._engine) as session:
            session.add(entity)
            session.commit()

    def update(self, entity: T) -> None:
        """
        Atualiza uma entidade existente no repositório e realiza o commit da transação.

        Args:
            entity (T): A entidade com os dados atualizados a ser persistida no banco de dados.
        """
        with Session(self._engine) as session:
            session.merge(entity)
            session.commit()

    def delete(self, entity: T) -> None:
        """
        Remove uma entidade do repositório e realiza o commit da transação.

        Args:
            entity (T): A entidade a ser removida do banco de dados.
        """
        with Session(self._engine) as session:
            session.delete(entity)
            session.commit()

    def count(self, predicate: Optional[ColumnElement[bool]] = None) -> int:
        """
        Retorna o número total de entidades no repositório que satisfazem o predicado.

        Args:
            predicate (Optional[ColumnElement[bool]]): Expressão booleana SQLAlchemy usada para
            filtrar os resultados.
                Se None, retorna a contagem de todas as entidades.

        Returns:
            int: Quantidade de entidades que satisfazem o predicado.
        """
        with Session(self._engine) as session:
            stmt = select(func.count()).select_from(self._model)
            if predicate is not None:
                stmt = stmt.where(predicate)
            result = session.execute(stmt).scalar_one()
            return result
