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
| 6. Classes 2 e 3 | Nao comecada | Conteudo de Brutamontes e Ligeira ja existe balanceado no MVP Python, falta portar. |
| 7. Acabamento | Nao comecada | |

## 2. O que existe hoje em `public/`

Nenhum destes arquivos foi commitado ainda.

```
public/
  index.php
  assets/
    css/{base,layout,combat,cards,tower}.css
    js/
      main.js
      core/{rng,combat,effects,state,tower}.js
      ui/{screens,cardView,combatView,towerView,rewardView,eventView,challengeView}.js
      data/{cards.json,enemy.json,events.json,challenges.json}
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

## 4. Ambiente local

Esta maquina tem tres pastas de XAMPP em `C:\`, so uma funciona:

| Pasta | Estado | Uso |
| --- | --- | --- |
| `C:\xampp` | So `phpMyAdmin/` e `php_old/`, sem `mysql/` nem `apache/` | Nao usar |
| `C:\xamppp` | So `htdocs/` e `phpMyAdmin/`, sem `mysql/` nem `apache/` | Nao usar |
| `C:\xampp2` | Instalacao completa: `mysql/`, `apache/`, `mysql_start.bat`, `xampp-control.exe` | **Esta e a que funciona** |

Testado em 16/09/2026: `C:\xampp2\mysql_start.bat` sobe o MySQL (MariaDB 10.4.32) na porta 3306,
conexao PDO como `root` sem senha funciona, batendo com os valores padrao ja documentados em
`app/config/config.example.php`. `htdocs/` do `xampp2` e onde o projeto precisa ficar acessivel
para rodar via Apache do XAMPP (ou seguir usando `php -S`, que nao depende do Apache).

## 5. Proximos passos, em ordem

### Fase 4: banco e conta

1. Copiar `app/config/config.example.php` para `app/config/config.php` (fica fora do git) apontando
   pro `xampp2`.
2. Rodar `database/schema.sql` e depois `database/seeds.sql` no MySQL do `xampp2` (via phpMyAdmin ou
   `mysql` CLI). **Antes disso, revisar se o `seeds.sql` atual bate com o catalogo real que ja saiu
   nos JSON da Fase 3** (20 cartas da Capimaga, bestiario completo, 3 eventos): o schema foi escrito
   na Fase 0, antes desse conteudo existir, e pode estar com dados de exemplo desatualizados.
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

- Brutamontes e Ligeira ja tem mecanica, estado exclusivo, 4 arquetipos e 20 cartas cada desenhados
  e testados no MVP Python (`flet_mvp/capitower/{cards,content}.py`). O trabalho aqui e
  majoritariamente porte, no mesmo padrao usado na Fase 3 para a Capimaga.
- Falta o passe de balanceamento comparando as tres classes.

### Fase 7: acabamento

- Arte de IA no lugar dos placeholders (o MVP Flet ja tem sprites gerados em `flet_mvp/assets/`,
  ver `08-prompts-de-assets.md` pelos prompts usados).
- Animacao, som, tutorial, responsivo, deploy na InfinityFree.

## 6. Decisoes que ainda precisam ser tomadas

- Os eventos que faltam (secao 3) precisam de uma sessao de brainstorm igual a que gerou os
  eventos atuais, antes de a Fase 3 poder ser chamada de fechada de verdade.
- Nenhuma outra decisao de design em aberto: `07-decisoes.md` continua valendo para tudo o que ja
  foi resolvido.
