// Elemento DOM de uma carta na mao. Sem framework, DOM puro (docs/04-arquitetura.md secao 8).

import { motivoBloqueio } from "../core/combat.js";

export function criarElementoCarta(carta, indice, estado, opcoes) {
  const { selecionada, aoClicar, aoJogarDuploClique } = opcoes;
  const motivo = motivoBloqueio(estado, carta);
  const bloqueada = motivo !== null;

  const el = document.createElement("div");
  el.className = "carta";
  if (bloqueada) el.classList.add("carta--bloqueada");
  if (selecionada) el.classList.add("carta--selecionada");
  el.title = bloqueada ? motivo : carta.texto;
  el.setAttribute("role", "button");
  el.setAttribute("tabindex", "0");

  const custo = document.createElement("div");
  custo.className = "carta__custo";
  custo.textContent = String(carta.custo);

  const nome = document.createElement("div");
  nome.className = "carta__nome";
  nome.textContent = carta.nome;

  const tipo = document.createElement("div");
  tipo.className = "carta__tipo";
  tipo.textContent = carta.tipo;

  const texto = document.createElement("div");
  texto.className = "carta__texto";
  texto.textContent = carta.texto;

  el.append(custo, nome, tipo, texto);

  el.addEventListener("click", () => aoClicar(indice));
  el.addEventListener("dblclick", () => aoJogarDuploClique(indice));
  el.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      aoJogarDuploClique(indice);
    }
  });

  return el;
}
