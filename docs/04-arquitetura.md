# 04. Arquitetura tecnica

## 1. Restricoes que definem tudo

O projeto roda em XAMPP no desenvolvimento e em **InfinityFree** na producao. Isso impoe:

- **Sem etapa de build.** Nada de Node, npm, bundler ou transpilador. O que esta no repositorio e
  exatamente o que roda no servidor.
- **Sem Composer.** Nenhuma dependencia PHP externa. Tudo que o back precisa e PDO e as funcoes
  nativas de sessao e hash.
- **Sem processos em segundo plano, sem WebSocket, sem cron.** Toda comunicacao e requisicao HTTP
  simples iniciada pelo cliente.
- **Deploy por FTP.** A estrutura precisa suportar copiar o conteudo e funcionar.

Consequencia positiva: o jogo e simples de hospedar em qualquer lugar e nao apodrece com o
ecossistema JavaScript.

## 2. Divisao de responsabilidade

| Onde | Responsavel por |
| --- | --- |
| **Cliente (JS)** | Todo o combate, embaralhamento, resolucao de cartas, animacao, interface, ordem dos encontros a partir da seed. |
| **Servidor (PHP)** | Autenticacao, catalogo de conteudo, persistencia da run, meta progressao, avaliacao de objetivos. |

O combate **nao** e validado no servidor. O jogo e single player, sem ranking. O servidor confia
no cliente e apenas guarda o estado. Isso so muda se algum dia existir competicao.

O servidor **avalia os objetivos** com base no relatorio de fim de run, e nao o cliente, para que
a lista de conquistas fique num lugar so e possa mudar sem atualizar o front.

## 3. Estrutura de pastas

```
CapiTower/
  app/                        nao servido diretamente ao navegador
    config/
      config.example.php      modelo versionado
      config.php              credenciais reais, fora do git
    core/
      Database.php            conexao PDO singleton
      Response.php            resposta JSON padronizada
      Auth.php                sessao, login, registro, hash
      Request.php             leitura e validacao de entrada
    models/
      User.php
      Catalog.php             classes, cartas, arquetipos, inimigos
      Run.php                 save e load da run
      Meta.php                desbloqueios, objetivos, estatisticas
    .htaccess                 Deny from all

  database/
    schema.sql                estrutura das tabelas
    seeds.sql                 conteudo do jogo (cartas, inimigos, objetivos)

  docs/                       esta documentacao

  public/                     raiz web
    index.php                 shell do jogo, uma pagina so
    assets/
      css/
        base.css              reset, variaveis, tipografia
        layout.css
        combat.css
        cards.css
      js/
        main.js               ponto de entrada, roteador de telas
        core/
          state.js            estado global da run
          rng.js              random com seed (mulberry32)
          combat.js           motor de combate
          effects.js          interpretador do formato de efeito
          tower.js            geracao da ordem dos andares
          api.js              wrapper de fetch
        ui/
          screens.js
          cardView.js
          combatView.js
          rewardView.js
        data/
          cache.js            catalogo baixado do servidor, guardado em memoria
      img/
        cards/ enemies/ ui/   placeholders agora, arte de IA depois
    api/
      auth/     register.php  login.php  logout.php  me.php
      catalog/  bootstrap.php
      run/      start.php  save.php  load.php  finish.php
      meta/     profile.php  objectives.php
```

## 4. Contrato da API

Todo endpoint responde JSON no mesmo envelope:

```json
{ "ok": true,  "data": { } }
{ "ok": false, "error": { "code": "AUTH_REQUIRED", "message": "Faca login" } }
```

Autenticacao por sessao PHP com cookie. Sem JWT, sem token no localStorage.

| Metodo | Rota | Funcao |
| --- | --- | --- |
| POST | `/api/auth/register.php` | Cria conta. Valida usuario unico, guarda `password_hash`. |
| POST | `/api/auth/login.php` | Abre sessao. |
| POST | `/api/auth/logout.php` | Encerra sessao. |
| GET | `/api/auth/me.php` | Retorna usuario logado ou 401. |
| GET | `/api/catalog/bootstrap.php` | Devolve o catalogo inteiro (classes, arquetipos, cartas, inimigos, eventos) mais o que o usuario tem desbloqueado. Uma chamada so no carregamento. |
| POST | `/api/run/start.php` | Cria run, gera seed, sorteia as 5 cartas iniciais. |
| POST | `/api/run/save.php` | Grava o snapshot do estado atual. |
| GET | `/api/run/load.php` | Devolve a run ativa, se existir. |
| POST | `/api/run/finish.php` | Fecha a run (vitoria ou derrota), calcula pontos, avalia objetivos, devolve o que foi desbloqueado. |
| GET | `/api/meta/profile.php` | Estatisticas, recordes e desbloqueios. |
| GET | `/api/meta/objectives.php` | Lista de objetivos com progresso. |

## 5. Estado da run

Snapshot em JSON, gravado numa coluna `estado_json`. Formato inicial:

```json
{
  "versao": 1,
  "classe": "conjuradora",
  "seed": 849213774,
  "andar": 23,
  "hp": 41,
  "hp_max": 70,
  "nivel_habilidade": 4,
  "deck": [12, 12, 7, 3, 19, 4, 4, 21],
  "andares_resolvidos": [1, 2, 3],
  "recompensas_usadas": { "carta": 3, "habilidade": 3 },
  "modificadores": [ { "tipo": "forca_permanente", "valor": 1 } ]
}
```

Regras:
- O save acontece **entre andares**, nunca no meio do combate. Fechar a aba durante um combate
  perde aquele combate, nao a run.
- `versao` existe para migrar saves quando o formato mudar.
- A ordem dos andares nao e salva, e **derivada da seed**, o que mantem o snapshot pequeno e
  garante que a torre seja a mesma ao retomar.

## 6. Formato de efeito de carta

Cartas nao guardam codigo, guardam dados. Um interpretador em `effects.js` executa. Exemplo:

```json
[
  { "op": "dano",    "alvo": "inimigo",  "valor": 6 },
  { "op": "invocar", "valor": 1 },
  { "op": "estado",  "alvo": "inimigo",  "estado": "fragilidade", "valor": 2 }
]
```

Operacoes previstas na primeira versao: `dano`, `dano_por_lacaio`, `bloco`, `bloco_por_lacaio`,
`estado`, `invocar`, `consumir_lacaios`, `comprar`, `ganhar_acao`, `curar`, `repetir`.

Vantagem: cartas novas entram por linha no banco, sem tocar em JavaScript. Limite conhecido:
efeitos muito exoticos vao acabar precisando de uma operacao propria, e tudo bem.

## 7. Seguranca minima

- `password_hash` com `PASSWORD_DEFAULT`, nunca MD5 ou SHA1.
- Toda query com PDO preparado, sem concatenacao de string.
- `htmlspecialchars` na saida de qualquer texto que venha do usuario.
- `app/` protegido por `.htaccess` com `Deny from all`, e cada arquivo em `app/` checa uma
  constante definida no ponto de entrada, para o caso do host ignorar o `.htaccess`.
- Sessao com `httponly` e `samesite=Lax`.
- Rate limit simples no login (contador por IP em tabela).

## 8. Convencoes de codigo

- PHP: PSR-12 no espirito, classes em PascalCase, metodos em camelCase.
- JS: modulos ES nativos, `const` por padrao, sem classes onde funcao resolve.
- Banco: tabelas no plural e em portugues sem acento, colunas em snake_case.
- Textos de jogo ficam no banco, nao no codigo.
