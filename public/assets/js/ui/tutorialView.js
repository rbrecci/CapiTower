// Fase 7: tutorial curto pra quem nunca jogou (docs/06-roadmap.md). E um overlay preso a
// document.body, nao a #app: assim ele empilha por cima de qualquer tela sem depender de quem
// chamou (screens.js mostra sozinho na primeira visita; towerView.js oferece de novo a qualquer
// momento pelo botao "Como jogar" na tela inicial), e sobrevive ao container.innerHTML = ""
// que cada tela roda ao trocar de lugar.

const CHAVE_VISTO = "capitower_tutorial_visto";

export function tutorialJaVisto() {
  try {
    return localStorage.getItem(CHAVE_VISTO) === "1";
  } catch {
    return true; // sem localStorage: melhor nao insistir toda hora do que quebrar a tela.
  }
}

function marcarVisto() {
  try {
    localStorage.setItem(CHAVE_VISTO, "1");
  } catch {
    // aba privada etc.: so nao persiste, ainda da pra abrir de novo pelo botao "Como jogar".
  }
}

const PASSOS = [
  {
    titulo: "Bem-vindo a CapiTower",
    texto:
      "Suba 51 andares batalhando com cartas. Se voce cair, a run acaba ali: sem retomar (permadeath).",
  },
  {
    titulo: "Acao e cartas",
    texto:
      "Cada carta custa Acao. Clique numa carta pra selecionar e de novo (ou no botao Jogar) pra jogar. Sem Acao sobrando, so da pra encerrar o turno.",
  },
  {
    titulo: "Bloco e alvo",
    texto:
      "Bloco absorve dano antes de tirar sua vida, e some no fim do turno (a nao ser que uma carta diga o contrario). Clique num inimigo pra escolher o alvo das suas cartas de ataque.",
  },
  {
    titulo: "Fim de turno",
    texto:
      "Quando acabar suas jogadas, clique em Fim de turno: os inimigos agem de acordo com a intencao mostrada acima deles.",
  },
  {
    titulo: "Entre andares",
    texto:
      "Depois de limpar uma sala, escolha uma carta nova ou evolua a habilidade da sua classe. O HP persiste entre andares: cuide dele.",
  },
];

// aoFechar e opcional: screens.js usa pra saber quando pode seguir em frente (nao usado hoje,
// mas mantem o tutorial independente de quem chamou, sem precisar reabrir a tela por baixo).
export function mostrarTutorial(aoFechar) {
  let indice = 0;
  const overlay = document.createElement("div");
  overlay.className = "tutorial-overlay";

  function desenhar() {
    overlay.innerHTML = "";
    const caixa = document.createElement("div");
    caixa.className = "tutorial-caixa";

    const passo = PASSOS[indice];

    const fecharX = document.createElement("button");
    fecharX.className = "tutorial-fechar";
    fecharX.textContent = "\u{2715}";
    fecharX.title = "Fechar tutorial";
    fecharX.addEventListener("click", fechar);
    caixa.appendChild(fecharX);

    const progresso = document.createElement("div");
    progresso.className = "tutorial-progresso";
    progresso.textContent = `${indice + 1} / ${PASSOS.length}`;

    const titulo = document.createElement("h2");
    titulo.textContent = passo.titulo;

    const texto = document.createElement("p");
    texto.textContent = passo.texto;

    const rodape = document.createElement("div");
    rodape.className = "tutorial-rodape";

    const pular = document.createElement("button");
    pular.className = "botao botao--fim-turno";
    pular.textContent = indice === 0 ? "Pular" : "Voltar";
    pular.addEventListener("click", () => {
      if (indice === 0) {
        fechar();
      } else {
        indice -= 1;
        desenhar();
      }
    });

    const proximo = document.createElement("button");
    proximo.className = "botao";
    proximo.textContent = indice === PASSOS.length - 1 ? "Entendi!" : "Proximo";
    proximo.addEventListener("click", () => {
      if (indice === PASSOS.length - 1) {
        fechar();
      } else {
        indice += 1;
        desenhar();
      }
    });

    rodape.append(pular, proximo);
    caixa.append(progresso, titulo, texto, rodape);
    overlay.appendChild(caixa);
  }

  function fechar() {
    marcarVisto();
    overlay.remove();
    if (aoFechar) aoFechar();
  }

  desenhar();
  document.body.appendChild(overlay);
}
