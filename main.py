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

    if categoriaRepository.count() > 0:
        print("Categorias já existem no banco de dados.")
        c = categoriaRepository.get_first()
    else:
        c = Categoria()
        c.nome = "Categoria Teste"
        categoriaRepository.add(c)

    if produtoRepository.count() > 0:
        print("Produtos já existem no banco de dados.")
    else:
        p = Produto()
        p.nome = "Produto Teste"
        p.preco = 10.99
        p.estoque = 100
        p.ativo = True
        p.categoria = c
        produtoRepository.add(p)

    produtos = produtoRepository.get_all(load_options=[joinedload(Produto.categoria)])
    for p in produtos:
        print(f"Produto: {p.nome}, Preço: {p.preco}, Categoria: {p.categoria.nome}")

    produtos = produtoRepository.produtos_por_preco(5.00, 15.00)
    for p in produtos:
        print(f"Produto dentro do intervalo de preço: {p.nome}, Preço: {p.preco}")

    uma_categoria = categoriaRepository.get_by_id(c.id)  # 'c' é a categoria que criamos

    if uma_categoria:
        # Agora, passe o objeto inteiro para o metodo
        produtos_da_categoria = categoriaRepository.get_produtos(uma_categoria)

        print(f"\n--- Produtos da categoria '{uma_categoria.nome}' ---")
        for p in produtos_da_categoria:
            print(f"  - {p.nome}")
