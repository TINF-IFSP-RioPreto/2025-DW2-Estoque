import pytest
from repositories.ProdutoRepository import ProdutoRepository
from models import Produto, Categoria


@pytest.fixture
def produto_repository(db_session):
    """
    Fixture que fornece uma instância do ProdutoRepository com uma sessão de
    banco de dados de teste.
    """
    # Para testar o ProdutoRepository, precisamos de uma engine que use a sessão de teste
    return ProdutoRepository(engine=db_session.bind)


@pytest.fixture
def categoria_exemplo(db_session):
    """Cria e insere uma categoria de exemplo para ser usada nos testes de produtos."""
    categoria = Categoria(nome="Eletrônicos")
    db_session.add(categoria)
    db_session.commit()
    return categoria


def test_add_produto(produto_repository, categoria_exemplo, db_session):
    """Testa a adição de um novo produto."""
    produto = Produto(
        nome="Smartphone",
        preco=1500.00,
        estoque=50,
        categoria_id=categoria_exemplo.id
    )
    produto_repository.add(produto)

    # Verifica se o produto foi adicionado consultando diretamente a sessão
    produto_adicionado = db_session.query(Produto).filter_by(nome="Smartphone").first()
    assert produto_adicionado is not None
    assert produto_adicionado.preco == 1500.00
    assert produto_adicionado.categoria.nome == "Eletrônicos"


def test_get_produto_by_id(produto_repository, categoria_exemplo, db_session):
    """Testa a busca de um produto pelo seu ID."""
    produto = Produto(nome="Tablet", preco=1200.00, categoria=categoria_exemplo)
    db_session.add(produto)
    db_session.commit()

    produto_encontrado = produto_repository.get_by_id(produto.id)
    assert produto_encontrado is not None
    assert produto_encontrado.nome == "Tablet"


def test_get_all_produtos(produto_repository, categoria_exemplo, db_session):
    """Testa a listagem de todos os produtos."""
    p1 = Produto(nome="Mouse", preco=80.00, categoria=categoria_exemplo)
    p2 = Produto(nome="Teclado", preco=150.00, categoria=categoria_exemplo)
    db_session.add_all([p1, p2])
    db_session.commit()

    produtos = produto_repository.get_all()
    assert len(produtos) == 2
    assert {p.nome for p in produtos} == {"Mouse", "Teclado"}


def test_update_produto(produto_repository, categoria_exemplo, db_session):
    """Testa a atualização de um produto existente."""
    produto = Produto(nome="Monitor", preco=800.00, categoria=categoria_exemplo)
    db_session.add(produto)
    db_session.commit()

    # Atualiza o preço do produto
    produto.preco = 850.50
    produto_repository.update(produto)

    produto_atualizado = db_session.get(Produto, produto.id)
    assert produto_atualizado.preco == 850.50


def test_delete_produto(produto_repository, categoria_exemplo, db_session):
    """Testa a remoção de um produto."""
    produto = Produto(nome="Webcam", preco=250.00, categoria=categoria_exemplo)
    db_session.add(produto)
    db_session.commit()

    produto_id = produto.id
    produto_repository.delete(produto)

    # A sessão de teste (`db_session`) não sabe que o objeto foi deletado por
    # outra sessão (a do repositório). Expirar o objeto força a sessão de
    # teste a recarregá-lo do banco de dados na próxima vez que for acessado.
    db_session.expire(produto)

    produto_deletado = db_session.get(Produto, produto_id)
    assert produto_deletado is None


def test_produtos_por_preco(produto_repository, categoria_exemplo, db_session):
    """Testa a busca de produtos por faixa de preço."""
    p1 = Produto(nome="Produto A", preco=10.00, categoria=categoria_exemplo)
    p2 = Produto(nome="Produto B", preco=25.00, categoria=categoria_exemplo)
    p3 = Produto(nome="Produto C", preco=50.00, categoria=categoria_exemplo)
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    produtos = produto_repository.produtos_por_preco(20.00, 40.00)
    assert len(produtos) == 1
    assert produtos[0].nome == "Produto B"


def test_produtos_sem_estoque(produto_repository, categoria_exemplo, db_session):
    """Testa a busca de produtos com estoque zero ou negativo."""
    p1 = Produto(nome="Produto Com Estoque", estoque=10, categoria=categoria_exemplo)
    p2 = Produto(nome="Produto Sem Estoque", estoque=0, categoria=categoria_exemplo)
    p3 = Produto(nome="Produto Estoque Negativo", estoque=-5, categoria=categoria_exemplo)
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    produtos = produto_repository.produtos_sem_estoque()
    assert len(produtos) == 2
    assert {p.nome for p in produtos} == {"Produto Sem Estoque", "Produto Estoque Negativo"}


def test_produtos_inativos(produto_repository, categoria_exemplo, db_session):
    """Testa a busca de produtos inativos."""
    p1 = Produto(nome="Produto Ativo", ativo=True, categoria=categoria_exemplo)
    p2 = Produto(nome="Produto Inativo", ativo=False, categoria=categoria_exemplo)
    db_session.add_all([p1, p2])
    db_session.commit()

    produtos = produto_repository.produtos_inativos()
    assert len(produtos) == 1
    assert produtos[0].nome == "Produto Inativo"


def test_count_produtos(produto_repository, categoria_exemplo, db_session):
    """Testa a contagem de produtos."""
    p1 = Produto(nome="Produto 1", categoria=categoria_exemplo, preco=10)
    p2 = Produto(nome="Produto 2", categoria=categoria_exemplo, preco=20)
    p3 = Produto(nome="Produto 3", categoria=categoria_exemplo, preco=30, ativo=False)
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    total = produto_repository.count()
    assert total == 3

    # Testa contagem com predicado
    inativos = produto_repository.count(predicate=Produto.ativo.is_(False))
    assert inativos == 1
    caros = produto_repository.count(predicate=Produto.preco > 15)
    assert caros == 2