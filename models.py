import uuid

from sqlalchemy import Boolean, Column, DateTime, DECIMAL, ForeignKey, func, Integer, \
    String, Uuid
from sqlalchemy.orm import relationship

from baseclass import BaseClass


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
