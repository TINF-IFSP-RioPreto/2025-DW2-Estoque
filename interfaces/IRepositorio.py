"""
Módulo que define a interface para o padrão de repositório.

Este módulo contém a classe abstrata `IRepository`, que estabelece um
contrato para operações de acesso a dados, como consultas e manipulações,
de forma genérica e desacoplada da implementação de persistência.
"""
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import ColumnElement

# Definição do tipo genérico T, que representa a entidade do modelo.
T = TypeVar('T')


class IRepository(Generic[T], ABC):
    """
    Interface genérica para repositório de dados.

    Esta interface define operações CRUD básicas e funcionalidades de consulta
    para qualquer tipo de entidade. Implementa o padrão Repository com suporte
    a generics.

    Type Parameters:
        T: O tipo da entidade que será gerenciada pelo repositório.
    """

    @abstractmethod
    def get_all(self,
                load_options: Optional[list] = None,
                page: int = None,
                page_size: int = None) -> list[T]:
        """
        Recupera todas as entidades do repositório, com paginação opcional.

        Args:
            load_options (Optional[list]): Lista de opções para carregamento
               adiantado de relacionamentos (ex: `joinedload`).
            page (int, opcional): O número da página (começando em 1).
            page_size (int, opcional): O número de itens por página.

        Returns:
            list[T]: Uma lista contendo todas as entidades do tipo T.
        """
        pass

    @abstractmethod
    def get(self,
            predicate: Optional[ColumnElement[bool]] = None,
            load_options: Optional[list] = None,
            page: int = None,
            page_size: int = None) -> list[T]:
        """
        Recupera entidades que satisfazem um predicado, com paginação opcional.

        Args:
            predicate (Optional[ColumnElement[bool]]): Uma expressão de filtro
                       (ex: `Model.coluna == valor`). Se None, retorna todas as entidades.
            load_options (Optional[list]): Lista de opções para carregamento
               adiantado de relacionamentos.
            page (int, opcional): O número da página (começando em 1).
            page_size (int, opcional): O número de itens por página.

        Returns:
            list[T]: Uma lista de entidades que satisfazem o predicado.
        """
        pass

    @abstractmethod
    def get_first(self,
                  predicate: Optional[ColumnElement[bool]] = None,
                  load_options: Optional[list] = None) -> Optional[T]:
        """
        Recupera a primeira entidade que satisfaz um predicado.

        Args:
            predicate (Optional[ColumnElement[bool]]): Uma expressão de filtro.
                       Se None, retorna a primeira entidade disponível.
            load_options (Optional[list]): Lista de opções para carregamento
               adiantado de relacionamentos.

        Returns:
            Optional[T]: A primeira entidade encontrada ou None.
        """
        pass

    @abstractmethod
    def get_by_id(self, *key: Any, load_options: Optional[list] = None) -> Optional[T]:
        """
        Recupera uma entidade pela sua chave primária.

        Args:
            *key: Valores da chave primária (suporta chaves compostas).
            load_options (Optional[list]): Lista de opções para carregamento
               adiantado de relacionamentos.

        Returns:
            Optional[T]: A entidade encontrada ou None.
        """
        pass

    @abstractmethod
    def add(self, entity: T) -> None:
        """
        Adiciona uma nova entidade ao repositório.

        Args:
            entity (T): A entidade a ser adicionada.
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        """
        Atualiza uma entidade existente no repositório.

        Args:
            entity (T): A entidade com os dados atualizados.
        """
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        """
        Remove uma entidade do repositório.

        Args:
            entity (T): A entidade a ser removida.
        """
        pass

    @abstractmethod
    def count(self, predicate: Optional[ColumnElement[bool]] = None) -> int:
        """
        Retorna o número de entidades que satisfazem um predicado.

        Args:
            predicate (Optional[ColumnElement[bool]]): Uma expressão de filtro.
                       Se None, conta todas as entidades.

        Returns:
            int: A quantidade de entidades.
        """
        pass