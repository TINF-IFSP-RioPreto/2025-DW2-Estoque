"""
Módulo que define o repositório de dados para a entidade Produto.

Este módulo contém a classe `ProdutoRepository`, que fornece métodos
específicos para consultar e manipular dados de produtos, além das
operações CRUD básicas herdadas de `ISQLAlchemyRepository`.
"""
from sqlalchemy import Engine

from interfaces.ISQLAlchemyRepository import ISQLAlchemyRepository
from models import Produto


class ProdutoRepository(ISQLAlchemyRepository[Produto]):
    """
    Repositório para a entidade Produto.

    Esta classe implementa métodos específicos para a manipulação de dados
    de produtos, como buscar por faixa de preço, sem estoque ou inativos.
    """
    def __init__(self, engine: Engine):
        """
        Inicializa o repositório de Produto.

        Args:
            engine (Engine): A instância do engine SQLAlchemy para se conectar ao banco.
        """
        super().__init__(engine, Produto)

    def produtos_por_preco(self,
                           preco_minimo: float,
                           preco_maximo: float,
                           page: int = None,
                           page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos dentro de um intervalo de preços.

        Args:
            preco_minimo (float): Preço mínimo do produto.
            preco_maximo (float): Preço máximo do produto.
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            list[Produto]: Lista de produtos dentro do intervalo de preços.
        """
        return self.get(predicate=self.model.preco.between(preco_minimo, preco_maximo),
                        page=page,
                        page_size=page_size)

    def produtos_sem_estoque(self, page: int = None, page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos que não estão em estoque (estoque <= 0).

        Args:
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            list[Produto]: Lista de produtos que não estão em estoque.
        """
        return self.get(predicate=self.model.estoque <= 0,
                        page=page,
                        page_size=page_size)

    def produtos_inativos(self, page: int = None, page_size: int = None) -> list[Produto]:
        """
        Obtém todos os produtos inativos (onde o campo `ativo` é False).

        Args:
            page (int, opcional): Número da página para paginação.
            page_size (int, opcional): Tamanho da página para paginação.

        Returns:
            list[Produto]: Lista de produtos inativos.
        """
        return self.get(predicate=self.model.ativo.is_(False),
                        page=page,
                        page_size=page_size)