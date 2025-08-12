from sqlalchemy import Engine

from interfaces.ISQLAlchemyRepository import ISQLAlchemyRepository
from models import Produto


class ProdutoRepository(ISQLAlchemyRepository[Produto]):
    def __init__(self, engine: Engine):
        super().__init__(engine, Produto)

    def produtos_por_preco(self, preco_minimo: float, preco_maximo: float, page: int = None,
                           page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos dentro de um intervalo de preços.

        Args:
            preco_minimo (float): Preço mínimo.
            preco_maximo (float): Preço máximo.

        Returns:
            list[Produto]: Lista de produtos dentro do intervalo de preços.
        """
        return self.get(predicate=self.model.preco.between(preco_minimo, preco_maximo),
                        page=page,
                        page_size=page_size)

    def produtos_sem_estoque(self, page: int = None, page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos que não estão em estoque.

        Returns:
            list[Produto]: Lista de produtos que não estão em estoque.
        """
        return self.get(predicate=self.model.estoque <= 0,
                        page=page,
                        page_size=page_size)

    def produtos_inativos(self, page: int = None, page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos inativos (ativo=False).

        Returns:
            list[Produto]: Lista de produtos inativos.
        """
        return self.get(predicate=self.model.ativo.is_(False),
                        page=page,
                        page_size=page_size)
