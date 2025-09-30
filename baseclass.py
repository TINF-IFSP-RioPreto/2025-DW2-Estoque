"""
Módulo que define a classe base para os modelos do SQLAlchemy.

Este módulo fornece a classe `BaseClass` que serve como a base declarativa
para todos os modelos da aplicação, permitindo que o SQLAlchemy gerencie
o mapeamento objeto-relacional.
"""
from sqlalchemy.orm import DeclarativeBase


class BaseClass(DeclarativeBase):
    """
    Classe base para os modelos do SQLAlchemy.

    Todos os modelos da aplicação devem herdar desta classe para serem
    automaticamente reconhecidos e gerenciados pelo SQLAlchemy.
    """
    pass