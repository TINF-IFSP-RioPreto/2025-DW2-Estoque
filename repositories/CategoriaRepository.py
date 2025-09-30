"""
Módulo que define o repositório de dados para a entidade Categoria.

Este módulo contém a classe `CategoriaRepository`, que fornece métodos
específicos para consultar e manipular dados de categorias, além
das operações CRUD básicas herdadas de `ISQLAlchemyRepository`.
"""
import uuid
from typing import Union

from sqlalchemy import Engine
from sqlalchemy.orm import joinedload, Session

from interfaces.ISQLAlchemyRepository import ISQLAlchemyRepository
from models import Categoria, Produto


class CategoriaRepository(ISQLAlchemyRepository[Categoria]):
    """
    Repositório para a entidade Categoria.

    Esta classe implementa métodos específicos para a manipulação de dados
    de categorias, como buscar produtos de uma categoria ou encontrar
    categorias sem produtos.
    """
    def __init__(self, engine: Engine):
        """
        Inicializa o repositório de Categoria.

        Args:
            engine (Engine): A instância do engine SQLAlchemy para se conectar ao banco.
        """
        super().__init__(engine, Categoria)

    def get_produtos(self,
                     categoria_info: Union[uuid.UUID, Categoria],
                     page: int = None,
                     page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos de uma categoria específica.

        Este método aceita tanto o objeto `Categoria` quanto o UUID da chave
        primária como argumento para identificar a categoria.

        Args:
            categoria_info (Union[Categoria, uuid.UUID]): O objeto Categoria ou o UUID da categoria.
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            list[Produto]: Lista de produtos pertencentes à categoria.

        Raises:
            TypeError: Se o argumento `categoria_info` não for um objeto Categoria nem um UUID.
            ValueError: Se `page` ou `page_size` forem menores que 1.
        """
        if isinstance(categoria_info, Categoria):
            with Session(self._engine) as session:
                # session.merge() anexa um objeto desanexado à sessão atual.
                # Isso nos permite carregar relacionamentos com segurança.
                categoria_gerenciada = session.merge(categoria_info)
                lista_de_produtos = list(categoria_gerenciada.lista_de_produtos)
        elif isinstance(categoria_info, uuid.UUID):
            categoria = self.get_by_id(categoria_info,
                                       load_options=[joinedload(Categoria.lista_de_produtos)])
            if not categoria:
                return []
            lista_de_produtos = list(categoria.lista_de_produtos)
        else:
            raise TypeError(
                "O argumento para get_produtos deve ser um objeto Categoria ou um UUID.")

        if page is not None and page_size is not None:
            if page < 1 or page_size < 1:
                raise ValueError("page e page_size devem ser maiores que 1.")
            start = (page - 1) * page_size
            end = start + page_size
            return lista_de_produtos[start:end]
        else:
            return lista_de_produtos

    def get_categorias_sem_produtos(self, page: int = None, page_size: int = None) -> list[Categoria]:
        """
        Obtém todas as categorias que não possuem produtos associados.

        Args:
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            list[Categoria]: Lista de categorias sem produtos.
        """
        return self.get(predicate=~self.model.lista_de_produtos.any(),
                        page=page,
                        page_size=page_size)