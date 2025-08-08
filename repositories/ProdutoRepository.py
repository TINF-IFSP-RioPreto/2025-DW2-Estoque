from sqlalchemy import Engine

from interfaces.ISQLAlchemyRepository import ISQLAlchemyRepository
from models import Produto


class ProdutoRepository(ISQLAlchemyRepository[Produto]):
    def __init__(self, engine: Engine):
        super().__init__(engine, Produto)

    def produtos_por_preco(self, preco_minimo: float, preco_maximo: float) -> list[Produto]:
        """
        Obtém todos os produtos dentro de um intervalo de preços.

        Args:
            preco_minimo (float): Preço mínimo.
            preco_maximo (float): Preço máximo.

        Returns:
            list[Produto]: Lista de produtos dentro do intervalo de preços.
        """
        return self.get(predicate=self.model.preco.between(preco_minimo, preco_maximo))
