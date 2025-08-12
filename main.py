from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload

from config import read_config
from models import Categoria, Produto
from repositories.CategoriaRepository import CategoriaRepository
from repositories.ProdutoRepository import ProdutoRepository

if __name__ == '__main__':
    config = read_config()
    engine = create_engine(url=config.url_bd, echo=False)

    produtoRepository = ProdutoRepository(engine)
    categoriaRepository = CategoriaRepository(engine)

    # if categoriaRepository.count() > 0:
    #     print("Categorias já existem no banco de dados.")
    #     c = categoriaRepository.get_first()
    # else:
    #     c = Categoria()
    #     c.nome = "Categoria Teste"
    #     categoriaRepository.add(c)
    #
    # if produtoRepository.count() > 0:
    #     print("Produtos já existem no banco de dados.")
    # else:
    #     p = Produto()
    #     p.nome = "Produto Teste2"
    #     p.preco = 10.99
    #     p.estoque = 0
    #     p.ativo = False
    #     p.categoria = c
    #     produtoRepository.add(p)

    print("Lista de produtos ==============================================")
    produtos = produtoRepository.get_all(load_options=[joinedload(Produto.categoria)])
    for p in produtos:
        print(f"Produto: {p.nome}, Preço: {p.preco}, Categoria: {p.categoria.nome}")

    print("Lista de produtos entre R$ 5 e R$ 15 ===========================")
    produtos = produtoRepository.produtos_por_preco(5.00, 15.00)
    for p in produtos:
        print(f"Produto dentro do intervalo de preço: {p.nome}, Preço: {p.preco}")

    c = categoriaRepository.get_first()
    uma_categoria = categoriaRepository.get_by_id(c.id)  # 'c' é a categoria que criamos

    if uma_categoria:
        # Agora, passe o objeto inteiro para o metodo
        produtos_da_categoria = categoriaRepository.get_produtos(uma_categoria)

        print(f"Produtos da categoria '{uma_categoria.nome}' ===========================")
        for p in produtos_da_categoria:
            print(f"  - {p.nome}")

    categorias_sem_produtos = categoriaRepository.get_categorias_sem_produtos()
    print("Categorias sem produtos ========================================")
    for categoria in categorias_sem_produtos:
        print(f"Categoria: {categoria.nome}")

    produtos_sem_estoque = produtoRepository.produtos_sem_estoque()
    print("Produtos sem estoque ===========================================")
    for p in produtos_sem_estoque:
        print(f"Produto sem estoque: {p.nome}, Preço: {p.preco}, Estoque: {p.estoque}, Ativo: {p.ativo}")

    produtos_inativos = produtoRepository.produtos_inativos()
    print("Produtos inativos ==============================================")
    for p in produtos_inativos:
        print(f"Produto sem estoque: {p.nome}, Preço: {p.preco}, Estoque: {p.estoque}, Ativo: {p.ativo}")
