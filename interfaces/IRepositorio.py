from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import ColumnElement

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
    def get_all(self,
                load_options: Optional[list] = None,
                page: int = None,
                page_size: int = None) -> list[T]:
        """
        Recupera todas as entidades do repositório.

        Args:
            load_options (Optional[list]): Lista de opções de carregamento
               (ex: [joinedload(Model.relationship)]).
            page (int): O número da página (começando em 1).
            page_size (int): O número de itens por página.
        Returns:
            list[T]: Uma lista contendo entidades do tipo T
        """
        pass

    @abstractmethod
    def get(self,
            predicate: Optional[ColumnElement[bool]] = None,
            load_options: Optional[list] = None,
            page: int = None,
            page_size: int = None) -> list[T]:
        """
        Recupera entidades baseadas em um predicado opcional.

        Args:
            predicate: Função que define o critério de filtragem.
                       Se None, retorna todas as entidades.
            load_options (Optional[list]): Lista de opções de carregamento
               (ex: [joinedload(Model.relationship)]).
            page (int): O número da página (começando em 1).
            page_size (int): O número de itens por página.

        Returns:
            list[T]: Uma lista contendo entidades do tipo T que satisfazem o predicado
        """
        pass

    @abstractmethod
    def get_first(self,
                  predicate: Optional[ColumnElement[bool]] = None,
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
