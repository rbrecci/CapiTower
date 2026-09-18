# CapiTower — Technical Review

Auditoria tecnica completa do repositorio em 18/09/2026 (HEAD `1595b1a`). Escrito sem acentos, na
mesma convencao dos outros documentos de `docs/`.

Metodo: leitura integral de todo o codigo-fonte das duas trilhas (PHP/JS em `public/` e `app/`,
Python/Flet em `flet_mvp/`), do schema e das seeds, e dos 10 documentos de `docs/`; execucao do
projeto (`php -S` + MySQL 8 local, banco `capitower` ja semeado nesta maquina) com uma conta de
teste descartavel (`audit_review`) criada so para a auditoria; um harness Node no diretorio
temporario da sessao que importa o motor real (`core/combat.js`, `core/state.js`) e simula 900
runs com um bot; sondagens da API com `curl`; e os 13 testes do MVP Python (`13/13 passaram`).
Nenhum arquivo do projeto foi alterado alem da criacao deste `Review.md`.

Cada finding traz a classificacao de evidencia pedida no prompt: **Confirmado** (reproduzido ao
vivo ou por script contra o codigo real), **Provavel** (deduzido do codigo, caminho claro, nao
reproduzido), **Possivel** (hipotese com base tecnica) ou **Sugestao**.

---

## 1. Executive Summary

O CapiTower e um deckbuilder roguelike de torre (51 andares, 3 classes, 60 cartas, 27 inimigos)
com o combate inteiro no cliente (JavaScript puro, ES modules, sem build) e um backend PHP/MySQL
minimo que autentica, serve o catalogo e guarda o snapshot da run entre andares. Existe uma segunda
implementacao completa em Python/Flet (`flet_mvp/`), declarada nos docs como "fonte da verdade"
de balanceamento, que nao compartilha nem codigo nem dados com a trilha de producao.

O que esta bom: o motor de combate JS (`core/combat.js` + `core/effects.js`) e puro, sem DOM,
deterministico por seed e sobreviveu a 900 runs simuladas sem lancar uma unica excecao; o formato
de efeito de carta em JSON e simples e cobriu 30 operacoes sem virar codigo; a separacao
motor/UI/orquestracao existe de verdade; o backend usa PDO preparado, `password_hash`,
sessao `httponly`/`SameSite=Lax` e rate limit; as decisoes de design estao registradas.

O que esta quebrado (confirmado ao vivo ou por script):

1. **Toda transicao de andar e assincrona e sem guarda** (`screens.js:proximoAndar`). Um clique
   duplo em "Fim de turno", numa recompensa, numa escolha de evento ou em "Descansar" executa a
   acao duas vezes e **pula um andar** (reproduzido: 3 → 5, 6 → 8, 8 → 10; duas cartas de
   recompensa por um ponto; duas cartas temporarias por um evento).
2. **Ligeira e Brutamontes podem comecar sem nenhuma fonte de dano** (8,3% e 1,6% dos sorteios
   iniciais, calculado sobre `cards.json`; 15 de 300 runs de Ligeira simuladas travaram no andar
   1–3 com inimigos que nao morrem). O MVP Python tinha a guarda `MIN_ATTACKS = 2`; o porte JS
   nao. Nao existe botao de abandonar run, entao a unica saida e morrer de proposito.
3. **A regra "um golpe por carta" do MVP nao foi portada** para `dano` + `dano_por_adrenalina` /
   `dano_por_consumido` (`bm_soco`, `bm_cabecada`, `bm_estampido`): Forca conta duas vezes,
   espinhos e reflexo disparam duas vezes (Soco de Sobra contra Guarda: 16 de dano e 6 de
   espinhos, contra 13 e 3 da referencia Python).
4. **Login por e-mail devolve 500** para qualquer e-mail com mais de 24 caracteres
   (`login_tentativas.usuario VARCHAR(24)` em modo estrito).
5. O retrato de estado usado pela animacao (`combatView.js:snapshotAntes`) **vaza para o combate
   seguinte**: todo combate comeca com flash verde, numero "+N" e som de cura nos inimigos novos.
6. `finish.php` nao e atomico: se qualquer coisa falhar depois de `Run::finalizar`, a run fica
   fechada e as estatisticas contadas, mas os objetivos nunca sao avaliados e os desbloqueios se
   perdem para sempre (reproduzido com um payload malformado; a resposta vem sem envelope JSON).

O que e perigoso a medio prazo: o snapshot da run nao tem validacao nem migracao (`versao` e
escrito e nunca lido), e o cliente **sempre** retoma a run ativa no boot sem oferecer saida — a
primeira renomeacao ou remocao de carta no catalogo com runs ativas no banco vai deixar esses
usuarios com "Erro ao carregar a torre" para sempre, sem acao possivel pela interface. E o
conteudo vive em tres copias (`cards.py`, `cards.json`, `seeds.sql`) e o motor em duas linguagens,
sem nenhum teste de paridade: as divergencias 2 e 3 acima ja sao consequencia disso.

Balanco: **0 CRITICAL, 8 HIGH, 16 MEDIUM, 16 LOW, 6 SUGGESTION** (secao 14). O projeto e um
prototipo funcional e bem documentado, com um motor que merece ser preservado, mas a camada de
orquestracao/persistencia e o processo de conteudo precisam de correcoes antes do deploy.

---

## 2. Project Overview

### 2.1 Stack

| Camada | Tecnologia | Observacao |
| --- | --- | --- |
| Front (producao) | HTML + CSS + JS ES modules, sem framework, sem build | `public/assets/js` (20 arquivos, ~3.300 linhas) |
| Back | PHP 8.4 procedural com 4 classes estaticas, PDO | `app/` (8 arquivos) + 13 endpoints em `public/api` |
| Banco | MySQL 8 (InfinityFree em producao) | `database/schema.sql` (13 tabelas), `seeds.sql` (1.103 linhas) |
| MVP paralelo | Python 3.13 + Flet 0.86.5 | `flet_mvp/` (~3.400 linhas, 2 arquivos de teste) |
| Ferramentas | nenhuma (sem lint, sem test runner, sem CI) | `.claude/launch.json` so define como subir os dois servidores |

### 2.2 Arquitetura (trilha PHP/JS)

```
main.js ──► ui/screens.js (orquestrador: auth, catalogo, run, salas, fim)
                │
                ├─► core/state.js   estadoGlobal { classes, catalogoCartas, inimigos, eventos, desafios, combate, run }
                │      ├─ novaRun / restaurarRun / serializarRun
                │      ├─ composicaoDaSala, eventos, desafios, recompensas
                │      └─ core/tower.js (ordem dos 51 andares a partir da seed)
                ├─► core/combat.js  motor: criarCombateDeSala, jogarCarta, fimDeTurno
                │      └─◄► core/effects.js (interpretador das 30 operacoes; import circular)
                ├─► core/api.js     fetch para public/api/*.php (cookie de sessao)
                └─► ui/*View.js     DOM puro, cada tela faz container.innerHTML = "" e redesenha

public/api/*.php ──► app/core/{Auth,Request,Response,Database} ──► app/models/{Run,Catalog,Meta,User} ──► MySQL
```

### 2.3 Fluxos principais

- **Inicializacao**: `main.js` → `iniciarJogo` → `autenticar` (tela de login se `me.php` der 401)
  → `carregarCatalogo` (`bootstrap.php`, uma vez) → `load.php`: se ha run ativa, `restaurarRun` e
  `renderSala(andarAtual)`; senao tela inicial com selecao de classe.
- **Run**: `comecarRun(classe)` → `start.php` cria a linha e a seed → `novaRun` sorteia 5 cartas
  distintas x2 copias → `proximoAndar` (avanca, salva, renderiza). Cada sala e um `renderX`; ao
  terminar, `proximoAndar` de novo. HP, deck, modificadores e nivel persistem no objeto `run`.
- **Combate**: `criarCombateDeSala` monta `estado` (jogador, inimigos, pilhas, rng por andar);
  `combatView.renderizarCombate` redesenha tudo a cada `handlers.aoMudar()`; quando
  `estado.status` sai de `"andamento"`, `screens.js:finalizarCombate` intercepta.
- **Cartas**: `jogarCarta` → `motivoBloqueio` → `resolverEfeitos(estado, carta.efeitos, ctx)`
  → switch por `op` em `effects.js` chamando mutadores exportados de `combat.js`.
- **Progressao**: elite/chefe dao 1 ponto: carta aleatoria da classe OU +1 nivel da habilidade;
  eventos (3), descanso (30%), desafio (modificador entre 2). Meta: `finish.php` calcula pontos,
  atualiza `usuario_estatisticas`, avalia 12 objetivos e devolve desbloqueios.
- **Save/Load**: `salvarProgresso` em `proximoAndar` (na ENTRADA do andar); o combate nunca e
  salvo. `restaurarRun` recompoe o deck buscando cada id no catalogo em memoria.

### 2.4 Sistemas existentes (avaliados na secao 5)

Combate, cartas/efeitos, deck/mao/compra/descarte, energia ("Acao"), dano/bloco/estados
(Forca, Fraqueza, Fragilidade, Veneno, Retaliacao, Evasao), recursos de classe (Lacaios,
Adrenalina, Impulso), poderes persistentes, inimigos com padrao/intencao/flags/fases, turnos, RNG
com seed, torre, eventos, descanso, desafio/modificadores, recompensas, morte/vitoria, save/load,
meta progressao (estatisticas, objetivos, desbloqueios), audio sintetizado, animacao por diff de
estado, tutorial. Nao existem: loja, moeda, reliquias, mapa ramificado, upgrade/remocao de carta,
multiplos saves.

---

## 3. Architecture Review

### 3.1 Pontos positivos

- **Motor puro.** `core/combat.js` e `core/effects.js` nao tocam DOM, `window`, `fetch` nem
  `localStorage`. Foi possivel importa-los em Node e rodar 900 runs sem nenhuma adaptacao. Isso e
  raro em prototipo rapido e e o maior ativo tecnico do projeto.
- **Determinismo por seed.** `rng.js` (mulberry32 + `derivarSeed`) da a cada andar/sorteio um
  gerador proprio; a torre nao precisa ser salva. Bom para reproducao de bugs.
- **Efeitos como dados.** 60 cartas e 27 inimigos entram por JSON; o interpretador tem um
  `default` que loga operacao desconhecida em vez de quebrar.
- **Fronteira cliente/servidor explicita e documentada** (`docs/04-arquitetura.md` secao 2), com
  envelope JSON unico e erros com codigo.
- **Backend com o basico certo:** PDO preparado em toda query, `EMULATE_PREPARES=false`,
  `password_hash`, `session_regenerate_id` no login, cookie `httponly`/`SameSite`, `.htaccess` +
  constante `CAPITOWER` em todo arquivo de `app/`, rate limit de login.
- **Docs de decisao** (`07-decisoes.md`, D01–D28) e registro de progresso honesto sobre o que foi
  e nao foi verificado ao vivo.

### 3.2 Problemas arquiteturais

**[ARC-01] Orquestracao por closures sem maquina de estado nem guarda de transicao (HIGH).**
`screens.js` define tudo dentro de `iniciarJogo` (linhas 108–312): 14 funcoes aninhadas
compartilhando `container` e `estadoGlobal`. Nao existe um estado "transicionando" — `proximoAndar`
(158–163) faz `avancarAndar` sincrono, depois `await salvarProgresso()`, depois `renderSala`. Entre
o `await` e o render, a tela anterior continua no DOM com todos os botoes vivos, e qualquer clique
repete a acao inteira (ver BUG-01). Tambem torna o fluxo intestavel fora do navegador: nenhuma
dessas funcoes pode ser importada.

**[ARC-02] Duas implementacoes do motor e tres copias do conteudo, sem paridade (HIGH).**
`flet_mvp/capitower/{cards,content,combat}.py` sao declarados fonte da verdade
(`docs/09` secao 3; `core/combat.js` linhas 1–9). O conteudo vive em `cards.py` → `cards.json`
(campo `origem` aponta pro Python) → `seeds.sql` (o unico que o jogo serve). Hoje `cards.json` e
`seeds.sql` batem (verifiquei por script: 60 cartas, 0 diferencas), mas `cards.py` ja diverge do
JS em regra (BUG-02, BUG-03, DES-01, DES-02), e nao ha nada que detecte a proxima divergencia.
`data/*.json` continuam servidos em `public/` sem nenhum `.js` que os leia.

**[ARC-03] Vocabulario de efeitos partido em dois modulos com import circular (MEDIUM).**
`effects.js` importa 15 funcoes de `combat.js` (linhas 14–29) e `combat.js` importa
`resolverEfeitos` de `effects.js` (linha 12). Funciona porque ES modules resolvem bindings tarde,
mas a consequencia pratica e que toda operacao nova exige mexer nos dois arquivos, e os
**poderes** (`vala_comum`, `banquete`, `ossos_firmes`, `peste`, `rugido`, `pavio_curto`, `calo`,
`olho_por_olho`, `segundo_folego`, `golpe_de_vista`, `rastro`, `bolso_fundo`) nao sao dados: sao
12 checagens `estado.jogador.poderes.includes("...")` espalhadas em 9 pontos do pipeline de turno
(`combat.js` 355, 386, 452, 486, 517, 522, 538, 543, 603, 690, 694, 700). Com 50 reliquias/poderes, cada
gancho de turno vira uma cadeia de ifs.

**[ARC-04] Classe hard-coded em seis lugares (MEDIUM).** `classe === "capimaga"|"brutamontes"|
"ligeira"` em `combat.js` (82, 84, 132, 341, 371, 398, 468, 560, 614), tabelas de texto por classe
em `state.js` (20–69), `textoRecurso` em `combatView.js` (236–244), `CLASSES_VALIDAS` em
`start.php` (16), a tabela `classes` no banco e `RETRATOS_CLASSE` em `towerView.js`. Uma quarta
classe exige tocar todos.

**[ARC-05] O banco finge ser fonte de verdade de coisas que o cliente sobrescreve (MEDIUM).**
`classes.hp_inicial` e `acao_por_turno` sao servidos no bootstrap e usados por `start.php` para
gravar `hp_atual`, mas `state.js:novaRun` (linhas 117–118) usa `HP_INICIAL = 80` e
`combat.js:ACAO_POR_TURNO = 3`, e o primeiro `save.php` sobrescreve o valor do servidor.
`habilidade_niveis.descricao` vai no bootstrap (`Catalog::classes`, 30 queries N+1) e a UI usa
`HABILIDADE_TEXTOS` de `state.js`. `habilidade_niveis.efeitos`, `run_cartas`, `cartas.arte`,
`inimigos.arte`, `arquetipos.cor`, `eventos.bloco_min/max`, `classes.inicial` nao sao lidos por
ninguem. Os docs dizem "HP inicial 70" (`01-gdd.md:198`, `02-classes:14`, default do schema), o
codigo usa 80.

**[ARC-06] Modelo de save sem versao efetiva, validacao, migracao ou abandono (MEDIUM; impacto
alto quando disparar — ver BUG-07).** `serializarRun` escreve `versao: 1`; `restaurarRun` nunca a
le. `restaurarRun` (323–350) faz `catalogoCartas.find(...)` sem checar `undefined`, confia em todos
os campos e o boot (`entrarOuRetomar`, 113–126) vai direto para `renderSala`. Nao ha "abandonar
run", "logout" nem "voltar ao menu" enquanto ha run ativa (grep por `logout`/`abandonar` em
`public/assets/js`: so a funcao exportada em `api.js`, sem chamador).

**[ARC-07] Endpoints PHP repetem boilerplate e nao tem tratamento de erro generico (LOW).**
Os 13 arquivos em `public/api` repetem 5–7 `require_once` + `define('CAPITOWER')` e so capturam
`PDOException`. `TypeError`/`Error` viram resposta sem envelope (confirmado em BUG-06).
`config['app']['ambiente']` nunca e lido, entao nao existe distincao dev/prod para exibicao de
erros. `Request::campo` (35–45) cai para `$_GET` em POST, o que permite `save.php?run_id=...` —
inocuo hoje, mas e uma porta.

**[ARC-08] Estado global mutavel montado por partes (LOW).** `estadoGlobal.run` e criado em
`novaRun`/`restaurarRun`, mas `run.id` e anexado em `screens.js` (117, 144) e `run.status` mudado
em `finalizarRun` (258); `estadoGlobal.combate` existe "para debug". `combatView.js` guarda
`indiceSelecionado` e `snapshotAntes` como variaveis de modulo (11, 17) que sobrevivem entre
combates (causa direta de BUG-05).

### 3.3 Acoplamento

- `combat.js ↔ effects.js`: circular (ARC-03).
- `combatView.js` → `towerView.js` (`RETRATOS_CLASSE`) e `rewardView.js` → `state.js`
  (`HABILIDADE_TEXTOS`): views importando de outras views e do estado por conveniencia; nao e
  grave, mas nao ha camada de "apresentacao de dados" (i18n, nomes, retratos) — cada view tem sua
  tabela (`NOMES_PODER`, `RETRATOS_INIMIGO`, `ROTULOS_STAT`, `rotulos` em `cabecalhoAndar`).
- `combatView.js:textoIntencao` (98–122) reimplementa a formula de dano de `receberAtaque`
  (596–599) e diverge dela (BUG-09). `cardView.js:28` mostra `carta.custo`, nao `custoDe(estado,
  carta)`.
- `cardView.js:60–69` acopla a mudanca de estado ao evento `animationend` do CSS (BUG-12).
- `towerView.js:120` repete `0.3` de `state.js:CURA_DESCANSO_PCT`.

### 3.4 Coesao

Boa nos modulos de motor (`rng`, `tower`, `combat`, `effects`) e nos modelos PHP. Fraca em
`screens.js` (auth + catalogo + ciclo da run + todas as salas + fim + perfil), em `state.js`
(catalogo + run + HP + recompensas + composicao de sala + desafios + eventos + save/load + 60 linhas
de texto de habilidade) e em `flet_mvp/capitower/ui.py` (1.611 linhas, classe `App` com 60+
metodos cobrindo animacao, layout, todas as telas e persistencia de recordes).

### 3.5 Escalabilidade (ver tambem secao 20, Future Scalability Analysis)

Onde quebra primeiro, em ordem: (1) poderes/reliquias por string no pipeline de turno (ARC-03);
(2) classe por `if` (ARC-04); (3) `renderizarCombate` redesenhando a tela inteira a cada clique
(hoje ~15 elementos, fica pesado com 5 inimigos + 10 cartas + reliquias + log); (4) o snapshot
sem versao (ARC-06) na primeira mudanca de formato; (5) o bootstrap que baixa o catalogo inteiro
(27 KB hoje, com 200 cartas e 100 inimigos vira 150–200 KB por carregamento, sem cache HTTP).

### 3.6 Technical Debt

- Divida consciente e documentada: eventos (3 de 8–12), balanceamento nunca jogado por gente,
  retratos de inimigo copiados e nao ligados, favicon/fonte nao ligados (`docs/09`).
- Divida nao documentada: tudo nas secoes 4, 5 e 6 deste review. A mais cara e ARC-02 (paridade
  entre tres copias de conteudo e dois motores), porque cada sessao de balanceamento vai ter que
  ser feita duas vezes ou vai divergir.
- Codigo morto acumulado em 6 dias (secao 4.6).

---

## 4. Code Quality Review

### 4.1 Bugs

Detalhados na secao 15. Lista curta, com evidencia:

| ID | Sev | Evidencia | Status |
| --- | --- | --- | --- |
| BUG-01 | HIGH | dois `click()` em "Fim de turno" com sala limpa: andar 3 → 5; evento: 6 → 8 e 2 cartas temporarias; recompensa: 8 → 10 e 2 copias de "Escudo de Carne" | Confirmado ao vivo |
| BUG-02 | HIGH | 15/300 runs de Ligeira travadas em 300 turnos no andar 1–3; P(0 fontes de dano) = 8,3% Ligeira, 1,6% Brutamontes | Confirmado por simulacao + calculo |
| BUG-03 | HIGH | `bm_soco` com Adrenalina 4 e Forca 2 contra Guarda (espinhos 3): 16 de dano / 6 de espinhos; Python: 13 / 3 | Confirmado por script |
| BUG-04 | HIGH | `POST login.php {"usuario":"audit_review@example.test"}` → `ERRO_INTERNO` 500 | Confirmado com curl |
| BUG-05 | MEDIUM | apos vencer o andar 1 jogando carta, o andar 2 renderiza com `.painel--cura` em "Sapo Musculoso" e "Capivarinha" | Confirmado ao vivo |
| BUG-06 | MEDIUM | `finish.php` com `deck:["x"]`: resposta vazia, run vira `vitoria`, perfil ganha 1105 pontos e 6 chefes, objetivos nao avaliados | Confirmado com curl |
| BUG-07 | HIGH | `restaurarRun` sem validacao + boot sem saida | Provavel (caminho claro, gatilho e mudanca de catalogo) |
| BUG-08 | MEDIUM | `carregarCatalogo` so em `iniciarJogo` | Confirmado por leitura |
| BUG-09 | MEDIUM | `textoIntencao` sem `fragilidade`/`evasao`; `carta__custo` estatico; `acaoMax` fixo | Confirmado por leitura |
| BUG-10 | MEDIUM | reload no chefe do andar 10 com HP 30 em combate → volta com 80/80 | Confirmado ao vivo |
| BUG-11 | MEDIUM | `rewardView.js:38–49` oferece "Habilidade" no nivel 10 e o clique so incrementa `recompensasHabilidadeUsadas` | Confirmado por leitura |
| BUG-12 | LOW | carta com `carta--jogada` e `pointer-events:none`, `getAnimations()[0].pending === true`, estado inalterado enquanto a aba nao pinta frames | Confirmado ao vivo (ambiente de preview), Possivel em uso real |
| BUG-13 | LOW | "Ritual Ganancioso" perde a primeira linha do texto em 375px; `.carta__texto { height: 23%; overflow: hidden }` | Confirmado ao vivo |

Bugs menores encontrados por leitura (secao 15): BUG-14 (escape HTML em JSON), BUG-15 (contagem
de chefes conta os dois Gemeos), BUG-16 (`aplicarEstado` escreve qualquer propriedade vinda do
dado), BUG-17 (rejeicoes nao tratadas em `comecarRun`/`abrirPerfil`; `salvarProgresso` engole
erro e a run segue sem salvar apos sessao expirar).

### 4.2 Codigo duplicado

- Formula de dano de inimigo em `combat.js:receberAtaque` e `combatView.js:textoIntencao` (com
  divergencia).
- `absorverOuPerderJogador` (242–249) e o miolo de `receberAtaque` (609–620) fazem a mesma
  absorcao de Bloco; a segunda tem o gatilho de Adrenalina nivel 5 e a primeira nao — reflexo e
  espinhos absorvidos inteiramente pelo Bloco **nao** dao Adrenalina, ataque absorvido da. Nao
  encontrei essa regra nos docs nem no Python; pode ser divergencia (Possivel).
- Cinco endpoints PHP com o mesmo prologo de 7 linhas; 4 `try/catch (PDOException)` identicos.
- `renderDescanso` recalcula `hpMax * 0.3` que `descansar` ja calcula.
- `Catalog::inimigos` roda 15 queries (3 por bloco) que poderiam ser 1.
- Tabela de texto de habilidade em `state.js` e em `seeds.sql` (`habilidade_niveis`).
- `LEGIAO_TEXTO`, `CASCA_GROSSA_TEXTO`, `LIGEIREZA_TEXTO` descrevem em prosa o que
  `TABELA_LACAIOS_INICIAIS`, `TABELA_ADRENALINA_INICIAL` e `verificarLigeireza` implementam em
  numeros — duas fontes que podem desandar (ja desandaram: nivel 5 de Ligeireza diz "+1 Acao no
  primeiro turno" e a HUD mostra "Acao 4/3").

Nao considero duplicacao: `montarBaralho` vs `build_starting_deck`, `gerarTorre` vs
`_generate_tower` — sao portes entre linguagens; o problema deles e ARC-02, nao duplicacao.

### 4.3 Complexidade

- `combat.js:fimDeTurno` (686–739) e `agirUmInimigo` (626–680): 50 linhas cada, com 4 e 3
  checagens repetidas de `estado.status !== "andamento"`. Nao e ilegivel, mas a necessidade de
  checar status apos cada passo mostra que a morte do jogador e "descoberta" por polling em vez de
  interromper a resolucao.
- `screens.js:finalizarRun` (256–269): callback aninhado 3 niveis para "voltar do perfil para a tela
  de fim de run" — `abrirPerfil(() => renderFimDeRun(..., () => abrirPerfil(irParaInicio)))`.
  Na segunda volta o comportamento muda (vai para o inicio em vez de voltar ao fim de run).
- `flet_mvp/capitower/ui.py:render_combat` (1045–1205): 160 linhas.
- Funcoes de resolucao dependem de `ctx` mutavel compartilhado (`consumidos` e escrito tanto por
  `consumir_lacaios` quanto por `consumir_adrenalina`).

### 4.4 Naming

- Bom no geral: portugues consistente, verbos no infinitivo, `snake_case` no banco/JSON e
  `camelCase` no JS. `docs/04` secao 8 define a convencao e ela e seguida.
- Inconsistencias: `Acao` na UI vs `acao`/`acaoMax` no estado vs `ACAO_POR_TURNO`; "Bloco" na UI
  e "Defesa" em `challenges.json`/MVP; `TAMANHO_MAO` vs `HAND_SIZE`; `estado` significa tres
  coisas (estado de combate, estado de status como "fraqueza", `estado_json`); `alvo` e ao mesmo
  tempo indice (`estado.alvo`) e string de escopo (`efeito.alvo`); `desafio` para uma sala que so
  da bonus (DES-01).
- `Request::escapar` chama-se "escapar" mas e usado para saida JSON (BUG-14).

### 4.5 Error Handling

- Cliente: `api.js:chamar` (6–21) assume que toda resposta e JSON; um fatal PHP (BUG-06) vira
  `SyntaxError` sem `codigo`. `salvarProgresso` engole erro e o jogo continua (sessao expirada →
  o jogador joga 20 andares sem salvar nada). `comecarRun`, `abrirPerfil`, `proximoAndar` e
  `iniciarRunNoServidor` nao tem `catch`; uma rejeicao deixa a tela como esta, sem mensagem.
  `main.js` so trata erro do boot.
- Servidor: so `PDOException`. `Auth::registrar` faz dois INSERTs sem transacao. `Run::finalizar`
  faz UPDATE + INSERT sem transacao e `finish.php` chama `Meta::avaliarObjetivos` depois, fora de
  qualquer transacao (BUG-06). `Request::texto` devolve `''` para nao-string, o que transforma
  `{"usuario": 123}` em "Informe usuario e senha" — aceitavel.
- Motor: o `default` de `resolverUm` loga e segue; `aplicarEstado` ignora estado desconhecido em
  silencio; `comprarCartas` com as duas pilhas vazias retorna sem log. Fallbacks silenciosos sao
  adequados para jogo, mas escondem erro de dado (BUG-16).

### 4.6 Dead Code

- `combat.js:criarCombate` (143–151, "mantido por compatibilidade", sem chamador).
- `combatView.js:criarTelaFim` + `handlers.aoReiniciar` (nunca acionado, `screens.js:251` diz isso).
- `state.js:gerarSeed` (99–101; a seed vem do servidor).
- `audio.js:somClique` (81–83).
- `ganharBloco(estado, "inimigo", ...)` — nenhuma carta usa.
- `tutorialView.js:mostrarTutorial(aoFechar)` — parametro nunca passado.
- `api.js:logout` — sem chamador.
- `public/assets/js/data/{cards,enemy,events,challenges}.json` — servidos, nao lidos.
- Banco: `run_cartas`, `habilidade_niveis.efeitos`, `cartas.arte`, `inimigos.arte`,
  `arquetipos.cor`, `eventos.bloco_min/bloco_max`, `classes.inicial`, `classes.acao_por_turno`
  (efetivamente).
- Config: `app.ambiente`, `app.nome`, `app.versao`.
- Assets: `public/assets/img/enemies/*` (6,1 MB), `icon.png` (1 MB), `LuckiestGuy-Regular.ttf` —
  copiados e nao referenciados (documentado em `docs/09`).
- `README.md` diz "Fase de planejamento e documentacao. Nao ha codigo de jogo ainda".

---

## 5. Game Systems Review

### 5.1 Combat

**Implementacao:** `core/combat.js` (749 linhas). `criarCombateDeSala` monta o estado; turno do
jogador = `jogarCarta` N vezes + `fimDeTurno`; `fimDeTurno` roda mordida dos lacaios → poderes de
fim de turno → veneno no jogador → Bolso Fundo → descarte → cada inimigo vivo age → veneno e decay
nos inimigos → `iniciarTurnoJogador`.

**Dependentes:** `effects.js`, `screens.js`, `combatView.js`, `cardView.js`.

**O que esta certo:** ordem de resolucao clara e comentada; `verificarFim` chamado apos cada
mutacao relevante; `alvoAtual` reaponta o alvo quando o atual cai; overflow de dano e Bloco
tratados; `fraquezaFresca`/`fragilidadeFresca` reproduzem exatamente a duracao dos testes Python
(`test_weak_1_...`, `test_frail_2_...`); Gemeos, Gertrudes em 3 fases, reflexo, espinhos,
crescimento e `mudaPadrao` funcionam (simulados).

**Problemas:**
- BUG-03: "um golpe por carta" nao portado — Forca, Fraqueza (arredondamento), Fragilidade,
  espinhos, reflexo e `mudaPadrao` contam por sub-efeito de dano, nao por carta.
- `causarDano` para `"todos"` (202–211) nao para se o jogador morrer por reflexo no meio do loop
  (`aplicarDanoInimigo` nao checa `status`): os inimigos seguintes ainda levam dano e podem morrer
  depois da derrota; `verificarFim` ja esta em `derrota`, entao o resultado fica certo, mas o log
  mostra "X cai!" depois de "Voce caiu." (LOW, Confirmado por leitura).
- `perderVidaJogador` (367–394) seta `derrota` direto e `jogarCarta` continua resolvendo os
  efeitos restantes da carta, poderes (`segundo_folego`, `golpe_de_vista`) e `verificarLigeireza`
  com o jogador morto. Sem efeito visivel hoje; e o tipo de coisa que vira bug quando entrar um
  efeito "ao morrer".
- `iniciarTurnoJogador:546` — `acao = 3 - roubarProximo` sem clamp; so o Rato rouba 1, entao nao
  fica negativo hoje. Com dois inimigos que roubam, a Acao fica negativa (Possivel, futuro).
- Veneno no jogador (`venenoTickJogador`) resolve **antes** dos ataques inimigos e o veneno nos
  inimigos **depois** dos ataques — assimetria nao documentada em `01-gdd.md`. Nao e bug, e regra
  escondida.
- Bloco do inimigo: `agirUmInimigo:628` zera no inicio da acao do proprio inimigo, entao o Bloco
  que ele ganhou no turno anterior dura o turno inteiro do jogador. Igual ao Python. Ok, mas a
  intencao "Defende 10" nao diz que o Bloco ja em campo sera zerado antes.

**Extensibilidade:** media. Novo tipo de acao de inimigo = 1 `else if` em `agirUmInimigo` + 1 em
`textoIntencao` + 1 em `iconeIntencao`. Novo poder = N ifs (ARC-03).

**Testabilidade:** alta (motor puro, seed). Testes: zero na trilha JS.

### 5.2 Cards / Effects

**Implementacao:** `effects.js` (30 operacoes), dados em `seeds.sql` (servidos) / `cards.json`
(espelho). Condicoes: `alvo_envenenado`, `consumidos>=N`, `impulso>=N`, `adrenalina>=N`,
`evasao>=N` (parse por `split(">=")`).

**Problemas:**
- BUG-03 (acima).
- BUG-16: `aplicarEstado` faz `if (nomeEstado in entidade) entidade[nomeEstado] += valor` —
  qualquer chave da entidade e valida (`"estado":"hp"`, `"acao"`, `"lacaios"`). Nenhuma validacao
  de esquema do JSON de efeitos no bootstrap nem no seed; um typo em `op` so aparece no log de
  combate, em jogo.
- `devolver_ultima` (197–209) so funciona se a ultima carta esta no descarte; um Poder com
  `custo > 0` vira `ultimaJogada` (`jogarCarta:514`) mas nao vai pro descarte (510–512) → "Nada
  para devolver". Inconsistencia de regra, LOW.
- `trocar_mao` descarta a mao e compra N; se a pilha de compra esvaziar no meio, reembaralha o
  descarte **incluindo as cartas que acabou de descartar** — pode devolver a mesma mao. LOW,
  Possivel divergencia (nao conferi o Python).
- Poder repetido na mao: a segunda copia fica bloqueada ("Poder ja em campo") e e descartada no
  fim do turno — comportamento razoavel, mas o tutorial nao explica e a carta so mostra o motivo
  no `title` (hover).
- Custo exibido e `carta.custo`, nao `custoDe` (BUG-09): com `proxima_gratis` ou Ligeireza nivel
  10 a carta mostra "1" e custa 0.

### 5.3 Deck / Hand / Draw / Discard

- Deck inicial: `novaRun` sorteia 5 distintas x2 (D18/D19). **Falta a guarda de ataque minimo do
  MVP** (`run.py:41–47`, `MIN_ATTACKS = 2`) e o reroll de 1 carta (`01-gdd.md:161`). BUG-02.
- Compra: `comprarCartas` reembaralha o descarte quando a pilha acaba; `bolso_fundo` guarda 1 e a
  mao seguinte tem 6. Sem limite de mao. Sem exaustao explicita: Poder jogado simplesmente nao
  volta ao descarte — sem log, sem contagem visivel.
- **A UI nao mostra tamanho da pilha de compra, do descarte, nem o deck** (`combatView.js` nao
  renderiza nada disso; nao ha tela de deck). Num deckbuilder isso e informacao primaria.
- Cartas sao referencias compartilhadas ao objeto do catalogo (`montarBaralho` empurra o mesmo
  objeto duas vezes). Funciona porque nada muta carta, e `_temporaria` e um clone. Se algum dia
  entrar "upgrade" (D06 diz que nao), quebra.

### 5.4 Energy ("Acao")

`ACAO_POR_TURNO = 3`; `ganhar_acao`, `acao_por_consumido`, Ligeireza, Largada e nivel 5 somam sem
teto; `roubar` subtrai. `acaoMax` (103) nunca muda → HUD "Acao 4/3" (BUG-09). `classes.acao_por_turno`
do banco e ignorado (ARC-05).

### 5.5 Damage / Block / Buffs / Debuffs

- Formulas: dano = (base + Forca) × 0,75 se Fraqueza (floor) × 1,5 se Fragilidade do alvo
  (floor); Bloco absorve primeiro. Consistente entre jogador e inimigo, exceto que
  `absorverOuPerderJogador` (reflexo/espinhos) nao dispara o gatilho de Adrenalina nivel 5 e
  `receberAtaque` dispara (4.2).
- Decay: Fraqueza/Fragilidade do jogador caem no inicio do turno dele (se nao frescas); as dos
  inimigos caem no fim da fase inimiga. Testado no Python, portado igual.
- Retaliacao: `Math.max` em valor e turnos (169–171) — duas Retaliacoes nao somam, a maior vale.
  Igual ao Python? Nao conferi; a carta diz "Retaliacao 3 por 2 turnos", entao `max` e defensavel.
- Evasao anula um ataque inteiro por ponto, antes do Bloco. Retaliacao dispara mesmo com o ataque
  totalmente absorvido pelo Bloco (621–623). Nao esta escrito em lugar nenhum visivel ao jogador.

### 5.6 Enemies / Intent

- 27 inimigos, padrao ciclico, `indice` inicial aleatorio quando permitido, flags. `intentAtual`
  mostra o proximo turno. `mudaPadrao` (Experimental) avanca o indice a cada golpe recebido — a
  intencao mostrada muda durante o turno do jogador; a re-renderizacao mostra isso, entao e
  legivel.
- **DES-04:** "Carregando o proximo golpe" nao mostra o valor do golpe (Garcom: 30; Gertrudes:
  26). O jogador nao consegue planejar Bloco para o unico ataque que realmente importa.
- BUG-09: a intencao ignora a Fragilidade do jogador (×1,5) e a Evasao.
- Retratos: `RETRATOS_INIMIGO` por **nome** so cobre Gertrudes; os 27 PNGs por id existem e nao
  sao usados (documentado).

### 5.7 Turns

Ver 5.1. Um detalhe de UX/estado: nao existe "fase inimiga" visivel — `fimDeTurno` resolve tudo
sincrono e a tela pula do fim do turno N para o inicio do turno N+1 com um diff de animacao. Com 3
inimigos atacando e veneno, o jogador ve varios numeros flutuando ao mesmo tempo e o log de 14
linhas, sem ordem. Nao e bug, e limitacao da arquitetura "redesenha tudo" (docs/09 reconhece).

### 5.8 RNG

- `mulberry32` + `derivarSeed(seed, sal)`; sais fixos por uso (`rngDoAndar(run, 1..5)`,
  `derivarSeed(seed, 999)` para o baralho, `derivarSeed(seed, sala.andar)` para o combate).
  Magic numbers sem constante nomeada, mas documentados em comentario.
- **Consequencia de design (BUG-10):** cada andar e 100% reproduzivel a partir da seed. Combinado
  com o save na entrada do andar, recarregar a pagina da o mesmo embaralhamento, a mesma intencao
  inicial e o HP de antes do combate: o jogador pode "ensaiar" um chefe indefinidamente. Slay the
  Spire salva o estado do combate justamente para fechar isso.
- Seed gerada no servidor (`random_int`), boa.
- `inteiroAleatorio(rng, 0)` retorna 0 e `escolher([], rng)` retorna `undefined` — nao tratado;
  `iniciarEvento` com `estadoGlobal.eventos` vazio quebraria (Possivel, so se o seed falhar).

### 5.9 Tower / Map

`tower.js:gerarTorre` porta o Python fielmente: 5 blocos × (5 combates, 1 elite entre a 3a e 8a
posicao, 1 evento, 1 descanso, 1 desafio, chefe no 10o) + andar 51. Sem ramificacao, sem preview:
o jogador nao ve o que vem (o MVP tem `show_floor_preview`; o JS nao). `ANDAR_FINAL = 51` vs
README/GDD "50 andares" (DOC-01).

### 5.10 Progression / Rewards

- `finalizarCombate` (271–311): elite/chefe → 1 ponto → `renderRecompensa` com **1 carta aleatoria
  da classe (pode repetir)** ou +1 nivel. GDD 4.2 (`01-gdd.md:174–178`) especifica "1 entre 3,
  nunca oferece carta que ja esta no deck"; o MVP implementa isso (`run.py:67–71`). DES-02.
- BUG-11: no nivel 10 a opcao de habilidade continua clicavel e desperdica o ponto.
- BUG-01 aplica-se aqui (duas cartas por ponto).
- `cartaAleatoria` usa `Math.min(pool.length - 1, ...)` defensivo, ok.

### 5.11 Events / Rest / Challenge

- Eventos: 3, sorteados com reposicao por andar (`escolher(estadoGlobal.eventos)`) — repetem na
  mesma run. Conhecido.
- Descanso: 30% do HP max, ok. BUG-01 (dobro).
- **DES-01 (Confirmado):** a sala "Desafio opcional" no JS aplica o modificador ANTES do combate
  (`screens.js:207–210`: `aplicarModificador` → `iniciarCombateDaSala`) e o combate e uma
  composicao comum sem nenhum agravante. D25 diz "**Vencer** da um modificador"; o MVP aplica um
  `challenge` real no combate (`content.py:200–203`: inimigos +2 Forca, ou +3 Forca/turno a partir
  do 6o) e so oferece o modificador depois ("Desafio vencido", `ui.py:1551–1575`). No JS o
  "desafio" e um bonus gratis + um combate normal, e nao e opcional (nao ha "recusar").
- `challenges.json` documenta `op` como `bloco_extra`/`acao_extra_turno1`/`compra_extra_turno1`,
  mas `aplicarModificador` so entende `forca_permanente`/`hp_max_permanente`; os outros 3 sao
  detectados por id no motor. Dois mecanismos para 5 itens (documentado em `docs/09`, mas e o
  tipo de excecao que vira norma).

### 5.12 Death / Victory / Restart

- Derrota: `perderVidaJogador` → `derrota` → `finalizarRun("derrota")` → `finish.php`. Se o
  `finish` falhar (rede, sessao, fatal), `console.error` e a tela de fim aparece igual; a run
  continua `ativa` no banco e o proximo boot retoma o andar com o HP de antes (BUG-10). A morte
  nao e durável.
- Vitoria no andar 51: idem.
- "Nova torre" chama `comecarRun` com o argumento errado: `towerView.js:174` faz
  `botao.addEventListener("click", onNovaRun)`, entao `comecarRun` recebe o `MouseEvent` como
  `classeSlug` → `iniciarRunNoServidor(event)` manda `{"classe":{"isTrusted":true}}` →
  `start.php` cai no default `capimaga` → `novaRun(seed, event)` → `cartasDaClasse(event)` filtra
  `carta.classe === event` → **deck vazio**; e `criarCombateDeSala({classe: event})` nao da nem o
  lacaio inicial (`classe === "capimaga"` e falso). **BUG-18 (HIGH, Provavel por leitura; nao
  reproduzi ao vivo porque a run de teste nao chegou ao fim pela UI).** O jogador que clica "Nova
  torre" na tela de fim de run entra num combate com mao vazia e 0 lacaios: so resta morrer.

### 5.13 Save / Load

- Ver ARC-06, BUG-07, BUG-10. Alem disso:
- `Run::salvar` aceita qualquer `andar` (`TINYINT`, ate 255) e qualquer deck; `andar_maximo`
  usa `GREATEST`. `Run::finalizar` calcula `pontos_meta = andar*10 + pontos*5 + 100` do que o
  cliente mandar. Documentado como decisao (`04-arquitetura.md` secao 2), mas a meta progressao
  (objetivos, desbloqueios, perfil) e inteiramente forjavel — confirmei com um `curl` que deu 1105
  pontos, 6 chefes e vitoria a uma conta que nunca passou do andar 10.
- `Run::criar` abandona runs ativas anteriores — bom, evita duas ativas. Mas duas abas abertas na
  mesma conta salvam por cima uma da outra sem conflito detectado (nao ha `versao`/`updated_at`
  no `save.php`).
- Snapshot nao guarda `cartasTemporarias` separado (deriva de `_temporaria`), ok; nao guarda
  `torre` (deriva da seed), ok; nao guarda o combate, por decisao.

### 5.14 Meta progression

- `Meta::avaliarObjetivos` e idempotente por chave primaria — bom.
- 3 dos 12 objetivos recompensam a mesma carta (`cm_baforada`: `marco-andar-10`,
  `derrotar-dorival`, `queda-precoce`); `INSERT IGNORE` faz os outros dois nao darem nada (DES-03).
- `chefes_derrotados` soma `count(chefes_derrotados)` — os Gemeos contam 2 (BUG-15).
- BUG-08: desbloqueio nao chega ao catalogo em memoria ate recarregar a pagina; "Nova torre" logo
  apos "Objetivo cumprido" comeca sem as cartas novas.
- 5 cartas da Capimaga sao `inicial = 0` → o pool inicial real e 15, e a tela inicial diz "20
  cartas" (`towerView.js:54`).

### 5.15 Audio / Animation / Tutorial

- Audio sintetizado por Web Audio, contexto sob demanda, mudo em `localStorage` — correto e sem
  asset. `somVitoria`/`somDerrota` usam `setTimeout` sem cancelamento (inocuo).
- Animacao por diff (`snapshotDe`/`aplicarEfeitosVisuais`): boa ideia dado o "redesenha tudo",
  mas o snapshot vaza entre combates (BUG-05) e a jogada depende de `animationend` (BUG-12).
- Tutorial: 5 passos, `localStorage`; aparece por cima da selecao de classe. Nao cobre: alvo
  padrao, poderes, recursos de classe, pilhas, o que e "desafio". Texto do passo 5 ("escolha uma
  carta nova ou evolua") sugere recompensa em toda sala; so elite/chefe dao.

---

## 6. State Management

**Onde vive:** `estadoGlobal` (`state.js:71–79`): catalogo (imutavel apos boot), `run` (mutavel),
`combate` (mutavel, um por sala). Mais `indiceSelecionado`/`snapshotAntes` em `combatView.js`,
`ctx` em `audio.js`, e `localStorage` para mudo/tutorial.

**Quem muta:** `state.js` (run), `combat.js`/`effects.js` (combate), `screens.js` (`run.id`,
`run.status`, `run.pontosRecompensa`, `run.recompensasHabilidadeUsadas` — direto, sem passar por
`state.js`), `combatView.js` (`estado.alvo` via `selecionarAlvo`, `indiceSelecionado`).

**Transicoes:** implicitas, por chamada de funcao. Nao ha enumeracao de telas nem checagem "estou
na tela certa para essa acao".

**Estados invalidos encontrados:**

| Cenario | Resultado | Ref |
| --- | --- | --- |
| Clique repetido em qualquer botao de transicao durante o `await` do save | acao dupla + andar pulado | BUG-01 |
| Duas abas na mesma conta | saves se sobrescrevem; a que perder a corrida ve outra run no reload | 5.13 |
| Fechar durante recompensa/evento/descanso | volta ao andar com o combate por refazer (HP de antes) | BUG-10 |
| `finish.php` falha | run `ativa` com status local `derrota`; reload retoma viva | BUG-10 |
| Catalogo muda com run ativa | `restaurarRun` monta deck com `undefined`; boot quebra sem saida | BUG-07 |
| "Nova torre" na tela de fim | `classe = MouseEvent` → deck vazio | BUG-18 |
| Vencer jogando carta → proximo combate | `snapshotAntes` do combate anterior aplicado ao novo | BUG-05 |
| Dado temporario → permanente | `run.hp` e sincronizado so no fim do combate; `curaDiferida` consumida no inicio do proximo combate, ok; `_temporaria` removida no chefe, ok | — |

**"A UI acredita X, o estado acredita Y":**
- Carta voou e sumiu (som tocou), estado nao mudou ate o `animationend` — se a re-renderizacao
  (Fim de turno, selecionar alvo) acontecer antes, a jogada e silenciosamente descartada
  (`cardView.js:65–68`, `combatView.js:347`). Provavel em duplo clique + clique rapido em "Fim de
  turno"; Confirmado no ambiente de preview com frames pausados (BUG-12).
- Intencao mostra N, ataque causa ⌊N×1,5⌋ com Fragilidade (BUG-09).
- Custo mostra 1, custa 0 (BUG-09).
- Tela de recompensa oferece "nivel 10 → 10" (BUG-11).
- Tela de fim de run diz "Permadeath: nao da para retomar (D12)" enquanto o servidor pode ainda
  ter a run ativa (BUG-10).

---

## 7. UX/UI Review

Avaliacao feita ao vivo em 1280×720 e 375×812 (preset mobile) no navegador embutido da sessao,
mais leitura de todo o CSS. Ressalva: o painel de preview desta sessao pausa animacoes quando nao
esta em primeiro plano, entao nao avaliei a *sensacao* das animacoes, so o resultado final.

### 7.1 Clareza

- **O que esta acontecendo:** o log de 14 linhas (`criarLog`) e a unica narrativa; apos "Fim de
  turno" com 3 inimigos ele estoura. Numeros flutuantes ajudam. Sem fase inimiga visivel (5.7).
- **O que posso fazer:** cartas bloqueadas ficam a 50% de opacidade com o motivo no `title`
  (so hover; no toque nao existe). "Poder ja em campo" e "Acao insuficiente" so no log ao tentar.
- **Quanto dano causara:** a carta mostra o texto estatico; Forca/Fraqueza nao entram (o MVP
  tambem nao mostra). A intencao inimiga mostra o dano com Forca/Fraqueza do inimigo, mas ignora
  a Fragilidade/Evasao do jogador (BUG-09) e esconde o valor de golpes carregados (DES-04).
- **Quanto recurso tenho:** HP, Acao, recurso de classe e estados: sim. Pilhas de compra/descarte,
  deck, cartas exauridas (Poderes): nao (5.3).
- **Onde estou:** cabecalho "Andar N de 51, Bloco, tipo" — bom. Sem preview do proximo andar, sem
  mapa. Sem indicacao de pontos de recompensa restantes ou nivel atual da habilidade fora da
  tela de recompensa.

### 7.2 Feedback

- Dano/cura/bloco/invocacao/morte: flash + numero + som. Vitoria/derrota: som + tela. Bom para
  o estagio.
- Erro: `console.error` para save/finish; nenhuma mensagem em tela. `comecarRun` falhando = botao
  que nao faz nada.
- Cura espuria no inicio de todo combate (BUG-05) — feedback errado, ativo.
- Sem feedback de "carregando" nas transicoes (BUG-01 e agravado por isso: o jogador clica de
  novo porque nada aconteceu).

### 7.3 Hierarquia visual e layout

- Combate em 1280×720: a tela mede 928 px de altura (`scrollHeight`) — cabecalho e intencao ficam
  fora da viewport quando a mao esta visivel, e "Fim de turno" e o log ficam abaixo da dobra
  (`.mao` de 365 a 585 px, `.log` de 649 a 717 px com scroll 178). O jogador rola entre a intencao
  e a mao a cada turno. O painel do jogador ocupa ~120 px de altura com um retrato e duas
  linhas. **UX-01 (MEDIUM).**
- Mobile 375×812: sem scroll horizontal (bom), 961 px de altura, cartas de 94 px com texto de 10 px
  cortado (BUG-13). "Fim de turno" abaixo da dobra.
- Molduras por tipo com cor distinta, custo em gema, nome/tipo em janela — legivel e bonito no
  desktop. Bosses e elites usam o mesmo emoji generico dos monstros comuns (retratos existem e nao
  estao ligados): o chefe de bloco nao parece chefe.
- Sem `:focus-visible` para cartas e paineis (`tabindex="0"` existe, foco invisivel); so o form
  de login tem estilo de foco.

### 7.4 Interacao

- Jogar carta: duplo clique **ou** clique + botao "Jogar" (`combatView.js:332–352`) — cobre
  toque. Enter/espaco no teclado — bom.
- Sem confirmacao em "Nova torre" (que cria run e abandona — e cai no BUG-18) nem em "Fim de
  turno" com Acao sobrando.
- Sem logout, sem abandonar run, sem voltar ao menu com run ativa (ARC-06).
- "Desafio opcional" nao tem "recusar" (DES-01).
- Tutorial abre por cima da selecao de classe na primeira visita; o botao "Como jogar" nao existe
  dentro do combate.
- Botao de som e um `button` fixo 40×40 no canto — fino. `alt=""` nos retratos e `h1.sr-somente`
  no logo — cuidado com acessibilidade que muitos protótipos nao tem.

### 7.5 UX de jogo (regras arbitrarias que o jogador precisa descobrir)

Bloco do inimigo dura o turno do jogador inteiro; veneno do jogador resolve antes dos ataques;
Retaliacao dispara mesmo com Bloco absorvendo; Evasao consome antes do Bloco; Poder nao volta ao
baralho; segunda copia de Poder e carta morta; Fraqueza "fresca" nao decai no primeiro turno;
`mudaPadrao` do Experimental; o "desafio" que nao e desafio; recompensa so em elite/chefe (o
tutorial sugere "depois de limpar uma sala"). Nenhuma dessas esta em tela.

---

## 8. Performance Review

Contexto: jogo de turnos, ~15 elementos de UI, 60 cartas, ≤3 inimigos. Complexidade algoritmica
e irrelevante; o que importa e rede e assets.

**[PERF-01] Assets superdimensionados (MEDIUM, Confirmado por tamanho de arquivo).**
`personagens/*.png`: 1,64–1,80 MB cada (4 arquivos, 6,6 MB) exibidos em ~100 px na selecao de
classe e no HUD; `frames/*.png`: 0,67–0,98 MB cada (3,0 MB) como `background-image` de cartas de
148 px; `cenarios/*.jpg`: 0,55–0,70 MB cada; `logo.png` 0,4 MB. Primeira sessao: ~5,5 MB na tela
inicial + ~3,6 MB ao entrar no primeiro combate. O alvo e InfinityFree (banda e CPU limitadas) e
celular. Redimensionar para 2× o tamanho exibido e converter para WebP reduziria ~90%.
`img/enemies/*.png` (6,1 MB) e `icon.png` (1 MB) nao sao servidos hoje, mas serao quando ligados.

**[PERF-02] Redesenho total por acao (LOW).** `renderizarCombate` recria toda a arvore a cada
clique (inclusive selecionar carta/alvo). Hoje imperceptivel. Cresce linearmente com inimigos ×
cartas × tags; nao vai ser problema antes de ~10× o conteudo atual. Nota: o `title` das cartas e
o `img` dos retratos sao recriados — cache do navegador resolve.

**[PERF-03] Bootstrap sem cache e com N+1 (LOW).** `Catalog::classes` faz 1 + 3 queries;
`Catalog::inimigos` faz 1 + 15; sem `Cache-Control`/ETag; 27 KB por carregamento. Irrelevante hoje,
relevante com 200 cartas em host compartilhado.

Sem vazamentos encontrados: listeners morrem com `innerHTML = ""`; `numero-flutuante` remove a si
mesmo; `setTimeout` de som e curto; `AudioContext` unico.

---

## 9. Security & Robustness

Contexto: single player, sem ranking, servidor confia no cliente por decisao (`04-arquitetura.md`
secao 2). Avaliado o que ainda importa nesse contexto.

- **[SEC-01] Meta progressao forjavel (MEDIUM, Confirmado, decisao documentada).** `finish.php`
  aceita `andar`, `pontos_recompensa`, `chefes_derrotados` e `deck` do cliente; um `curl` com a
  sessao deu vitoria, 1105 pontos, andar 51 e 6 chefes a uma conta no andar 10. Nao e "bug" sob a
  decisao atual, mas invalida qualquer futuro leaderboard/objetivo competitivo e, junto com
  BUG-10, torna os objetivos farmaveis sem ferramenta nenhuma (basta recarregar).
- **[BUG-04] `login_tentativas.usuario VARCHAR(24)` (HIGH).** Login por e-mail falha com 500 antes
  de responder — e tambem faz o rate limit nao registrar essas tentativas (a excecao aborta o
  INSERT). Como a resposta e sempre 500 nesse caminho, nao e um bypass util para forca bruta, mas
  e um bug de disponibilidade da funcao "usuario ou e-mail".
- **[BUG-06] `finish.php` nao atomico + fatal sem envelope (MEDIUM).** Entrada malformada
  (`deck: ["x"]`) causa `TypeError` em `Meta::contextoDaRun:61` (`static fn(array $carta)`) depois
  de `Run::finalizar` ter feito UPDATE + INSERT. Resultado: run fechada, estatisticas contadas,
  objetivos nunca avaliados, resposta vazia. Tambem acontece por qualquer erro de banco entre os
  passos.
- **[SEC-02] CSRF (LOW).** Sem token. Mitigado por `SameSite=Lax` (cookie nao vai em POST
  cross-site) e por `Content-Type: application/json` (form HTML nao gera JSON; fetch cross-origin
  faz preflight que o servidor nao responde). Aceitavel hoje; documentar a dependencia dessas duas
  condicoes.
- **[SEC-03] Cookie `secure = false` no exemplo de config** e docs mandam ligar em producao; nao
  ha checagem automatica. `session.cookie_lifetime = 0` (sessao) — ok.
- **[SEC-04] Enumeracao de usuario/e-mail (LOW):** `register.php` responde 409 "ja cadastrado".
  Aceitavel para o contexto.
- **[SEC-05] Rate limit por IP com janela em `login_tentativas` sem expurgo (LOW):** a tabela
  cresce para sempre; atras de NAT escolar (o ambiente descrito em `docs/09`) 8 tentativas em 15
  min bloqueiam a turma inteira.
- **[SEC-06] Senha sem limite superior (LOW):** bcrypt trunca em 72 bytes; `password_hash` com
  entrada de 1 MB e CPU gratis para quem quiser. Limitar a 128.
- **[BUG-14] `Request::escapar` (`htmlspecialchars`) aplicado a JSON (LOW):** a UI usa
  `textContent`, entao `o'neil@x` viraria `o&#039;neil@x` na tela. Hoje so o e-mail pode ter
  esses caracteres e nao e exibido. Escape pertence a quem renderiza HTML, nao a API.
- **Save corruptivel (ARC-06/BUG-07):** o servidor nao valida o snapshot; um cliente antigo,
  uma aba com JS velho ou um edit manual grava algo que o boot nao consegue ler e nao ha
  recuperacao pela UI.
- **Positivo:** nenhuma concatenacao de SQL encontrada; `IN (?,?,?)` em `Meta::contextoDaRun`
  montado com placeholders; `app/.htaccess Deny from all` + constante; sem `eval`, sem `innerHTML`
  com dado do usuario (tudo `textContent`); catalogo publico sem login e intencional.

---

## 10. Testability

- **Trilha JS: zero testes.** O motor e perfeitamente testavel (importei em Node sem shim; 900
  runs, 0 excecoes). A ausencia e mais custosa aqui do que o normal porque o motor e um porte de
  outro motor que **tem** 13 testes de regra (`flet_mvp/tests/test_combat.py`, todos passando):
  os casos ja existem, so nao foram portados — e dois deles falhariam no JS hoje
  (`test_split_damage_card_is_one_hit`, `test_split_damage_card_triggers_thorns_once` → BUG-03).
- `screens.js` e intestavel (closures, DOM, fetch). `state.js` e testavel exceto
  `carregarCatalogo`. Os `*View.js` sao testaveis com jsdom, mas nada exige isso agora.
- Backend: sem testes; `Meta::condicaoBatida` e `Run::finalizar` sao funcoes puras o bastante para
  testes com um banco de teste.
- RNG controlavel por seed em tudo — otimo para testes de regressao ("seed X, andar Y, jogadas Z
  → estado W").
- Testes concretos sugeridos na secao 18.

---

## 11. Dependencies & Configuration

- **Sem dependencias JS ou PHP** (decisao D16). Nao ha lockfile porque nao ha pacote. Positivo:
  zero superficie de supply chain. Negativo: sem lint, sem formatter, sem type check — os erros de
  tipo desta auditoria (`comecarRun(MouseEvent)`, BUG-18) seriam pegos por JSDoc + `tsc --checkJs`
  sem introduzir build.
- **Python:** `flet==0.86.5` pinado (bom); `requirements.txt` e `pyproject.toml` duplicam o pin.
- **Config PHP:** `config.example.php` documenta bem; `ambiente`, `nome`, `versao` nao sao usados
  (ARC-07). Nao ha `.env`; `config.php` fora do git (correto).
- **Schema:** `CREATE TABLE IF NOT EXISTS` + `ON DUPLICATE KEY UPDATE` — idempotente, mas sem
  migracoes: alterar uma coluna existente exige SQL manual fora do repositorio. `runs.andar_atual
  TINYINT UNSIGNED` (255) ok para 51. `login_tentativas.usuario VARCHAR(24)` — BUG-04.
  `usuarios.email VARCHAR(160)` vs `register.php` limita a 160 — ok.
- **`.claude/launch.json`:** `php -S` na 8000 e `flet run --web` na 8550 — funcionam
  (verificado).
- **`.gitignore`** cobre config real, APK, `Assets/` bruto, `__pycache__`. `.git` tem 25 MB por
  causa dos PNGs (aceitavel; usar Git LFS so se a arte crescer).
- **Docs desatualizados:** `README.md` ("Nao ha codigo de jogo ainda", "50 andares", stack sem
  mencionar que o catalogo vem do banco); `01-gdd.md` HP 70 e recompensa 1-de-3; `04-arquitetura.md`
  secao 3 lista `data/cache.js` que nao existe e nao lista `tower.js`/`audio.js`/6 views. DOC-01.

Ferramentas rodadas: `php -l` em todos os `.php` (ok), `node --check` em todos os `.js` (ok),
`python tests/test_combat.py` (13/13), simulacao Node (900 runs, 0 excecoes, 15 softlocks).

---

## 12. Maintainability

Pergunta central: quanto custa adicionar conteudo sem quebrar?

| Tarefa | Custo hoje | Onde doi |
| --- | --- | --- |
| Nova carta com ops existentes | 1 linha em `seeds.sql` (+ espelho em `cards.json` e `cards.py` se quiser manter paridade) | ARC-02: tres lugares; nenhum valida o JSON |
| Nova carta com op nova | `effects.js` (case) + `combat.js` (mutador) + talvez `ctx` | ARC-03 |
| Novo poder/reliquia | 1 case em `effects.js` + N ifs em `combat.js` + `NOMES_PODER` em `combatView.js` | ARC-03; nada garante que o if foi posto em todos os ganchos |
| Novo inimigo | 1 linha em `seeds.sql` + `encontros`; se tiver flag nova, `criarInimigo` + `aplicarDanoInimigo`/`agirUmInimigo` + `textoIntencao` + `iconeIntencao` | ok para dados, 4 pontos para comportamento |
| Novo tipo de acao inimiga | `agirUmInimigo` + `textoIntencao` + `iconeIntencao` | 3 pontos, sem registro |
| Nova classe | 6+ arquivos (ARC-04) + banco | alto |
| Novo tipo de sala | `tower.js` + `screens.js:renderSala` + view + `cabecalhoAndar.rotulos` + `salaDaRecompensa` | medio |
| Novo objetivo | 1 linha em `seeds.sql`; tipo novo = 1 case em `Meta::condicaoBatida` + contexto | bom |
| Mudar formato do save | sem migracao; runs ativas quebram (BUG-07) | alto |
| Balancear numeros | mudar em `seeds.sql` **e** em `cards.py` para o MVP continuar sendo referencia | ARC-02 |

Encontrabilidade: boa — nomes de arquivo dizem o que fazem, comentarios de cabecalho apontam para
docs e decisoes. Consistencia: boa dentro de cada trilha. Documentacao: acima da media em
quantidade, com partes desatualizadas. Um dev novo em 6 meses vai perder tempo principalmente
em (a) descobrir que `data/*.json` nao e o que o jogo usa, (b) entender por que existem dois
jogos no repo e qual manda, (c) achar todos os ganchos de um poder.

---

## 13. Cross-System Issues

- **Combate + save (BUG-10, ARC-06):** save na entrada do andar + RNG deterministico por andar +
  morte nao duravel se `finish` falhar = reload-scum total. Interage com meta progressao: qualquer
  objetivo vira garantido com paciencia.
- **UI + estado (BUG-01, BUG-05, BUG-12):** a UI e redesenhada a partir do estado, mas a UI
  tambem *agenda* mudancas de estado (animationend) e *fica viva* durante mudancas assincronas
  (await do save). Os dois lados do contrato "estado e a verdade" sao violados.
- **Cartas + estados (BUG-03):** o formato de efeito nao tem a nocao de "golpe"; cada op de dano
  e um golpe; qualquer carta "X, +Y por Z" interage errado com Forca/espinhos/reflexo/mudaPadrao.
- **Recompensa + catalogo + meta (BUG-08, DES-03):** desbloqueios sao gravados no banco e nunca
  chegam ao catalogo em memoria; 3 objetivos dao a mesma carta.
- **Fim de run + nova run (BUG-18):** o callback de "Nova torre" recebe o evento do DOM no lugar
  da classe e o servidor, tolerante demais, aceita `{"classe":{}}` como Capimaga, enquanto o
  cliente monta um deck vazio — dois sistemas "resilientes" produzindo um estado invalido juntos.
- **Auth + rate limit (BUG-04):** a tabela de rate limit tem restricao de tamanho pensada para
  usuario e o login aceita e-mail.
- **Animacao + logica (BUG-12):** ja descrito; a mesma decisao tambem faz com que a segunda carta
  clicada durante a animacao da primeira seja perdida em silencio (o `innerHTML = ""` da
  re-renderizacao remove o elemento antes do `animationend`).
- **Modificadores + desafio (DES-01):** o mecanismo de modificador por id no motor
  (`estado.modificadores`) e o mecanismo por `op` em `aplicarModificador` foram somados sem
  reavaliar quando o modificador entra; o resultado e um bonus antes do combate.
- **MVP + producao (ARC-02):** o MVP guarda a `busy` flag (`ui.py:365`), `MIN_ATTACKS`, reroll,
  recompensa 1-de-3, desafio real, preview de andar e um golpe por carta — seis comportamentos de
  qualidade que o porte perdeu sem registro em `07-decisoes.md`.

---

## 14. Findings

| ID | Severidade | Categoria | Local | Problema | Impacto |
|----|------------|-----------|-------|----------|---------|
| BUG-01 | HIGH | State/UX | `ui/screens.js:158–163, 243–252, 271–311` | Transicao de andar assincrona sem guarda; tela antiga fica viva durante o save | Clique duplo executa acao 2× e pula andar (confirmado) |
| BUG-02 | HIGH | Game design/Correctness | `core/state.js:105–133` vs `flet_mvp/capitower/run.py:41–47` | Deck inicial sem garantia de fonte de dano (Ligeira 8,3%, Brutamontes 1,6%) | Run invencivel desde o andar 1, sem abandonar |
| BUG-03 | HIGH | Correctness/Balance | `core/effects.js:58–60, 137–143, 149–156`; `combat.js:202–211` | "Um golpe por carta" nao portado para `dano` + `dano_por_*` | Forca 2×, espinhos/reflexo 2× em 3 cartas da Brutamontes (confirmado) |
| BUG-04 | HIGH | Backend | `database/schema.sql:42`; `app/core/Auth.php:89–96`; `public/api/auth/login.php:27` | `login_tentativas.usuario VARCHAR(24)` recebe o e-mail | Login por e-mail > 24 chars = 500 (confirmado) |
| BUG-07 | HIGH | Persistence/Robustness | `core/state.js:323–350`; `ui/screens.js:113–126` | `restaurarRun` sem validacao; boot sempre retoma; sem abandonar | Mudanca de catalogo com run ativa = usuario travado para sempre (provavel) |
| BUG-18 | HIGH | Correctness | `ui/towerView.js:174`; `ui/screens.js:141–147, 266`; `api/run/start.php:17–20` | "Nova torre" passa o `MouseEvent` como `classeSlug` | Run nova com deck vazio (provavel) |
| ARC-01 | HIGH | Architecture | `ui/screens.js:108–312` | Orquestracao em closures, sem maquina de estado nem estado "transicionando" | Causa raiz de BUG-01; intestavel |
| ARC-02 | HIGH | Architecture/Process | `flet_mvp/capitower/*.py`, `data/*.json`, `database/seeds.sql` | Dois motores e tres copias do conteudo sem paridade | BUG-02, BUG-03, DES-01, DES-02 ja sao divergencias |
| BUG-05 | MEDIUM | UI/State | `ui/combatView.js:17, 316–318, 360, 432–433` | `snapshotAntes` nao e limpo quando o combate termina | Flash/numero/som de cura espurios em todo combate novo (confirmado) |
| BUG-06 | MEDIUM | Backend/Robustness | `public/api/run/finish.php:22–31`; `app/models/Run.php:124–175`; `app/models/Meta.php:61` | `finalizar` + `avaliarObjetivos` sem transacao; `TypeError` sem envelope | Desbloqueios perdidos permanentemente em falha parcial (confirmado) |
| BUG-08 | MEDIUM | State | `ui/screens.js:110` | Catalogo carregado uma vez; desbloqueio nao entra na proxima run da sessao | Recompensa de objetivo invisivel ate F5 |
| BUG-09 | MEDIUM | UX/State | `ui/combatView.js:105–107, 259`; `ui/cardView.js:28` | Intencao ignora Fragilidade/Evasao; custo estatico; `acaoMax` fixo | Jogador planeja com numero errado |
| BUG-10 | MEDIUM | Design/Persistence | `ui/screens.js:158–163, 256–269`; `docs/04:135–137` | Save na entrada do andar + RNG por andar + morte nao duravel | Reload-scum; objetivos farmaveis (confirmado) |
| BUG-11 | MEDIUM | UX/Design | `ui/rewardView.js:38–49`; `ui/screens.js:301–305` | Opcao de habilidade no nivel 10 e clicavel e desperdica o ponto | Perda de recompensa |
| DES-01 | MEDIUM | Game design | `ui/screens.js:199–211`; `ui/challengeView.js`; `docs/07 D25`; `content.py:200–203` | Desafio = bonus antes de um combate comum, sem recusa | Regressao de design vs D25 e MVP |
| DES-02 | MEDIUM | Game design | `ui/screens.js:290–306`; `core/state.js:186–189`; `docs/01:159–178` | Recompensa 1 carta aleatoria com repeticao; sem reroll inicial; sem visualizar deck | Menos decisao que o GDD promete |
| UX-01 | MEDIUM | UX | `css/combat.css`, `ui/combatView.js` | Combate de 928 px em 720p; intencao e "Fim de turno" fora da dobra; sem pilhas/deck; sem logout/abandonar | Rolagem a cada turno; informacao primaria ausente |
| PERF-01 | MEDIUM | Performance | `public/assets/img/ui/{personagens,frames,cenarios}` | 1,6–1,8 MB por retrato, ~9 MB na primeira sessao | Lento em InfinityFree/celular |
| SEC-01 | MEDIUM | Security (decisao) | `public/api/run/finish.php`; `app/models/Run.php:132–134` | Meta progressao inteiramente forjavel | Invalida ranking futuro; farm de objetivos (confirmado) |
| ARC-03 | MEDIUM | Architecture | `core/effects.js:14–29`; `core/combat.js` (12 `poderes.includes`) | Import circular; poderes por string no pipeline | Cada poder novo toca N ganchos |
| ARC-04 | MEDIUM | Architecture | `core/combat.js` (9 `classe ===`), `state.js`, `combatView.js`, `start.php` | Classe hard-coded em 6 lugares | 4a classe = 6+ arquivos |
| ARC-05 | MEDIUM | Architecture/Data | `core/state.js:10`, `combat.js:14`, `database/schema.sql:62–63, 73–82, 206–216` | Banco e cliente discordam sobre quem e a fonte de HP/Acao/textos; tabelas mortas | Confusao de origem; docs dizem 70, jogo usa 80 |
| ARC-06 | MEDIUM | Architecture/Persistence | `core/state.js:300–350`; `ui/screens.js:113–126` | `versao` nunca lida; sem migracao; sem abandonar run | Habilita BUG-07/BUG-10 |
| TEST-01 | MEDIUM | Testability | `public/assets/js/` | Zero testes num motor portado de outro que tem 13 | Divergencias passam sem aviso |
| BUG-12 | LOW | UI/State | `ui/cardView.js:60–69`; `ui/combatView.js:342–348`; `css/cards.css:63–66` | Jogada acoplada a `animationend` | Jogada perdida/travada quando a animacao nao roda (confirmado em preview) |
| BUG-13 | LOW | UI | `css/cards.css:130–143` | `.carta__texto` 23% de altura com `overflow:hidden` centrado | Texto de carta cortado nas duas pontas (confirmado em 375 px) |
| BUG-14 | LOW | Backend | `app/core/Request.php:68–71`; `login.php:39–40`; `me.php:17–18`; `profile.php:15` | `htmlspecialchars` em saida JSON | Dupla codificacao na UI para `'`/`&` |
| BUG-15 | LOW | Backend/Meta | `app/models/Run.php:135–136, 165` | `chefes_derrotados` conta ids (Gemeos = 2) | Estatistica inflada |
| BUG-16 | LOW | Robustness | `core/combat.js:305–313` | `aplicarEstado` escreve qualquer propriedade da entidade vinda do dado | Typo em carta muta `hp`/`acao` em silencio |
| BUG-17 | LOW | Robustness/UX | `ui/screens.js:141–156, 133–139` | Rejeicoes nao tratadas; save falha em silencio | Sessao expirada = 20 andares sem salvar, sem aviso |
| DES-03 | LOW | Game design/Content | `database/seeds.sql:1057–1103`; `ui/towerView.js:54` | 3 objetivos dao `cm_baforada`; UI diz "20 cartas" com 15 no pool; 3 eventos com reposicao | Recompensa vazia; texto errado |
| DES-04 | LOW | UX/Design | `ui/combatView.js:118` | "Carregando o proximo golpe" sem valor | Golpe de 26–30 sem como planejar |
| UX-02 | LOW | UX/A11y | `css/*.css`; `ui/tutorialView.js` | Sem `:focus-visible`; motivo de bloqueio so em `title`; tutorial sobre a selecao de classe | Teclado/toque sem feedback |
| PERF-02 | LOW | Performance | `ui/combatView.js:414–434` | Redesenho total por acao | Ok hoje; limite ~10× conteudo |
| PERF-03 | LOW | Performance | `app/models/Catalog.php:30–48, 85–150` | N+1 (19 queries) e sem cache HTTP | Ok hoje |
| SEC-02..06 | LOW | Security | `app/core/Auth.php`, `config.example.php`, `register.php` | CSRF sem token (mitigado), `secure=false`, enumeracao, tabela sem expurgo, senha sem teto | Baixo no contexto atual |
| ARC-07 | LOW | Architecture | `public/api/*.php`; `app/core/Request.php:35–45` | Boilerplate repetido; so `PDOException`; GET fallback; `ambiente` ignorado | Manutencao; erros sem envelope |
| ARC-08 | LOW | Architecture | `core/state.js:71–79`; `ui/screens.js:117,144,258`; `ui/combatView.js:11,17` | Estado global montado por partes; globais de modulo entre combates | Causa BUG-05 |
| DEAD-01 | LOW | Code quality | secao 4.6 | ~12 itens de codigo/dados/config mortos; README desatualizado | Ruido para quem chega |
| DOC-01 | LOW | Docs | `README.md`, `docs/01-gdd.md:198`, `docs/04:31–88` | HP 70/80, 50/51 andares, recompensa 1-de-3, estrutura de pastas | Docs mentem sobre o codigo |
| SUG-01 | SUGGESTION | Process | — | Teste de paridade Python ↔ JS por seed | Fecha ARC-02 |
| SUG-02 | SUGGESTION | Architecture | `ui/screens.js` | Maquina de estado explicita para telas | Fecha ARC-01 |
| SUG-03 | SUGGESTION | Architecture | `core/combat.js` | Registro de poderes/ganchos (`aoIniciarTurno`, `aoPerderVida`...) | Fecha ARC-03 |
| SUG-04 | SUGGESTION | Tooling | raiz | JSDoc + `tsc --checkJs` sem build; validador de JSON de cartas | Pegaria BUG-18/BUG-16 |
| SUG-05 | SUGGESTION | Persistence | `core/state.js`, `save.php` | Salvar o combate (ou ao menos `hp` e turno) e versionar o snapshot | Fecha BUG-10/ARC-06 |
| SUG-06 | SUGGESTION | UX | `ui/combatView.js` | Pilhas, deck, fase inimiga passo a passo, foco visivel | Fecha UX-01 |

Totais: **CRITICAL 0 · HIGH 8 · MEDIUM 16 · LOW 16 · SUGGESTION 6** (SEC-02..06 contados como 1
linha LOW na tabela, 5 itens na secao 9).

---

## 15. Detailed Findings

### [BUG-01] Transicao de andar assincrona sem guarda: acoes duplas e andar pulado

**Severity:** HIGH · **Category:** State / UX · **Status:** Confirmado ao vivo

**Location:** `public/assets/js/ui/screens.js:158–163` (`proximoAndar`), `243–252` (`aoMudar`),
`271–311` (`finalizarCombate`), `179–197` (`iniciarDescanso`, `iniciarEvento`), `141–147`
(`comecarRun`); `ui/rewardView.js:235, 251`; `ui/eventView.js:294`; `ui/towerView.js:135, 78`.

**Problem:** `proximoAndar` faz `avancarAndar(run)` (sincrono), depois `await salvarProgresso()`,
depois `renderSala`. Durante o `await`, a tela anterior continua no DOM com os botoes ativos e
nenhum deles e desabilitado. Cada view liga o callback direto ao `click` sem `disabled`, sem flag
`busy` (o MVP tem: `ui.py:365 self.busy`) e sem checar se a acao ainda vale. O mesmo vale para o
combate: `aoMudar` chama `finalizarCombate` toda vez que e disparado com `status !== "andamento"`,
e "Fim de turno" continua renderizado ate o save voltar.

**Evidence (ao vivo, conta `audit_review`):**
- Andar 3, inimigos com hp 0, dois `click()` em "Fim de turno": `run.andar` 3 → 5; o andar 4
  (desafio) nunca foi mostrado.
- Andar 6 (Vestiario), dois cliques em "Vasculhar": `run.andar` 6 → 8, `deck` 10 → 12,
  `cartasTemporarias` 2; o descanso do andar 7 foi pulado.
- Andar 8 (elite), dois cliques em "Carta: Escudo de Carne": `run.andar` 8 → 10, duas copias no
  deck, `pontosRecompensa` 1 (uma carta a mais que o permitido); o andar 9 pulado.
- `comecarRun` tem a mesma estrutura: dois cliques na classe = dois `start.php` (o segundo
  abandona o primeiro), dois `novaRun` sobre o mesmo `estadoGlobal.run` e dois `proximoAndar`.

**Why it matters:** o gatilho e um duplo clique ou um clique repetido por impaciencia — exatamente
o que acontece com latencia de InfinityFree e sem indicador de carregamento. Nao corrompe o
banco, mas corrompe a run (andares pulados, recompensas duplicadas, pontos inconsistentes com
`recompensasHabilidadeUsadas`, objetivos como "andar 10" batidos sem passar por ele).

**Recommendation:** (1) uma flag de transicao em `screens.js` (`let transicionando = false`)
checada e setada no inicio de `proximoAndar`/`finalizarCombate`/`comecarRun` e limpa apos
`renderSala`; (2) `container.innerHTML = ""` (ou um overlay "salvando...") **antes** do `await`;
(3) `button.disabled = true` no primeiro clique em toda view de escolha; (4) `aoMudar` deve
desligar-se apos a primeira chamada com `status !== "andamento"`. A solucao estrutural e SUG-02.

**Priority:** Immediate.

---

### [BUG-02] Deck inicial sem fonte de dano: run invencivel desde o andar 1

**Severity:** HIGH · **Category:** Game design / Correctness · **Status:** Confirmado por
simulacao e calculo

**Location:** `core/state.js:105–133` (`novaRun`); referencia `flet_mvp/capitower/run.py:41–47`
(`_draw_starting`, `MIN_ATTACKS = 2`) e `49–57` (`reroll`).

**Problem:** `novaRun` sorteia 5 cartas distintas da classe sem nenhuma restricao. Contando toda
fonte possivel de dano (ops `dano*`, `invocar`, `retaliacao`, `estado veneno`, poderes
`pavio_curto`/`olho_por_olho`/`golpe_de_vista`/`peste`/`vala_comum`), a Ligeira tem 13 de 20
cartas sem dano e a Brutamontes 10 de 20. P(5 cartas sem nenhuma fonte) = C(13,5)/C(20,5) =
**8,3%** (Ligeira) e C(10,5)/C(20,5) = **1,6%** (Brutamontes). Mesmo com uma fonte "tecnica"
(so `bm_olho`, que depende de perder vida), a run e praticamente perdida. A Capimaga escapa porque
comeca com lacaio (2 de dano/turno).

**Evidence:** harness Node com bot ganancioso, 300 runs por classe sobre o motor real:
15 runs de Ligeira atingiram 300 turnos no mesmo combate (andares 1–3), ex.:
`seed 744386 andar 1 capivarinha×3 hpJog 80 hpIni 8/8,8/8,8/8 deck
lg_lama,lg_truque,lg_rastro,lg_rolamento,lg_respiro`. 0 excecoes.

**Why it matters:** e um em cada doze jogadores de Ligeira abrindo o jogo e nao conseguindo matar
uma capivarinha de 8 HP. Nao ha "abandonar run" (ARC-06): a saida e parar de bloquear e morrer.
O MVP (fonte de balanceamento) tinha a guarda e o reroll; o porte perdeu os dois sem registro em
`07-decisoes.md`.

**Recommendation:** portar `MIN_ATTACKS` (ou melhor: "pelo menos 2 cartas com op de dano direto")
para `novaRun`, usando o mesmo `rngBaralho` em loop como o Python; portar o reroll (D18/GDD 4.1);
adicionar "abandonar run" (tambem resolve BUG-07). Cobrir com teste: para toda seed 1..10.000 e
classe, `deck` tem ≥ 2 cartas com dano.

**Priority:** Immediate.

---

### [BUG-03] "Um golpe por carta" nao portado: Forca e espinhos contam por sub-efeito

**Severity:** HIGH · **Category:** Correctness / Balance · **Status:** Confirmado por script

**Location:** `core/effects.js:58–60` (`dano`), `137–143` (`dano_por_adrenalina`), `149–156`
(`dano_por_consumido`); `core/combat.js:202–211` (`causarDano`), `251–287`
(`aplicarDanoInimigo`). Referencia: `flet_mvp/capitower/combat.py:344–359` (`DMG_KINDS`,
`_add_dmg`, `_flush_hit`) e commit `29abfbb "Motor: um golpe por carta"`;
`tests/test_combat.py:test_split_damage_card_is_one_hit` e
`test_split_damage_card_triggers_thorns_once`.

**Problem:** no Python, `dmg`, `dmg_plus`, `dmg_per_adren`, `dmg_per_consumed` etc. acumulam num
golpe pendente e so `dmg` com `new_strike=True` abre outro. No JS cada op chama `causarDano`
separado: Forca soma em cada um, Fraqueza arredonda em cada um, Fragilidade multiplica cada um,
espinhos/reflexo/`mudaPadrao` disparam em cada um. `docs/09-progresso-e-proximos-passos.md`
(secao 3, Fase 6, item `core/effects.js`) diz que `dano_condicional` resolveu isso — resolveu so
para os `if`; `bm_soco` ("7, +1 por Adrenalina"), `bm_cabecada` ("10,
+3 por consumido") e `bm_estampido` ("6 a todos, +2 por consumido") continuam em dois golpes.

**Evidence:** script Node: Brutamontes, Forca 2, Adrenalina 4, `bm_soco` contra Guarda (espinhos
3): JS causa **16** e sofre **6** de espinhos (e ainda ganha Adrenalina entre os golpes, o que
aumenta o segundo); a referencia da 13 e 3. `lg_cambalhota` ("4 duas vezes") esta certo nos dois.

**Why it matters:** as tres cartas sao o arquetipo Couro/Estampido da Brutamontes; contra
Guarda/elite5 (espinhos) e Bolha (reflexo) o jogador toma o dobro, contra inimigos comuns causa
mais do que o balanceado. Todo playtest de Brutamontes no JS mede um jogo diferente do MVP.

**Recommendation:** reproduzir o golpe pendente em `resolverEfeitos`: acumular `dano`,
`dano_por_*` e `dano_condicional` num `ctx.golpe = {valor, alvo}` e so descarregar (chamando
`causarDano` uma vez) ao encontrar uma op que nao seja de dano, um `dano` novo, ou no fim da
carta. Portar os 2 testes.

**Priority:** Immediate.

---

### [BUG-04] Login por e-mail devolve 500: coluna de 24 caracteres recebe o e-mail

**Severity:** HIGH · **Category:** Backend · **Status:** Confirmado com curl

**Location:** `database/schema.sql:42` (`login_tentativas.usuario VARCHAR(24) NULL`);
`app/core/Auth.php:89–96` (`registrarTentativa`); `public/api/auth/login.php:24–27`.

**Problem:** `login.php` aceita "usuario ou e-mail" (`buscarPorUsuarioOuEmail`) e grava o
identificador em `login_tentativas.usuario`. MySQL 8 em `STRICT_TRANS_TABLES` rejeita string
maior que 24 → `PDOException` → `ERRO_INTERNO`. Como o INSERT vem depois do `password_verify`,
a senha certa tambem falha.

**Evidence:** `POST /api/auth/login.php {"usuario":"audit_review@example.test","senha":...}` →
`{"ok":false,"error":{"code":"ERRO_INTERNO"}}`; o mesmo com `"usuario":"audit_review"` → ok.

**Recommendation:** `usuario VARCHAR(160)` (ou gravar so o `usuario_id`/hash do identificador),
com `ALTER TABLE` documentado — o `CREATE TABLE IF NOT EXISTS` nao vai aplicar. Truncar o
identificador antes do INSERT como defesa extra.

**Priority:** Immediate (uma linha).

---

### [BUG-05] Snapshot de animacao vaza para o proximo combate

**Severity:** MEDIUM · **Category:** UI / State · **Status:** Confirmado ao vivo

**Location:** `ui/combatView.js:17` (`let snapshotAntes`), `316–318` e `336–339` (setado antes de
`jogarCarta`), `360` (antes de `fimDeTurno`), `432–433` (consumido e zerado so em
`renderizarCombate`); `ui/screens.js:244–249` (quando `status !== "andamento"`, `renderizarCombate`
nao e chamado).

**Problem:** o snapshot e tirado antes da acao e limpo no render seguinte. Quando a acao termina
o combate, `screens.js` desvia para recompensa/proximo andar e o render nunca acontece; o
snapshot fica em memoria de modulo e e aplicado ao **primeiro render do combate seguinte**: os
inimigos novos (hp cheio) sao comparados com os antigos (hp 0–1) → `painel--cura`, "+25"
flutuante e `somCura`. Se o jogador tinha mais lacaios antes do golpe final que no inicio do
combate novo nao ha efeito; se tinha menos, "+N 💀" espurio.

**Evidence:** andar 1 vencido com Ritual Ganancioso; no render do andar 2,
`document.querySelectorAll('.painel--cura')` → `["Sapo Musculoso","Capivarinha Encharcada"]`,
`combate.log` so com "Legiao: comeca com 1 lacaio(s). --- Turno 1 ---".

**Recommendation:** zerar `snapshotAntes` em `criarCombateDeSala`/no inicio de
`iniciarCombateDaSala` (ex.: exportar `resetarAnimacao()` de `combatView.js`), ou guardar o
snapshot **dentro** do `estado` de combate em vez de variavel de modulo. Mesmo para
`indiceSelecionado`.

**Priority:** Short term (5 linhas).

---

### [BUG-06] `finish.php` nao atomico e fatal sem envelope: desbloqueios perdidos

**Severity:** MEDIUM · **Category:** Backend / Robustness · **Status:** Confirmado com curl

**Location:** `public/api/run/finish.php:22–31`; `app/models/Run.php:124–175`;
`app/models/Meta.php:55–81` (`contextoDaRun`, `static fn(array $carta)` na linha 61).

**Problem:** `Run::finalizar` faz `UPDATE runs` + `INSERT ... ON DUPLICATE KEY` e retorna; so
depois `Meta::contextoDaRun` e `avaliarObjetivos` rodam. Nada esta em transacao. Qualquer excecao
nao-PDO (aqui, `TypeError` porque um item do deck nao e array) escapa do `try/catch (PDOException)`
e o PHP responde 500 com corpo vazio. A run ja esta `vitoria`/`derrota` e nao aceita novo
`finish` ("ja finalizada"), entao os objetivos daquela run nunca serao avaliados.

**Evidence:** `finish.php {"run_id":5,"resultado":"vitoria","estado_json":{"deck":["x"],
"andar":51,"pontos_recompensa":99,"chefes_derrotados":[...6 ids]}}` → resposta vazia;
`profile.php` em seguida: `runs_totais 1, vitorias 1, andar_recorde 51, pontos_meta_total 1105,
chefes_derrotados 6`; `load.php` → `run: null`. Nenhum objetivo em `usuario_objetivos`.

**Recommendation:** `beginTransaction` cobrindo `finalizar` + `avaliarObjetivos`; `catch
(Throwable)` em todos os endpoints devolvendo o envelope; validar `deck` como lista de objetos
com `id` string antes de usar; `api.js:chamar` checar `resposta.ok`/content-type antes de
`.json()`.

**Priority:** Short term.

---

### [BUG-07] Restauracao sem validacao + boot sem saida: usuario travado para sempre

**Severity:** HIGH · **Category:** Persistence / Robustness · **Status:** Provavel (caminho
determinado por leitura; gatilho e uma mudanca de catalogo com runs ativas)

**Location:** `core/state.js:323–350` (`restaurarRun`: `catalogoCartas.find(...)` sem checar
`undefined`, `{...undefined, _temporaria: true}`), `ui/screens.js:113–126` (`entrarOuRetomar`
sempre renderiza a run ativa), `main.js:25–31` (erro do boot vira texto fixo). Sem
logout/abandonar em nenhuma view.

**Problem:** o deck e reconstruido por `id` contra o catalogo **filtrado por usuario**
(`Catalog::cartas`: `inicial = 1 OR desbloqueada`). Se um id do snapshot nao esta no catalogo
(carta renomeada/removida em `seeds.sql`, carta que virou `inicial = 0` — a Fase 5 fez isso com 5
cartas —, `usuario_desbloqueios` apagada, ou catalogo de outra versao do cliente), o deck fica
com `undefined`; `criarElementoCarta(undefined)` lanca `TypeError` em `carta.tipo`; o boot mostra
"Erro ao carregar a torre. Veja o console." e, como o boot **sempre** retoma a run ativa e nao
existe botao para abandona-la nem para sair, o usuario nunca mais entra. `versao` do snapshot e
gravada e nunca lida, entao nao ha ponto de migracao.

**Why it matters:** o roadmap prevê passe de balanceamento e brainstorm de conteudo; a primeira
renomeacao de slug com jogadores ativos dispara isso em massa, e a unica correcao e no banco.

**Recommendation:** (1) `restaurarRun` valida (`versao`, campos, cada id encontrado) e, em falha,
oferece "abandonar run" chamando um novo endpoint `run/abandon.php` (ou reusa `start.php` que ja
abandona); (2) botao "Abandonar run" e "Sair" sempre visiveis; (3) guardar no snapshot o suficiente
para nao depender de slug (ou nunca renomear slug, com teste que compara `seeds.sql` com os
snapshots ativos); (4) `try/catch` em `entrarOuRetomar` caindo para a tela inicial com aviso.

**Priority:** Immediate (a parte de UI/saida), Short term (validacao/migracao).

---

### [BUG-18] "Nova torre" passa o evento de clique como classe: run com deck vazio

**Severity:** HIGH · **Category:** Correctness · **Status:** Provavel por leitura (nao
reproduzido: a run de teste nao chegou ao fim pela UI; o caminho e inequivoco)

**Location:** `ui/towerView.js:174` (`botao.addEventListener("click", onNovaRun)`);
`ui/screens.js:266` (`renderFimDeRun(container, run, desbloqueios, comecarRun, ...)`), `141–147`
(`comecarRun(classeSlug)`); `core/state.js:95–97` (`cartasDaClasse`), `105–121`;
`public/api/run/start.php:17–20`.

**Problem:** `renderInicio` chama `onComecar(classe.slug)`, mas `renderFimDeRun` liga `onNovaRun`
direto ao `click`, entao `comecarRun` recebe o `MouseEvent`. `JSON.stringify({classe: event})`
manda `{"classe":{"isTrusted":true}}`; `Request::texto` devolve `'capimaga'` (default, porque o
valor nao e string) e o servidor cria a run como Capimaga; o cliente faz `novaRun(seed, event)` →
`cartasDaClasse(event)` compara `carta.classe === MouseEvent` → `[]` → `deck = []`;
`run.classe = MouseEvent` vai para o save. O combate abre com mao vazia e, como
`classe === "capimaga"` e falso em `criarCombateDeSala:82`, com 0 lacaios.

**Recommendation:** `renderFimDeRun` deve levar o jogador de volta a selecao de classe
(`irParaInicio`) ou chamar `onNovaRun(run.classe)`; `comecarRun` deve validar o slug contra
`estadoGlobal.classes`; `novaRun` deve lancar se `cartasDaClasse` vier vazio; `start.php` deve
responder 422 em vez de cair no default (o default so serve para o caminho do bug).

**Priority:** Immediate.

---

### [ARC-01] Orquestracao de telas em closures, sem estado de transicao

**Severity:** HIGH · **Category:** Architecture · **Status:** Confirmado por leitura

**Location:** `ui/screens.js:108–312`.

**Problem:** 14 funcoes aninhadas em `iniciarJogo` compartilham `container` e o global. Nao ha
representacao de "em que tela estou" nem de "estou no meio de uma transicao"; toda tela e
`container.innerHTML = ""` + append. Os `await` de rede acontecem com a tela anterior viva
(BUG-01). Callbacks aninhados para "voltar" (`finalizarRun`, 264–268) mudam de comportamento na
segunda volta. Nada e importavel para teste.

**Recommendation (SUG-02):** um objeto de fluxo com `estado` (`auth | inicio | sala:<tipo> |
recompensa | fim | transicionando`) e um unico `irPara(proximo, dados)` que (a) rejeita chamadas
durante `transicionando`, (b) limpa o container antes de qualquer `await`, (c) e a unica funcao
que chama `render*`. Views recebem callbacks que so retornam intencoes (`{tipo: "escolherCarta"}`)
em vez de mutar `run` diretamente.

**Priority:** Short term (junto com BUG-01).

---

### [ARC-02] Dois motores e tres copias do conteudo sem paridade

**Severity:** HIGH · **Category:** Architecture / Process · **Status:** Confirmado (divergencias
existentes)

**Location:** `flet_mvp/capitower/{cards,content,combat,run}.py`;
`public/assets/js/data/{cards,enemy,events,challenges}.json`; `database/seeds.sql`;
`core/{combat,effects,state,tower}.js`.

**Problem:** os docs elegem o Python como fonte de verdade e o JS como porte, mas nao existe (a)
geracao de `seeds.sql` a partir de `cards.py`, (b) teste de paridade, (c) lista de divergencias
aceitas. Divergencias encontradas nesta auditoria: um golpe por carta (BUG-03), `MIN_ATTACKS` e
reroll (BUG-02), recompensa 1-de-3 sem repeticao (DES-02), desafio com agravante e modificador
apos vencer (DES-01), preview de andar, `busy` flag (BUG-01), `START_HP` 80 vs docs 70. Em
compensacao `cards.json` ≡ `seeds.sql` (verificado) e `enemy.json` bate com o `INSERT` de
Gertrudes.

**Recommendation (SUG-01):** decidir uma fonte: ou o JSON/SQL vira canonico e `cards.py` e gerado
(ou apagado), ou um script `tools/parity.py` roda os 13 testes do Python e o equivalente em Node
para as mesmas seeds e compara `hp`/`bloco`/`log`. Registrar em `07-decisoes.md` cada
divergencia aceita. Remover `data/*.json` de `public/` (ou parar de chama-los de espelho).

**Priority:** Short term.

---

### [BUG-08] Catalogo carregado uma vez por sessao: desbloqueio nao chega a run seguinte

**Severity:** MEDIUM · **Category:** State · **Status:** Confirmado por leitura

**Location:** `ui/screens.js:110` (`await carregarCatalogo()` so em `iniciarJogo`); `256–269`
(`finalizarRun` recebe `desbloqueios` e so os exibe); `core/state.js:83–91`.

**Problem:** `Catalog::cartas` filtra por `usuario_desbloqueios`, mas o cliente so chama
`bootstrap.php` no boot. Apos "Objetivo cumprido: ... desbloqueia Putrefacao", "Nova torre" usa
`estadoGlobal.catalogoCartas` antigo: `novaRun` e `cartaAleatoria` nao veem as cartas novas ate
um F5.

**Recommendation:** se `desbloqueios.length > 0`, `await carregarCatalogo()` antes de renderizar
a tela de fim (ou em `comecarRun`).

**Priority:** Short term.

---

### [BUG-09] Numeros mostrados divergem dos numeros aplicados

**Severity:** MEDIUM · **Category:** UX / State · **Status:** Confirmado por leitura

**Location:** `ui/combatView.js:105–107` (intencao: `valor + forca`, `× 0.75` se Fraqueza do
inimigo) vs `core/combat.js:596–608` (`receberAtaque`: tambem `× 1.5` se `jogador.fragilidade`
e anulado por `evasao`); `ui/combatView.js:259` (`Acao ${acao}/${acaoMax}` com `acaoMax` fixo
em 3, `combat.js:103`) vs Ligeira nivel 5 / Largada / `ganhar_acao`; `ui/cardView.js:28`
(`carta.custo`) vs `core/combat.js:465–475` (`custoDe`: 0 com `proximaGratis` ou Ligeireza 10).

**Problem:** "Ataca 10" com Fragilidade 2 causa 15; carta "1" custa 0 depois de Baralho Marcado;
"Acao 4/3". A regra "quanto dano causara / quanto custa" e a informacao mais importante de um
jogo de cartas e esta duplicada na view em vez de vir do motor.

**Recommendation:** exportar de `combat.js` `danoPrevisto(estado, inimigo, acao)` (reusando o
calculo de `receberAtaque`) e usar `custoDe` na view; `acaoMax` deve ser o valor efetivo do turno
ou sumir.

**Priority:** Short term.

---

### [BUG-10] Save na entrada do andar + RNG deterministico + morte nao duravel = reload-scum

**Severity:** MEDIUM · **Category:** Game design / Persistence · **Status:** Confirmado ao vivo

**Location:** `ui/screens.js:158–163` (save apos `avancarAndar`), `256–269` (`finalizarRun`
engole erro), `219–220` (seed do combate = `derivarSeed(run.seed, sala.andar)`);
`docs/04-arquitetura.md:135–137`.

**Problem:** documentado como "fechar a aba durante um combate perde aquele combate, nao a run";
a consequencia nao documentada e que o jogador **ganha** com isso: HP volta ao de antes do
combate, o embaralhamento e a intencao inicial sao identicos, e o combate pode ser ensaiado ate
sair perfeito. Se `finish.php` falhar (rede, sessao, BUG-06), a morte nem e registrada.

**Evidence:** chefe do andar 10 com `combate.jogador.hp = 30`; `navigate` para a mesma URL →
retoma andar 10 com `run.hp 80`, `combate.jogador.hp 80`.

**Recommendation (SUG-05):** salvar o combate (o `estado` e serializavel exceto `rng`; basta
guardar a seed e o numero de chamadas, ou re-derivar o rng por turno) ou, no minimo, salvar
`hp`/`turno` ao fim de cada turno do jogador; salvar `derrota` no servidor **antes** de mostrar a
tela; se o `finish` falhar, tentar de novo no proximo boot (`run.status` ja esta no snapshot —
`load.php` podia devolver `status !== "jogando"` e o cliente refazer o `finish`).

**Priority:** Medium term (design), Short term (durabilidade da morte).

---

### [BUG-11] Recompensa de habilidade no nivel 10 desperdica o ponto

**Severity:** MEDIUM · **Category:** UX / Design · **Status:** Confirmado por leitura

**Location:** `ui/rewardView.js:38–49` (botao sempre ativo; texto "Ja no nivel maximo");
`ui/screens.js:301–305` (`recompensasHabilidadeUsadas += 1; subirNivelHabilidade` no-op);
`core/state.js:195–197`.

**Recommendation:** `opcaoHabilidade.disabled = true` no nivel 10, ou nao renderizar; nao contar
em `recompensasHabilidadeUsadas` quando nao subiu (afeta o objetivo `so-no-osso`).

**Priority:** Short term.

---

### [DES-01] "Desafio opcional" e um bonus gratis antes de um combate comum

**Severity:** MEDIUM · **Category:** Game design (regressao vs decisao registrada) · **Status:**
Confirmado por leitura

**Location:** `ui/screens.js:199–211`; `ui/challengeView.js:20` ("Escolha um modificador
permanente ... antes do combate desta sala"); `core/state.js:208–224` (`composicaoDaSala`: desafio
usa `bloco.combates` comum). Referencia: `docs/07-decisoes.md` D25 ("**Vencer** da um modificador
de run"); `flet_mvp/capitower/content.py:200–203` (`CHALLENGES`: inimigos +2 Forca / +3 por turno
apos o 6o), `combat.py:141, 698`, `ui.py:1551–1575` ("Desafio vencido").

**Problem:** no JS o jogador escolhe 1 de 2 buffs (todos positivos: Forca, HP, Bloco, Acao,
compra) e entra num combate identico ao comum, ja com o buff. Nao ha risco, nao ha "opcional"
(sem recusar) e a palavra "desafio" nao descreve nada. O mecanismo de `challenge` do MVP nao foi
portado.

**Recommendation:** portar `CHALLENGES` como flag de combate (`criarCombateDeSala({desafio})`),
oferecer "Recusar (combate comum, sem modificador)", e mover `aplicarModificador` para
`finalizarCombate` quando `sala.tipo === "desafio"` e o combate foi vencido.

**Priority:** Medium term.

---

### [DES-02] Recompensa de carta sem escolha e sem controle de repeticao

**Severity:** MEDIUM · **Category:** Game design · **Status:** Confirmado por leitura

**Location:** `ui/screens.js:290–306`; `core/state.js:186–189`; `ui/rewardView.js:3–4`
(comentario admite "pode repetir uma que ja esta no deck"). Referencia: `docs/01-gdd.md:174–178`;
`flet_mvp/capitower/run.py:67–71`.

**Problem:** o GDD e o MVP dao 3 opcoes sem repetir carta do deck; o JS sorteia 1 e pode repetir.
Somado a ausencia de reroll inicial e de tela de deck, a "decisao central" (GDD 4.3,
especialista × generalista) fica sem informacao para ser tomada.

**Recommendation:** portar `reward_options(3)` e uma tela de deck (lista agrupada por id com
contagem); mostrar quantos pontos de recompensa faltam.

**Priority:** Medium term.

---

### [UX-01] Tela de combate nao cabe na viewport; informacao primaria ausente

**Severity:** MEDIUM · **Category:** UX · **Status:** Confirmado ao vivo

**Location:** `css/combat.css` (paineis e mao sem `max-height`/layout em grade);
`ui/combatView.js` (sem pilhas/deck; `criarPainelJogador` 246–282).

**Evidence:** 1280×720 → `scrollHeight 928`; `.cabecalho-andar` em y = −163 e `.intencao` em
y = −81 com a mao visivel; `.botao--fim-turno` e `.log` abaixo de 649 px. 375×812 → 961 px.

**Recommendation:** grade de 3 linhas (`inimigos | jogador+intencao | mao+acoes`) com
`height: 100dvh` e a mao em linha unica com scroll horizontal no celular; contadores de compra /
descarte / exaustao ao lado da mao; deck acessivel por botao; "Fim de turno" sempre visivel
(sticky); logout/abandonar no cabecalho.

**Priority:** Medium term.

---

### [PERF-01] Assets de imagem de 0,4 a 1,8 MB para elementos de 100–150 px

**Severity:** MEDIUM · **Category:** Performance · **Status:** Confirmado por tamanho de arquivo

**Location:** `public/assets/img/ui/personagens/*.png` (1.644–1.804 KB), `frames/*.png`
(668–979 KB), `cenarios/*.jpg` (554–701 KB), `logo.png` (416 KB); `img/enemies/*.png` (~235 KB ×
27) e `icon.png` (1.040 KB) ainda nao servidos.

**Recommendation:** exportar em 2× o tamanho exibido (retrato 256 px, moldura 400 px, cenario
1920 px), WebP com fallback, `loading="lazy"` nos retratos da selecao de classe, `preload` das 4
molduras ao entrar na torre. Meta: < 1,5 MB na primeira sessao.

**Priority:** Short term (antes do deploy).

---

### [SEC-01] Meta progressao inteiramente confiada ao cliente

**Severity:** MEDIUM · **Category:** Security (decisao documentada) · **Status:** Confirmado

**Location:** `public/api/run/finish.php`; `app/models/Run.php:132–136, 156–172`;
`app/models/Meta.php:55–81`; `docs/04-arquitetura.md` secao 2.

**Problem:** a decisao de nao validar combate e razoavel; o que nao esta escrito e que
`andar_maximo`, `pontos_recompensa`, `chefes_derrotados` e `deck` — as entradas de **todos** os
objetivos e de todas as estatisticas — vem do cliente sem cruzamento com o que o servidor sabe
(`runs.andar_maximo` acumulado pelos saves, por exemplo). Com BUG-10, nem `curl` e necessario.

**Recommendation:** usar `runs.andar_maximo` (mantido por `save.php` com `GREATEST`) em vez do
valor do `finish`; contar `pontos_recompensa` no servidor a partir dos andares elite/chefe
derivados da seed (o servidor pode rodar `gerarTorre` — e determinista e sem dependencia);
registrar chefes derrotados via `save.php` ao sair da sala. Reavaliar quando/se existir ranking.

**Priority:** Long term (a menos que entre ranking).

---

### [ARC-03] Vocabulario de efeitos partido e poderes por string

**Severity:** MEDIUM · **Category:** Architecture · **Status:** Confirmado por leitura

**Location:** `core/effects.js:14–29` ↔ `core/combat.js:12`; `combat.js:355, 386, 452, 517,
522, 538, 543, 603, 690, 694, 700` (`poderes.includes`).

**Recommendation (SUG-03):** tabela `PODERES = { calo: { aoIniciarTurno(estado) {...} }, ... }` e
o pipeline chamando `dispararGancho(estado, "aoIniciarTurno")`; mover os mutadores de
`combat.js` para um `core/mutadores.js` que ambos importam, eliminando o ciclo. So vale a pena
quando entrar o 13o poder ou a primeira reliquia — hoje e divida conhecida, nao bug.

**Priority:** Medium term.

---

### [ARC-04] Classe hard-coded em seis lugares

**Severity:** MEDIUM · **Category:** Architecture · **Status:** Confirmado por leitura

**Location:** listados em 3.2. **Recommendation:** um `core/classes.js` com
`{ slug, recursoInicial(nivel), aoPerderVida, aoAbsorver, aoJogarCarta, textoRecurso, textos }`
por classe, consultado pelo motor e pela view; `start.php` valida contra a tabela `classes` e
nao contra uma constante. **Priority:** Medium term (antes da 4a classe).

---

### [ARC-05] Fonte de verdade ambigua entre banco e cliente; tabelas mortas

**Severity:** MEDIUM · **Category:** Architecture / Data · **Status:** Confirmado por leitura

**Location:** `core/state.js:10` (`HP_INICIAL = 80`), `core/combat.js:14`; `database/schema.sql:62–63`
(`hp_inicial` default 70, `acao_por_turno`), `73–82` (`habilidade_niveis.efeitos`), `206–216`
(`run_cartas`); `docs/01-gdd.md:198` (HP 70).

**Recommendation:** ou o cliente le `classes.hp_inicial`/`acao_por_turno`/`habilidade_niveis` do
bootstrap (e apaga as constantes/tabelas JS), ou as colunas saem do schema. Apagar `run_cartas`
ate existir quem escreva nela. Corrigir os docs para 80 ou o codigo para 70.

**Priority:** Short term (decisao), Medium term (execucao).

---

### [ARC-06] Snapshot sem versao efetiva, validacao, migracao ou abandono

Detalhado em BUG-07 e BUG-10. **Severity:** MEDIUM (habilita dois HIGH/MEDIUM).
**Recommendation:** `restaurarRun` com `switch (versao)`, validacao, e um caminho de saida.
**Priority:** Short term.

---

### [TEST-01] Motor JS sem testes, com 13 casos prontos no Python

**Severity:** MEDIUM · **Category:** Testability · **Recommendation:** secao 18.
**Priority:** Short term.

---

### [BUG-12] Mudanca de estado acoplada a `animationend`

**Severity:** LOW · **Category:** UI / State · **Status:** Confirmado no ambiente de preview
(frames pausados); Possivel em uso real

**Location:** `ui/cardView.js:60–69`; `ui/combatView.js:342–348`; `css/cards.css:63–66`
(`.carta--jogada { animation ...; pointer-events: none }`).

**Problem:** a carta ganha a classe, toca som, e so muda o estado no `animationend`. Se o
`animationend` nao vem (aba sem frames — observado: `getAnimations()[0].pending === true`, estado
inalterado, carta invisivel e inclicavel; `display:none` por qualquer motivo; `prefers-reduced-
motion` se algum dia for respeitado; elemento removido por outra re-renderizacao antes do fim),
a jogada some sem log. Uma segunda carta clicada durante a animacao da primeira e perdida em
silencio quando o render da primeira faz `innerHTML = ""`.

**Recommendation:** mudar o estado imediatamente e animar a *saida* no render seguinte (a
carta que nao esta mais na mao pode ser animada a partir de um "fantasma" com `position:
absolute`); ou, no minimo, um `setTimeout` de fallback de 400 ms e um `try { el.getAnimations() }`
para pular a animacao quando nao houver.

**Priority:** Medium term.

---

### [BUG-13] Texto da carta cortado

**Severity:** LOW · **Category:** UI · **Status:** Confirmado em 375 px (e parcialmente em 1280)

**Location:** `css/cards.css:130–143` (`.carta__texto`: `height: 23%`, `align-items: center`,
`overflow: hidden`, `font-size: 0.68em`). 6 cartas tem texto de 75–82 caracteres (`bm_pavio`,
`cm_ritual`, `cm_mordida`, `lg_pega`, `bm_estampido`, `bm_calo`).

**Evidence:** 375×812, "Ritual Ganancioso" exibe "lacaios. Causa 4 de dano a todos os inimigos por
lacaio" (sem "Consome ate 3"); "Escudo de Carne" perde "consumido."

**Recommendation:** `align-items: flex-start` + `font-size` reduzido a partir de 60 caracteres
(classe `carta--texto-longo`), ou tooltip por toque (`click` longo) em vez de `title`.

**Priority:** Short term.

---

### [BUG-14] a [BUG-17], [DES-03], [DES-04], [UX-02], [PERF-02], [PERF-03], [SEC-02..06],
[ARC-07], [ARC-08], [DEAD-01], [DOC-01]

Descritos nas secoes 4–11 com local e evidencia; todos LOW. Recomendacoes resumidas:

- BUG-14: escapar so onde renderiza HTML; API devolve texto cru.
- BUG-15: contar chefes por sala (`sala.tipo === "chefe"`) ou por slug de encontro.
- BUG-16: whitelist `ESTADOS_VALIDOS = ["forca","fraqueza","fragilidade","veneno"]` em
  `aplicarEstado`; validador de JSON de cartas rodando sobre `seeds.sql` (SUG-04).
- BUG-17: `try/catch` com mensagem em tela em `comecarRun`/`abrirPerfil`; `salvarProgresso`
  falhando com `AUTH_REQUIRED` deve voltar para o login preservando `run` em memoria.
- DES-03: revisar recompensas dos 12 objetivos (3 dao `cm_baforada`); texto "20 cartas" → "ate
  20"; sortear eventos sem reposicao por run.
- DES-04: `textoIntencao` para `carregar` deve olhar o proximo item do padrao e mostrar
  "Carregando: Ataca 30 no proximo turno".
- UX-02: `:focus-visible` em `.carta` e `.painel--inimigo`; motivo de bloqueio como badge na
  carta; tutorial so apos escolher a classe.
- PERF-02/03: nada agora; medir quando o conteudo dobrar.
- SEC-02..06: token CSRF simples na sessao quando houver tempo; `secure` automatico se
  `$_SERVER['HTTPS']`; `DELETE FROM login_tentativas WHERE criado_em < NOW() - INTERVAL 1 DAY`
  no proprio login; `strlen($senha) <= 128`.
- ARC-07: `public/api/_bootstrap.php` com os requires, `set_exception_handler` devolvendo o
  envelope, e leitura de `app.ambiente` para `display_errors`.
- ARC-08: `run.id` e `status` no construtor; estado de view dentro do `estado` de combate.
- DEAD-01: remover os itens da secao 4.6 num commit so.
- DOC-01: README, GDD (HP, recompensa), `04-arquitetura.md` (estrutura real).

---

## 16. Positive Findings

- **`core/combat.js` + `core/effects.js` como motor puro e deterministico.** Importavel em Node
  sem shim, 900 runs sem excecao, seed reproduz tudo. E o que deve ser preservado em qualquer
  refatoracao.
- **`rng.js:derivarSeed`** — um gerador independente por andar/uso, sem consumir a sequencia da
  torre; simples e correto.
- **Diff de estado para animacao** (`snapshotDe`/`aplicarEfeitosVisuais`) — resolve "o que mudou"
  sem sujar o motor com ganchos de UI; so precisa viver no lugar certo (BUG-05).
- **Audio sem asset** via Web Audio, contexto sob demanda, mudo persistido com `try/catch`.
- **Backend com o basico de seguranca certo** desde o inicio (PDO preparado, `password_hash`,
  `session_regenerate_id`, `httponly`/`SameSite`, `Deny from all` + constante, rate limit).
- **`Meta::avaliarObjetivos` idempotente** por chave primaria composta.
- **`Run::criar` abandona a run ativa anterior** — evita duas runs ativas por conta.
- **`textContent` em toda a UI**, nenhum `innerHTML` com dado de usuario; `alt`, `role`,
  `tabindex`, `sr-somente` presentes.
- **Documentacao de decisoes e de progresso** honesta sobre o que nao foi verificado — este
  review confirmou varios dos "falta testar ao vivo" listados em `docs/09`.
- **MVP Flet com `busy` flag, testes de regra e `_guard_handlers`** — padroes que o porte deveria
  ter herdado.

---

## 17. Recommended Refactoring Roadmap

### Immediate (antes de qualquer playtest com gente)

1. BUG-01: flag de transicao + limpar a tela antes do `await` + `disabled` nos botoes.
2. BUG-02: guarda de fontes de dano no sorteio inicial (+ reroll).
3. BUG-03: golpe pendente em `resolverEfeitos` + portar os 2 testes.
4. BUG-18: "Nova torre" → selecao de classe; `start.php` 422 para classe invalida.
5. BUG-04: `ALTER TABLE login_tentativas MODIFY usuario VARCHAR(160)`.
6. BUG-07 (parte UI): botoes "Abandonar run" e "Sair" + `try/catch` no boot com fallback.
7. BUG-05: zerar `snapshotAntes`/`indiceSelecionado` ao criar combate.

### Short Term (1–2 semanas)

8. BUG-06 + ARC-07: `_bootstrap.php`, `catch (Throwable)`, transacao em `finish`, `api.js` checa
   `resposta.ok`.
9. BUG-08, BUG-09, BUG-11, BUG-13, BUG-17.
10. ARC-06: `restaurarRun` com validacao e `versao`; `finish` durável (BUG-10 parte 2).
11. TEST-01: portar os 13 testes + testes de fluxo (secao 18) num `tests/` Node sem framework.
12. PERF-01: reexportar as imagens.
13. ARC-05 (decisao) + DOC-01: uma fonte para HP/Acao/textos; docs corrigidos.
14. ARC-02 (parte 1): decidir a fonte canonica do conteudo; remover `data/*.json` de `public/`.

### Medium Term (antes de expandir conteudo)

15. ARC-01/SUG-02: maquina de estado de telas; views passam a devolver intencoes.
16. DES-01, DES-02, DES-04, UX-01, UX-02: desafio real, recompensa 1-de-3, deck/pilhas, layout em
    grade, fase inimiga passo a passo, foco.
17. BUG-12: estado primeiro, animacao depois.
18. ARC-03/SUG-03: registro de poderes com ganchos; quebrar o ciclo `combat ↔ effects`.
19. ARC-04: `core/classes.js`.
20. SUG-05: save de combate (fecha reload-scum).
21. ARC-02 (parte 2)/SUG-01: paridade automatizada ou aposentar o MVP como referencia.

### Long Term (escala)

22. SEC-01: servidor deriva andar/pontos/chefes da seed e dos saves, se ranking entrar.
23. Bootstrap com ETag/cache e catalogo por versao.
24. Render incremental do combate (ou um micro-framework de templates) quando inimigos × cartas ×
    reliquias passar de ~50 elementos.
25. Migracoes de schema versionadas (`database/migrations/NNN.sql`).

---

## 18. Suggested Tests

Todos executaveis em Node puro (`node --test`) importando `public/assets/js/core/*.js`, sem
navegador — comprovado pelo harness desta auditoria.

**Motor (portar de `flet_mvp/tests/test_combat.py`, mesmos nomes):**
- `um_golpe_por_carta`: `bm_soco` com Forca 3 e Adrenalina 4 → dano 14 num golpe; contra Guarda
  → espinhos 3 (falha hoje, BUG-03).
- `duas_dano_sao_dois_golpes`: `lg_cambalhota` contra Guarda → espinhos 6.
- `fraqueza_1_dura_um_turno`, `fragilidade_2_cobre_duas_fases`, `fraqueza_de_evento_nao_decai_no_turno_1`.
- `retaliacao_1_turno_so_na_proxima_fase`.
- `gemeo_herda_forca`, `gertrudes_muda_de_fase_em_66_e_33`, `experimental_muda_padrao_ao_apanhar`.
- `vitoria_e_derrota_no_mesmo_passo`: reflexo mata o jogador ao matar o ultimo inimigo → status
  esperado documentado (hoje: `vitoria` se a queda vier antes do reflexo, `derrota` se depois).
- `poder_segunda_copia_bloqueada`, `devolver_ultima_com_poder`.
- `acao_nunca_negativa` (quando entrar segundo inimigo com `roubar`).

**Run/estado:**
- `deck_inicial_tem_fonte_de_dano`: para seed 1..10.000 × 3 classes (falha hoje, BUG-02).
- `serializar_restaurar_idempotente`: `restaurarRun(serializarRun(run))` reproduz `run`
  (inclusive `_temporaria`).
- `restaurar_rejeita_carta_desconhecida`: snapshot com id inexistente → erro tratado, nao
  `TypeError` (falha hoje, BUG-07).
- `torre_deterministica`: `gerarTorre(seed)` duas vezes igual; elite entre posicoes 3–8; 51 andares.
- `modificadores_por_id`: casco_duro/largada/mao_firme (o script Node avulso citado em `docs/09`
  deveria virar este teste).

**Fluxo (com jsdom ou um `document` minimo):**
- `transicao_ignora_segundo_clique`: dois `click()` em "Fim de turno" com sala limpa → `andar`
  avanca 1 (falha hoje, BUG-01).
- `snapshot_nao_vaza`: vencer jogando carta → proximo render sem `.painel--cura`.
- `nova_torre_pede_classe` (BUG-18).

**Backend (PHP, contra banco de teste):**
- `login_por_email_longo` (BUG-04), `finish_atomico_com_payload_invalido` (BUG-06),
  `condicaoBatida` para os 6 tipos, `start_com_classe_invalida_422`, `save_em_run_de_outro_usuario_404`.

**Simulacao (nao e teste de asserção, e de regressao):**
- manter o harness de 300 runs/classe como `tools/simular.mjs` e falhar se aparecer excecao ou
  softlock; imprimir andar medio por classe para o passe de balanceamento.

---

## 19. Final Technical Assessment

- **Arquitetura:** a divisao motor / estado / orquestracao / views existe e o motor e o melhor
  pedaco do projeto. A orquestracao (`screens.js`) e o modelo de save sao o elo fraco: sem estado
  de transicao, sem versao, sem saida. A existencia de dois jogos no repositorio sem paridade e o
  maior risco de processo.
- **Qualidade de codigo:** legivel, comentada, consistente em nomes; poucos bugs de "linha" e
  varios bugs de "borda entre sistemas". Codigo morto e duplicacoes sao de prototipo e baratas de
  limpar.
- **Robustez:** fragil onde o cliente encontra o servidor (transicoes assincronas, erros nao-PDO,
  restore sem validacao, morte nao duravel). Zero excecoes em 900 runs simuladas mostra que o
  motor em si e solido.
- **Extensibilidade:** boa para cartas e inimigos com vocabulario existente; media para
  operacoes/acoes novas; ruim para poderes, classes e formato de save.
- **UX/UI:** bonito e responsivo para o estagio; falta informacao primaria de deckbuilder
  (pilhas, deck, preview), a tela de combate nao cabe em 720p, e varios numeros mostrados nao
  sao os aplicados.
- **Manutencao:** um dev novo acha as coisas, mas vai ser enganado por `data/*.json`, pelo README e
  pelas constantes que "vem do banco".
- **Riscos futuros, em ordem:** (1) mudanca de catalogo travando usuarios (BUG-07/ARC-06); (2)
  balanceamento feito duas vezes ou divergindo (ARC-02); (3) reload-scum invalidando qualquer meta
  progressao (BUG-10/SEC-01); (4) pipeline de poderes virando cadeia de ifs (ARC-03).

Recomendacao objetiva: fechar os 7 itens "Immediate" (todos pequenos: nenhum passa de ~40 linhas
salvo o golpe pendente), portar os testes, e so entao fazer o playtest humano que os docs pedem —
hoje um playtest de Brutamontes ou Ligeira mediria regras diferentes das balanceadas no MVP.

---

## 20. Future Scalability Analysis

Cenario: 200 cartas, 100 inimigos, 50 reliquias, 5 personagens, 3+ atos, dezenas de efeitos, tipos
novos de combate, eventos com estado, desbloqueaveis, achievements, meta progression, multiplos
saves.

| Parte | Sofre quando | Por que | Sinal |
| --- | --- | --- | --- |
| `combat.js` ganchos de poder (ARC-03) | ~15 reliquias/poderes | cada gancho e um `if` em 8 funcoes; esquecer um e silencioso | primeira reliquia "ao comprar carta" ou "ao matar inimigo" |
| `classe ===` (ARC-04) | 4o personagem | 6 arquivos + banco | ja |
| `effects.js` switch (30 cases) | ~60 operacoes | `ctx` compartilhado e sem tipo; condicoes por `split(">=")` | primeira condicao composta ("se X e Y") |
| Snapshot da run (ARC-06) | primeira mudanca de formato | `versao` nao lida; sem migracao | proximo campo novo em `serializarRun` |
| `restaurarRun` por slug (BUG-07) | primeira renomeacao/remocao de carta | deck depende do catalogo atual | passe de balanceamento |
| `renderizarCombate` total (PERF-02) | ~5 inimigos + 10 cartas + 20 reliquias + log | recria ~200 nos por clique; animacao por diff so olha hp/bloco/lacaios | quando entrar reliquia com contador visivel |
| `tower.js` fixo (5 blocos × 10) | 2o ato / mapa ramificado | `bloco`, `andar` e `NOMES_BLOCO` sao aritmetica, nao dados | ja, se houver ato 2 |
| Eventos (`aplicarEfeitoEvento`, 7 ops) | evento com estado, escolha condicional ou consequencia futura | `run` nao tem lugar para "flags de evento" alem de `curaDiferida`/`fraquezaProximoCombate` | primeiro evento "lembra que voce..." |
| `Meta::condicaoBatida` (6 tipos) | achievements por contagem acumulada ("mate 100 sapos") | contexto e so da run atual; sem contadores por usuario | primeiro objetivo cumulativo |
| Bootstrap (27 KB, 19 queries) | 200 cartas + 100 inimigos | sem cache, sem versao de catalogo, `Catalog::classes` N+1 | 150 KB por F5 em host compartilhado |
| `runs` uma ativa por usuario | multiplos saves/slots | `Run::criar` abandona a anterior; `load.php` devolve a ultima | primeira pedida de "slot" |
| Tres copias de conteudo (ARC-02) | 200 cartas | manutencao ×3, paridade manual | ja (BUG-03) |
| `screens.js` closures (ARC-01) | tipo de sala novo / loja / evento multi-tela | tudo aninhado; sem estado nem historico | primeira tela com "voltar" |
| Docs vs codigo | continuamente | sem geracao nem checagem | ja (HP, recompensa, 50/51) |

Ordem de quebra provavel: ARC-06/BUG-07 (na proxima mudanca de conteudo) → ARC-02 (no proximo
balanceamento) → ARC-03 (na primeira reliquia) → ARC-01 (na primeira tela com fluxo) → ARC-04 (na
4a classe) → PERF-02/bootstrap (bem depois).

O que aguenta a escala como esta: `rng.js`, o formato de efeito como dado (com um validador),
o esquema de banco para conteudo (`cartas`/`inimigos`/`encontros`/`eventos`/`desafios` com JSON),
e o envelope da API.
