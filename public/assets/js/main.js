// Ponto de entrada. Delega tudo para o roteador de telas (docs/06-roadmap.md, Fase 2: a
// torre inteira, nao so um combate avulso).

import { iniciarJogo } from "./ui/screens.js";

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("app");
  iniciarJogo(container).catch((erro) => {
    console.error("Falha ao iniciar a torre:", erro);
    container.textContent = "Erro ao carregar a torre. Veja o console.";
  });
});
