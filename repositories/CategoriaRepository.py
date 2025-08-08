import uuid
from typing import Union

from sqlalchemy import Engine
from sqlalchemy.orm import joinedload, Session

from interfaces.ISQLAlchemyRepository import ISQLAlchemyRepository
from models import Categoria, Produto


class CategoriaRepository(ISQLAlchemyRepository[Categoria]):
    def __init__(self, engine: Engine):
        super().__init__(engine, Categoria)

    def get_produtos(self,
                     categoria_info: Union[uuid.UUID, Categoria],
                     page: int = None,
                     page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos de uma categoria específica.
        Aceita tanto o objeto Categoria quanto o UUID da chave primária como argumento.

        Args:
            categoria_info (Union[Categoria, uuid.UUID]): O objeto Categoria ou o UUID da categoria.
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            list[Produto]: Lista de produtos pertencentes à categoria.

        Raises:
            TypeError: Se o argumento fornecido não for um objeto Categoria nem um UUID.
        """
        if isinstance(categoria_info, Categoria):
            with Session(self._engine) as session:
                # session.merge() anexa um objeto desanexado à sessão atual.
                # Isso nos permite carregar relacionamentos preguiçosos (lazy-load) com segurança.
                categoria_gerenciada = session.merge(categoria_info)
                lista_de_produtos = list(categoria_gerenciada.lista_de_produtos)
        elif isinstance(categoria_info, uuid.UUID):
            categoria = self.get_by_id(categoria_info,
                                       load_options=[joinedload(Categoria.lista_de_produtos)])
            if not categoria:
                return []
            lista_de_produtos = list(categoria.lista_de_produtos)
        else:
            raise TypeError("O argumento para get_produtos deve ser um objeto Categoria ou um UUID.")

        if page and page_size:
            # Se houver page e page_size, paginamos os resultados.
            if page < 1 or page_size < 1:
                raise ValueError("page e page_size devem ser maiores que 1.")
            start = (page - 1) * page_size
            end = start + page_size
            return lista_de_produtos[start:end]
        else:
            # Caso contrário, obtemos todos os produtos.
            return lista_de_produtos
