// Tela de recompensa depois de vencer elite ou chefe de bloco (D21: 10 pontos por run, 5
// elites + 5 chefes; o chefao do andar 51 nao da ponto, entao esta tela nunca aparece nele).
// Escolha carta contra habilidade. A opcao de carta sorteia 1 do catalogo completo da Capimaga
// e pode repetir uma que ja esta no deck; a opcao de habilidade mostra o efeito real do proximo
// nivel de Legiao (LEGIAO_TEXTO, portado de flet_mvp/capitower/content.py), aplicado de verdade
// pelo motor em core/combat.js.

import { MAX_NIVEL_HABILIDADE, LEGIAO_TEXTO } from "../core/state.js";

export function renderRecompensa(container, run, cartaSorteada, onEscolherCarta, onEscolherHabilidade) {
  container.innerHTML = "";

  const raiz = document.createElement("div");
  raiz.className = "tela-centro tela-recompensa";

  const titulo = document.createElement("h2");
  titulo.textContent = "Sala limpa! Escolha uma recompensa.";
  raiz.appendChild(titulo);

  const opcoes = document.createElement("div");
  opcoes.className = "opcoes-recompensa";

  const opcaoCarta = document.createElement("button");
  opcaoCarta.className = "opcao-recompensa";
  const tituloCarta = document.createElement("div");
  tituloCarta.className = "opcao-recompensa__titulo";
  tituloCarta.textContent = `Carta: ${cartaSorteada.nome}`;
  const textoCarta = document.createElement("div");
  textoCarta.className = "opcao-recompensa__texto";
  textoCarta.textContent = `${cartaSorteada.texto} (custo ${cartaSorteada.custo}, adiciona 1 copia ao deck).`;
  opcaoCarta.append(tituloCarta, textoCarta);
  opcaoCarta.addEventListener("click", onEscolherCarta);

  const opcaoHabilidade = document.createElement("button");
  opcaoHabilidade.className = "opcao-recompensa";
  const tituloHab = document.createElement("div");
  tituloHab.className = "opcao-recompensa__titulo";
  const proximo = Math.min(MAX_NIVEL_HABILIDADE, run.nivelHabilidade + 1);
  tituloHab.textContent = `Habilidade: Legiao nivel ${run.nivelHabilidade} -> ${proximo}`;
  const textoHab = document.createElement("div");
  textoHab.className = "opcao-recompensa__texto";
  textoHab.textContent =
    run.nivelHabilidade >= MAX_NIVEL_HABILIDADE
      ? "Ja no nivel maximo da Legiao."
      : LEGIAO_TEXTO[proximo];
  opcaoHabilidade.append(tituloHab, textoHab);
  opcaoHabilidade.addEventListener("click", onEscolherHabilidade);

  opcoes.append(opcaoCarta, opcaoHabilidade);
  raiz.appendChild(opcoes);
  container.appendChild(raiz);
}
