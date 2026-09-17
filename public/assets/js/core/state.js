// Estado global do jogo. Fase 1 so tinha o catalogo e o combate avulso; Fase 2 acrescenta o
// estado da run (docs/04-arquitetura.md secao 5): HP persistente, andar atual, deck que
// cresce por recompensa, nivel da habilidade e modificadores do desafio opcional (D25).

import { montarBaralho } from "./combat.js";
import { gerarTorre } from "./tower.js";
import { criarRng, derivarSeed, embaralhar, escolher } from "./rng.js";
import { carregarCatalogoDoServidor } from "./api.js";

export const HP_INICIAL = 80;
export const MAX_NIVEL_HABILIDADE = 10; // 10 niveis reais nas tres habilidades, ver *_TEXTO abaixo
export const MAX_MODIFICADORES_POR_RUN = 5; // D25
export const CURA_DESCANSO_PCT = 0.3; // D07: cura escassa, so descanso e evento
export const CARTAS_INICIAIS_SORTEADAS = 5; // D18: sorteia 5 cartas do catalogo, 2 copias cada = 10
export const CLASSE_PADRAO = "capimaga";

// Texto de cada nivel das tres habilidades, portado de flet_mvp/capitower/content.py:CLASSES.
// O efeito mecanico de cada nivel mora em core/combat.js (lacaios/Adrenalina iniciais, gatilhos
// de Legiao/Casca Grossa/Ligeireza).
export const LEGIAO_TEXTO = {
  1: "Comeca o combate com 1 lacaio",
  2: "+1 lacaio inicial (2)",
  3: "+1 lacaio inicial (3)",
  4: "+1 lacaio inicial (4)",
  5: "Ao invocar, 20% de chance de invocar 1 a mais",
  6: "+1 lacaio inicial (5)",
  7: "+1 lacaio inicial (6)",
  8: "+1 lacaio inicial (7)",
  9: "Uma vez por combate, ao ficar sem lacaios, invoca 2",
  10: "Comeca o combate com o dobro de lacaios",
};

export const CASCA_GROSSA_TEXTO = {
  1: "Comeca cada combate com 2 de Adrenalina",
  2: "+1 de Adrenalina inicial (3)",
  3: "+1 de Adrenalina inicial (4)",
  4: "A primeira vez que perde vida no combate rende 2",
  5: "Ganha 1 tambem quando a Defesa absorve um ataque inteiro",
  6: "+1 de Adrenalina inicial (5)",
  7: "Teto de Adrenalina sobe de 10 para 15",
  8: "+1 de Adrenalina inicial (6)",
  9: "Ao cair a metade da vida, ganha 3 na hora (1x por combate)",
  10: "Toda Adrenalina ganha e dobrada",
};

export const LIGEIREZA_TEXTO = {
  1: "Ao jogar a 5a carta do turno, ganha +1 Acao",
  2: "Passa a ativar na 4a carta",
  3: "A ativacao tambem compra 1 carta",
  4: "Passa a ativar na 3a carta",
  5: "Comeca cada combate com +1 Acao no primeiro turno",
  6: "A ativacao passa a dar +2 Acao",
  7: "Passa a ativar na 2a carta",
  8: "A ativacao compra 2 cartas",
  9: "Ativa duas vezes por turno (a 2a exige o dobro)",
  10: "A primeira carta de cada turno custa 0",
};

export const HABILIDADE_TEXTOS = {
  capimaga: LEGIAO_TEXTO,
  brutamontes: CASCA_GROSSA_TEXTO,
  ligeira: LIGEIREZA_TEXTO,
};

export const HABILIDADE_NOMES = {
  capimaga: "Legiao",
  brutamontes: "Casca Grossa",
  ligeira: "Ligeireza",
};

export const estadoGlobal = {
  classes: null, // catalogo das 3 classes (nome/mecanica/habilidade), ver data/api/catalog/bootstrap.php
  catalogoCartas: null,
  inimigos: null, // { inimigos, blocos, finalId, fasesFinal }, ver data/enemy.json
  eventos: null,
  desafios: null,
  combate: null,
  run: null,
};

// Fase 4: o catalogo vem do banco via api/catalog/bootstrap.php, nao mais dos JSON estaticos
// em data/ (que continuam no repo so como seed/referencia, ver database/seeds.sql).
export async function carregarCatalogo() {
  const dados = await carregarCatalogoDoServidor();
  estadoGlobal.classes = dados.classes;
  estadoGlobal.catalogoCartas = dados.cartas;
  estadoGlobal.inimigos = dados.inimigos;
  estadoGlobal.eventos = dados.eventos;
  estadoGlobal.desafios = dados.desafios;
  return estadoGlobal;
}

// Cartas da classe escolhida dentro do catalogo desbloqueado (Fase 6: o catalogo tem as 3
// classes juntas, ver app/models/Catalog.php::cartas).
export function cartasDaClasse(classe) {
  return estadoGlobal.catalogoCartas.filter((carta) => carta.classe === classe);
}

export function gerarSeed() {
  return Date.now() >>> 0;
}

// ------------------------------------------------------------------------- ciclo de vida da run

export function novaRun(seed, classe = CLASSE_PADRAO) {
  // D18: o baralho comeca com 5 cartas sorteadas do catalogo da classe, 2 copias de cada (10
  // cartas). Gerador proprio (sal fixo), separado do de tower.js, para nao consumir a mesma
  // sequencia de numeros que gera a ordem da torre a partir da mesma seed.
  const rngBaralho = criarRng(derivarSeed(seed, 999));
  const cartasSorteadas = embaralhar(cartasDaClasse(classe), rngBaralho).slice(0, CARTAS_INICIAIS_SORTEADAS);

  const run = {
    seed,
    classe,
    andar: 0, // 0 = ainda nao entrou na torre, current() so vale com andar >= 1
    torre: gerarTorre(seed),
    hp: HP_INICIAL,
    hpMax: HP_INICIAL,
    forcaPermanente: 0,
    nivelHabilidade: 1,
    deck: montarBaralho(cartasSorteadas),
    cartasTemporarias: [], // D03/evento Vestiario: cartas que somem ao entrar no proximo chefe
    modificadores: [], // ids dos desafios ja escolhidos nesta run
    pontosRecompensa: 0,
    status: "jogando", // jogando | vitoria | derrota
    fraquezaProximoCombate: 0,
    curaDiferida: 0,
    chefesDerrotados: [], // slugs de chefe vencidos nesta run (Fase 5: avaliacao de objetivos)
    recompensasHabilidadeUsadas: 0, // Fase 5: objetivo "vitoria_sem_habilidade" conta essa escolha
  };
  estadoGlobal.run = run;
  return run;
}

// Marca chefes vencidos nesta run (Fase 5: meta progressao). Chamado depois de uma sala de
// chefe ou do chefao final terminar em vitoria; ids repetidos (ex: religar a mesma run) nao
// duplicam a lista.
export function registrarChefesDerrotados(run, ids) {
  for (const id of ids) {
    if (!run.chefesDerrotados.includes(id)) run.chefesDerrotados.push(id);
  }
}

export function andarAtual(run) {
  return run.torre[run.andar - 1];
}

export function avancarAndar(run) {
  run.andar += 1;
  return andarAtual(run);
}

// Um gerador novo por andar (e por "sal", quando o mesmo andar precisa de mais de um sorteio,
// por exemplo o evento e depois o combate). Deriva da seed da run, entao a run inteira continua
// reproduzivel a partir de um numero so (docs/04-arquitetura.md secao 5).
export function rngDoAndar(run, sal = 0) {
  return criarRng(derivarSeed(run.seed, run.andar * 1000 + sal));
}

// -------------------------------------------------------------------------------------- HP/cura

export function curar(run, valor) {
  const antes = run.hp;
  run.hp = Math.min(run.hpMax, run.hp + Math.max(0, Math.round(valor)));
  return run.hp - antes;
}

export function perderHp(run, valor) {
  run.hp = Math.max(1, run.hp - Math.max(0, Math.round(valor)));
}

export function descansar(run) {
  return curar(run, run.hpMax * CURA_DESCANSO_PCT);
}

// Sincroniza o HP da run com o resultado de um combate que acabou de terminar (D07: o HP
// persiste entre andares, entao o que sobrou do jogador vira o HP com que a run entra no
// proximo andar).
export function sincronizarHpPosCombate(run, estadoCombate) {
  run.hp = Math.max(0, estadoCombate.jogador.hp);
  run.hpMax = estadoCombate.jogador.hpMax;
}

// ------------------------------------------------------------------------------ recompensas

export function cartaAleatoria(run, rng) {
  const pool = cartasDaClasse(run.classe);
  return pool[Math.min(pool.length - 1, Math.floor(rng() * pool.length))];
}

export function adicionarCartaAoDeck(run, carta) {
  run.deck = [...run.deck, carta];
}

export function subirNivelHabilidade(run) {
  if (run.nivelHabilidade < MAX_NIVEL_HABILIDADE) run.nivelHabilidade += 1;
}

// ---------------------------------------------------------------------------- inimigos da sala

// Bestiario real por bloco (flet_mvp/capitower/content.py:ENEMIES/BLOCKS/FINAL_BOSS). Devolve a
// lista de defs de inimigo que entram juntos na sala (1 a 3 para combate comum e desafio, o
// elite do bloco, os 1 ou 2 chefes do bloco, ou a Soberana Gertrudes com as fases no andar 51).
function resolverDefInimigo(dados, id) {
  return { id, ...dados.inimigos[id] };
}

export function composicaoDaSala(sala, rng) {
  const dados = estadoGlobal.inimigos;
  if (sala.tipo === "final") {
    return [{ id: dados.finalId, ...dados.inimigos[dados.finalId], fases: dados.fasesFinal }];
  }
  const bloco = dados.blocos[sala.bloco];
  let ids;
  if (sala.tipo === "elite") {
    ids = [bloco.eliteId];
  } else if (sala.tipo === "chefe") {
    ids = bloco.chefeIds;
  } else {
    // combate, desafio: sorteia uma das composicoes comuns do bloco.
    ids = escolher(bloco.combates, rng);
  }
  return ids.map((id) => resolverDefInimigo(dados, id));
}

// -------------------------------------------------------------------------- desafio opcional

export function desafiosDisponiveis(run) {
  return estadoGlobal.desafios.filter((d) => !run.modificadores.includes(d.id));
}

export function podeOferecerDesafio(run) {
  return run.modificadores.length < MAX_MODIFICADORES_POR_RUN && desafiosDisponiveis(run).length > 0;
}

export function aplicarModificador(run, desafio) {
  run.modificadores.push(desafio.id);
  const { op, valor } = desafio.efeito;
  if (op === "forca_permanente") {
    run.forcaPermanente += valor;
  } else if (op === "hp_max_permanente") {
    run.hpMax += valor;
    curar(run, valor);
  }
}

// ------------------------------------------------------------------------------------ eventos

export function aplicarEfeitoEvento(run, efeito, rng) {
  if (efeito.op === "curar_pct") {
    curar(run, run.hpMax * efeito.valor);
  } else if (efeito.op === "curar_pct_diferido") {
    run.curaDiferida += run.hpMax * efeito.valor;
  } else if (efeito.op === "chance_fraqueza") {
    if (rng() < efeito.chance) run.fraquezaProximoCombate += efeito.valor;
  } else if (efeito.op === "perder_hp") {
    perderHp(run, efeito.valor);
  } else if (efeito.op === "forca_permanente") {
    run.forcaPermanente += efeito.valor;
  } else if (efeito.op === "carta_temporaria") {
    // Evento Vestiario: ganha 1 copia extra de uma carta aleatoria da classe, so ate o proximo
    // chefe de bloco (removida em removerCartasTemporarias). A copia e um clone com uma marca
    // propria, para nao remover por engano uma copia "de verdade" da mesma carta.
    const original = cartaAleatoria(run, rng);
    const copia = { ...original, _temporaria: true };
    adicionarCartaAoDeck(run, copia);
    run.cartasTemporarias.push(copia);
  }
  // "nada" nao faz nada de proposito.
}

// Remove do deck as copias temporarias ainda nao usadas (evento Vestiario). Chamado ao entrar
// numa sala de chefe de bloco ou no chefao final, "ate o proximo chefe" (docs/03-conteudo.md
// secao 7).
export function removerCartasTemporarias(run) {
  if (run.cartasTemporarias.length === 0) return;
  const temporarias = new Set(run.cartasTemporarias);
  run.deck = run.deck.filter((carta) => !temporarias.has(carta));
  run.cartasTemporarias = [];
}

// Aplica os efeitos pendentes de evento (cura diferida, fraqueza do proximo combate) bem no
// comeco do combate seguinte e limpa os dois, para nao vazar para o combate depois desse.
export function consumirEfeitosPendentes(run) {
  const fraqueza = run.fraquezaProximoCombate;
  if (run.curaDiferida > 0) {
    curar(run, run.curaDiferida);
    run.curaDiferida = 0;
  }
  run.fraquezaProximoCombate = 0;
  return { fraqueza };
}

// ------------------------------------------------------------------------- save/load (Fase 4)

// Converte a run para o snapshot que o servidor guarda em runs.estado_json
// (docs/04-arquitetura.md secao 5). Desvio do exemplo da secao 5: "deck" e uma lista de
// {id, temporaria} em vez de ids soltos, porque o id real da carta e um slug (string) e uma
// copia temporaria do evento Vestiario precisa ficar marcavel por copia, nao so por id.
export function serializarRun(run) {
  return {
    versao: 1,
    classe: run.classe,
    seed: run.seed,
    andar: run.andar,
    hp: run.hp,
    hp_max: run.hpMax,
    forca_permanente: run.forcaPermanente,
    nivel_habilidade: run.nivelHabilidade,
    deck: run.deck.map((carta) => ({ id: carta.id, temporaria: Boolean(carta._temporaria) })),
    modificadores: run.modificadores,
    pontos_recompensa: run.pontosRecompensa,
    status: run.status,
    fraqueza_proximo_combate: run.fraquezaProximoCombate,
    cura_diferida: run.curaDiferida,
    chefes_derrotados: run.chefesDerrotados,
    recompensas_habilidade: run.recompensasHabilidadeUsadas,
  };
}

// Reconstroi a run a partir do snapshot salvo. A torre nao e salva, e derivada de novo da
// seed (docs secao 5); o deck e remontado buscando cada id no catalogo ja carregado.
export function restaurarRun(estadoJson) {
  const deck = estadoJson.deck.map((item) => {
    const original = estadoGlobal.catalogoCartas.find((carta) => carta.id === item.id);
    return item.temporaria ? { ...original, _temporaria: true } : original;
  });

  const run = {
    seed: estadoJson.seed,
    classe: estadoJson.classe ?? CLASSE_PADRAO,
    andar: estadoJson.andar,
    torre: gerarTorre(estadoJson.seed),
    hp: estadoJson.hp,
    hpMax: estadoJson.hp_max,
    forcaPermanente: estadoJson.forca_permanente,
    nivelHabilidade: estadoJson.nivel_habilidade,
    deck,
    cartasTemporarias: deck.filter((carta) => carta._temporaria),
    modificadores: estadoJson.modificadores,
    pontosRecompensa: estadoJson.pontos_recompensa,
    status: estadoJson.status,
    fraquezaProximoCombate: estadoJson.fraqueza_proximo_combate,
    curaDiferida: estadoJson.cura_diferida,
    chefesDerrotados: estadoJson.chefes_derrotados ?? [],
    recompensasHabilidadeUsadas: estadoJson.recompensas_habilidade ?? 0,
  };
  estadoGlobal.run = run;
  return run;
}
