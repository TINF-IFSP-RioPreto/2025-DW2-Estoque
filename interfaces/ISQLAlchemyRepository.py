from abc import ABC
from typing import Any, cast, Optional

from sqlalchemy import ColumnElement, Engine, func, select, Select
from sqlalchemy.orm import Session

from interfaces.IRepositorio import IRepository, T


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

    def __init__(self,
                 engine: Engine = None,
                 model: T = None):
        """
        Inicializa o repositório com um engine SQLAlchemy e um modelo.

        Args:
            engine (Engine): Instância do SQLAlchemy Engine para conexão com o banco de dados.
            model (T): Classe do modelo ORM que este repositório irá gerenciar.
        """
        self._engine = engine
        self._model = model

    @property  # Propriedade para acessar o engine do SQLAlchemy associado ao repositório.
    def engine(self):
        return self._engine

    @property  # Propriedade que retorna a classe do modelo ORM gerenciado pelo repositório.
    def model(self):
        return self._model

    def get_all(self,
                load_options: Optional[list] = None,
                page: int = None,
                page_size: int = None) -> list[T]:
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
        if not key:
            return None  # Retorna None se nenhuma chave for fornecida

        with Session(self._engine) as session:
            if len(key) == 1:
                # Chave primária simples (ex: id)
                identity = key[0]
            else:
                # Chave primária composta (ex: order_id, product_id)
                identity = key

            result = session.get(self._model, identity, options=load_options)
            return result

    def add(self, entity: T) -> None:
        with Session(self._engine) as session:
            session.add(entity)
            session.commit()

    def update(self, entity: T) -> None:
        with Session(self._engine) as session:
            session.merge(entity)
            session.commit()

    def delete(self, entity: T) -> None:
        with Session(self._engine) as session:
            session.delete(entity)
            session.commit()

    def count(self, predicate: Optional[ColumnElement[bool]] = None) -> int:
        with Session(self._engine) as session:
            stmt = select(func.count()).select_from(self._model)
            if predicate is not None:
                stmt = stmt.where(predicate)
            result = session.execute(stmt).scalar_one()
            return result

    @staticmethod
    def _build_statement(stmt: select,
                         load_options: Optional[list] = None,
                         page: int = None,
                         page_size: int = None) -> Select:
        """
        Constrói uma declaração SQLAlchemy com opções de carregamento e paginação.

        Args:
            stmt (select): Objeto select do SQLAlchemy.
            load_options (Optional[list]): Opções de carregamento (ex: joinedload).
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            Select: Objeto select modificado com as opções fornecidas.
        """
        if load_options:
            stmt = stmt.options(*load_options)
        if page and page_size:
            if page < 1 or page_size < 1:
                raise ValueError("page e page_size devem ser maiores que 1.")
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size)
        return stmt
