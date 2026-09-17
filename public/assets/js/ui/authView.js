// Tela de login/cadastro (Fase 4: banco e conta). Aparece antes da torre porque toda run
// agora pertence a uma conta (docs/04-arquitetura.md secao 4). Mesmo padrao dos outros
// arquivos de ui/: DOM puro, refaz o miolo a cada render.

export function renderAuth(container, { modo, erro, onEntrar, onRegistrar, onAlternarModo }) {
  container.innerHTML = "";
  const tela = document.createElement("div");
  tela.className = "tela-centro";

  const titulo = document.createElement("h1");
  titulo.textContent = "CapiTower";

  const subtitulo = document.createElement("p");
  subtitulo.className = "tela-centro__texto";
  subtitulo.textContent =
    modo === "registrar" ? "Crie uma conta para guardar sua torre." : "Entre para continuar sua torre.";

  const form = document.createElement("form");
  form.className = "form-auth";

  const campoUsuario = document.createElement("input");
  campoUsuario.type = "text";
  campoUsuario.name = "usuario";
  campoUsuario.placeholder = "Usuario";
  campoUsuario.autocomplete = "username";
  campoUsuario.required = true;

  const campoEmail = document.createElement("input");
  campoEmail.type = "email";
  campoEmail.name = "email";
  campoEmail.placeholder = "E-mail";
  campoEmail.autocomplete = "email";
  campoEmail.required = true;

  const campoSenha = document.createElement("input");
  campoSenha.type = "password";
  campoSenha.name = "senha";
  campoSenha.placeholder = "Senha";
  campoSenha.autocomplete = modo === "registrar" ? "new-password" : "current-password";
  campoSenha.required = true;

  const erroEl = document.createElement("p");
  erroEl.className = "form-auth__erro";
  erroEl.textContent = erro ?? "";

  const botaoEnviar = document.createElement("button");
  botaoEnviar.type = "submit";
  botaoEnviar.className = "botao botao--comecar";
  botaoEnviar.textContent = modo === "registrar" ? "Criar conta" : "Entrar";

  const botaoAlternar = document.createElement("button");
  botaoAlternar.type = "button";
  botaoAlternar.className = "form-auth__alterna";
  botaoAlternar.textContent =
    modo === "registrar" ? "Ja tenho conta, entrar" : "Nao tenho conta, criar uma";
  botaoAlternar.addEventListener("click", onAlternarModo);

  form.append(campoUsuario);
  if (modo === "registrar") form.append(campoEmail);
  form.append(campoSenha, erroEl, botaoEnviar);

  form.addEventListener("submit", (evento) => {
    evento.preventDefault();
    const usuario = campoUsuario.value.trim();
    const senha = campoSenha.value;
    if (modo === "registrar") {
      onRegistrar(usuario, campoEmail.value.trim(), senha);
    } else {
      onEntrar(usuario, senha);
    }
  });

  tela.append(titulo, subtitulo, form, botaoAlternar);
  container.appendChild(tela);
}
