// Roteador de telas da Fase 2: a torre inteira. Orquestra tela inicial, cada tipo de sala
// (combate, elite, evento, descanso, desafio, chefe, chefe final) e o fim de run
// (docs/06-roadmap.md Fase 2, docs/07-decisoes.md D02/D07/D08/D12/D20/D21/D25).
//
// O combate em si continua sendo renderizado por combatView.js (Fase 1), sem nenhuma mudanca
// nele: este arquivo intercepta o callback de mudanca de estado e, assim que o status deixa de
// ser "andamento", desvia para a tela de recompensa, para o proximo andar ou para o fim de run,
// em vez de deixar o combatView desenhar a tela de fim generica dele.

import { criarCombateDeSala } from "../core/combat.js";
import { renderizarCombate } from "./combatView.js";
import { embaralhar, escolher, derivarSeed } from "../core/rng.js";
import { salaDaRecompensa } from "../core/tower.js";
import {
  renderInicio,
  renderDescanso,
  renderFimDeRun,
  cabecalhoAndar,
  aplicarFundoDaSala,
} from "./towerView.js";
import { renderRecompensa } from "./rewardView.js";
import { renderEvento } from "./eventView.js";
import { renderDesafio, renderSemDesafioDisponivel } from "./challengeView.js";
import { renderAuth } from "./authView.js";
import { renderPerfil } from "./profileView.js";
import { mostrarTutorial, tutorialJaVisto } from "./tutorialView.js";
import {
  usuarioAtual,
  login,
  registrar,
  iniciarRunNoServidor,
  salvarRunNoServidor,
  carregarRunAtivaDoServidor,
  finalizarRunNoServidor,
  carregarPerfilDoServidor,
  carregarObjetivosDoServidor,
} from "../core/api.js";
import {
  estadoGlobal,
  carregarCatalogo,
  novaRun,
  avancarAndar,
  andarAtual,
  rngDoAndar,
  sincronizarHpPosCombate,
  descansar,
  cartaAleatoria,
  adicionarCartaAoDeck,
  subirNivelHabilidade,
  desafiosDisponiveis,
  podeOferecerDesafio,
  aplicarModificador,
  aplicarEfeitoEvento,
  consumirEfeitosPendentes,
  composicaoDaSala,
  removerCartasTemporarias,
  registrarChefesDerrotados,
  serializarRun,
  restaurarRun,
} from "../core/state.js";

async function autenticar(container) {
  try {
    await usuarioAtual();
    return;
  } catch (erro) {
    if (erro.codigo !== "AUTH_REQUIRED") throw erro;
  }

  await new Promise((resolve) => {
    let modo = "login";
    let mensagemErro = null;

    function desenhar() {
      renderAuth(container, {
        modo,
        erro: mensagemErro,
        onEntrar: async (usuario, senha) => {
          try {
            await login(usuario, senha);
            resolve();
          } catch (erro) {
            mensagemErro = erro.message;
            desenhar();
          }
        },
        onRegistrar: async (usuario, email, senha) => {
          try {
            await registrar(usuario, email, senha);
            resolve();
          } catch (erro) {
            mensagemErro = erro.message;
            desenhar();
          }
        },
        onAlternarModo: () => {
          modo = modo === "login" ? "registrar" : "login";
          mensagemErro = null;
          desenhar();
        },
      });
    }

    desenhar();
  });
}

export async function iniciarJogo(container) {
  await autenticar(container);
  await carregarCatalogo();
  await entrarOuRetomar();

  async function entrarOuRetomar() {
    const dados = await carregarRunAtivaDoServidor();
    if (dados.run) {
      const run = restaurarRun(dados.run.estado_json);
      run.id = dados.run.id;
      if (run.andar <= 0) {
        proximoAndar();
      } else {
        renderSala(andarAtual(run));
      }
      return;
    }
    irParaInicio();
  }

  function irParaInicio() {
    renderInicio(container, estadoGlobal.classes, comecarRun, () => abrirPerfil(irParaInicio));
    if (!tutorialJaVisto()) mostrarTutorial();
  }

  async function abrirPerfil(onVoltar) {
    const [perfil, objetivosDados] = await Promise.all([
      carregarPerfilDoServidor(),
      carregarObjetivosDoServidor(),
    ]);
    renderPerfil(container, perfil, objetivosDados.objetivos, onVoltar);
  }

  async function comecarRun(classeSlug) {
    const resposta = await iniciarRunNoServidor(classeSlug);
    const run = novaRun(resposta.run.seed, classeSlug);
    run.id = resposta.run.id;
    await salvarProgresso();
    proximoAndar();
  }

  async function salvarProgresso() {
    const run = estadoGlobal.run;
    try {
      await salvarRunNoServidor(run.id, serializarRun(run));
    } catch (erro) {
      console.error("Falha ao salvar a run:", erro);
    }
  }

  async function proximoAndar() {
    const run = estadoGlobal.run;
    const sala = avancarAndar(run);
    await salvarProgresso();
    renderSala(sala);
  }

  function renderSala(sala) {
    aplicarFundoDaSala(sala);
    if (sala.tipo === "descanso") {
      iniciarDescanso(sala);
    } else if (sala.tipo === "evento") {
      iniciarEvento(sala);
    } else if (sala.tipo === "desafio") {
      iniciarDesafio(sala);
    } else {
      // combate, elite, chefe, final: todos entram direto em combate.
      iniciarCombateDaSala(sala);
    }
  }

  function iniciarDescanso(sala) {
    const run = estadoGlobal.run;
    renderDescanso(container, run, sala, () => {
      descansar(run);
      proximoAndar();
    });
  }

  function iniciarEvento(sala) {
    const run = estadoGlobal.run;
    const rngEscolha = rngDoAndar(run, 1);
    const evento = escolher(estadoGlobal.eventos, rngEscolha);
    renderEvento(container, sala, evento, (indiceEscolha) => {
      const escolha = evento.escolhas[indiceEscolha];
      const rngEfeito = rngDoAndar(run, 2);
      for (const efeito of escolha.efeitos) aplicarEfeitoEvento(run, efeito, rngEfeito);
      proximoAndar();
    });
  }

  function iniciarDesafio(sala) {
    const run = estadoGlobal.run;
    if (!podeOferecerDesafio(run)) {
      renderSemDesafioDisponivel(container, sala, () => iniciarCombateDaSala(sala));
      return;
    }
    const rngSorteio = rngDoAndar(run, 3);
    const opcoes = embaralhar(desafiosDisponiveis(run), rngSorteio).slice(0, 2);
    renderDesafio(container, sala, opcoes, (desafioEscolhido) => {
      aplicarModificador(run, desafioEscolhido);
      iniciarCombateDaSala(sala);
    });
  }

  function iniciarCombateDaSala(sala) {
    const run = estadoGlobal.run;
    if (sala.tipo === "chefe" || sala.tipo === "final") {
      removerCartasTemporarias(run);
    }
    const { fraqueza } = consumirEfeitosPendentes(run);
    const seed = derivarSeed(run.seed, sala.andar);
    const composicao = composicaoDaSala(sala, rngDoAndar(run, 5));
    const estadoCombate = criarCombateDeSala({
      baralho: run.deck,
      composicao,
      seed,
      hpAtual: run.hp,
      hpMax: run.hpMax,
      forcaBonus: run.forcaPermanente,
      fraquezaInicial: fraqueza,
      nivelHabilidade: run.nivelHabilidade,
      classe: run.classe,
      modificadores: run.modificadores,
    });
    estadoGlobal.combate = estadoCombate; // referencia para debug/QA, ver core/state.js

    container.innerHTML = "";
    const raiz = document.createElement("div");
    raiz.className = "tela-sala tela-sala--combate";
    raiz.appendChild(cabecalhoAndar(sala));
    const sub = document.createElement("div");
    raiz.appendChild(sub);
    container.appendChild(raiz);

    const handlers = {
      aoMudar: () => {
        if (estadoCombate.status !== "andamento") {
          finalizarCombate(sala, estadoCombate);
        } else {
          renderizarCombate(sub, estadoCombate, handlers);
        }
      },
      aoReiniciar: () => {}, // nunca acionado: o fim de combate e interceptado acima
    };
    renderizarCombate(sub, estadoCombate, handlers);
  }

  async function finalizarRun(resultado) {
    const run = estadoGlobal.run;
    run.status = resultado;
    let desbloqueios = [];
    try {
      const resposta = await finalizarRunNoServidor(run.id, resultado, serializarRun(run));
      desbloqueios = resposta.desbloqueios ?? [];
    } catch (erro) {
      console.error("Falha ao finalizar a run:", erro);
    }
    renderFimDeRun(container, run, desbloqueios, comecarRun, () =>
      abrirPerfil(() => renderFimDeRun(container, run, desbloqueios, comecarRun, () => abrirPerfil(irParaInicio)))
    );
  }

  function finalizarCombate(sala, estadoCombate) {
    const run = estadoGlobal.run;
    sincronizarHpPosCombate(run, estadoCombate);

    if (estadoCombate.status === "derrota") {
      finalizarRun("derrota");
      return;
    }

    if (sala.tipo === "chefe" || sala.tipo === "final") {
      registrarChefesDerrotados(run, estadoCombate.inimigos.map((inimigo) => inimigo.id));
    }

    if (sala.tipo === "final") {
      finalizarRun("vitoria");
      return;
    }

    if (salaDaRecompensa(sala.tipo)) {
      run.pontosRecompensa += 1;
      const rngRecompensa = rngDoAndar(run, 4);
      const cartaSorteada = cartaAleatoria(run, rngRecompensa);
      renderRecompensa(
        container,
        run,
        cartaSorteada,
        () => {
          adicionarCartaAoDeck(run, cartaSorteada);
          proximoAndar();
        },
        () => {
          run.recompensasHabilidadeUsadas += 1;
          subirNivelHabilidade(run);
          proximoAndar();
        }
      );
      return;
    }

    proximoAndar();
  }
}
