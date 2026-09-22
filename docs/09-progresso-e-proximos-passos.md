# 09. Progresso e próximos passos

Registro do que já foi construído na trilha PHP/JS (a trilha de produção, ver `04-arquitetura.md`)
e do que falta, atualizado em 17/09/2026. O MVP em `flet_mvp/` continua sendo só a referência de
design já balanceada, não faz parte desta lista.

## 1. Estado por fase (`06-roadmap.md`)

| Fase | Status | Observação |
| --- | --- | --- |
| 0. Fundação | Feita | Docs e decisões D01 a D28 fechadas em `07-decisoes.md`. |
| 1. Protótipo de combate | Feita | Verificada jogando no navegador. |
| 2. A torre | Feita | Verificada subindo do andar 1 ao 50 numa run só. |
| 3. Conteúdo da Capimaga | Feita, com uma pendência | Ver seção 3. |
| 4. Banco e conta | Feita | Verificada criando conta, logando, salvando e retomando run entre andares. |
| 5. Meta progressão | Feita, com uma pendência | 12 objetivos em rascunho (seção 3), verificados ao vivo via banco e navegador. Precisam de revisão humana antes de virar lista definitiva. |
| 6. Classes 2 e 3 | Feita, verificada ao vivo | Porte completo (motor, efeitos, banco, UI), jogado no navegador com as duas classes novas. Ver seção 3. |
| 7. Acabamento | Quase feita, falta só o deploy | Arte, animação, som, tutorial e responsivo feitos e verificados ao vivo. Só falta o deploy na InfinityFree, que precisa da conta do dono do projeto. Ver seção 3. |

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
    img/
      ui/{icon.png,logo.png,cenarios/*.jpg,frames/*.png,personagens/*.png}
      enemies/*.png  # copiados nesta sessao, ainda NAO usados por nenhum .js (ver secao 5)
      cards/.gitkeep # vazio: nenhuma arte por carta existe em lugar nenhum ainda
    fonts/LuckiestGuy-Regular.ttf  # copiada nesta sessao, ainda NAO referenciada em nenhum .css
```

Resumo do que cada parte faz:

- `core/rng.js`: mulberry32 com seed, usado tanto para embaralhar o baralho quanto para gerar a
  ordem da torre (`derivarSeed`).
- `core/effects.js`: interpretador do formato de efeito de carta. Além das operações previstas em
  `04-arquitetura.md` seção 6, foram acrescentadas `dano_defesa`, `manter_bloco`, `espalhar_veneno`,
  `poder` e `se` (condicional), exigidas por cartas e chefes reais que não cabiam no vocabulário
  original.
- `core/combat.js`: motor de combate. Foi estendido de 1 para **N inimigos simultaneos** (não
  previsto explicitamente na Fase 1 nem 2), porque o bestiário real tem grupos de até 3 e o chefe
  Gêmeos Rosca Direta depende de herdar buff de um irmão morto.
- `core/tower.js`: gera os 5 blocos e os 6 tipos de sala a partir da seed.
- `core/state.js`: estado completo da run (seed, andar, HP persistente, baralho, modificadores,
  nível da Legião, efeito pendente de evento).
- `data/cards.json`: as 20 cartas da Capimaga, portadas de `flet_mvp/capitower/cards.py`, com campo
  `origem` apontando pra carta original em Python.
- `data/enemy.json`: bestiário completo dos 5 blocos, os 5 chefes nomeados e a Soberana Gertrudes
  com 3 fases, portados de `flet_mvp/capitower/content.py`.
- `data/events.json`: 3 eventos (Bebedouro, Halteres Perdida, Vestiario). Ver pendência abaixo.
- `data/challenges.json`: os 5 modificadores de desafio opcional desenhados no MVP (espelho de
  referência; quem serve de verdade é a tabela `desafios` via `database/seeds.sql`).

## 3. Desvios e pendências conhecidas

- **Eventos incompletos.** O roadmap da Fase 3 pede 8 a 12 eventos; só existem 3 desenhados em
  qualquer lugar (docs ou MVP Python). Os 3 foram portados, os outros 5 a 9 não foram inventados de
  propósito, porque isso é conteúdo/roteiro novo, decisão de design e não de código. **Precisa de
  uma passada de brainstorm de eventos antes de fechar a Fase 3 de verdade.**
- **Modificadores de desafio: os 5 portados em 17/09/2026.** Faltavam Casco Duro, Largada e Mão
  Firme (`flet_mvp/capitower/content.py:MODIFIERS`); Força Bruta e Fôlego Extra já existiam.
  Diferente dos dois primeiros (que só somam num campo da run, `core/state.js:aplicarModificador`),
  esses três são efeitos que se repetem em todo combate da run, então precisaram de um mecanismo
  novo: `criarCombateDeSala` agora recebe `modificadores` (`screens.js` passa `run.modificadores`)
  e guarda em `estado.modificadores`; o motor checa o id direto nesse array em vez de interpretar
  o campo `efeito.op` do desafio (que continua só documentação pra esses três).
  - Casco Duro (+1 Bloco em todo ganho de Bloco do jogador): centralizado em
    `combat.js:ganharBloco`, o único lugar por onde todo Bloco do jogador passa (cartas e poderes
    como Calo/Ossos Firmes), em vez de espalhar a checagem em cada efeito.
  - Largada (+1 Ação no primeiro turno de cada combate) e Mão Firme (compra +1 carta no primeiro
    turno de cada combate): checados em `combat.js:iniciarTurnoJogador` com `estado.turno === 1`,
    no mesmo padrão já usado ali pro bônus de Ação da Ligeira nível 5+.
  - `database/seeds.sql` ganhou os 3 `INSERT ... ON DUPLICATE KEY UPDATE` novos na tabela
    `desafios` (e quem serve pro jogo de verdade, via `api/catalog/bootstrap.php` — Fase 4 trocou
    o catálogo do JSON estatico pelo banco, ver seção 5); `data/challenges.json` só foi atualizado
    a título de espelho de referência.
  - **Verificado**: script Node avulso importando `core/combat.js` direto (sem navegador, sem
    DOM) confirmando os 3 efeitos isolados — Casco Duro somando +1 sobre um ganho de Bloco de
    teste, Largada dando Ação 4/3 no turno 1, Mão Firme puxando a 6a carta no turno 1 — e o caso
    sem nenhum modificador continuando igual a antes (regressão). Rodei também `seeds.sql` contra
    o banco local (os 5 desafios aparecem com `SELECT slug, nome, ordem FROM desafios`) e joguei
    uma carta de verdade no navegador depois da mudança em `ganharBloco`, sem erro no console.
    **Não cheguei a jogar uma run de verdade que sorteasse um dos 3 desafios novos na sala de
    desafio opcional** (a escolha é aleatória entre 2 de N disponíveis, `screens.js:iniciarDesafio`),
    então o caminho "escolher na tela e ver refletido nas rodadas seguintes" só foi coberto pelo
    teste isolado, não ponta a ponta pela UI.
- **3 chefes não verificados ao vivo.** Dorival, Sargento Capitolino e a Soberana Gertrudes foram
  jogados de verdade em combate. Marlene Cardio, Professor Helio Whey e os Gêmeos Rosca Direta
  foram conferidos só por varredura automática dos dados (todas as operações de efeito existem e
  são válidas), não por uma partida real. Vale jogar contra os três antes de considerar a Fase 3
  fechada.
- **Bug de baralho inicial corrigido durante a Fase 3.** O baralho estava sorteando as 20 cartas
  inteiras em vez de 5 cartas distintas com 2 cópias cada (regra D18). Corrigido em `state.js`.
- **Balanceamento nunca testado com gente de verdade.** A última simulação registrada (bot
  ganancioso, `flet_mvp/README.md`) é do MVP Python, antes da Fase 3 portar o conteúdo real pro PHP.
  Vale jogar sessões manuais assim que a Fase 4 permitir persistir progresso.
- **Fase 6 (Brutamontes e Ligeira): código escrito numa sessão só, nunca rodado.** Feito nesta
  sessão, sem verificação ao vivo ainda (sem XAMPP disponível para testar no momento). Detalhe em
  `02-classes-e-arquetipos.md` seções 5 e 6 (números de referência) e `flet_mvp/capitower/
  {cards,content,combat}.py` (fonte da verdade, já balanceada no MVP Python). O que foi feito:
  - `core/combat.js`: `jogador.classe` guia setup (lacaios só pra Capimaga, Adrenalina inicial pra
    Brutamontes por `TABELA_ADRENALINA_INICIAL`), `custoDe`/`motivoBloqueio`/`jogarCarta` levam
    `estado` para checar Ligeira nível 10 (1a carta gratis) e `proximaGratis`; `perderVidaJogador`
    centraliza toda perda de vida do jogador (ataque, veneno, reflexo/espinhos) pra disparar
    Adrenalina e Olho por Olho igual ao Python; `ganharAdrenalina`/`consumirAdrenalina`,
    `verificarLigeireza` (gatilhos 1x/2x por turno, limiar por nível), Retaliação e Evasão em
    `receberAtaque`, poderes novos (`rugido`, `pavio_curto`, `calo`, `olho_por_olho`,
    `segundo_folego`, `golpe_de_vista`, `rastro`, `bolso_fundo`) nos pontos certos do turno.
  - `core/effects.js`: 16 operações novas (`perder_vida`, `ganhar_adrenalina`,
    `consumir_adrenalina`, `dano_por_adrenalina`, `bloco_por_adrenalina`, `dano_por_consumido`,
    `bloco_por_consumido`, `acao_por_consumido`, `retaliacao`, `evasao`, `dano_por_impulso`,
    `bloco_por_impulso`, `dano_condicional`, `devolver_ultima`, `proxima_gratis`, `trocar_mao`) e
    condições `adrenalina>=N`/`evasao>=N`. `dano_condicional` é um desvio proposital do formato de
    "golpe acumulado" do Python (`dmg_plus`/`_add_dmg`): em vez de reabrir um segundo golpe (o que
    aplicaria Força/Fraqueza duas vezes), embute o bônus condicional num único efeito de dano.
  - `core/state.js`, `core/api.js`, `ui/screens.js`: `novaRun`/`cartaAleatoria`/`serializarRun`/
    `restaurarRun` agora levam `classe`; `iniciarRunNoServidor(classe)` manda pro servidor.
  - `ui/towerView.js`: tela inicial virou seleção de classe (le `estadoGlobal.classes` do
    bootstrap) em vez de "Começar a subir" direto.
  - `ui/rewardView.js`, `ui/combatView.js`: nome/texto da habilidade e o rotulo do recurso (HUD)
    ficaram por classe (`HABILIDADE_TEXTOS`/`HABILIDADE_NOMES` em `state.js`).
  - `public/api/run/start.php`: le `classe` do corpo da requisição (era fixo em `capimaga`).
  - `public/assets/js/data/cards.json`: as 40 cartas novas (20 Brutamontes, 20 Ligeira), formato
    igual ao das 20 da Capimaga, com `origem` apontando pro `.py`. JSON validado (60 cartas, 20 por
    classe).
  - `database/seeds.sql`: `INSERT` de `brutamontes`/`ligeira` em `classes`, os 20 níveis de
    habilidade de cada uma, os 8 arquétipos novos e as 40 cartas (efeitos como o mesmo JSON do
    `cards.json`). Sintaxe JS (`node --check`) e PHP (`php -l`) passaram; **o SQL em si não rodou
    contra um banco** (sem `xampp2` de pe nesta sessão).
  - **Verificado ao vivo em 17/09/2026.** `seeds.sql` rodado contra o banco local (ver seção 4
    sobre a troca de XAMPP por Apache/MySQL80 standalone nesta máquina). Jogadas confirmadas sem
    erro de servidor nem de console: Brutamontes (dano por Adrenalina de `Soco de Sobra`,
    Adrenalina automática por `perderVidaJogador` em `Mais Uma Série`, consumo em `Explosão de
    Fôlego`, Retaliação em `Queixo de Ferro` disparando nos dois ataques do Rato de Academia,
    overflow de dano matando um inimigo e sobrando pro outro) e Ligeira (compra de carta e ganho
    de Impulso em `Passo Curto`). Run avançou do andar 1 ao 2 sem problema.
  - **Falta ainda:** o passe de balanceamento comparando as três classes lado a lado (números de
    `02-classes-e-arquetipos.md` seções 5.2/5.4/6.2/6.4), que é mais sessão de playtest humano do
    que verificação técnica — não fechei isso nesta sessão.
- **Retratos de inimigo, favicon e fonte de exibição: arquivos copiados, código não mexido.** Os
  27 retratos do bestiário (`assets/img/enemies/`), o ícone do MVP Flet e a fonte LuckiestGuy
  estão em `public/` desde 17/09/2026, mas nenhum `.js`/`.css`/`.php` foi alterado pra usa-los —
  o jogo continua igual visualmente. Passo a passo de como ligar cada um, ver a seção "Assets do
  MVP" no fim da seção 5.

## 4. Ambiente local

**Atualizado em 17/09/2026: o XAMPP (`C:\xampp2`) descrito antes não existe mais nesta máquina.**
Foi substituido por uma instalação "solta" de Apache 2.4 + PHP 8.4 + MySQL 8.0 (não XAMPP/WAMP),
rodando como serviços Windows (`Apache2.4`, `MySQL80`), provavelmente porque a máquina é
compartilhada com outros projetos da escola (há `C:\CT_Dev`, `C:\Apache\htdocs\FichaDigital` etc.
usando o mesmo MySQL). Detalhe:

| Item | Caminho / valor |
| --- | --- |
| PHP | `C:\php\php.exe` (8.4.1, já no PATH) |
| MySQL client | `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` (8.0.40, já no PATH) |
| Serviço MySQL | `MySQL80`, porta 3306, `root` **com senha** (não mais vazio como no XAMPP) |
| Serviço Apache | `Apache2.4`, mas sem vhost pro CapiTower — não serve este projeto |
| `app/config/config.php` | Criado nesta sessão, fora do git. `senha` = a mesma usada pelo
  `FichaDigital` (outro projeto PHP nesta máquina, `C:\Apache\htdocs\FichaDigital\config\app.local.php`) |

Como não há vhost do Apache pro projeto, a forma de rodar continua sendo `php -S` (já configurado
em `.claude/launch.json` como `php-web`, porta 8000), que só precisa do MySQL de pe — não do
Apache. `database/schema.sql` e `database/seeds.sql` já foram aplicados contra o banco `capitower`
nesta máquina (ambos são idempotentes: `CREATE TABLE IF NOT EXISTS` e `ON DUPLICATE KEY UPDATE`,
rodar de novo depois de mudar o catálogo é seguro).

## 5. Próximos passos, em ordem

### Fase 4: banco e conta (feita — lista abaixo é o registro histórico da implementação, não um TODO)

1. Copiar `app/config/config.example.php` para `app/config/config.php` (fica fora do git, ver
   seção 4 para os valores atuais desta máquina).
2. Rodar `database/schema.sql` e depois `database/seeds.sql` no MySQL local (via phpMyAdmin ou
   `mysql` CLI).
3. Implementar `app/core/{Database,Response,Auth,Request}.php` conforme `04-arquitetura.md` seção 3
   e 7 (PDO preparado, `password_hash`, sessão com `httponly`/`samesite=Lax`, rate limit de login).
4. Implementar os endpoints de `04-arquitetura.md` seção 4: `api/auth/{register,login,logout,me}.php`,
   `api/catalog/bootstrap.php`, `api/run/{start,save,load,finish}.php`, `api/meta/{profile,objectives}.php`.
5. Trocar `data/*.json` (usados hoje como fonte local fixa) por uma chamada a
   `api/catalog/bootstrap.php`: o catálogo passa a vir do banco, os JSON continuam existindo só como
   seed de referência, não mais como fonte servida ao cliente.
6. Implementar save/load do snapshot `estado_json` (formato já descrito em `04-arquitetura.md`
   seção 5) entre andares, e retomar run ativa ao entrar.
7. Verificar de verdade: criar conta, logar, começar uma run, fechar a aba no meio de um andar,
   voltar e continuar do mesmo andar. Esse é o critério de saída da Fase 4.

### Fase 5: meta progressão (feita, rascunho para revisão)

- `objetivos` semeada com 12 linhas (`database/seeds.sql`, bloco "OBJETIVOS"): 3 marcos de andar,
  vitória da torre, 5 chefes nomeados, e 3 objetivos mais difíceis (2 deles ocultos até serem
  batidos). Cada `condicao` é um JSON `{"tipo":...}` avaliado em
  `app/models/Meta.php::condicaoBatida()`.
- Pool inicial reduzido: as 5 cartas do arquétipo Putrefação (`cm_baforada`, `cm_pus`, `cm_peste`,
  `cm_contagio`, `cm_mordida`) viraram `inicial = 0`. `objetivos.recompensa_tipo` e
  `usuario_desbloqueios.tipo` ganharam o valor `arquetipo`, para destravar o arquétipo inteiro de
  uma vez (ver nota no topo de `database/schema.sql`).
- `app/models/Meta.php::avaliarObjetivos()` roda dentro de `public/api/run/finish.php` depois de
  `Run::finalizar()`, grava `usuario_objetivos`/`usuario_desbloqueios` e devolve o que foi
  desbloqueado agora pro cliente mostrar na tela de fim de run.
- `public/assets/js/ui/profileView.js` (novo): estatísticas e lista de objetivos com progresso,
  acessível pelo botão "Ver perfil" na tela inicial e na tela de fim de run.
- **Pendência:** a lista de 12 objetivos é um rascunho meu, não validado por playtest nem revisado
  pelo dono do projeto. Ver relatório da sessão que implementou a Fase 5 para a lista completa e o
  raciocínio de cada um.

### Fase 6: classes 2 e 3

- Porte feito e verificado ao vivo nesta sessão (ver seção 3): motor (`core/combat.js`,
  `core/effects.js`), banco (`database/seeds.sql`) e UI (seleção de classe, HUD por recurso) para
  Brutamontes (Adrenalina) e Ligeira (Impulso), no mesmo padrão usado na Fase 3 para a Capimaga.
- **Falta só o passe de balanceamento** comparando as três classes lado a lado (playtest humano,
  não verificação técnica).

### Fase 7: acabamento (começada em 17/09/2026)

- **Arte integrada nesta sessão**, a partir de arquivos que apareceram em `Assets/` (raiz do
  projeto, não versionado, gerados por IA em 11/09/2026) e foram copiados para
  `public/assets/img/ui/`:
  - `logo.png`: logo do jogo na tela inicial (`towerView.js:renderInicio`).
  - `cenarios/{poco,academia,laboratorio,refeitorio,jardim,menu}.jpg`: fundo de tela cheio,
    trocado por bloco atual via `towerView.js:aplicarFundoDaSala()` (chamado em
    `screens.js:renderSala`) contra um `<div id="fundo-cenario">` fixo atras de `#app`
    (`public/index.php`, CSS em `base.css`). **Achado não óbvio:** um `background` sólido em
    `html, body` vira o "canvas" do viewport e a spec CSS pinta isso abaixo de qualquer
    descendente, mesmo com `z-index` negativo — teve que sair do `html, body` e morar só no
    `#fundo-cenario` pro cenário aparecer.
  - `frames/{ataque,defesa,poder,utilidade}.png`: moldura ilustrada por tipo de carta, uma pra
    cada um dos 4 tipos que já existem no catálogo. `cardView.js` agora põe
    `carta--tipo-<tipo>` no elemento; `cards.css` usa a moldura como `background-image` da carta
    inteira (`aspect-ratio: 848/1264`, igual ao PNG de origem, pra nunca esticar) e posiciona
    custo/nome+tipo/texto em cima das 3 "janelas" transparentes desenhadas na moldura (custo no
    círculo de gema, nome+tipo na janela de arte — não há arte própria por carta ainda, então essa
    janela virou a área do título —, texto na janela inferior). As coordenadas das janelas foram
    medidas escaneando o canal alpha do PNG (script Python de uso único, não versionado), não
    chutadas visualmente.
  - `personagens/{capimaga,brutamontes,ligeira,soberana-gertrudes}.png`: retrato de classe na
    tela inicial (`towerView.js:renderInicio`, `.opcao-classe`) e no painel do jogador durante o
    combate (`combatView.js:criarPainelJogador`, por `estado.jogador.classe`); a Soberana
    Gertrudes também ganhou retrato próprio no painel de inimigo (`RETRATOS_INIMIGO`, casado pelo
    nome exato em `enemy.json`). O resto do bestiário continua no emoji genérico (🐸 vivo / 💀
    caído) — sem arte por inimigo ainda. (Nota da sessão: cheguei a achar, por erro de leitura
    visual da minha parte, que esses 4 PNGs eram prévia de marketplace de clip-art com fundo sujo
    e selos colados; o dono do projeto corrigiu e a verificação objetiva do canal alpha confirmou
    que os arquivos sempre foram limpos — sem transparência real e sem badge nenhum. Registrado
    aqui só pra quem ler a sessão entender por que o retrato demorou uma rodada a mais pra entrar.)
- **Animação de carta, dano e invocação integrada em 17/09/2026.** A tela de combate inteira é
  redesenhada do zero a cada mudança de estado (`combatView.js:renderizarCombate`, arquitetura da
  Fase 1), então não há "de" e "para" no DOM pra fazer `transition`: tudo virou `@keyframes` de
  um tiro só, disparado por classe temporária que `combatView.js` calcula comparando um retrato do
  estado tirado logo antes de uma ação mutar `estado` (jogar carta, fim de turno) contra o estado
  depois (`snapshotDe`/`aplicarEfeitosVisuais`). Sem isso a única forma de saber "o que mudou"
  seria remexer no motor (`core/combat.js`), que fica limpo, sem nenhum gancho de UI.
  - Carta jogada: `cardView.js` adia a chamada de `aoJogarDuploClique` (dblclick, Enter/espaço, e
    o botão "Jogar" em `combatView.js`) até o `animationend` de `.carta--jogada` (voa pra cima e
    desaparece, `cards.css`), com guarda contra reentrada (`classList.contains`) pra não disparar
    a jogada duas vezes se o jogador clicar de novo durante a animação. Carta bloqueada
    (`motivoBloqueio`) no anima: joga direto só pra mostrar o motivo no log, igual comportamento
    de antes.
  - Dano/cura/bloco: `painel--impacto` (tremor + flash vermelho) ou `painel--cura` (flash verde) na
    `.painel` do alvo, mais um `<span class="numero-flutuante">` (`-N`, `+N`, `+N 🛡️`) que sobe e
    some sozinho (remove-se no próprio `animationend`, sem vazar no DOM).
  - Invocação: ganho de lacaios (Legião da Capimaga) mostra `+N 💀` flutuando no painel do
    jogador, mesmo mecanismo.
  - Queda de inimigo: `painel--inimigo--morrendo` (fade + grayscale + leve encolhida,
    `animation-fill-mode: forwards`) toca uma vez quando o hp cruza de >0 pra 0 nessa mesma
    renderização; o estado final bate com o `painel--inimigo--caido` estático que já existia,
    então não há salto visual quando a keyframe termina.
  - **Verificado ao vivo** (server PHP solto em `localhost:8010` pra não brigar com outra sessão
    usando a porta 8000 do `php-web` de `.claude/launch.json`): joguei Costela Solta na Capimaga,
    vi a carta voar e sumir da mão, o Sapo Musculoso tremer/flashar e o "-7" flutuar, e o contador
    de Lacaios subir com o "+1 💀" (a carta tem efeito de invocar). Testei também o Escudo de
    Carne (ganho de Bloco) e "Fim de turno". Sem erro no console em nenhum passo.
  - **Falta testar ao vivo:** a queda de um inimigo de verdade (não cheguei a matar o Sapo
    Musculoso na sessão de verificação, o código só foi inspecionado por leitura) e as classes
    Brutamontes/Ligeira (Adrenalina/Impulso reaproveitam a mesma barra de HP e bloco, então devem
    funcionar sem mudança, mas não foram clicadas nesta sessão).
- **Som, tutorial e responsivo mobile integrados em 17/09/2026 (mesmo dia, sessão seguinte, a
  pedido do dono do projeto: "avance tudo que conseguir sem mim").** Sem o dono por perto pra
  aprovar nada visual, então as três coisas usam só mecanismos que não dependem de asset externo
  nenhum:
  - **Som** (`core/audio.js`, novo): não há nenhum arquivo de áudio no projeto, e baixar de fonte
    externa exige permissão explícita que não fazia sentido pedir no meio de uma sessão autônoma
    (docs raiz do agente). Solução: efeitos curtos sintetizados na hora com a Web Audio API
    (osciladores com envelope de ganho, sem asset nenhum) — carta jogada, dano, cura, bloco,
    invocação, morte de inimigo, vitória e derrota (3 notas em arpejo pros dois últimos). Todos os
    ganchos moram nos mesmos pontos da animação (`combatView.js:aplicarDiferencaEntidade`/
    `aplicarEfeitosVisuais`, `cardView.js:jogar`, `towerView.js:renderFimDeRun`), reaproveitando o
    diff de estado que já existia pra animação. Um botão de mudo fixo (`main.js:criarBotaoSom`,
    preso a `document.body`, não a `#app`, pra sobreviver a troca de tela) persiste a escolha em
    `localStorage` (`capitower_som_mudo`); sem `localStorage` (aba privada) o som só não persiste
    a preferência entre recarregamentos, não quebra nada. AudioContext é criado sob demanda no
    primeiro som (autoplay policy dos navegadores exige gesto do usuário antes).
  - **Tutorial** (`ui/tutorialView.js`, novo): overlay de 5 passos curtos (Ação/cartas, Bloco/alvo,
    Fim de turno, progressão entre andares) preso a `document.body` (mesma razão do botão de som:
    sobrevive a qualquer `container.innerHTML = ""` de tela, e assim tanto faz de qual tela ele foi
    aberto). Aparece sozinho na primeira visita a tela inicial (`screens.js:irParaInicio`, flag
    `capitower_tutorial_visto` no `localStorage`) e fica disponível de novo a qualquer momento pelo
    botão "Como jogar" que entrou do lado de "Ver perfil" na tela inicial
    (`towerView.js:renderInicio`). Não interrompe nenhuma run em andamento: só aparece na tela
    inicial, nunca no meio de um combate.
  - **Responsivo mobile**: media queries `max-width: 640px`/`420px` acrescentadas ao fim de
    `combat.css`, `cards.css`, `tower.css` e `layout.css` (paineis, retratos, barra de HP, log e
    botões encolhem; carta de 148px cai pra 108px e depois 94px). **Achado não óbvio:** o texto da
    carta (`carta__nome`/`carta__tipo`/`carta__texto`/`carta__custo`) fica posicionado em % dentro
    da moldura PNG (janelas medidas por canal alfa, ver acima), então encolher só a largura da
    carta sem encolher a fonte na mesma proporção faz o texto estourar a janela e ser cortado pelo
    `overflow: hidden` (vi isso acontecer ao vivo: "Explosão Óssea" perdendo a frase inteira). A
    correção foi mover o `font-size` pra `.carta` em vez de deixar cada filho com `em` solto: como
    `font-size` em `em` é relativo ao font-size do próprio elemento (não do body), definir
    `.carta { font-size: 11.7px }` (= `16px * 108/148`) faz nome/tipo/texto/custo encolherem na
    mesma razão da largura automaticamente, sem precisar sobrescrever cada um.
  - **Verificado ao vivo** (mesmo server solto em `localhost:8010`): tutorial abre e fecha sem
    erro (aberto via `import()` no console pra não interromper a run já em andamento da sessão de
    verificação anterior), botão de som alterna o ícone e persiste em `localStorage`, todas as 8
    funções de som de `core/audio.js` disparadas sem exceção no console. Layout mobile conferido
    redimensionando a aba pra 375x812 (preset "mobile" do navegador da sessão): sem scroll
    horizontal, cartas legíveis, nenhum texto cortado depois da correção de `font-size`.
  - **Falta testar ao vivo:** som de verdade (só confirmei que a Web Audio API não lança exceção,
    não "ouvi" nada por não ter áudio na sessão de verificação) e o tutorial no fluxo real (fluxo
    testado foi só via `import()` direto no console, não pela tela inicial de verdade, porque a
    conta usada na verificação já tinha uma run ativa no banco).
- Falta só: **deploy na InfinityFree**, que não dá pra fazer sem a conta/credenciais do dono do
  projeto — criar conta e entrar com senha em serviço de terceiro são ações que o agente não faz
  sozinho por política de segurança, precisa ser o dono do projeto fazendo ou autorizando passo a
  passo.

### Assets do MVP: copiados em 17/09/2026, ainda NÃO ligados ao jogo (próximo passo)

A pedido do dono do projeto ("copia todos os assets já presentes na pasta de assets do mvp pra
não ter que gerar tudo de novo"), copiei pra `public/assets/` tudo que existia em
`flet_mvp/assets/` e ainda não tinha equivalente no trilha PHP/JS. **Só copiei os arquivos —
nenhum `.js`/`.css`/`.php` foi tocado, o jogo continua se comportando exatamente como antes.**
Isto aqui é o mapa de como usar o que já está copiado, pra economizar o trabalho de descoberta na
próxima sessão.

**O que foi copiado, e o que ficou de fora:**

- `public/assets/img/enemies/<id>.png` (27 arquivos novos): os retratos do bestiário inteiro —
  15 monstros comuns, 5 elites, 6 chefes de bloco e a Soberana Gertrudes — gerados via os prompts
  de `08-prompts-de-assets.md` (estilo cartoon consistente com a Capimaga, 512px RGBA, fundo
  branco). O `<id>` de cada arquivo bate exatamente com a chave de `data/enemy.json` (`inimigos`)
  e com `inimigo.id` no motor (`combat.js:criarInimigo`), então não precisa de tabela de
  conversão nenhuma.
- `public/assets/img/ui/icon.png` (1 arquivo): ícone que o MVP Flet usa no launcher do APK. Nunca
  foi pensado pra favicon de navegador (arquivo grande, resolução pra ícone de app), só serve como
  ponto de partida.
- `public/assets/fonts/LuckiestGuy-Regular.ttf` (1 arquivo): fonte de exibição usada no MVP Flet
  (Google Font, licença OFL, pode embutir sem problema). Nenhuma tela hoje usa fonte custom, só
  `--fonte` de `base.css` (system font stack).
- **Não copiei** (já existe versão equivalente e melhor em `public/`, copiar por cima seria
  regressão): `logo.png`, os 6 `bg_*.jpg` (cenários) e as 4 `frame_*.png`, além dos retratos de
  `capimaga`/`brutamontes`/`ligeira.png`. Esses vieram de uma leva de arte diferente e mais
  recente (pasta `Assets/` na raiz do projeto, não versionada, ver seção 3 mais acima) — são
  arquivos maiores/mais nitidos que os equivalentes do MVP Flet (conferido por tamanho de arquivo,
  ex.: `logo.png` do MVP tem 290KB contra 415KB do que já está em uso).
- **Não existe em lugar nenhum ainda** (nem MVP Python, nem `Assets/`): arte individual por carta.
  `public/assets/img/cards/` continua vazio de propósito — só há as 4 molduras por tipo
  (Ataque/Defesa/Poder/Utilidade), sem ilustração própria por carta.

**Como ligar cada coisa no jogo (nenhuma feita ainda, só o mapa do trabalho):**

1. **Retratos de inimigo** (o maior ganho visual, substitui os emojis genéricos 🐸/💀 de quase
   todo o bestiário): `combatView.js` tem um `RETRATOS_INIMIGO` que hoje só cobre a Soberana
   Gertrudes, mapeado por **nome exato**. Trocar por um mapa por **id** (a chave dos 27 arquivos
   novos), lido de `inimigo.id` (já existe no objeto, vem de `criarInimigo`/`resolverDefInimigo`
   em `combat.js`/`state.js`, não precisa mudar o motor). Decisão pendente: a Gertrudes agora tem
   dois retratos — `personagens/soberana-gertrudes.png` (já em uso, estilo "retrato de hero card",
   maior) e o novo `enemies/gertrudes.png` (mesmo traco/tamanho dos outros 26). Escolher qual usar
   no painel de combate; a outra sobra pra outro lugar (ex.: tela de fim de run) ou fica sem uso.
2. **Favicon**: acrescentar `<link rel="icon" href="assets/img/ui/icon.png">` no `<head>` de
   `index.php`. Como o arquivo é grande/pensado pra launcher de app (não pra navegador), vale
   redimensionar antes (32x32 ou 64x64 costuma bastar pra favicon; 180x180 se quiser
   apple-touch-icon também) em vez de servir o PNG original direto.
3. **Fonte de exibição**: `@font-face` em `base.css` apontando pra
   `assets/fonts/LuckiestGuy-Regular.ttf`, aplicada em títulos/telas de destaque (`h1`,
   `.tela-fim__titulo`, talvez `.cabecalho-andar`) mantendo o corpo do texto (cartas, log, botões)
   na fonte de sistema atual — texto pequeno numa fonte tão estilizada perde legibilidade.
4. **Arte por carta**: é trabalho de geração nova, não de porte (não existe em lugar nenhum pra
   copiar). Precisaria de um doc de prompts novo nos moldes de `08-prompts-de-assets.md`, cobrindo
   as 60 cartas (20 por classe), e de mudar `cards.css` (`.carta__arte` hoje e ocupada por
   nome+tipo, porque não há arte própria; sobraria pra ilustração e nome/tipo mudariam de lugar na
   moldura). Vale avaliar se compensa o esforço antes de começar — cada carta já mostra nome e
   tipo com clareza sem arte própria.

## 6. Decisões que ainda precisam ser tomadas

- Os eventos que faltam (seção 3) precisam de uma sessão de brainstorm igual a que gerou os
  eventos atuais, antes de a Fase 3 poder ser chamada de fechada de verdade.
- Nenhuma outra decisão de design em aberto: `07-decisoes.md` continua valendo para tudo o que já
  foi resolvido.
