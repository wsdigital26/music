// script.js

let dados = {};
let produtosFiltrados = [];

async function carregarProdutos() {
    try {
        const resposta = await fetch("produtos_hayamax.json");
        dados = await resposta.json();
        produtosFiltrados = dados;
        gerarCategorias();
        exibirProdutos();
    } catch (erro) {
        console.error("Erro ao carregar os produtos:", erro);
    }
}

function gerarCategorias() {
    const menu = document.getElementById("menu-categorias");
    menu.innerHTML = "";

    // Cria e adiciona primeiro o botão "Todos"
    const todos = document.createElement("button");
    todos.textContent = "Todos";
    todos.onclick = () => {
        produtosFiltrados = dados;
        exibirProdutos();
    };
    menu.appendChild(todos);

    // Depois adiciona as demais categorias
    Object.keys(dados).forEach(categoria => {
        const botao = document.createElement("button");
        botao.textContent = categoria;
        botao.onclick = () => {
            produtosFiltrados = { [categoria]: dados[categoria] };
            exibirProdutos();
        };
        menu.appendChild(botao);
    });
}

function exibirProdutos() {
    const container = document.querySelector(".produto-container");
    container.innerHTML = "";

    Object.entries(produtosFiltrados).forEach(([categoria, produtos]) => {
        produtos.forEach(produto => {
            const card = document.createElement("div");
            card.classList.add("produto");

            // Alteração: Código abaixo do nome e acima do preço
            card.innerHTML = `
                <img src="${produto['Imagem (URL)']}" alt="${produto.Nome}" onerror="this.src='https://via.placeholder.com/150'">
                <h4>${produto.Nome}</h4>
                <small>Código: ${produto.Código}</small>  <!-- Código abaixo do nome -->
                <p>${produto.Preço}</p>
            `;

            card.onclick = () => {
                localStorage.setItem("produtoSelecionado", JSON.stringify(produto));
                window.location.href = "produto.html";
            };

            container.appendChild(card);
        });
    });
}

function buscarProduto() {
    const termo = document.getElementById("busca-produto").value.toLowerCase();
    const resultados = {};

    Object.entries(dados).forEach(([categoria, produtos]) => {
        const filtrados = produtos.filter(p => p.Nome.toLowerCase().includes(termo));
        if (filtrados.length > 0) {
            resultados[categoria] = filtrados;
        }
    });

    produtosFiltrados = resultados;
    exibirProdutos();
}

carregarProdutos();
