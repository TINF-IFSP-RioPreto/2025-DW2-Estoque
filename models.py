import uuid
from typing import Union

from sqlalchemy import Boolean, Column, DateTime, DECIMAL, Engine, ForeignKey, func, Integer, \
    String, Uuid
from sqlalchemy.orm import joinedload, relationship, Session

from baseclass import BaseClass
from interfaces.IRepositorio import ISQLAlchemyRepository


class datasMixin:
    dta_cadastro = Column(DateTime,
                          server_default=func.now(),
                          nullable=False)
    dta_atualizacao = Column(DateTime,
                             onupdate=func.now(),
                             default=func.now(),
                             nullable=False)


class Categoria(datasMixin, BaseClass):
    __tablename__ = 'categorias'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(256), nullable=False)

    lista_de_produtos = relationship("Produto",
                                     back_populates="categoria",
                                     cascade="all, delete-orphan")


class Produto(datasMixin, BaseClass):
    __tablename__ = 'produtos'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(256), nullable=False)
    preco = Column(DECIMAL(precision=10, scale=2), default=0.00)
    estoque = Column(Integer, default=0)
    ativo = Column(Boolean, nullable=False, default=True)
    categoria_id = Column(Uuid(as_uuid=True), ForeignKey("categorias.id"))

    categoria = relationship("Categoria",
                             back_populates="lista_de_produtos")


class ProdutoRepository(ISQLAlchemyRepository[Produto]):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.model = Produto

    def produtos_por_preco(self, preco_minimo: float, preco_maximo: float) -> list[Produto]:
        """
        Obtém todos os produtos dentro de um intervalo de preços.

        Args:
            preco_minimo (float): Preço mínimo.
            preco_maximo (float): Preço máximo.

        Returns:
            list[Produto]: Lista de produtos dentro do intervalo de preços.
        """
        return self.get(self.model.preco.between(preco_minimo, preco_maximo))


class CategoriaRepository(ISQLAlchemyRepository[Categoria]):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.model = Categoria

    def get_produtos(self, categoria_info: Union[uuid.UUID, Categoria]) -> list[Produto]:
        """
        Obtém todos os produtos de uma categoria específica.
        Aceita tanto o objeto Categoria quanto o UUID da chave primária como argumento.

        Args:
            categoria_info (Union[Categoria, uuid.UUID]): O objeto Categoria ou o UUID da categoria.

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

                # Agora que a categoria está "viva" na sessão, podemos acessar a lista de produtos.
                # O SQLAlchemy fará o lazy-load aqui, executando uma consulta para buscar os
                # produtos.
                produtos = categoria_gerenciada.lista_de_produtos

                # É uma boa prática retornar uma cópia da lista para evitar problemas
                # se a sessão for fechada e os objetos Produto tiverem relacionamentos.
                return list(produtos)
        elif isinstance(categoria_info, uuid.UUID):
            categoria = self.get_by_id(categoria_info,
                                       load_options=[joinedload(Categoria.lista_de_produtos)])
            if categoria:
                return categoria.lista_de_produtos
            return []
        else:
            raise TypeError(
                "O argumento para get_produtos deve ser um objeto Categoria ou um UUID.")
