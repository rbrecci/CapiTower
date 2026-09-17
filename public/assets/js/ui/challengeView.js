// Tela de desafio opcional: escolher 1 modificador entre 2 sorteados antes do combate da sala
// (D25, docs/07-decisoes.md Q4). Modificador e sempre aditivo e de valor fixo, maximo 5 por run.

import { cabecalhoAndar } from "./towerView.js";

export function renderDesafio(container, sala, opcoesDesafio, onEscolher) {
  container.innerHTML = "";
  const raiz = document.createElement("div");
  raiz.className = "tela-sala";
  raiz.appendChild(cabecalhoAndar(sala));

  const tela = document.createElement("div");
  tela.className = "tela-centro tela-desafio";

  const titulo = document.createElement("h2");
  titulo.textContent = "Desafio opcional";

  const texto = document.createElement("p");
  texto.className = "tela-centro__texto";
  texto.textContent = "Escolha um modificador permanente para o resto da run antes do combate desta sala.";

  tela.append(titulo, texto);

  const opcoes = document.createElement("div");
  opcoes.className = "opcoes-evento";

  opcoesDesafio.forEach((desafio) => {
    const botao = document.createElement("button");
    botao.className = "opcao-evento";
    const nome = document.createElement("div");
    nome.className = "opcao-evento__titulo";
    nome.textContent = desafio.nome;
    const descricao = document.createElement("div");
    descricao.className = "opcao-evento__texto";
    descricao.textContent = desafio.texto;
    botao.append(nome, descricao);
    botao.addEventListener("click", () => onEscolher(desafio));
    opcoes.appendChild(botao);
  });

  tela.appendChild(opcoes);
  raiz.appendChild(tela);
  container.appendChild(raiz);
}

export function renderSemDesafioDisponivel(container, sala, onContinuar) {
  container.innerHTML = "";
  const raiz = document.createElement("div");
  raiz.className = "tela-sala";
  raiz.appendChild(cabecalhoAndar(sala));

  const tela = document.createElement("div");
  tela.className = "tela-centro";

  const titulo = document.createElement("h2");
  titulo.textContent = "Desafio opcional";

  const texto = document.createElement("p");
  texto.className = "tela-centro__texto";
  texto.textContent = "Sem modificador novo para oferecer (limite de 5 por run ou pool esgotado). Direto para o combate.";

  const botao = document.createElement("button");
  botao.className = "botao";
  botao.textContent = "Entrar em combate";
  botao.addEventListener("click", onContinuar);

  tela.append(titulo, texto, botao);
  raiz.appendChild(tela);
  container.appendChild(raiz);
}
