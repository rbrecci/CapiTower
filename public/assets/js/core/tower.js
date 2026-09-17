// Geracao da ordem dos andares da torre (docs/04-arquitetura.md secao 3,
// docs/06-roadmap.md Fase 2, docs/07-decisoes.md D02/D08/D20/D21).
// Porta a logica de flet_mvp/capitower/run.py:_generate_tower para JS: cada bloco de 10
// andares tem 5 combates comuns, 1 elite, 1 evento, 1 descanso e 1 desafio embaralhados,
// com o elite forcado a cair entre a 3a e a 8a posicao do bloco, mais o chefe fixo no
// 10o andar. No topo (andar 51) fica o chefe final, que nao entra no sorteio de bloco.

import { criarRng, embaralhar, inteiroAleatorio } from "./rng.js";

export const ANDARES_POR_BLOCO = 10;
export const NUM_BLOCOS = 5;
export const ANDAR_FINAL = NUM_BLOCOS * ANDARES_POR_BLOCO + 1; // 51
export const TIPOS_SALA = ["combate", "elite", "evento", "descanso", "desafio", "chefe"];

export const NOMES_BLOCO = [
  "Bloco 1, O Poco",
  "Bloco 2, A Academia",
  "Bloco 3, O Laboratorio",
  "Bloco 4, O Refeitorio",
  "Bloco 5, O Jardim Suspenso",
];

function montarEntradasDoBloco() {
  const entradas = [];
  for (let i = 0; i < 5; i++) entradas.push({ tipo: "combate" });
  entradas.push({ tipo: "elite" });
  entradas.push({ tipo: "evento" });
  entradas.push({ tipo: "descanso" });
  entradas.push({ tipo: "desafio" });
  return entradas;
}

// Gera a torre inteira (51 andares) a partir da seed da run. Determinístico: a mesma seed
// sempre devolve a mesma ordem, entao a torre nunca precisa ser salva (so a seed).
export function gerarTorre(seed) {
  const rng = criarRng(seed >>> 0);
  const andares = [];

  for (let bloco = 0; bloco < NUM_BLOCOS; bloco++) {
    const entradas = embaralhar(montarEntradasDoBloco(), rng);

    // Forca o elite a cair entre a 3a e a 8a posicao do bloco (indices 2 a 7 de 0 a 8),
    // igual a flet_mvp/capitower/run.py:_generate_tower.
    const indiceElite = entradas.findIndex((e) => e.tipo === "elite");
    const alvo = 2 + inteiroAleatorio(rng, 6);
    const tmp = entradas[indiceElite];
    entradas[indiceElite] = entradas[alvo];
    entradas[alvo] = tmp;

    entradas.push({ tipo: "chefe" });

    entradas.forEach((sala, indice) => {
      andares.push({
        andar: bloco * ANDARES_POR_BLOCO + indice + 1,
        bloco,
        nomeBloco: NOMES_BLOCO[bloco],
        tipo: sala.tipo,
      });
    });
  }

  andares.push({
    andar: ANDAR_FINAL,
    bloco: NUM_BLOCOS - 1,
    nomeBloco: NOMES_BLOCO[NUM_BLOCOS - 1],
    tipo: "final",
  });

  return andares;
}

// Salas que dao ponto de recompensa (D21: 5 elites + 5 chefes de bloco; o chefe do andar 51
// nao conta) e por isso abrem a tela de recompensa depois de vencidas.
export function salaDaRecompensa(tipo) {
  return tipo === "elite" || tipo === "chefe";
}
