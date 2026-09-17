// Tela de perfil (Fase 5: meta progressao, docs/07-decisoes.md D12/D13). Mostra as
// estatisticas acumuladas de app/models/Meta.php::perfil() e a lista de objetivos com
// progresso de Meta.php::objetivos(). Mesmo padrao dos outros arquivos de ui/: DOM puro,
// refaz o miolo a cada render.

const ROTULOS_STAT = {
  runs_totais: "Runs totais",
  vitorias: "Vitorias",
  andar_recorde: "Andar recorde",
  pontos_meta_total: "Pontos de meta",
  chefes_derrotados: "Chefes derrotados",
};

export function renderPerfil(container, perfil, objetivos, onVoltar) {
  container.innerHTML = "";
  const tela = document.createElement("div");
  tela.className = "tela-sala";

  const titulo = document.createElement("h1");
  titulo.textContent = `Perfil de ${perfil.usuario?.usuario ?? "capivara"}`;
  tela.appendChild(titulo);

  const stats = document.createElement("div");
  stats.className = "opcoes-recompensa";
  for (const [chave, rotulo] of Object.entries(ROTULOS_STAT)) {
    const item = document.createElement("div");
    item.className = "opcao-recompensa";
    const itemTitulo = document.createElement("div");
    itemTitulo.className = "opcao-recompensa__titulo";
    itemTitulo.textContent = rotulo;
    const itemValor = document.createElement("div");
    itemValor.className = "opcao-recompensa__texto";
    itemValor.textContent = String(perfil.estatisticas?.[chave] ?? 0);
    item.append(itemTitulo, itemValor);
    stats.appendChild(item);
  }
  tela.appendChild(stats);

  const subtitulo = document.createElement("h2");
  subtitulo.textContent = "Objetivos";
  tela.appendChild(subtitulo);

  const lista = document.createElement("div");
  lista.className = "opcoes-recompensa";
  if (objetivos.length === 0) {
    const vazio = document.createElement("p");
    vazio.className = "tela-centro__texto";
    vazio.textContent = "Nenhum objetivo visivel ainda.";
    lista.appendChild(vazio);
  }
  for (const objetivo of objetivos) {
    const item = document.createElement("div");
    const concluido = Boolean(objetivo.concluido_em);
    item.className = "opcao-recompensa";
    const itemTitulo = document.createElement("div");
    itemTitulo.className = "opcao-recompensa__titulo";
    itemTitulo.textContent = `${concluido ? "[Concluido] " : ""}${objetivo.nome}`;
    const itemTexto = document.createElement("div");
    itemTexto.className = "opcao-recompensa__texto";
    itemTexto.textContent = objetivo.descricao;
    item.append(itemTitulo, itemTexto);
    lista.appendChild(item);
  }
  tela.appendChild(lista);

  const botaoVoltar = document.createElement("button");
  botaoVoltar.className = "botao";
  botaoVoltar.textContent = "Voltar";
  botaoVoltar.addEventListener("click", onVoltar);
  tela.appendChild(botaoVoltar);

  container.appendChild(tela);
}
