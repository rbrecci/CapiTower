// Telas da torre que nao sao nem combate, nem recompensa, nem evento: a tela inicial, o
// descanso (D07: cura escassa, so aqui e no evento) e o fim de run (D12: vitoria ou derrota,
// permadeath, sem retomar). Segue o padrao dos outros arquivos de ui/: DOM puro, refaz o miolo
// a cada render.

export function renderInicio(container, onComecar, onVerPerfil) {
  container.innerHTML = "";
  const tela = document.createElement("div");
  tela.className = "tela-centro";

  const titulo = document.createElement("h1");
  titulo.textContent = "CapiTower";

  const subtitulo = document.createElement("p");
  subtitulo.className = "tela-centro__texto";
  subtitulo.textContent = "51 andares, HP que persiste, permadeath. Jogue a Capimaga: 20 cartas, Legiao de 10 niveis, 5 chefes de bloco e a Soberana Gertrudes no topo.";

  const botao = document.createElement("button");
  botao.className = "botao botao--comecar";
  botao.textContent = "Comecar a subir";
  botao.addEventListener("click", onComecar);

  const botaoPerfil = document.createElement("button");
  botaoPerfil.className = "botao botao--fim-turno";
  botaoPerfil.textContent = "Ver perfil";
  botaoPerfil.addEventListener("click", onVerPerfil);

  tela.append(titulo, subtitulo, botao, botaoPerfil);
  container.appendChild(tela);
}

export function cabecalhoAndar(sala) {
  const rotulos = {
    combate: "Combate",
    elite: "Elite",
    evento: "Evento",
    descanso: "Descanso",
    desafio: "Desafio opcional",
    chefe: "Chefe de bloco",
    final: "Chefao final",
  };
  const el = document.createElement("div");
  el.className = "cabecalho-andar";
  el.textContent = `Andar ${sala.andar} de 51, ${sala.nomeBloco}, ${rotulos[sala.tipo] ?? sala.tipo}`;
  return el;
}

export function renderDescanso(container, run, sala, onContinuar) {
  container.innerHTML = "";
  const raiz = document.createElement("div");
  raiz.className = "tela-sala";
  raiz.appendChild(cabecalhoAndar(sala));

  const cura = Math.round(run.hpMax * 0.3);

  const tela = document.createElement("div");
  tela.className = "tela-centro";

  const titulo = document.createElement("h2");
  titulo.textContent = "Uma sala tranquila para respirar.";

  const texto = document.createElement("p");
  texto.className = "tela-centro__texto";
  texto.textContent = `Descansar aqui recupera ${cura} de HP (${run.hp}/${run.hpMax} atual).`;

  const botao = document.createElement("button");
  botao.className = "botao";
  botao.textContent = "Descansar";
  botao.addEventListener("click", onContinuar);

  tela.append(titulo, texto, botao);
  raiz.appendChild(tela);
  container.appendChild(raiz);
}

export function renderFimDeRun(container, run, desbloqueios, onNovaRun, onVerPerfil) {
  container.innerHTML = "";
  const tela = document.createElement("div");
  tela.className = "tela-fim";

  const titulo = document.createElement("h1");
  if (run.status === "vitoria") {
    titulo.className = "tela-fim__titulo tela-fim__titulo--vitoria";
    titulo.textContent = "Vitoria! A torre caiu.";
  } else {
    titulo.className = "tela-fim__titulo tela-fim__titulo--derrota";
    titulo.textContent = "Derrota";
  }

  const resumo = document.createElement("p");
  resumo.className = "tela-fim__resumo";
  resumo.textContent =
    run.status === "vitoria"
      ? `Voce chegou ao topo, andar ${run.andar} de 51.`
      : `Sua run acabou no andar ${run.andar} de 51. Permadeath: nao da para retomar (D12).`;

  const stats = document.createElement("p");
  stats.className = "tela-fim__resumo";
  stats.textContent = `Nivel da habilidade: ${run.nivelHabilidade}. Cartas no deck: ${run.deck.length}. Modificadores: ${
    run.modificadores.length > 0 ? run.modificadores.join(", ") : "nenhum"
  }.`;

  const botao = document.createElement("button");
  botao.className = "botao botao--reiniciar";
  botao.textContent = "Nova torre";
  botao.addEventListener("click", onNovaRun);

  const botaoPerfil = document.createElement("button");
  botaoPerfil.className = "botao botao--fim-turno";
  botaoPerfil.textContent = "Ver perfil";
  botaoPerfil.addEventListener("click", onVerPerfil);

  tela.append(titulo, resumo, stats);

  if (desbloqueios && desbloqueios.length > 0) {
    const listaDesbloqueios = document.createElement("div");
    listaDesbloqueios.className = "opcoes-recompensa";
    for (const desbloqueio of desbloqueios) {
      const item = document.createElement("div");
      item.className = "opcao-recompensa";
      const itemTitulo = document.createElement("div");
      itemTitulo.className = "opcao-recompensa__titulo";
      itemTitulo.textContent = `Objetivo cumprido: ${desbloqueio.nome}`;
      const itemTexto = document.createElement("div");
      itemTexto.className = "opcao-recompensa__texto";
      itemTexto.textContent = desbloqueio.descricao;
      item.append(itemTitulo, itemTexto);
      listaDesbloqueios.appendChild(item);
    }
    tela.appendChild(listaDesbloqueios);
  }

  tela.append(botao, botaoPerfil);
  container.appendChild(tela);
}
