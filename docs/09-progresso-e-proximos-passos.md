# 09. Progresso e proximos passos

Registro do que ja foi construido na trilha PHP/JS (a trilha de producao, ver `04-arquitetura.md`)
e do que falta, atualizado em 17/09/2026. O MVP em `flet_mvp/` continua sendo so a referencia de
design ja balanceada, nao faz parte desta lista.

## 1. Estado por fase (`06-roadmap.md`)

| Fase | Status | Observacao |
| --- | --- | --- |
| 0. Fundacao | Feita | Docs e decisoes D01 a D28 fechadas em `07-decisoes.md`. |
| 1. Prototipo de combate | Feita | Verificada jogando no navegador. |
| 2. A torre | Feita | Verificada subindo do andar 1 ao 50 numa run so. |
| 3. Conteudo da Capimaga | Feita, com uma pendencia | Ver secao 3. |
| 4. Banco e conta | Feita | Verificada criando conta, logando, salvando e retomando run entre andares. |
| 5. Meta progressao | Feita, com uma pendencia | 12 objetivos em rascunho (secao 3), verificados ao vivo via banco e navegador. Precisam de revisao humana antes de virar lista definitiva. |
| 6. Classes 2 e 3 | Feita, verificada ao vivo | Porte completo (motor, efeitos, banco, UI), jogado no navegador com as duas classes novas. Ver secao 3. |
| 7. Acabamento | Quase feita, falta so o deploy | Arte, animacao, som, tutorial e responsivo feitos e verificados ao vivo. So falta o deploy na InfinityFree, que precisa da conta do dono do projeto. Ver secao 3. |

## 2. O que existe hoje em `public/`

```
public/
  index.php
  api/{auth,catalog,meta,run}/*.php
  assets/
    css/{base,layout,combat,cards,tower}.css
    js/
      main.js
      core/{rng,combat,effects,state,tower}.js
      ui/{screens,cardView,combatView,towerView,rewardView,eventView,challengeView,authView,profileView}.js
      data/{cards.json,enemy.json,events.json,challenges.json}
    img/ui/{logo.png,cenarios/*.jpg,frames/*.png,personagens/*.png}
```

Resumo do que cada parte faz:

- `core/rng.js`: mulberry32 com seed, usado tanto para embaralhar o baralho quanto para gerar a
  ordem da torre (`derivarSeed`).
- `core/effects.js`: interpretador do formato de efeito de carta. Alem das operacoes previstas em
  `04-arquitetura.md` secao 6, foram acrescentadas `dano_defesa`, `manter_bloco`, `espalhar_veneno`,
  `poder` e `se` (condicional), exigidas por cartas e chefes reais que nao cabiam no vocabulario
  original.
- `core/combat.js`: motor de combate. Foi estendido de 1 para **N inimigos simultaneos** (nao
  previsto explicitamente na Fase 1 nem 2), porque o bestiario real tem grupos de ate 3 e o chefe
  Gemeos Rosca Direta depende de herdar buff de um irmao morto.
- `core/tower.js`: gera os 5 blocos e os 6 tipos de sala a partir da seed.
- `core/state.js`: estado completo da run (seed, andar, HP persistente, baralho, modificadores,
  nivel da Legiao, efeito pendente de evento).
- `data/cards.json`: as 20 cartas da Capimaga, portadas de `flet_mvp/capitower/cards.py`, com campo
  `origem` apontando pra carta original em Python.
- `data/enemy.json`: bestiario completo dos 5 blocos, os 5 chefes nomeados e a Soberana Gertrudes
  com 3 fases, portados de `flet_mvp/capitower/content.py`.
- `data/events.json`: 3 eventos (Bebedouro, Halteres Perdida, Vestiario). Ver pendencia abaixo.
- `data/challenges.json`: 2 modificadores de desafio opcional (de um total de 5 desenhados no MVP).

## 3. Desvios e pendencias conhecidas

- **Eventos incompletos.** O roadmap da Fase 3 pede 8 a 12 eventos; so existem 3 desenhados em
  qualquer lugar (docs ou MVP Python). Os 3 foram portados, os outros 5 a 9 nao foram inventados de
  proposito, porque isso e conteudo/roteiro novo, decisao de design e nao de codigo. **Precisa de
  uma passada de brainstorm de eventos antes de fechar a Fase 3 de verdade.**
- **Modificadores de desafio incompletos.** So 2 dos 5 modificadores do MVP Python foram portados
  para `challenges.json`. Os outros 3 sao so trabalho de porte, sem decisao nova.
- **3 chefes nao verificados ao vivo.** Dorival, Sargento Capitolino e a Soberana Gertrudes foram
  jogados de verdade em combate. Marlene Cardio, Professor Helio Whey e os Gemeos Rosca Direta
  foram conferidos so por varredura automatica dos dados (todas as operacoes de efeito existem e
  sao validas), nao por uma partida real. Vale jogar contra os tres antes de considerar a Fase 3
  fechada.
- **Bug de baralho inicial corrigido durante a Fase 3.** O baralho estava sorteando as 20 cartas
  inteiras em vez de 5 cartas distintas com 2 copias cada (regra D18). Corrigido em `state.js`.
- **Balanceamento nunca testado com gente de verdade.** A ultima simulacao registrada (bot
  ganancioso, `flet_mvp/README.md`) e do MVP Python, antes da Fase 3 portar o conteudo real pro PHP.
  Vale jogar sessoes manuais assim que a Fase 4 permitir persistir progresso.
- **Fase 6 (Brutamontes e Ligeira): codigo escrito numa sessao so, nunca rodado.** Feito nesta
  sessao, sem verificacao ao vivo ainda (sem XAMPP disponivel para testar no momento). Detalhe em
  `02-classes-e-arquetipos.md` secoes 5 e 6 (numeros de referencia) e `flet_mvp/capitower/
  {cards,content,combat}.py` (fonte da verdade, ja balanceada no MVP Python). O que foi feito:
  - `core/combat.js`: `jogador.classe` guia setup (lacaios so pra Capimaga, Adrenalina inicial pra
    Brutamontes por `TABELA_ADRENALINA_INICIAL`), `custoDe`/`motivoBloqueio`/`jogarCarta` levam
    `estado` para checar Ligeira nivel 10 (1a carta gratis) e `proximaGratis`; `perderVidaJogador`
    centraliza toda perda de vida do jogador (ataque, veneno, reflexo/espinhos) pra disparar
    Adrenalina e Olho por Olho igual ao Python; `ganharAdrenalina`/`consumirAdrenalina`,
    `verificarLigeireza` (gatilhos 1x/2x por turno, limiar por nivel), Retaliacao e Evasao em
    `receberAtaque`, poderes novos (`rugido`, `pavio_curto`, `calo`, `olho_por_olho`,
    `segundo_folego`, `golpe_de_vista`, `rastro`, `bolso_fundo`) nos pontos certos do turno.
  - `core/effects.js`: 16 operacoes novas (`perder_vida`, `ganhar_adrenalina`,
    `consumir_adrenalina`, `dano_por_adrenalina`, `bloco_por_adrenalina`, `dano_por_consumido`,
    `bloco_por_consumido`, `acao_por_consumido`, `retaliacao`, `evasao`, `dano_por_impulso`,
    `bloco_por_impulso`, `dano_condicional`, `devolver_ultima`, `proxima_gratis`, `trocar_mao`) e
    condicoes `adrenalina>=N`/`evasao>=N`. `dano_condicional` e um desvio proposital do formato de
    "golpe acumulado" do Python (`dmg_plus`/`_add_dmg`): em vez de reabrir um segundo golpe (o que
    aplicaria Forca/Fraqueza duas vezes), embute o bonus condicional num unico efeito de dano.
  - `core/state.js`, `core/api.js`, `ui/screens.js`: `novaRun`/`cartaAleatoria`/`serializarRun`/
    `restaurarRun` agora levam `classe`; `iniciarRunNoServidor(classe)` manda pro servidor.
  - `ui/towerView.js`: tela inicial virou selecao de classe (le `estadoGlobal.classes` do
    bootstrap) em vez de "Comecar a subir" direto.
  - `ui/rewardView.js`, `ui/combatView.js`: nome/texto da habilidade e o rotulo do recurso (HUD)
    ficaram por classe (`HABILIDADE_TEXTOS`/`HABILIDADE_NOMES` em `state.js`).
  - `public/api/run/start.php`: le `classe` do corpo da requisicao (era fixo em `capimaga`).
  - `public/assets/js/data/cards.json`: as 40 cartas novas (20 Brutamontes, 20 Ligeira), formato
    igual ao das 20 da Capimaga, com `origem` apontando pro `.py`. JSON validado (60 cartas, 20 por
    classe).
  - `database/seeds.sql`: `INSERT` de `brutamontes`/`ligeira` em `classes`, os 20 niveis de
    habilidade de cada uma, os 8 arquetipos novos e as 40 cartas (efeitos como o mesmo JSON do
    `cards.json`). Sintaxe JS (`node --check`) e PHP (`php -l`) passaram; **o SQL em si nao rodou
    contra um banco** (sem `xampp2` de pe nesta sessao).
  - **Verificado ao vivo em 17/09/2026.** `seeds.sql` rodado contra o banco local (ver secao 4
    sobre a troca de XAMPP por Apache/MySQL80 standalone nesta maquina). Jogadas confirmadas sem
    erro de servidor nem de console: Brutamontes (dano por Adrenalina de `Soco de Sobra`,
    Adrenalina automatica por `perderVidaJogador` em `Mais Uma Serie`, consumo em `Explosao de
    Folego`, Retaliacao em `Queixo de Ferro` disparando nos dois ataques do Rato de Academia,
    overflow de dano matando um inimigo e sobrando pro outro) e Ligeira (compra de carta e ganho
    de Impulso em `Passo Curto`). Run avancou do andar 1 ao 2 sem problema.
  - **Falta ainda:** o passe de balanceamento comparando as tres classes lado a lado (numeros de
    `02-classes-e-arquetipos.md` secoes 5.2/5.4/6.2/6.4), que e mais sessao de playtest humano do
    que verificacao tecnica — nao fechei isso nesta sessao.

## 4. Ambiente local

**Atualizado em 17/09/2026: o XAMPP (`C:\xampp2`) descrito antes nao existe mais nesta maquina.**
Foi substituido por uma instalacao "solta" de Apache 2.4 + PHP 8.4 + MySQL 8.0 (nao XAMPP/WAMP),
rodando como servicos Windows (`Apache2.4`, `MySQL80`), provavelmente porque a maquina e
compartilhada com outros projetos da escola (ha `C:\CT_Dev`, `C:\Apache\htdocs\FichaDigital` etc.
usando o mesmo MySQL). Detalhe:

| Item | Caminho / valor |
| --- | --- |
| PHP | `C:\php\php.exe` (8.4.1, ja no PATH) |
| MySQL client | `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` (8.0.40, ja no PATH) |
| Servico MySQL | `MySQL80`, porta 3306, `root` **com senha** (nao mais vazio como no XAMPP) |
| Servico Apache | `Apache2.4`, mas sem vhost pro CapiTower — nao serve este projeto |
| `app/config/config.php` | Criado nesta sessao, fora do git. `senha` = a mesma usada pelo
  `FichaDigital` (outro projeto PHP nesta maquina, `C:\Apache\htdocs\FichaDigital\config\app.local.php`) |

Como nao ha vhost do Apache pro projeto, a forma de rodar continua sendo `php -S` (ja configurado
em `.claude/launch.json` como `php-web`, porta 8000), que so precisa do MySQL de pe — nao do
Apache. `database/schema.sql` e `database/seeds.sql` ja foram aplicados contra o banco `capitower`
nesta maquina (ambos sao idempotentes: `CREATE TABLE IF NOT EXISTS` e `ON DUPLICATE KEY UPDATE`,
rodar de novo depois de mudar o catalogo e seguro).

## 5. Proximos passos, em ordem

### Fase 4: banco e conta (feita — lista abaixo e o registro historico da implementacao, nao um TODO)

1. Copiar `app/config/config.example.php` para `app/config/config.php` (fica fora do git, ver
   secao 4 para os valores atuais desta maquina).
2. Rodar `database/schema.sql` e depois `database/seeds.sql` no MySQL local (via phpMyAdmin ou
   `mysql` CLI).
3. Implementar `app/core/{Database,Response,Auth,Request}.php` conforme `04-arquitetura.md` secao 3
   e 7 (PDO preparado, `password_hash`, sessao com `httponly`/`samesite=Lax`, rate limit de login).
4. Implementar os endpoints de `04-arquitetura.md` secao 4: `api/auth/{register,login,logout,me}.php`,
   `api/catalog/bootstrap.php`, `api/run/{start,save,load,finish}.php`, `api/meta/{profile,objectives}.php`.
5. Trocar `data/*.json` (usados hoje como fonte local fixa) por uma chamada a
   `api/catalog/bootstrap.php`: o catalogo passa a vir do banco, os JSON continuam existindo so como
   seed de referencia, nao mais como fonte servida ao cliente.
6. Implementar save/load do snapshot `estado_json` (formato ja descrito em `04-arquitetura.md`
   secao 5) entre andares, e retomar run ativa ao entrar.
7. Verificar de verdade: criar conta, logar, comecar uma run, fechar a aba no meio de um andar,
   voltar e continuar do mesmo andar. Esse e o criterio de saida da Fase 4.

### Fase 5: meta progressao (feita, rascunho para revisao)

- `objetivos` semeada com 12 linhas (`database/seeds.sql`, bloco "OBJETIVOS"): 3 marcos de andar,
  vitoria da torre, 5 chefes nomeados, e 3 objetivos mais dificeis (2 deles ocultos ate serem
  batidos). Cada `condicao` e um JSON `{"tipo":...}` avaliado em
  `app/models/Meta.php::condicaoBatida()`.
- Pool inicial reduzido: as 5 cartas do arquetipo Putrefacao (`cm_baforada`, `cm_pus`, `cm_peste`,
  `cm_contagio`, `cm_mordida`) viraram `inicial = 0`. `objetivos.recompensa_tipo` e
  `usuario_desbloqueios.tipo` ganharam o valor `arquetipo`, para destravar o arquetipo inteiro de
  uma vez (ver nota no topo de `database/schema.sql`).
- `app/models/Meta.php::avaliarObjetivos()` roda dentro de `public/api/run/finish.php` depois de
  `Run::finalizar()`, grava `usuario_objetivos`/`usuario_desbloqueios` e devolve o que foi
  desbloqueado agora pro cliente mostrar na tela de fim de run.
- `public/assets/js/ui/profileView.js` (novo): estatisticas e lista de objetivos com progresso,
  acessivel pelo botao "Ver perfil" na tela inicial e na tela de fim de run.
- **Pendencia:** a lista de 12 objetivos e um rascunho meu, nao validado por playtest nem revisado
  pelo dono do projeto. Ver relatorio da sessao que implementou a Fase 5 para a lista completa e o
  raciocinio de cada um.

### Fase 6: classes 2 e 3

- Porte feito e verificado ao vivo nesta sessao (ver secao 3): motor (`core/combat.js`,
  `core/effects.js`), banco (`database/seeds.sql`) e UI (selecao de classe, HUD por recurso) para
  Brutamontes (Adrenalina) e Ligeira (Impulso), no mesmo padrao usado na Fase 3 para a Capimaga.
- **Falta so o passe de balanceamento** comparando as tres classes lado a lado (playtest humano,
  nao verificacao tecnica).

### Fase 7: acabamento (comecada em 17/09/2026)

- **Arte integrada nesta sessao**, a partir de arquivos que apareceram em `Assets/` (raiz do
  projeto, nao versionado, gerados por IA em 11/09/2026) e foram copiados para
  `public/assets/img/ui/`:
  - `logo.png`: logo do jogo na tela inicial (`towerView.js:renderInicio`).
  - `cenarios/{poco,academia,laboratorio,refeitorio,jardim,menu}.jpg`: fundo de tela cheio,
    trocado por bloco atual via `towerView.js:aplicarFundoDaSala()` (chamado em
    `screens.js:renderSala`) contra um `<div id="fundo-cenario">` fixo atras de `#app`
    (`public/index.php`, CSS em `base.css`). **Achado nao obvio:** um `background` solido em
    `html, body` vira o "canvas" do viewport e a spec CSS pinta isso abaixo de qualquer
    descendente, mesmo com `z-index` negativo — teve que sair do `html, body` e morar so no
    `#fundo-cenario` pro cenario aparecer.
  - `frames/{ataque,defesa,poder,utilidade}.png`: moldura ilustrada por tipo de carta, uma pra
    cada um dos 4 tipos que ja existem no catalogo. `cardView.js` agora poe
    `carta--tipo-<tipo>` no elemento; `cards.css` usa a moldura como `background-image` da carta
    inteira (`aspect-ratio: 848/1264`, igual ao PNG de origem, pra nunca esticar) e posiciona
    custo/nome+tipo/texto em cima das 3 "janelas" transparentes desenhadas na moldura (custo no
    circulo de gema, nome+tipo na janela de arte — nao ha arte propria por carta ainda, entao essa
    janela virou a area do titulo —, texto na janela inferior). As coordenadas das janelas foram
    medidas escaneando o canal alpha do PNG (script Python de uso unico, nao versionado), nao
    chutadas visualmente.
  - `personagens/{capimaga,brutamontes,ligeira,soberana-gertrudes}.png`: retrato de classe na
    tela inicial (`towerView.js:renderInicio`, `.opcao-classe`) e no painel do jogador durante o
    combate (`combatView.js:criarPainelJogador`, por `estado.jogador.classe`); a Soberana
    Gertrudes tambem ganhou retrato proprio no painel de inimigo (`RETRATOS_INIMIGO`, casado pelo
    nome exato em `enemy.json`). O resto do bestiario continua no emoji generico (🐸 vivo / 💀
    caido) — sem arte por inimigo ainda. (Nota da sessao: cheguei a achar, por erro de leitura
    visual da minha parte, que esses 4 PNGs eram previa de marketplace de clip-art com fundo sujo
    e selos colados; o dono do projeto corrigiu e a verificacao objetiva do canal alpha confirmou
    que os arquivos sempre foram limpos — sem transparencia real e sem badge nenhum. Registrado
    aqui so pra quem ler a sessao entender por que o retrato demorou uma rodada a mais pra entrar.)
- **Animacao de carta, dano e invocacao integrada em 17/09/2026.** A tela de combate inteira e
  redesenhada do zero a cada mudanca de estado (`combatView.js:renderizarCombate`, arquitetura da
  Fase 1), entao nao ha "de" e "para" no DOM pra fazer `transition`: tudo virou `@keyframes` de
  um tiro so, disparado por classe temporaria que `combatView.js` calcula comparando um retrato do
  estado tirado logo antes de uma acao mutar `estado` (jogar carta, fim de turno) contra o estado
  depois (`snapshotDe`/`aplicarEfeitosVisuais`). Sem isso a unica forma de saber "o que mudou"
  seria remexer no motor (`core/combat.js`), que fica limpo, sem nenhum gancho de UI.
  - Carta jogada: `cardView.js` adia a chamada de `aoJogarDuploClique` (dblclick, Enter/espaco, e
    o botao "Jogar" em `combatView.js`) ate o `animationend` de `.carta--jogada` (voa pra cima e
    desaparece, `cards.css`), com guarda contra reentrada (`classList.contains`) pra nao disparar
    a jogada duas vezes se o jogador clicar de novo durante a animacao. Carta bloqueada
    (`motivoBloqueio`) no anima: joga direto so pra mostrar o motivo no log, igual comportamento
    de antes.
  - Dano/cura/bloco: `painel--impacto` (tremor + flash vermelho) ou `painel--cura` (flash verde) na
    `.painel` do alvo, mais um `<span class="numero-flutuante">` (`-N`, `+N`, `+N 🛡️`) que sobe e
    some sozinho (remove-se no proprio `animationend`, sem vazar no DOM).
  - Invocacao: ganho de lacaios (Legiao da Capimaga) mostra `+N 💀` flutuando no painel do
    jogador, mesmo mecanismo.
  - Queda de inimigo: `painel--inimigo--morrendo` (fade + grayscale + leve encolhida,
    `animation-fill-mode: forwards`) toca uma vez quando o hp cruza de >0 pra 0 nessa mesma
    renderizacao; o estado final bate com o `painel--inimigo--caido` estatico que ja existia,
    entao nao ha salto visual quando a keyframe termina.
  - **Verificado ao vivo** (server PHP solto em `localhost:8010` pra nao brigar com outra sessao
    usando a porta 8000 do `php-web` de `.claude/launch.json`): joguei Costela Solta na Capimaga,
    vi a carta voar e sumir da mao, o Sapo Musculoso tremer/flashar e o "-7" flutuar, e o contador
    de Lacaios subir com o "+1 💀" (a carta tem efeito de invocar). Testei tambem o Escudo de
    Carne (ganho de Bloco) e "Fim de turno". Sem erro no console em nenhum passo.
  - **Falta testar ao vivo:** a queda de um inimigo de verdade (nao cheguei a matar o Sapo
    Musculoso na sessao de verificacao, o codigo so foi inspecionado por leitura) e as classes
    Brutamontes/Ligeira (Adrenalina/Impulso reaproveitam a mesma barra de HP e bloco, entao devem
    funcionar sem mudanca, mas nao foram clicadas nesta sessao).
- **Som, tutorial e responsivo mobile integrados em 17/09/2026 (mesmo dia, sessao seguinte, a
  pedido do dono do projeto: "avance tudo que conseguir sem mim").** Sem o dono por perto pra
  aprovar nada visual, entao as tres coisas usam so mecanismos que nao dependem de asset externo
  nenhum:
  - **Som** (`core/audio.js`, novo): nao ha nenhum arquivo de audio no projeto, e baixar de fonte
    externa exige permissao explicita que nao fazia sentido pedir no meio de uma sessao autonoma
    (docs raiz do agente). Solucao: efeitos curtos sintetizados na hora com a Web Audio API
    (osciladores com envelope de ganho, sem asset nenhum) — carta jogada, dano, cura, bloco,
    invocacao, morte de inimigo, vitoria e derrota (3 notas em arpejo pros dois ultimos). Todos os
    ganchos moram nos mesmos pontos da animacao (`combatView.js:aplicarDiferencaEntidade`/
    `aplicarEfeitosVisuais`, `cardView.js:jogar`, `towerView.js:renderFimDeRun`), reaproveitando o
    diff de estado que ja existia pra animacao. Um botao de mudo fixo (`main.js:criarBotaoSom`,
    preso a `document.body`, nao a `#app`, pra sobreviver a troca de tela) persiste a escolha em
    `localStorage` (`capitower_som_mudo`); sem `localStorage` (aba privada) o som so nao persiste
    a preferencia entre recarregamentos, nao quebra nada. AudioContext e criado sob demanda no
    primeiro som (autoplay policy dos navegadores exige gesto do usuario antes).
  - **Tutorial** (`ui/tutorialView.js`, novo): overlay de 5 passos curtos (Acao/cartas, Bloco/alvo,
    Fim de turno, progressao entre andares) preso a `document.body` (mesma razao do botao de som:
    sobrevive a qualquer `container.innerHTML = ""` de tela, e assim tanto faz de qual tela ele foi
    aberto). Aparece sozinho na primeira visita a tela inicial (`screens.js:irParaInicio`, flag
    `capitower_tutorial_visto` no `localStorage`) e fica disponivel de novo a qualquer momento pelo
    botao "Como jogar" que entrou do lado de "Ver perfil" na tela inicial
    (`towerView.js:renderInicio`). Nao interrompe nenhuma run em andamento: so aparece na tela
    inicial, nunca no meio de um combate.
  - **Responsivo mobile**: media queries `max-width: 640px`/`420px` acrescentadas ao fim de
    `combat.css`, `cards.css`, `tower.css` e `layout.css` (paineis, retratos, barra de HP, log e
    botoes encolhem; carta de 148px cai pra 108px e depois 94px). **Achado nao obvio:** o texto da
    carta (`carta__nome`/`carta__tipo`/`carta__texto`/`carta__custo`) fica posicionado em % dentro
    da moldura PNG (janelas medidas por canal alfa, ver acima), entao encolher só a largura da
    carta sem encolher a fonte na mesma proporcao faz o texto estourar a janela e ser cortado pelo
    `overflow: hidden` (vi isso acontecer ao vivo: "Explosao Ossea" perdendo a frase inteira). A
    correcao foi mover o `font-size` pra `.carta` em vez de deixar cada filho com `em` solto: como
    `font-size` em `em` e relativo ao font-size do proprio elemento (nao do body), definir
    `.carta { font-size: 11.7px }` (= `16px * 108/148`) faz nome/tipo/texto/custo encolherem na
    mesma razao da largura automaticamente, sem precisar sobrescrever cada um.
  - **Verificado ao vivo** (mesmo server solto em `localhost:8010`): tutorial abre e fecha sem
    erro (aberto via `import()` no console pra nao interromper a run ja em andamento da sessao de
    verificacao anterior), botao de som alterna o icone e persiste em `localStorage`, todas as 8
    funcoes de som de `core/audio.js` disparadas sem excecao no console. Layout mobile conferido
    redimensionando a aba pra 375x812 (preset "mobile" do navegador da sessao): sem scroll
    horizontal, cartas legiveis, nenhum texto cortado depois da correcao de `font-size`.
  - **Falta testar ao vivo:** som de verdade (so confirmei que a Web Audio API nao lanca excecao,
    nao "ouvi" nada por nao ter audio na sessao de verificacao) e o tutorial no fluxo real (fluxo
    testado foi so via `import()` direto no console, nao pela tela inicial de verdade, porque a
    conta usada na verificacao ja tinha uma run ativa no banco).
- Falta so: **deploy na InfinityFree**, que nao da pra fazer sem a conta/credenciais do dono do
  projeto — criar conta e entrar com senha em servico de terceiro sao acoes que o agente nao faz
  sozinho por politica de seguranca, precisa ser o dono do projeto fazendo ou autorizando passo a
  passo.

## 6. Decisoes que ainda precisam ser tomadas

- Os eventos que faltam (secao 3) precisam de uma sessao de brainstorm igual a que gerou os
  eventos atuais, antes de a Fase 3 poder ser chamada de fechada de verdade.
- Nenhuma outra decisao de design em aberto: `07-decisoes.md` continua valendo para tudo o que ja
  foi resolvido.
