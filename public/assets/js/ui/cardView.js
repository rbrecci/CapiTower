// Elemento DOM de uma carta na mao. Sem framework, DOM puro (docs/04-arquitetura.md secao 8).

import { motivoBloqueio } from "../core/combat.js";
import { somCarta } from "../core/audio.js";

// Fase 7: moldura ilustrada por tipo (Assets/Frame*.png, ver docs/09). Os 4 tipos de carta
// batem 1:1 com os 4 arquivos em assets/img/ui/frames/.
const TIPOS_FRAME = ["Ataque", "Defesa", "Poder", "Utilidade"];

export function criarElementoCarta(carta, indice, estado, opcoes) {
  const { selecionada, aoClicar, aoJogarDuploClique } = opcoes;
  const motivo = motivoBloqueio(estado, carta);
  const bloqueada = motivo !== null;

  const el = document.createElement("div");
  el.className = "carta";
  if (TIPOS_FRAME.includes(carta.tipo)) {
    el.classList.add(`carta--tipo-${carta.tipo.toLowerCase()}`);
  }
  if (bloqueada) el.classList.add("carta--bloqueada");
  if (selecionada) el.classList.add("carta--selecionada");
  el.title = bloqueada ? motivo : carta.texto;
  el.setAttribute("role", "button");
  el.setAttribute("tabindex", "0");

  const custo = document.createElement("div");
  custo.className = "carta__custo";
  custo.textContent = String(carta.custo);

  const arte = document.createElement("div");
  arte.className = "carta__arte";

  const nome = document.createElement("div");
  nome.className = "carta__nome";
  nome.textContent = carta.nome;

  const tipo = document.createElement("div");
  tipo.className = "carta__tipo";
  tipo.textContent = carta.tipo;

  arte.append(nome, tipo);

  const texto = document.createElement("div");
  texto.className = "carta__texto";
  texto.textContent = carta.texto;

  el.append(custo, arte, texto);

  el.addEventListener("click", () => aoClicar(indice));
  el.addEventListener("dblclick", () => jogar());
  el.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      jogar();
    }
  });

  // Bloqueada joga direto (so pra mostrar o motivo no log, sem animar uma carta que nao sai da
  // mao). Jogavel anima a saida primeiro e so muda o estado quando a animacao termina.
  function jogar() {
    if (bloqueada) {
      aoJogarDuploClique(indice);
      return;
    }
    if (el.classList.contains("carta--jogada")) return;
    el.classList.add("carta--jogada");
    somCarta();
    el.addEventListener("animationend", () => aoJogarDuploClique(indice), { once: true });
  }

  return el;
}
