// Wrapper de fetch para a API do servidor (docs/04-arquitetura.md secao 4). Sessao por
// cookie (credentials: "same-origin"), sem token em localStorage. Todo endpoint responde
// { ok: true, data } ou { ok: false, error: { code, message } }; erro vira excecao aqui, com
// codigo e status anexados, para quem chamou decidir o que mostrar.

async function chamar(caminho, { metodo = "GET", corpo } = {}) {
  const resposta = await fetch(`api/${caminho}`, {
    method: metodo,
    credentials: "same-origin",
    headers: corpo !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: corpo !== undefined ? JSON.stringify(corpo) : undefined,
  });
  const json = await resposta.json();
  if (!json.ok) {
    const erro = new Error(json.error?.message ?? "Erro desconhecido");
    erro.codigo = json.error?.code ?? "ERRO_DESCONHECIDO";
    erro.status = resposta.status;
    throw erro;
  }
  return json.data;
}

export function registrar(usuario, email, senha) {
  return chamar("auth/register.php", { metodo: "POST", corpo: { usuario, email, senha } });
}

export function login(usuario, senha) {
  return chamar("auth/login.php", { metodo: "POST", corpo: { usuario, senha } });
}

export function logout() {
  return chamar("auth/logout.php", { metodo: "POST" });
}

export function usuarioAtual() {
  return chamar("auth/me.php");
}

export function carregarCatalogoDoServidor() {
  return chamar("catalog/bootstrap.php");
}

export function iniciarRunNoServidor(classe) {
  return chamar("run/start.php", { metodo: "POST", corpo: { classe } });
}

export function salvarRunNoServidor(runId, estadoJson) {
  return chamar("run/save.php", { metodo: "POST", corpo: { run_id: runId, estado_json: estadoJson } });
}

export function carregarRunAtivaDoServidor() {
  return chamar("run/load.php");
}

export function finalizarRunNoServidor(runId, resultado, estadoJson) {
  return chamar("run/finish.php", {
    metodo: "POST",
    corpo: { run_id: runId, resultado, estado_json: estadoJson },
  });
}

export function carregarPerfilDoServidor() {
  return chamar("meta/profile.php");
}

export function carregarObjetivosDoServidor() {
  return chamar("meta/objectives.php");
}
