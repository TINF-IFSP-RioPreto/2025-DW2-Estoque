"""
Módulo que define os modelos de dados da aplicação usando SQLAlchemy.

Este módulo contém as classes `Categoria` e `Produto`, que representam as
tabelas do banco de dados, e a classe `datasMixin` para campos de data comuns.
"""
import uuid

from sqlalchemy import (Boolean, Column, DateTime, DECIMAL, ForeignKey, func,
                        Integer, String, Uuid)
from sqlalchemy.orm import relationship

from baseclass import BaseClass


class datasMixin:
    """
    Mixin que adiciona colunas de data de cadastro e atualização.

    Este mixin pode ser usado em qualquer modelo SQLAlchemy para adicionar
    automaticamente os campos `dta_cadastro` e `dta_atualizacao`.

    Attributes:
        dta_cadastro (DateTime): Data e hora do cadastro do registro.
                                 É preenchido automaticamente no momento da criação.
        dta_atualizacao (DateTime): Data e hora da última atualização do registro.
                                    É atualizado automaticamente sempre que o
                                    registro é modificado.
    """
    dta_cadastro = Column(DateTime,
                          server_default=func.now(),
                          nullable=False)
    dta_atualizacao = Column(DateTime,
                             onupdate=func.now(),
                             default=func.now(),
                             nullable=False)


class Categoria(datasMixin, BaseClass):
    """
    Representa uma categoria de produtos no banco de dados.

    Attributes:
        id (uuid.UUID): Identificador único da categoria (chave primária).
        nome (str): Nome da categoria.
        lista_de_produtos (list[Produto]): Relacionamento com os produtos
                                           que pertencem a esta categoria.
    """
    __tablename__ = 'categorias'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(256), nullable=False)

    lista_de_produtos = relationship("Produto",
                                     back_populates="categoria",
                                     cascade="all, delete-orphan")


class Produto(datasMixin, BaseClass):
    """
    Representa um produto no banco de dados.

    Attributes:
        id (uuid.UUID): Identificador único do produto (chave primária).
        nome (str): Nome do produto.
        preco (DECIMAL): Preço do produto.
        estoque (int): Quantidade do produto em estoque.
        ativo (bool): Indica se o produto está ativo (padrão: True).
        categoria_id (uuid.UUID): Chave estrangeira para a tabela de categorias.
        categoria (Categoria): Relacionamento com a categoria à qual o
                               produto pertence.
    """
    __tablename__ = 'produtos'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(256), nullable=False)
    preco = Column(DECIMAL(precision=10, scale=2), default=0.00)
    estoque = Column(Integer, default=0)
    ativo = Column(Boolean, nullable=False, default=True)
    categoria_id = Column(Uuid(as_uuid=True), ForeignKey("categorias.id"))

    categoria = relationship("Categoria",
                             back_populates="lista_de_produtos")