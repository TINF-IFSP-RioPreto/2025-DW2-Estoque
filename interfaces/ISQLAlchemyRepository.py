"""
Módulo que define a implementação base de um repositório SQLAlchemy.

Fornece a classe `ISQLAlchemyRepository` que implementa a interface `IRepository`
usando SQLAlchemy para operações de banco de dados.
"""
from abc import ABC
from typing import Any, cast, Optional, Type

from sqlalchemy import ColumnElement, Engine, func, select, Select
from sqlalchemy.orm import Session

from interfaces.IRepositorio import IRepository, T


class ISQLAlchemyRepository(IRepository[T], ABC):
    """
    Implementação IRepository para SQLAlchemy.

    Esta classe fornece uma base para repositórios que utilizam SQLAlchemy como ORM.

    Type Parameters:
        T: O tipo da entidade que será gerenciada pelo repositório.

    Attributes:
        _engine (Engine): Instância do SQLAlchemy Engine para conexão com o banco de dados.
        _model (Type[T]): Classe do modelo ORM que este repositório gerencia.
    """

    def __init__(self,
                 engine: Engine,
                 model: Type[T]):
        """
        Inicializa o repositório com um engine SQLAlchemy e um modelo.

        Args:
            engine (Engine): Instância do SQLAlchemy Engine para conexão com o banco de dados.
            model (Type[T]): Classe do modelo ORM que este repositório irá gerenciar.
        """
        self._engine = engine
        self._model = model

    @property
    def engine(self) -> Engine:
        """A instância do engine do SQLAlchemy associada ao repositório."""
        return self._engine

    @property
    def model(self) -> Type[T]:
        """A classe do modelo ORM gerenciada pelo repositório."""
        return self._model

    def get_all(self,
                load_options: Optional[list] = None,
                page: int = None,
                page_size: int = None) -> list[T]:
        """
        Recupera todas as entidades do repositório com paginação opcional.

        Args:
            load_options (Optional[list]): Opções para carregamento adiantado
                                           de relacionamentos.
            page (int, opcional): O número da página (começando em 1).
            page_size (int, opcional): O número de itens por página.

        Returns:
            list[T]: Uma lista de todas as entidades.
        """
        with Session(self._engine) as session:
            stmt = select(self._model)
            stmt = self._build_statement(stmt, load_options=load_options, page=page,
                                         page_size=page_size)
            result = session.execute(stmt).scalars().all()
            return cast(list[T], result)

    def get(self,
            predicate: Optional[ColumnElement[bool]] = None,
            load_options: Optional[list] = None,
            page: int = None,
            page_size: int = None) -> list[T]:
        """
        Recupera entidades que correspondem a um predicado com paginação opcional.

        Args:
            predicate (Optional[ColumnElement[bool]]): Um filtro para a consulta.
            load_options (Optional[list]): Opções para carregamento adiantado
                                           de relacionamentos.
            page (int, opcional): O número da página (começando em 1).
            page_size (int, opcional): O número de itens por página.

        Returns:
            list[T]: Uma lista de entidades que correspondem ao predicado.
        """
        stmt = select(self._model)
        if predicate is not None:
            stmt = stmt.where(predicate)
        stmt = self._build_statement(stmt, load_options=load_options, page=page,
                                     page_size=page_size)
        with Session(self._engine) as session:
            result = session.execute(stmt).scalars().all()
            return cast(list[T], result)

    def get_first(self,
                  predicate: Optional[ColumnElement[bool]] = None,
                  load_options: Optional[list] = None) -> Optional[T]:
        """
        Recupera a primeira entidade que corresponde a um predicado.

        Args:
            predicate (Optional[ColumnElement[bool]]): Um filtro para a consulta.
            load_options (Optional[list]): Opções para carregamento adiantado
                                           de relacionamentos.

        Returns:
            Optional[T]: A primeira entidade encontrada, ou None.
        """
        stmt = select(self._model)
        if predicate is not None:
            stmt = stmt.where(predicate)
        stmt = self._build_statement(stmt, load_options=load_options)

        with Session(self._engine) as session:
            result = session.execute(stmt).scalars().first()
            return result

    def get_by_id(self,
                  *key: Any,
                  load_options: Optional[list] = None) -> Optional[T]:
        """
        Recupera uma entidade pela sua chave primária.

        Args:
            *key: O valor(es) da chave primária. Suporta chaves compostas.
            load_options (Optional[list]): Opções para carregamento adiantado
                                           de relacionamentos.

        Returns:
            Optional[T]: A entidade encontrada, ou None.
        """
        if not key:
            return None

        with Session(self._engine) as session:
            identity = key[0] if len(key) == 1 else key
            result = session.get(self._model, identity, options=load_options)
            return result

    def add(self, entity: T) -> None:
        """
        Adiciona uma nova entidade ao banco de dados.

        Args:
            entity (T): A entidade a ser adicionada.
        """
        with Session(self._engine) as session:
            session.add(entity)
            session.commit()

    def bulk_add(self, entities: list[T]) -> None:
        """
        Adiciona múltiplas entidades ao banco de dados em uma única transação.

        Args:
            entities (list[T]): Uma lista de entidades a serem adicionadas.
        """
        with Session(self._engine) as session:
            session.bulk_save_objects(entities)
            session.commit()

    def update(self, entity: T) -> None:
        """
        Atualiza uma entidade existente no banco de dados.

        Args:
            entity (T): A entidade a ser atualizada.
        """
        with Session(self._engine) as session:
            session.merge(entity)
            session.commit()

    def delete(self, entity: T) -> None:
        """
        Remove uma entidade do banco de dados.

        Args:
            entity (T): A entidade a ser removida.
        """
        with Session(self._engine) as session:
            session.delete(session.merge(entity))
            session.commit()

    def count(self, predicate: Optional[ColumnElement[bool]] = None) -> int:
        """
        Conta o número de entidades que correspondem a um predicado.

        Args:
            predicate (Optional[ColumnElement[bool]]): Um filtro para a contagem.
                                                      Se None, conta todas as entidades.

        Returns:
            int: O número de entidades.
        """
        with Session(self._engine) as session:
            stmt = select(func.count()).select_from(self._model)
            if predicate is not None:
                stmt = stmt.where(predicate)
            result = session.execute(stmt).scalar_one()
            return result

    @staticmethod
    def _build_statement(stmt: Select,
                         load_options: Optional[list] = None,
                         page: int = None,
                         page_size: int = None) -> Select:
        """
        Constrói uma declaração SQLAlchemy com opções de carregamento e paginação.

        Args:
            stmt (Select): Objeto select do SQLAlchemy.
            load_options (Optional[list]): Opções de carregamento (ex: joinedload).
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            Select: Objeto select modificado com as opções fornecidas.

        Raises:
            ValueError: Se `page` ou `page_size` forem menores que 1.
        """
        if load_options:
            stmt = stmt.options(*load_options)
        if page is not None and page_size is not None:
            if page < 1 or page_size < 1:
                raise ValueError("page e page_size devem ser maiores que 1.")
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size)
        return stmt