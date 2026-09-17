// Interpretador do formato de efeito de carta (docs/04-arquitetura.md secao 6).
// Cartas guardam dados, nao codigo. Cada operacao le "op" e mexe no estado do combate.
// Operacoes: dano, dano_por_lacaio, bloco, bloco_por_lacaio, estado, invocar,
// consumir_lacaios, comprar, ganhar_acao, curar, repetir, dano_defesa, manter_bloco,
// espalhar_veneno, poder, se. As ultimas 5 entraram na Fase 3 para portar o vocabulario que
// as 20 cartas da Capimaga usam de verdade (flet_mvp/capitower/cards.py, comentario no topo).
//
// Fase 6 acrescenta o vocabulario de Brutamontes e Ligeira (mesma fonte): perder_vida,
// ganhar_adrenalina, consumir_adrenalina, dano_por_adrenalina, bloco_por_adrenalina,
// dano_por_consumido, bloco_por_consumido, acao_por_consumido, retaliacao, evasao,
// dano_por_impulso, bloco_por_impulso, dano_condicional, devolver_ultima, proxima_gratis,
// trocar_mao. "poder" e "se" ja eram genericos e sao reaproveitados sem mudanca.

import {
  causarDano,
  ganharBloco,
  aplicarEstado,
  invocarLacaios,
  consumirLacaios,
  comprarCartas,
  alvoAtual,
  entidadesAlvo,
  manterBloco,
  espalharVeneno,
  registrarPoder,
  perderVidaJogador,
  ganharAdrenalina,
  consumirAdrenalina,
} from "./combat.js";

export function resolverEfeitos(estado, efeitos, ctx) {
  for (const efeito of efeitos) {
    resolverUm(estado, efeito, ctx);
  }
}

// Condicoes usadas pelas cartas das tres classes (flet_mvp/capitower/combat.py:check_condition):
// "consumidos>=N", "impulso>=N", "adrenalina>=N", "evasao>=N" e "alvo_envenenado".
function condicaoVerdadeira(estado, condicao, ctx) {
  if (condicao === "alvo_envenenado") {
    const alvo = alvoAtual(estado);
    return Boolean(alvo && alvo.veneno > 0);
  }
  const partes = condicao.split(">=");
  if (partes.length === 2) {
    const chave = partes[0];
    const valor = Number(partes[1]);
    if (chave === "consumidos") return (ctx.consumidos ?? 0) >= valor;
    if (chave === "impulso") return (ctx.impulso ?? 0) >= valor;
    if (chave === "adrenalina") return estado.jogador.adrenalina >= valor;
    if (chave === "evasao") return estado.jogador.evasao >= valor;
  }
  return false;
}

function resolverUm(estado, efeito, ctx) {
  switch (efeito.op) {
    case "dano":
      causarDano(estado, efeito.alvo, efeito.valor);
      break;
    case "dano_por_lacaio": {
      const qtd = efeito.fonte === "consumidos" ? (ctx.consumidos ?? 0) : estado.jogador.lacaios;
      if (qtd > 0) {
        causarDano(estado, efeito.alvo, efeito.valor * qtd);
      }
      break;
    }
    case "bloco":
      ganharBloco(estado, "jogador", efeito.valor);
      break;
    case "bloco_por_lacaio": {
      const qtd = efeito.fonte === "consumidos" ? (ctx.consumidos ?? 0) : estado.jogador.lacaios;
      const teto = efeito.teto ?? Infinity;
      ganharBloco(estado, "jogador", Math.min(teto, efeito.valor * qtd));
      break;
    }
    case "dano_defesa": {
      const teto = efeito.teto ?? Infinity;
      if (estado.jogador.bloco > 0) {
        causarDano(estado, efeito.alvo ?? "inimigo", Math.min(teto, estado.jogador.bloco));
      } else {
        estado.log.push("Sem Bloco para bater. Nada acontece.");
      }
      break;
    }
    case "manter_bloco":
      manterBloco(estado);
      break;
    case "estado":
      aplicarEstado(estado, efeito.alvo, efeito.estado, efeito.valor);
      break;
    case "espalhar_veneno":
      espalharVeneno(estado);
      break;
    case "invocar":
      invocarLacaios(estado, efeito.valor);
      break;
    case "consumir_lacaios":
      ctx.consumidos = consumirLacaios(estado, efeito.valor);
      break;
    case "comprar":
      comprarCartas(estado, efeito.valor);
      break;
    case "ganhar_acao":
      estado.jogador.acao += efeito.valor;
      estado.log.push(`+${efeito.valor} de Acao.`);
      break;
    case "curar": {
      const alvos = entidadesAlvo(estado, efeito.alvo ?? "jogador");
      for (const alvo of alvos) {
        const antes = alvo.hp;
        alvo.hp = Math.min(alvo.hpMax, alvo.hp + efeito.valor);
        if (alvo.hp > antes) {
          const nome = alvo === estado.jogador ? "Voce" : alvo.nome;
          estado.log.push(`${nome} cura ${alvo.hp - antes}.`);
        }
      }
      break;
    }
    case "poder":
      registrarPoder(estado, efeito.nome);
      break;
    case "se":
      if (condicaoVerdadeira(estado, efeito.condicao, ctx)) {
        resolverEfeitos(estado, efeito.efeitos ?? [], ctx);
      }
      break;
    case "perder_vida":
      perderVidaJogador(estado, efeito.valor);
      break;
    case "ganhar_adrenalina":
      ganharAdrenalina(estado, efeito.valor);
      break;
    case "consumir_adrenalina":
      ctx.consumidos = consumirAdrenalina(estado, efeito.valor);
      break;
    case "dano_por_adrenalina": {
      if (estado.jogador.adrenalina > 0) {
        const teto = efeito.teto ?? Infinity;
        causarDano(estado, efeito.alvo, Math.min(teto, efeito.valor * estado.jogador.adrenalina));
      }
      break;
    }
    case "bloco_por_adrenalina": {
      const teto = efeito.teto ?? Infinity;
      ganharBloco(estado, "jogador", Math.min(teto, efeito.valor * estado.jogador.adrenalina));
      break;
    }
    case "dano_por_consumido": {
      const qtd = ctx.consumidos ?? 0;
      if (qtd > 0) {
        const teto = efeito.teto ?? Infinity;
        causarDano(estado, efeito.alvo, Math.min(teto, efeito.valor * qtd));
      }
      break;
    }
    case "bloco_por_consumido":
      ganharBloco(estado, "jogador", efeito.valor * (ctx.consumidos ?? 0));
      break;
    case "acao_por_consumido": {
      const qtd = ctx.consumidos ?? 0;
      if (qtd > 0) {
        const ganho = efeito.valor * qtd;
        estado.jogador.acao += ganho;
        estado.log.push(`+${ganho} de Acao.`);
      }
      break;
    }
    case "retaliacao":
      estado.jogador.retaliacao = Math.max(estado.jogador.retaliacao, efeito.valor);
      estado.jogador.retaliacaoTurnos = Math.max(estado.jogador.retaliacaoTurnos, efeito.turnos);
      estado.log.push(`Retaliacao ${efeito.valor}.`);
      break;
    case "evasao":
      estado.jogador.evasao += efeito.valor;
      estado.log.push(`+${efeito.valor} de Evasao.`);
      break;
    case "dano_por_impulso": {
      const n = Math.min(efeito.teto ?? Infinity, ctx.impulso ?? 0);
      if (n > 0) {
        causarDano(estado, efeito.alvo, efeito.valor * n);
      } else {
        estado.log.push("Nenhuma carta antes desta. Nada acontece.");
      }
      break;
    }
    case "bloco_por_impulso": {
      const n = Math.min(efeito.teto ?? Infinity, ctx.impulso ?? 0);
      ganharBloco(estado, "jogador", efeito.valor * n);
      break;
    }
    case "dano_condicional": {
      const extra = condicaoVerdadeira(estado, efeito.condicao, ctx) ? efeito.extra : 0;
      causarDano(estado, efeito.alvo, efeito.base + extra);
      break;
    }
    case "devolver_ultima": {
      const carta = estado.jogador.ultimaJogada;
      const indice = carta ? estado.descarte.indexOf(carta) : -1;
      if (indice >= 0) {
        estado.descarte.splice(indice, 1);
        estado.mao.push(carta);
        estado.log.push(`${carta.nome} volta a mao.`);
        estado.jogador.ultimaJogada = null;
      } else {
        estado.log.push("Nada para devolver.");
      }
      break;
    }
    case "proxima_gratis":
      estado.jogador.proximaGratis = true;
      break;
    case "trocar_mao": {
      const n = estado.mao.length;
      estado.descarte.push(...estado.mao);
      estado.mao = [];
      comprarCartas(estado, n);
      break;
    }
    case "repetir":
      for (let i = 0; i < (efeito.vezes ?? 1); i++) {
        resolverEfeitos(estado, efeito.efeitos ?? [], ctx);
      }
      break;
    default:
      estado.log.push(`Operacao desconhecida: ${efeito.op}.`);
  }
}
