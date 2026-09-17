// Renderiza a tela de combate inteira a cada mudanca de estado. Sem framework: refaz o
// miolo do DOM a cada render (Fase 1). A Fase 3 troca o inimigo unico por uma lista (bestiario
// real, chefes com 2 inimigos como os Gemeos): cada inimigo vivo vira um painel clicavel que
// seleciona o alvo das cartas.

import { jogarCarta, fimDeTurno, intentAtual, selecionarAlvo, motivoBloqueio } from "../core/combat.js";
import { criarElementoCarta } from "./cardView.js";
import { RETRATOS_CLASSE } from "./towerView.js";
import { somDano, somCura, somBloco, somInvocacao, somMorteInimigo, somCarta } from "../core/audio.js";

let indiceSelecionado = null;

// Fase 7: dano/cura/bloco/invocacao viram animacao comparando um retrato do estado tirado
// imediatamente antes de uma acao mutar `estado` (jogar carta, fim de turno) contra o estado
// depois da mutacao. Guardado aqui porque a tela e redesenhada do zero a cada renderizarCombate
// (sem diffing de DOM), entao nao da pra descobrir "o que mudou" olhando so pro estado atual.
let snapshotAntes = null;

function snapshotDe(estado) {
  return {
    jogadorHp: estado.jogador.hp,
    jogadorBloco: estado.jogador.bloco,
    jogadorLacaios: estado.jogador.lacaios ?? 0,
    inimigos: estado.inimigos.map((i) => ({ hp: i.hp, bloco: i.bloco })),
  };
}

function mostrarNumeroFlutuante(ancora, texto, tipo) {
  const numero = document.createElement("span");
  numero.className = `numero-flutuante numero-flutuante--${tipo}`;
  numero.textContent = texto;
  numero.style.setProperty("--deslocamento-x", `${Math.round((Math.random() - 0.5) * 30)}px`);
  ancora.appendChild(numero);
  numero.addEventListener("animationend", () => numero.remove(), { once: true });
}

function aplicarDiferencaEntidade(painel, hpAntes, hpDepois, blocoAntes, blocoDepois) {
  const dano = hpAntes - hpDepois;
  if (dano > 0) {
    painel.classList.add("painel--impacto");
    mostrarNumeroFlutuante(painel, `-${dano}`, "dano");
    somDano();
  } else if (hpDepois > hpAntes) {
    painel.classList.add("painel--cura");
    mostrarNumeroFlutuante(painel, `+${hpDepois - hpAntes}`, "cura");
    somCura();
  }
  const ganhoBloco = blocoDepois - blocoAntes;
  if (ganhoBloco > 0) {
    mostrarNumeroFlutuante(painel, `+${ganhoBloco} \u{1F6E1}\u{FE0F}`, "bloco");
    somBloco();
  }
}

function aplicarEfeitosVisuais(raiz, estado, antes) {
  if (!antes) return;

  const painelJogador = raiz.querySelector(".painel--jogador");
  if (painelJogador) {
    aplicarDiferencaEntidade(painelJogador, antes.jogadorHp, estado.jogador.hp, antes.jogadorBloco, estado.jogador.bloco);
    const ganhoLacaios = (estado.jogador.lacaios ?? 0) - antes.jogadorLacaios;
    if (ganhoLacaios > 0) {
      mostrarNumeroFlutuante(painelJogador, `+${ganhoLacaios} \u{1F480}`, "invocacao");
      somInvocacao();
    }
  }

  raiz.querySelectorAll(".painel--inimigo").forEach((painel) => {
    const indice = Number(painel.dataset.indice);
    const snap = antes.inimigos[indice];
    const inimigo = estado.inimigos[indice];
    if (!snap || !inimigo) return;
    aplicarDiferencaEntidade(painel, snap.hp, inimigo.hp, snap.bloco, inimigo.bloco);
    if (snap.hp > 0 && inimigo.hp <= 0) {
      painel.classList.add("painel--inimigo--morrendo");
      somMorteInimigo();
    }
  });
}

// Fase 7: a Soberana Gertrudes e o unico inimigo com arte propria por enquanto
// (Assets/SoberanaGertrudes.png, ver docs/09). O resto do bestiario continua no emoji generico.
const RETRATOS_INIMIGO = {
  "Soberana Gertrudes": "assets/img/ui/personagens/soberana-gertrudes.png",
};

function preencherRetrato(el, src, emojiFallback) {
  if (src) {
    const img = document.createElement("img");
    img.src = src;
    img.alt = "";
    el.appendChild(img);
  } else {
    el.textContent = emojiFallback;
  }
}

function textoIntencao(inimigo) {
  const acoes = intentAtual(inimigo);
  return acoes
    .map((acao) => {
      const vezes = acao.vezes ?? 1;
      const sufixoVezes = vezes > 1 ? ` x${vezes}` : "";
      if (acao.tipo === "ataque") {
        let dmg = acao.valor + inimigo.forca;
        if (inimigo.fraqueza > 0) dmg = Math.floor(dmg * 0.75);
        return `Ataca ${dmg}${sufixoVezes}`;
      }
      if (acao.tipo === "bloco") return `Defende ${acao.valor}`;
      if (acao.tipo === "veneno") return `Aplica Veneno ${acao.valor}`;
      if (acao.tipo === "fraqueza") return `Aplica Fraqueza ${acao.valor}`;
      if (acao.tipo === "fragilidade") return `Aplica Fragilidade ${acao.valor}`;
      if (acao.tipo === "forca") return `Ganha ${acao.valor} de Forca`;
      if (acao.tipo === "forca_todos") return `Toda a sala ganha ${acao.valor} de Forca`;
      if (acao.tipo === "curar") return `Cura ${acao.valor}`;
      if (acao.tipo === "curar_todos") return `Cura a sala em ${acao.valor}`;
      if (acao.tipo === "roubar") return "Rouba 1 Acao do seu proximo turno";
      if (acao.tipo === "carregar") return "Carregando o proximo golpe";
      return acao.tipo;
    })
    .join(" + ");
}

function iconeIntencao(inimigo) {
  const primeira = intentAtual(inimigo)[0];
  if (!primeira) return "\u{2753}";
  if (primeira.tipo === "bloco") return "\u{1F6E1}\u{FE0F}";
  if (primeira.tipo === "carregar") return "\u{23F3}";
  if (["forca", "forca_todos", "curar", "curar_todos"].includes(primeira.tipo)) return "\u{2728}";
  if (["veneno", "fraqueza", "fragilidade", "roubar"].includes(primeira.tipo)) return "\u{2620}\u{FE0F}";
  return "\u{2694}\u{FE0F}";
}

function criarBarraHp(hp, hpMax) {
  const barra = document.createElement("div");
  barra.className = "barra-hp";
  const preenchido = document.createElement("div");
  preenchido.className = "barra-hp__preenchido";
  preenchido.style.width = `${Math.max(0, Math.min(100, (hp / hpMax) * 100))}%`;
  const texto = document.createElement("span");
  texto.className = "barra-hp__texto";
  texto.textContent = `${hp}/${hpMax}`;
  barra.append(preenchido, texto);
  return barra;
}

function criarTagsEstado(entidade) {
  const tags = document.createElement("div");
  tags.className = "tags-estado";
  const defs = [
    ["bloco", "\u{1F6E1}\u{FE0F}", entidade.bloco],
    ["forca", "\u{1F4AA}", entidade.forca],
    ["fraqueza", "\u{1F4C9}", entidade.fraqueza],
    ["fragilidade", "\u{1FA9E}", entidade.fragilidade],
    ["veneno", "\u{2620}\u{FE0F}", entidade.veneno],
  ];
  // Retaliacao e Evasao so existem no jogador (Brutamontes/Ligeira), inimigos nao tem os campos.
  if (entidade.retaliacao > 0) defs.push(["retaliacao", "\u{1F94A}", entidade.retaliacao]);
  if (entidade.evasao > 0) defs.push(["evasao", "\u{1F4A8}", entidade.evasao]);
  for (const [nome, icone, valor] of defs) {
    if (valor > 0) {
      const tag = document.createElement("span");
      tag.className = `tag tag--${nome}`;
      tag.textContent = `${icone} ${valor}`;
      tags.appendChild(tag);
    }
  }
  return tags;
}

function criarPainelInimigo(inimigo, indice, estado, handlers) {
  const painel = document.createElement("div");
  painel.className = "painel painel--inimigo";
  painel.dataset.indice = String(indice);
  const vivo = inimigo.hp > 0;

  if (!vivo) {
    painel.classList.add("painel--inimigo--caido");
  } else if (indice === estado.alvo) {
    painel.classList.add("painel--inimigo--alvo");
  }

  if (vivo) {
    const intencao = document.createElement("div");
    intencao.className = "intencao";
    const iconeSpan = document.createElement("span");
    iconeSpan.className = "intencao__icone";
    iconeSpan.textContent = iconeIntencao(inimigo);
    const textoSpan = document.createElement("span");
    textoSpan.className = "intencao__texto";
    textoSpan.textContent = textoIntencao(inimigo);
    intencao.append(iconeSpan, textoSpan);
    painel.appendChild(intencao);
  }

  const retrato = document.createElement("div");
  retrato.className = "retrato retrato--inimigo";
  preencherRetrato(retrato, vivo ? RETRATOS_INIMIGO[inimigo.nome] : null, vivo ? "\u{1F438}" : "\u{1F480}");

  const nome = document.createElement("div");
  nome.className = "nome-entidade";
  nome.textContent = inimigo.nome;

  painel.append(retrato, nome, criarBarraHp(inimigo.hp, inimigo.hpMax), criarTagsEstado(inimigo));

  if (vivo) {
    painel.setAttribute("role", "button");
    painel.setAttribute("tabindex", "0");
    painel.title = indice === estado.alvo ? "Alvo atual" : "Selecionar como alvo";
    const selecionar = () => {
      selecionarAlvo(estado, indice);
      handlers.aoMudar();
    };
    painel.addEventListener("click", selecionar);
    painel.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" || ev.key === " ") {
        ev.preventDefault();
        selecionar();
      }
    });
  }

  return painel;
}

function criarPaineisInimigos(estado, handlers) {
  const wrapper = document.createElement("div");
  wrapper.className = "paineis-inimigos";
  estado.inimigos.forEach((inimigo, indice) => {
    wrapper.appendChild(criarPainelInimigo(inimigo, indice, estado, handlers));
  });
  return wrapper;
}

// Recurso exclusivo de cada classe na HUD (flet_mvp/capitower/combat.py:resource_label).
function textoRecurso(jogador) {
  if (jogador.classe === "brutamontes") {
    return `\u{1F525} Adrenalina ${jogador.adrenalina}/${jogador.adrenalinaCap}`;
  }
  if (jogador.classe === "ligeira") {
    return `\u{1F4A8} Impulso ${jogador.cartasJogadasNoTurno}`;
  }
  return `\u{1F480} Lacaios ${jogador.lacaios}/${jogador.lacaiosCap}`;
}

function criarPainelJogador(estado) {
  const painel = document.createElement("div");
  painel.className = "painel painel--jogador";

  const retrato = document.createElement("div");
  retrato.className = "retrato retrato--jogador";
  preencherRetrato(retrato, RETRATOS_CLASSE[estado.jogador.classe], "\u{1F9AB}");

  const contadores = document.createElement("div");
  contadores.className = "contadores";

  const acao = document.createElement("span");
  acao.className = "contador contador--acao";
  acao.textContent = `\u{26A1} Acao ${estado.jogador.acao}/${estado.jogador.acaoMax}`;

  const recurso = document.createElement("span");
  recurso.className = "contador contador--lacaios";
  recurso.textContent = textoRecurso(estado.jogador);

  contadores.append(acao, recurso);

  painel.append(retrato, criarBarraHp(estado.jogador.hp, estado.jogador.hpMax), contadores, criarTagsEstado(estado.jogador));

  if (estado.jogador.poderes.length > 0) {
    const poderes = document.createElement("div");
    poderes.className = "tags-estado";
    for (const nome of estado.jogador.poderes) {
      const tag = document.createElement("span");
      tag.className = "tag tag--poder";
      tag.textContent = `\u{2B50} ${NOMES_PODER[nome] ?? nome}`;
      poderes.appendChild(tag);
    }
    painel.appendChild(poderes);
  }

  return painel;
}

// Nome visivel de cada poder das 3 classes na HUD (flet_mvp/capitower/cards.py:POWER_NAMES).
const NOMES_PODER = {
  vala_comum: "Vala Comum",
  banquete: "Banquete",
  ossos_firmes: "Ossos Firmes",
  peste: "Peste Ossea",
  rugido: "Rugido",
  pavio_curto: "Pavio Curto",
  calo: "Calo",
  olho_por_olho: "Olho por Olho",
  segundo_folego: "Segundo Folego",
  golpe_de_vista: "Golpe de Vista",
  rastro: "Rastro de Lama",
  bolso_fundo: "Bolso Fundo",
};

function criarPainelMao(estado, handlers) {
  const painel = document.createElement("div");
  painel.className = "painel-mao";

  const mao = document.createElement("div");
  mao.className = "mao";

  const elementosCarta = [];

  estado.mao.forEach((carta, indice) => {
    const el = criarElementoCarta(carta, indice, estado, {
      selecionada: indice === indiceSelecionado,
      aoClicar: (i) => {
        indiceSelecionado = indiceSelecionado === i ? null : i;
        handlers.aoMudar();
      },
      aoJogarDuploClique: (i) => {
        snapshotAntes = snapshotDe(estado);
        jogarCarta(estado, i);
        indiceSelecionado = null;
        handlers.aoMudar();
      },
    });
    elementosCarta[indice] = el;
    mao.appendChild(el);
  });

  const rodape = document.createElement("div");
  rodape.className = "rodape-mao";

  if (indiceSelecionado !== null && estado.mao[indiceSelecionado]) {
    const idx = indiceSelecionado;
    const jogar = document.createElement("button");
    jogar.className = "botao botao--jogar";
    jogar.textContent = `Jogar ${estado.mao[idx].nome}`;
    jogar.addEventListener("click", () => {
      const executar = () => {
        snapshotAntes = snapshotDe(estado);
        jogarCarta(estado, idx);
        indiceSelecionado = null;
        handlers.aoMudar();
      };
      const cartaEl = elementosCarta[idx];
      const bloqueada = motivoBloqueio(estado, estado.mao[idx]) !== null;
      if (cartaEl && !bloqueada) {
        cartaEl.classList.add("carta--jogada");
        somCarta();
        cartaEl.addEventListener("animationend", executar, { once: true });
      } else {
        executar();
      }
    });
    rodape.appendChild(jogar);
  }

  const fimTurno = document.createElement("button");
  fimTurno.className = "botao botao--fim-turno";
  fimTurno.textContent = "Fim de turno";
  fimTurno.addEventListener("click", () => {
    indiceSelecionado = null;
    snapshotAntes = snapshotDe(estado);
    fimDeTurno(estado);
    handlers.aoMudar();
  });
  rodape.appendChild(fimTurno);

  painel.append(mao, rodape);
  return painel;
}

function criarLog(estado) {
  const painel = document.createElement("div");
  painel.className = "log";
  const lista = document.createElement("ul");
  const recentes = estado.log.slice(-14);
  for (const linha of recentes) {
    const li = document.createElement("li");
    li.textContent = linha;
    lista.appendChild(li);
  }
  painel.appendChild(lista);
  painel.scrollTop = painel.scrollHeight;
  return painel;
}

function criarTelaFim(estado, handlers) {
  const tela = document.createElement("div");
  tela.className = "tela-fim";

  const titulo = document.createElement("h1");
  if (estado.status === "vitoria") {
    titulo.className = "tela-fim__titulo tela-fim__titulo--vitoria";
    titulo.textContent = "Vitoria!";
  } else {
    titulo.className = "tela-fim__titulo tela-fim__titulo--derrota";
    titulo.textContent = "Derrota";
  }

  const resumo = document.createElement("p");
  resumo.className = "tela-fim__resumo";
  resumo.textContent = `Combate encerrado no turno ${estado.turno}.`;

  const botao = document.createElement("button");
  botao.className = "botao botao--reiniciar";
  botao.textContent = "Jogar novamente";
  botao.addEventListener("click", () => {
    indiceSelecionado = null;
    handlers.aoReiniciar();
  });

  tela.append(titulo, resumo, botao);
  return tela;
}

export function renderizarCombate(container, estado, handlers) {
  container.innerHTML = "";

  if (estado.status !== "andamento") {
    container.appendChild(criarTelaFim(estado, handlers));
    return;
  }

  const raiz = document.createElement("div");
  raiz.className = "combate";
  raiz.append(
    criarPaineisInimigos(estado, handlers),
    criarPainelJogador(estado),
    criarPainelMao(estado, handlers),
    criarLog(estado)
  );
  container.appendChild(raiz);

  aplicarEfeitosVisuais(raiz, estado, snapshotAntes);
  snapshotAntes = null;
}
