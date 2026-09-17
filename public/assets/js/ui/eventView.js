// Tela de evento narrativo (docs/03-conteudo.md secao 7). Regra da Fase 2: nenhum evento da
// ponto de recompensa nem mexe no deck, entao as escolhas so tocam HP, Fraqueza futura e Forca
// permanente (docs/04-arquitetura.md, dados em data/events.json).

import { cabecalhoAndar } from "./towerView.js";

export function renderEvento(container, sala, evento, onEscolher) {
  container.innerHTML = "";
  const raiz = document.createElement("div");
  raiz.className = "tela-sala";
  raiz.appendChild(cabecalhoAndar(sala));

  const tela = document.createElement("div");
  tela.className = "tela-centro tela-evento";

  const titulo = document.createElement("h2");
  titulo.textContent = evento.titulo;

  const texto = document.createElement("p");
  texto.className = "tela-centro__texto";
  texto.textContent = evento.texto;

  tela.append(titulo, texto);

  const opcoes = document.createElement("div");
  opcoes.className = "opcoes-evento";

  evento.escolhas.forEach((escolha, indice) => {
    const botao = document.createElement("button");
    botao.className = "opcao-evento";
    const tituloEscolha = document.createElement("div");
    tituloEscolha.className = "opcao-evento__titulo";
    tituloEscolha.textContent = escolha.texto;
    const resultado = document.createElement("div");
    resultado.className = "opcao-evento__texto";
    resultado.textContent = escolha.resultado;
    botao.append(tituloEscolha, resultado);
    botao.addEventListener("click", () => onEscolher(indice));
    opcoes.appendChild(botao);
  });

  tela.appendChild(opcoes);
  raiz.appendChild(tela);
  container.appendChild(raiz);
}
