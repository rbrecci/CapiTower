// Ponto de entrada. Delega tudo para o roteador de telas (docs/06-roadmap.md, Fase 2: a
// torre inteira, nao so um combate avulso).

import { iniciarJogo } from "./ui/screens.js";
import { estaMudo, alternarMudo } from "./core/audio.js";

// Fase 7: botao de som fixo, fora de #app, pra ficar acessivel em qualquer tela sem entrar na
// renderizacao de nenhuma delas (elas fazem container.innerHTML = "" a cada troca de tela).
function criarBotaoSom() {
  const botao = document.createElement("button");
  botao.className = "botao-som";
  const atualizar = () => {
    const mudo = estaMudo();
    botao.textContent = mudo ? "\u{1F507}" : "\u{1F50A}";
    botao.title = mudo ? "Ativar som" : "Silenciar";
  };
  botao.addEventListener("click", () => {
    alternarMudo();
    atualizar();
  });
  atualizar();
  document.body.appendChild(botao);
}

document.addEventListener("DOMContentLoaded", () => {
  criarBotaoSom();
  const container = document.getElementById("app");
  iniciarJogo(container).catch((erro) => {
    console.error("Falha ao iniciar a torre:", erro);
    container.textContent = "Erro ao carregar a torre. Veja o console.";
  });
});
