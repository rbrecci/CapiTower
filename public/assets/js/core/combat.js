// Motor de combate. Roda inteiro no cliente (docs/04-arquitetura.md secao 2).
// Porta o vocabulario e os numeros de flet_mvp/capitower/combat.py para o formato de
// efeito em JSON. Fase 3 troca o inimigo unico da Fase 1/2 por uma lista de inimigos
// (necessario para o chefe Gemeos Rosca Direta, que herda Forca do irmao ao morrer, e
// para o bestiario de verdade, que poe mais de um inimigo na mesma sala de combate comum).
// Fase 6 acrescenta as mecanicas exclusivas de Brutamontes (Adrenalina, Casca Grossa,
// Retaliacao) e Ligeira (Impulso, Ligeireza, Evasao), guardadas atras de checagens de
// `jogador.classe` para nao mudar nada do comportamento da Capimaga (flet_mvp/capitower/
// combat.py e a fonte da verdade dos tres, ver docs/02-classes-e-arquetipos.md).

import { criarRng, embaralhar, inteiroAleatorio } from "./rng.js";
import { resolverEfeitos } from "./effects.js";

export const ACAO_POR_TURNO = 3;
export const TAMANHO_MAO = 5;
export const LACAIOS_CAP = 10;
export const MORDIDA_LACAIO = 2; // dano de cada lacaio no fim do turno do jogador
export const COPIAS_POR_CARTA = 2; // D18: cada carta sorteada do baralho inicial entra em 2 copias
export const ADRENALINA_CAP_BASE = 10;
export const ADRENALINA_CAP_NIVEL7 = 15; // Casca Grossa nivel 7: teto sobe de 10 para 15

// Legiao: lacaios iniciais por nivel de habilidade (flet_mvp/capitower/combat.py:_setup_class).
// Nivel 5+: 20% de chance de invocar 1 lacaio a mais toda vez que invoca (ver invocarLacaios).
// Nivel 9+: uma vez por combate, ao ficar com 0 lacaios depois de consumir, invoca 2 (ver
// verificarLegiao9). Nivel 10: comeca com o dobro da tabela.
const TABELA_LACAIOS_INICIAIS = { 1: 1, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6, 8: 7, 9: 7, 10: 7 };

// Casca Grossa: Adrenalina inicial por nivel (flet_mvp/capitower/combat.py:_setup_class).
const TABELA_ADRENALINA_INICIAL = { 1: 2, 2: 3, 3: 4, 4: 4, 5: 4, 6: 5, 7: 5, 8: 6, 9: 6, 10: 6 };

function lacaiosIniciaisPorNivel(nivel) {
  const base = TABELA_LACAIOS_INICIAIS[nivel] ?? 1;
  const total = base * (nivel >= 10 ? 2 : 1);
  return Math.min(LACAIOS_CAP, total);
}

export function montarBaralho(cartas) {
  const baralho = [];
  for (const carta of cartas) {
    for (let i = 0; i < COPIAS_POR_CARTA; i++) baralho.push(carta);
  }
  return baralho;
}

function criarInimigo(def, rng) {
  const flags = def.flags ?? {};
  const podeAleatorizar = def.padrao.length > 1 && !flags.chefe && !flags.inicioFixo;
  return {
    id: def.id,
    nome: def.nome,
    nota: def.nota ?? "",
    hp: def.hp,
    hpMax: def.hp,
    bloco: 0,
    forca: 0,
    fraqueza: 0,
    fragilidade: 0,
    veneno: 0,
    padrao: def.padrao,
    indice: podeAleatorizar ? inteiroAleatorio(rng, def.padrao.length) : 0,
    flags,
    fase: 0,
    fasesDef: def.fases ?? null,
  };
}

// composicao: lista de defs de inimigo (1 a 3, ver core/state.js:composicaoDaSala) que entram
// juntos na sala. HP e o que sobrou do andar anterior (D07): a run inteira usa esta funcao.
export function criarCombateDeSala({
  baralho,
  composicao,
  seed,
  hpAtual,
  hpMax,
  forcaBonus = 0,
  fraquezaInicial = 0,
  nivelHabilidade = 1,
  classe = "capimaga",
  modificadores = [],
}) {
  const rng = criarRng(seed >>> 0);
  const lacaiosIniciais = classe === "capimaga" ? lacaiosIniciaisPorNivel(nivelHabilidade) : 0;
  const adrenalinaCap = nivelHabilidade >= 7 ? ADRENALINA_CAP_NIVEL7 : ADRENALINA_CAP_BASE;
  const adrenalinaInicial = classe === "brutamontes" ? Math.min(adrenalinaCap, TABELA_ADRENALINA_INICIAL[nivelHabilidade] ?? 2) : 0;
  const estado = {
    turno: 0,
    status: "andamento", // andamento | vitoria | derrota
    log: [],
    rng,
    modificadores, // ids dos desafios opcionais ativos na run (D25), ver core/state.js:aplicarModificador
    jogador: {
      classe,
      hp: hpAtual,
      hpMax,
      bloco: 0,
      forca: forcaBonus,
      fraqueza: fraquezaInicial,
      fraquezaFresca: fraquezaInicial > 0,
      fragilidade: 0,
      fragilidadeFresca: false,
      veneno: 0,
      acao: 0,
      acaoMax: ACAO_POR_TURNO,
      roubarProximo: 0,
      lacaios: lacaiosIniciais,
      lacaiosCap: LACAIOS_CAP,
      adrenalina: adrenalinaInicial,
      adrenalinaCap,
      primeiraPerdaUsada: false,
      metadeVidaUsada: false,
      retaliacao: 0,
      retaliacaoTurnos: 0,
      evasao: 0,
      ligeirezaGatilhos: 0,
      ultimaJogada: null,
      proximaGratis: false,
      nivelHabilidade,
      legiao9Usado: false,
      poderes: [],
      manterBloco: false,
      cartasJogadasNoTurno: 0,
    },
    inimigos: composicao.map((def) => criarInimigo(def, rng)),
    alvo: 0,
    compra: embaralhar(baralho.slice(), rng),
    mao: [],
    descarte: [],
  };
  if (lacaiosIniciais > 0) {
    estado.log.push(`Legiao: comeca com ${lacaiosIniciais} lacaio(s).`);
  }
  if (classe === "brutamontes") {
    estado.log.push(`Casca Grossa: comeca com ${adrenalinaInicial} de Adrenalina.`);
  }
  if (fraquezaInicial > 0) {
    estado.log.push(`Chega neste combate com Fraqueza ${fraquezaInicial}.`);
  }
  iniciarTurnoJogador(estado);
  return estado;
}

// Combate avulso de 1 inimigo so, sem torre (Fase 1). Mantido por compatibilidade.
export function criarCombate(catalogoCartas, defInimigo, seed) {
  return criarCombateDeSala({
    baralho: montarBaralho(catalogoCartas),
    composicao: [defInimigo],
    seed,
    hpAtual: 80,
    hpMax: 80,
  });
}

// ------------------------------------------------------------- compra / mao
export function comprarCartas(estado, n) {
  for (let i = 0; i < n; i++) {
    if (estado.compra.length === 0) {
      if (estado.descarte.length === 0) return;
      estado.compra = embaralhar(estado.descarte, estado.rng);
      estado.descarte = [];
      estado.log.push("Reembaralha o descarte.");
    }
    estado.mao.push(estado.compra.pop());
  }
}

function descartarMao(estado) {
  estado.descarte.push(...estado.mao);
  estado.mao = [];
}

// -------------------------------------------------------------------- alvo
export function inimigosVivos(estado) {
  return estado.inimigos.filter((e) => e.hp > 0);
}

// Sempre devolve um inimigo vivo (ou null se a sala esta limpa), reapontando estado.alvo se o
// alvo atual acabou de cair (docs/04-arquitetura.md; espelha Combat._target do Python).
export function alvoAtual(estado) {
  const atual = estado.inimigos[estado.alvo];
  if (atual && atual.hp > 0) return atual;
  const vivos = inimigosVivos(estado);
  if (vivos.length === 0) return null;
  estado.alvo = estado.inimigos.indexOf(vivos[0]);
  return vivos[0];
}

export function selecionarAlvo(estado, indice) {
  if (indice >= 0 && indice < estado.inimigos.length && estado.inimigos[indice].hp > 0) {
    estado.alvo = indice;
  }
}

// Resolve a lista de entidades que um efeito de carta afeta a partir do campo "alvo".
export function entidadesAlvo(estado, alvo) {
  if (alvo === "todos") return inimigosVivos(estado);
  if (alvo === "jogador") return [estado.jogador];
  const atual = alvoAtual(estado);
  return atual ? [atual] : [];
}

// --------------------------------------------------------------- resolucao
export function causarDano(estado, alvo, valorBase) {
  let dmg = valorBase + estado.jogador.forca;
  if (estado.jogador.fraqueza > 0) dmg = Math.floor(dmg * 0.75);
  const alvos = entidadesAlvo(estado, alvo);
  if (alvos.length === 0) {
    estado.log.push("Sem alvo vivo. Nada acontece.");
    return;
  }
  for (const entidade of alvos) aplicarDanoInimigo(estado, entidade, dmg, true);
}

function processarQuedaInimigo(estado, inimigo) {
  estado.log.push(`${inimigo.nome} cai!`);
  if (inimigo.flags.gemeo) {
    for (const outro of inimigosVivos(estado)) {
      if (outro.flags.gemeo) {
        outro.forca += inimigo.flags.gemeo;
        estado.log.push(`${outro.nome} herda +${inimigo.flags.gemeo} de Forca!`);
      }
    }
  }
}

function atualizarFaseGertrudes(estado, inimigo) {
  if (!inimigo.flags.fases || inimigo.hp <= 0 || !inimigo.fasesDef) return;
  const fracao = inimigo.hp / inimigo.hpMax;
  for (let i = 0; i < inimigo.fasesDef.length; i++) {
    const fase = inimigo.fasesDef[i];
    if (fracao > fase.fracaoMin) {
      if (i > inimigo.fase) {
        inimigo.fase = i;
        inimigo.padrao = fase.padrao;
        inimigo.indice = 0;
        estado.log.push(`${inimigo.nome} muda de postura! (fase ${i + 1})`);
      }
      return;
    }
  }
}

function absorverOuPerderJogador(estado, dano) {
  const absorvido = Math.min(estado.jogador.bloco, dano);
  estado.jogador.bloco -= absorvido;
  const passou = dano - absorvido;
  if (passou > 0) {
    perderVidaJogador(estado, passou);
  }
}

function aplicarDanoInimigo(estado, inimigo, dmg, ehAtaque) {
  if (inimigo.hp <= 0 || dmg <= 0) return;
  let dmgFinal = dmg;
  if (ehAtaque && inimigo.fragilidade > 0) dmgFinal = Math.floor(dmgFinal * 1.5);
  const absorvido = Math.min(inimigo.bloco, dmgFinal);
  inimigo.bloco -= absorvido;
  const passou = dmgFinal - absorvido;
  inimigo.hp -= passou;
  const sufixo = absorvido > 0 ? ` (${absorvido} no Bloco)` : "";
  estado.log.push(`${inimigo.nome} recebe ${passou} de dano${sufixo}.`);

  if (inimigo.hp <= 0) {
    inimigo.hp = 0;
    processarQuedaInimigo(estado, inimigo);
    verificarFim(estado);
    return;
  }

  if (ehAtaque && passou > 0) {
    if (inimigo.flags.reflete) {
      const volta = Math.floor(passou * inimigo.flags.reflete);
      if (volta > 0) {
        estado.log.push(`${inimigo.nome} reflete ${volta}.`);
        absorverOuPerderJogador(estado, volta);
      }
    }
    if (inimigo.flags.espinhos) {
      estado.log.push(`${inimigo.nome} contra ataca com ${inimigo.flags.espinhos}.`);
      absorverOuPerderJogador(estado, inimigo.flags.espinhos);
    }
    if (inimigo.flags.mudaPadrao) {
      inimigo.indice += 1;
    }
  }
  atualizarFaseGertrudes(estado, inimigo);
  verificarFim(estado);
}

export function ganharBloco(estado, quem, valor) {
  if (valor <= 0) return;
  let total = valor;
  if (quem === "jogador") {
    // Desafio "Casco Duro" (flet_mvp/capitower/content.py:MODIFIERS): +1 em todo ganho de Bloco
    // do jogador. Fica aqui, no unico lugar por onde todo bloco do jogador passa (cartas e
    // poderes como Calo/Ossos Firmes), em vez de espalhar a checagem em cada efeito.
    if (estado.modificadores?.includes("casco_duro")) total += 1;
    estado.jogador.bloco += total;
  } else {
    const alvo = alvoAtual(estado);
    if (alvo) alvo.bloco += total;
  }
  estado.log.push(`+${total} de Bloco.`);
}

export function aplicarEstado(estado, alvo, nomeEstado, valor) {
  const alvos = entidadesAlvo(estado, alvo);
  for (const entidade of alvos) {
    if (nomeEstado in entidade) entidade[nomeEstado] += valor;
  }
  if (alvos.length === 0) return;
  const nomeAlvo = alvo === "todos" ? "Todos os inimigos" : alvo === "jogador" ? "Voce" : alvos[0].nome;
  estado.log.push(`${nomeAlvo} recebe ${nomeEstado} ${valor}.`);
}

export function manterBloco(estado) {
  estado.jogador.manterBloco = true;
  estado.log.push("O Bloco fica para o proximo turno.");
}

export function espalharVeneno(estado) {
  const alvo = alvoAtual(estado);
  if (alvo && alvo.veneno > 0) {
    for (const outro of inimigosVivos(estado)) {
      if (outro !== alvo && outro.veneno < alvo.veneno) outro.veneno = alvo.veneno;
    }
    estado.log.push(`Contagio: Veneno ${alvo.veneno} se espalha.`);
  } else {
    estado.log.push("O alvo nao esta envenenado. Nada para espalhar.");
  }
}

export function registrarPoder(estado, nome) {
  if (!estado.jogador.poderes.includes(nome)) {
    estado.jogador.poderes.push(nome);
  }
  estado.log.push("Poder em campo.");
}

// ------------------------------------------------------------------- Brutamontes: Adrenalina
export function ganharAdrenalina(estado, n) {
  if (estado.jogador.classe !== "brutamontes" || n <= 0) return;
  const nivel = estado.jogador.nivelHabilidade;
  const total = nivel >= 10 ? n * 2 : n;
  const antes = estado.jogador.adrenalina;
  estado.jogador.adrenalina = Math.min(estado.jogador.adrenalinaCap, estado.jogador.adrenalina + total);
  const ganho = estado.jogador.adrenalina - antes;
  if (ganho > 0) estado.log.push(`+${ganho} de Adrenalina.`);
}

export function consumirAdrenalina(estado, n) {
  const usados = Math.min(n, estado.jogador.adrenalina);
  estado.jogador.adrenalina -= usados;
  if (usados > 0) {
    estado.log.push(`Gasta ${usados} de Adrenalina.`);
    if (estado.jogador.poderes.includes("pavio_curto")) {
      for (const inimigo of inimigosVivos(estado)) {
        aplicarDanoInimigo(estado, inimigo, usados, false);
      }
    }
  }
  return usados;
}

// Perda de vida direta (nao passa por Bloco): cartas "perder_vida" e o dano que atravessou o
// Bloco em receberAtaque/venenoTickJogador. Espelha flet_mvp/capitower/combat.py:_lose_hp,
// incluindo o gatilho de Adrenalina da Brutamontes (so acontece nessa classe) e Olho por Olho.
export function perderVidaJogador(estado, valor, { deAtaque = false, atacante = null } = {}) {
  if (valor <= 0) return;
  estado.jogador.hp -= valor;
  estado.log.push(`Voce perde ${valor} de vida.`);
  if (estado.jogador.classe === "brutamontes") {
    let ganho = 1;
    if (estado.jogador.nivelHabilidade >= 4 && !estado.jogador.primeiraPerdaUsada) ganho = 2;
    estado.jogador.primeiraPerdaUsada = true;
    if (estado.jogador.poderes.includes("rugido")) ganho += 1;
    ganharAdrenalina(estado, ganho);
    if (
      estado.jogador.nivelHabilidade >= 9 &&
      !estado.jogador.metadeVidaUsada &&
      estado.jogador.hp <= estado.jogador.hpMax / 2
    ) {
      estado.jogador.metadeVidaUsada = true;
      ganharAdrenalina(estado, 3);
    }
  }
  if (deAtaque && atacante && atacante.hp > 0 && estado.jogador.poderes.includes("olho_por_olho")) {
    aplicarDanoInimigo(estado, atacante, 3, false);
  }
  if (estado.jogador.hp <= 0) {
    estado.jogador.hp = 0;
    estado.status = "derrota";
    estado.log.push("Voce caiu.");
  }
}

// -------------------------------------------------------------------------- Ligeira: Ligeireza
function verificarLigeireza(estado) {
  if (estado.jogador.classe !== "ligeira") return;
  const nivel = estado.jogador.nivelHabilidade;
  let limiar = 5;
  if (nivel >= 2) limiar = 4;
  if (nivel >= 4) limiar = 3;
  if (nivel >= 7) limiar = 2;
  const maxGatilhos = nivel >= 9 ? 2 : 1;
  if (estado.jogador.ligeirezaGatilhos >= maxGatilhos) return;
  const necessario = limiar * (estado.jogador.ligeirezaGatilhos + 1);
  if (estado.jogador.cartasJogadasNoTurno < necessario) return;
  estado.jogador.ligeirezaGatilhos += 1;
  const ganho = nivel >= 6 ? 2 : 1;
  estado.jogador.acao += ganho;
  let msg = `Ligeireza: +${ganho} Acao`;
  if (nivel >= 8) {
    comprarCartas(estado, 2);
    msg += ", compra 2";
  } else if (nivel >= 3) {
    comprarCartas(estado, 1);
    msg += ", compra 1";
  }
  estado.log.push(msg + ".");
}

export function invocarLacaios(estado, n) {
  if (n <= 0) return;
  let total = n;
  if (estado.jogador.nivelHabilidade >= 5 && estado.rng() < 0.2) {
    total += 1;
    estado.log.push("Legiao: lacaio extra!");
  }
  const antes = estado.jogador.lacaios;
  estado.jogador.lacaios = Math.min(estado.jogador.lacaiosCap, estado.jogador.lacaios + total);
  const ganhos = estado.jogador.lacaios - antes;
  if (ganhos > 0) estado.log.push(`Invoca ${ganhos} lacaio(s).`);
}

function verificarLegiao9(estado) {
  if (
    estado.jogador.nivelHabilidade >= 9 &&
    estado.jogador.lacaios === 0 &&
    !estado.jogador.legiao9Usado
  ) {
    estado.jogador.legiao9Usado = true;
    estado.jogador.lacaios = 2;
    estado.log.push("Legiao: sem lacaios, invoca 2.");
  }
}

export function consumirLacaios(estado, n) {
  const usados = Math.min(n, estado.jogador.lacaios);
  estado.jogador.lacaios -= usados;
  if (usados > 0) {
    estado.log.push(`Consome ${usados} lacaio(s).`);
    if (estado.jogador.poderes.includes("banquete")) {
      comprarCartas(estado, 1);
      estado.log.push("Banquete: compra 1.");
    }
  }
  verificarLegiao9(estado);
  return usados;
}

// ---------------------------------------------------------------- jogador
// Ligeira nivel 10: a primeira carta de cada turno custa 0. "proxima_gratis" (Golpe Baixo,
// Baralho Marcado) tem prioridade e vale para qualquer classe (flet_mvp/capitower/combat.py:
// cost_of).
export function custoDe(estado, carta) {
  if (estado.jogador.proximaGratis) return 0;
  if (
    estado.jogador.classe === "ligeira" &&
    estado.jogador.nivelHabilidade >= 10 &&
    estado.jogador.cartasJogadasNoTurno === 0
  ) {
    return 0;
  }
  return carta.custo;
}

function nomePoder(carta) {
  const efeito = carta.efeitos.find((e) => e.op === "poder");
  return efeito ? efeito.nome : null;
}

export function motivoBloqueio(estado, carta) {
  if (estado.status !== "andamento") return "Combate encerrado";
  if (carta.tipo === "Poder") {
    const nome = nomePoder(carta);
    if (nome && estado.jogador.poderes.includes(nome)) return "Poder ja em campo";
  }
  if (estado.jogador.acao < custoDe(estado, carta)) return "Acao insuficiente";
  return null;
}

export function podeJogar(estado, carta) {
  return motivoBloqueio(estado, carta) === null;
}

export function jogarCarta(estado, indiceMao) {
  if (estado.status !== "andamento" || indiceMao < 0 || indiceMao >= estado.mao.length) return;
  const carta = estado.mao[indiceMao];
  const motivo = motivoBloqueio(estado, carta);
  if (motivo) {
    estado.log.push(motivo + ".");
    return;
  }
  estado.jogador.acao -= custoDe(estado, carta);
  estado.jogador.proximaGratis = false;
  estado.mao.splice(indiceMao, 1);
  const ctx = { consumidos: 0, impulso: estado.jogador.cartasJogadasNoTurno };
  estado.log.push(`Joga ${carta.nome}.`);
  resolverEfeitos(estado, carta.efeitos, ctx);
  if (carta.tipo !== "Poder") {
    estado.descarte.push(carta);
  }
  estado.jogador.cartasJogadasNoTurno += 1;
  if (carta.custo > 0 && !carta.efeitos.some((e) => e.op === "devolver_ultima")) {
    estado.jogador.ultimaJogada = carta;
  }
  if (estado.jogador.poderes.includes("segundo_folego") && estado.jogador.cartasJogadasNoTurno === 3) {
    comprarCartas(estado, 1);
    estado.log.push("Segundo Folego: compra 1.");
  }
  if (
    estado.jogador.poderes.includes("golpe_de_vista") &&
    estado.jogador.cartasJogadasNoTurno === 4 &&
    inimigosVivos(estado).length > 0
  ) {
    estado.log.push("Golpe de Vista!");
    causarDano(estado, "inimigo", 6);
  }
  verificarLigeireza(estado);
  verificarFim(estado);
}

// ------------------------------------------------------------------ turno
function iniciarTurnoJogador(estado) {
  estado.turno += 1;
  if (!estado.jogador.manterBloco) estado.jogador.bloco = 0;
  estado.jogador.manterBloco = false;
  if (estado.jogador.poderes.includes("calo") && estado.jogador.adrenalina >= 2) {
    const ganho = Math.floor(estado.jogador.adrenalina / 2);
    ganharBloco(estado, "jogador", ganho);
    estado.log.push(`Calo: +${ganho} de Bloco.`);
  }
  if (estado.jogador.poderes.includes("vala_comum")) {
    invocarLacaios(estado, 1);
  }
  estado.jogador.acao = ACAO_POR_TURNO - estado.jogador.roubarProximo;
  estado.jogador.roubarProximo = 0;
  estado.jogador.cartasJogadasNoTurno = 0;
  estado.jogador.ultimaJogada = null;
  estado.jogador.proximaGratis = false;
  estado.jogador.ligeirezaGatilhos = 0;
  if (estado.jogador.fraqueza > 0 && !estado.jogador.fraquezaFresca) estado.jogador.fraqueza -= 1;
  if (estado.jogador.fragilidade > 0 && !estado.jogador.fragilidadeFresca) estado.jogador.fragilidade -= 1;
  estado.jogador.fraquezaFresca = false;
  estado.jogador.fragilidadeFresca = false;
  if (estado.jogador.retaliacaoTurnos > 0) {
    estado.jogador.retaliacaoTurnos -= 1;
    if (estado.jogador.retaliacaoTurnos === 0) estado.jogador.retaliacao = 0;
  }
  if (estado.turno === 1 && estado.jogador.classe === "ligeira" && estado.jogador.nivelHabilidade >= 5) {
    estado.jogador.acao += 1;
  }
  // Desafios "Largada" e "Mao Firme" (flet_mvp/capitower/content.py:MODIFIERS): so no primeiro
  // turno de cada combate, nao em todo turno.
  if (estado.turno === 1 && estado.modificadores?.includes("largada")) {
    estado.jogador.acao += 1;
  }
  comprarCartas(estado, TAMANHO_MAO);
  if (estado.turno === 1 && estado.modificadores?.includes("mao_firme")) {
    comprarCartas(estado, 1);
    estado.log.push("Mao Firme: compra 1 carta extra.");
  }
  estado.log.push(`--- Turno ${estado.turno} ---`);
}

function mordidaDosLacaios(estado) {
  if (estado.jogador.lacaios <= 0) return;
  let total = 0;
  for (let i = 0; i < estado.jogador.lacaios; i++) {
    const vivos = inimigosVivos(estado);
    if (vivos.length === 0) break;
    const alvo = vivos[inteiroAleatorio(estado.rng, vivos.length)];
    aplicarDanoInimigo(estado, alvo, MORDIDA_LACAIO, false);
    total += 1;
  }
  if (total > 0) estado.log.push(`Lacaios morderam ${total} vez(es).`);
}

function venenoTickJogador(estado) {
  if (estado.jogador.veneno <= 0) return;
  perderVidaJogador(estado, estado.jogador.veneno);
  estado.jogador.veneno -= 1;
  verificarFim(estado);
}

function receberAtaque(estado, inimigo, valorBase) {
  let dmg = valorBase + inimigo.forca;
  if (inimigo.fraqueza > 0) dmg = Math.floor(dmg * 0.75);
  if (estado.jogador.fragilidade > 0) dmg = Math.floor(dmg * 1.5);
  if (estado.jogador.evasao > 0) {
    estado.jogador.evasao -= 1;
    estado.log.push(`Evasao anula o ataque de ${inimigo.nome}.`);
    if (estado.jogador.poderes.includes("rastro")) {
      comprarCartas(estado, 1);
      estado.log.push("Rastro de Lama: compra 1.");
    }
    return;
  }
  const absorvido = Math.min(estado.jogador.bloco, dmg);
  estado.jogador.bloco -= absorvido;
  const passou = dmg - absorvido;
  if (passou === 0 && dmg > 0) {
    estado.log.push(`Bloco absorve ${absorvido} de ${inimigo.nome}.`);
    if (estado.jogador.classe === "brutamontes" && estado.jogador.nivelHabilidade >= 5) {
      ganharAdrenalina(estado, 1);
    }
  } else if (passou > 0) {
    if (absorvido > 0) estado.log.push(`Bloco absorve ${absorvido}.`);
    perderVidaJogador(estado, passou, { deAtaque: true, atacante: inimigo });
  }
  if (estado.jogador.retaliacao > 0) {
    aplicarDanoInimigo(estado, inimigo, estado.jogador.retaliacao, false);
  }
}

function agirUmInimigo(estado, inimigo) {
  if (inimigo.hp <= 0 || estado.status !== "andamento") return;
  inimigo.bloco = 0;
  if (inimigo.flags.blocoTodoTurno) {
    inimigo.bloco += inimigo.flags.blocoTodoTurno;
    estado.log.push(`${inimigo.nome} ganha ${inimigo.flags.blocoTodoTurno} de Bloco.`);
  }
  const acoes = intentAtual(inimigo);
  for (const acao of acoes) {
    if (estado.status !== "andamento" || inimigo.hp <= 0) return;
    const vezes = acao.vezes ?? 1;
    if (acao.tipo === "ataque") {
      for (let i = 0; i < vezes; i++) {
        receberAtaque(estado, inimigo, acao.valor);
        if (estado.status !== "andamento") break;
      }
    } else if (acao.tipo === "bloco") {
      inimigo.bloco += acao.valor;
    } else if (acao.tipo === "forca") {
      inimigo.forca += acao.valor;
      estado.log.push(`${inimigo.nome} ganha +${acao.valor} de Forca.`);
    } else if (acao.tipo === "forca_todos") {
      for (const outro of inimigosVivos(estado)) outro.forca += acao.valor;
      estado.log.push(`${inimigo.nome} buffa a sala (+${acao.valor} Forca).`);
    } else if (acao.tipo === "fraqueza") {
      estado.jogador.fraqueza += acao.valor;
      estado.jogador.fraquezaFresca = true;
      estado.log.push(`${inimigo.nome} aplica Fraqueza ${acao.valor}.`);
    } else if (acao.tipo === "fragilidade") {
      estado.jogador.fragilidade += acao.valor;
      estado.jogador.fragilidadeFresca = true;
      estado.log.push(`${inimigo.nome} aplica Fragilidade ${acao.valor}.`);
    } else if (acao.tipo === "veneno") {
      estado.jogador.veneno += acao.valor;
      estado.log.push(`${inimigo.nome} aplica Veneno ${acao.valor}.`);
    } else if (acao.tipo === "curar") {
      const antes = inimigo.hp;
      inimigo.hp = Math.min(inimigo.hpMax, inimigo.hp + acao.valor);
      estado.log.push(`${inimigo.nome} cura ${inimigo.hp - antes}.`);
    } else if (acao.tipo === "curar_todos") {
      for (const outro of inimigosVivos(estado)) outro.hp = Math.min(outro.hpMax, outro.hp + acao.valor);
      estado.log.push(`${inimigo.nome} cura a sala em ${acao.valor}.`);
    } else if (acao.tipo === "roubar") {
      estado.jogador.roubarProximo += acao.valor;
      estado.log.push(`${inimigo.nome} rouba ${acao.valor} Acao do proximo turno.`);
    } else if (acao.tipo === "carregar") {
      // nada agora: so telegrafa o golpe do proximo turno na intencao.
    }
    verificarFim(estado);
  }
  if (inimigo.hp > 0) {
    inimigo.indice += 1;
    if (inimigo.flags.crescimento) inimigo.forca += inimigo.flags.crescimento;
  }
}

export function intentAtual(inimigo) {
  return inimigo.padrao[inimigo.indice % inimigo.padrao.length];
}

export function fimDeTurno(estado) {
  if (estado.status !== "andamento") return;

  mordidaDosLacaios(estado);
  if (estado.status === "andamento" && estado.jogador.poderes.includes("ossos_firmes") && estado.jogador.lacaios > 0) {
    ganharBloco(estado, "jogador", estado.jogador.lacaios);
    estado.log.push(`Ossos Firmes: +${estado.jogador.lacaios} de Bloco.`);
  }
  if (estado.status === "andamento" && estado.jogador.poderes.includes("peste")) {
    for (const inimigo of inimigosVivos(estado)) inimigo.veneno += 2;
    estado.log.push("Peste Ossea: Veneno 2 em todos.");
  }
  if (estado.status === "andamento") venenoTickJogador(estado);
  let guardada = null;
  if (estado.jogador.poderes.includes("bolso_fundo") && estado.mao.length > 0) {
    const indice = inteiroAleatorio(estado.rng, estado.mao.length);
    guardada = estado.mao[indice];
    estado.mao.splice(indice, 1);
    estado.log.push(`Bolso Fundo: guarda ${guardada.nome}.`);
  }
  descartarMao(estado);
  if (guardada) estado.mao.push(guardada);
  verificarFim(estado);
  if (estado.status !== "andamento") return;

  for (const inimigo of inimigosVivos(estado)) {
    if (estado.status !== "andamento") break;
    agirUmInimigo(estado, inimigo);
  }
  verificarFim(estado);
  if (estado.status !== "andamento") return;

  for (const inimigo of inimigosVivos(estado)) {
    if (inimigo.veneno > 0) {
      inimigo.hp -= inimigo.veneno;
      estado.log.push(`${inimigo.nome} sofre ${inimigo.veneno} de Veneno.`);
      inimigo.veneno -= 1;
      if (inimigo.hp <= 0) {
        inimigo.hp = 0;
        processarQuedaInimigo(estado, inimigo);
      } else {
        atualizarFaseGertrudes(estado, inimigo);
      }
    }
    if (inimigo.hp > 0) {
      if (inimigo.fraqueza > 0) inimigo.fraqueza -= 1;
      if (inimigo.fragilidade > 0) inimigo.fragilidade -= 1;
    }
  }
  verificarFim(estado);
  if (estado.status !== "andamento") return;

  iniciarTurnoJogador(estado);
}

function verificarFim(estado) {
  if (estado.status !== "andamento") return;
  if (inimigosVivos(estado).length === 0) {
    estado.status = "vitoria";
    estado.log.push("Sala limpa.");
  } else if (estado.jogador.hp <= 0) {
    estado.status = "derrota";
  }
}
