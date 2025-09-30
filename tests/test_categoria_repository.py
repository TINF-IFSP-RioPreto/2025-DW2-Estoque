import uuid
import pytest
from models import Categoria, Produto
from repositories.CategoriaRepository import CategoriaRepository


@pytest.fixture
def categoria_repository(db_session):
    """
    Fixture que fornece uma instância do CategoriaRepository com uma sessão
    de banco de dados de teste.
    """
    return CategoriaRepository(engine=db_session.bind)


def test_add_categoria(categoria_repository, db_session):
    """Testa a adição de uma nova categoria."""
    categoria = Categoria(nome="Livros")
    categoria_repository.add(categoria)

    categoria_adicionada = db_session.query(Categoria).filter_by(nome="Livros").first()
    assert categoria_adicionada is not None
    assert categoria_adicionada.nome == "Livros"


def test_get_categoria_by_id(categoria_repository, db_session):
    """Testa a busca de uma categoria pelo seu ID."""
    categoria = Categoria(nome="Móveis")
    db_session.add(categoria)
    db_session.commit()

    categoria_encontrada = categoria_repository.get_by_id(categoria.id)
    assert categoria_encontrada is not None
    assert categoria_encontrada.nome == "Móveis"


def test_get_all_categorias(categoria_repository, db_session):
    """Testa a listagem de todas as categorias."""
    c1 = Categoria(nome="Roupas")
    c2 = Categoria(nome="Calçados")
    db_session.add_all([c1, c2])
    db_session.commit()

    categorias = categoria_repository.get_all()
    assert len(categorias) == 2
    assert {c.nome for c in categorias} == {"Roupas", "Calçados"}


def test_update_categoria(categoria_repository, db_session):
    """Testa a atualização de uma categoria existente."""
    categoria = Categoria(nome="Jardinagem")
    db_session.add(categoria)
    db_session.commit()

    categoria.nome = "Jardinagem e Paisagismo"
    categoria_repository.update(categoria)

    categoria_atualizada = db_session.get(Categoria, categoria.id)
    assert categoria_atualizada.nome == "Jardinagem e Paisagismo"


def test_delete_categoria(categoria_repository, db_session):
    """Testa a remoção de uma categoria."""
    categoria = Categoria(nome="Brinquedos")
    db_session.add(categoria)
    db_session.commit()

    categoria_id = categoria.id
    categoria_repository.delete(categoria)
    db_session.expire(categoria)

    categoria_deletada = db_session.get(Categoria, categoria_id)
    assert categoria_deletada is None


def test_get_produtos_de_categoria_com_objeto(categoria_repository, db_session):
    """Testa a busca de produtos de uma categoria usando o objeto Categoria."""
    cat = Categoria(nome="Ferramentas")
    p1 = Produto(nome="Martelo", categoria=cat)
    p2 = Produto(nome="Serrote", categoria=cat)
    db_session.add_all([cat, p1, p2])
    db_session.commit()

    produtos = categoria_repository.get_produtos(cat)
    assert len(produtos) == 2
    assert {p.nome for p in produtos} == {"Martelo", "Serrote"}


def test_get_produtos_de_categoria_com_uuid(categoria_repository, db_session):
    """Testa a busca de produtos de uma categoria usando o UUID."""
    cat = Categoria(nome="Esportes")
    p1 = Produto(nome="Bola de Futebol", categoria=cat)
    db_session.add_all([cat, p1])
    db_session.commit()

    produtos = categoria_repository.get_produtos(cat.id)
    assert len(produtos) == 1
    assert produtos[0].nome == "Bola de Futebol"


def test_get_produtos_de_categoria_inexistente(categoria_repository):
    """Testa a busca de produtos de uma categoria que não existe."""
    produtos = categoria_repository.get_produtos(uuid.uuid4())
    assert len(produtos) == 0


def test_get_categorias_sem_produtos(categoria_repository, db_session):
    """Testa a busca por categorias que não têm produtos associados."""
    cat_com_produto = Categoria(nome="Comida")
    cat_sem_produto = Categoria(nome="Bebida")
    prod = Produto(nome="Pizza", categoria=cat_com_produto)
    db_session.add_all([cat_com_produto, cat_sem_produto, prod])
    db_session.commit()

    categorias = categoria_repository.get_categorias_sem_produtos()
    assert len(categorias) == 1
    assert categorias[0].nome == "Bebida"


def test_count_categorias(categoria_repository, db_session):
    """Testa a contagem de categorias."""
    c1 = Categoria(nome="Categoria A")
    c2 = Categoria(nome="Categoria B")
    c3 = Categoria(nome="Outra Categoria")
    db_session.add_all([c1, c2, c3])
    db_session.commit()

    total = categoria_repository.count()
    assert total == 3

    # Testa contagem com predicado
    especificas = categoria_repository.count(predicate=Categoria.nome.like('Categoria%'))
    assert especificas == 2


def test_get_produtos_paginado(categoria_repository, db_session):
    """Testa a paginação de produtos de uma categoria."""
    cat = Categoria(nome="Paginação")
    for i in range(10):
        db_session.add(Produto(nome=f"Produto {i+1}", categoria=cat))
    db_session.add(cat)
    db_session.commit()

    # Testa a primeira página
    produtos_p1 = categoria_repository.get_produtos(cat, page=1, page_size=5)
    assert len(produtos_p1) == 5
    assert produtos_p1[0].nome == "Produto 1"

    # Testa a segunda página
    produtos_p2 = categoria_repository.get_produtos(cat, page=2, page_size=5)
    assert len(produtos_p2) == 5
    assert produtos_p2[0].nome == "Produto 6"


def test_get_produtos_paginacao_invalida(categoria_repository, db_session):
    """Testa se a paginação com valores inválidos levanta um erro."""
    # Cria uma categoria para que a função não retorne antes de checar a paginação
    cat = Categoria(nome="Categoria para Teste de Erro")
    db_session.add(cat)
    db_session.commit()

    with pytest.raises(ValueError, match="page e page_size devem ser maiores que 1."):
        categoria_repository.get_produtos(cat, page=0, page_size=5)

    with pytest.raises(ValueError, match="page e page_size devem ser maiores que 1."):
        categoria_repository.get_produtos(cat, page=1, page_size=0)