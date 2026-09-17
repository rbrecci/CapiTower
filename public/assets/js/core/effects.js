// Interpretador do formato de efeito de carta (docs/04-arquitetura.md secao 6).
// Cartas guardam dados, nao codigo. Cada operacao le "op" e mexe no estado do combate.
// Operacoes: dano, dano_por_lacaio, bloco, bloco_por_lacaio, estado, invocar,
// consumir_lacaios, comprar, ganhar_acao, curar, repetir, dano_defesa, manter_bloco,
// espalhar_veneno, poder, se. As ultimas 5 entraram na Fase 3 para portar o vocabulario que
// as 20 cartas da Capimaga usam de verdade (flet_mvp/capitower/cards.py, comentario no topo).

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
} from "./combat.js";

export function resolverEfeitos(estado, efeitos, ctx) {
  for (const efeito of efeitos) {
    resolverUm(estado, efeito, ctx);
  }
}

// Condicoes usadas pelas cartas da Capimaga (flet_mvp/capitower/combat.py:check_condition):
// "consumidos>=N", "impulso>=N" e "alvo_envenenado".
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
    case "repetir":
      for (let i = 0; i < (efeito.vezes ?? 1); i++) {
        resolverEfeitos(estado, efeito.efeitos ?? [], ctx);
      }
      break;
    default:
      estado.log.push(`Operacao desconhecida: ${efeito.op}.`);
  }
}
