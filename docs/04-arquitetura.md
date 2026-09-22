# 04. Arquitetura técnica

## 1. Restrições que definem tudo

O projeto roda em XAMPP no desenvolvimento e em **InfinityFree** na produção. Isso impõe:

- **Sem etapa de build.** Nada de Node, npm, bundler ou transpilador. O que está no repositório é
  exatamente o que roda no servidor.
- **Sem Composer.** Nenhuma dependência PHP externa. Tudo que o back precisa é PDO e as funções
  nativas de sessão e hash.
- **Sem processos em segundo plano, sem WebSocket, sem cron.** Toda comunicação é requisição HTTP
  simples iniciada pelo cliente.
- **Deploy por FTP.** A estrutura precisa suportar copiar o conteúdo e funcionar.

Consequência positiva: o jogo é simples de hospedar em qualquer lugar e não apodrece com o
ecossistema JavaScript.

## 2. Divisão de responsabilidade

| Onde | Responsável por |
| --- | --- |
| **Cliente (JS)** | Todo o combate, embaralhamento, resolução de cartas, animação, interface, ordem dos encontros a partir da seed. |
| **Servidor (PHP)** | Autenticação, catálogo de conteúdo, persistência da run, meta progressão, avaliação de objetivos. |

O combate **não** é validado no servidor. O jogo é single player, sem ranking. O servidor confia
no cliente e apenas guarda o estado. Isso só muda se algum dia existir competição.

O servidor **avalia os objetivos** com base no relatório de fim de run, e não o cliente, para que
a lista de conquistas fique num lugar só e possa mudar sem atualizar o front.

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

Autenticação por sessão PHP com cookie. Sem JWT, sem token no localStorage.

| Método | Rota | Função |
| --- | --- | --- |
| POST | `/api/auth/register.php` | Cria conta. Valida usuário único, guarda `password_hash`. |
| POST | `/api/auth/login.php` | Abre sessão. |
| POST | `/api/auth/logout.php` | Encerra sessão. |
| GET | `/api/auth/me.php` | Retorna usuário logado ou 401. |
| GET | `/api/catalog/bootstrap.php` | Devolve o catálogo inteiro (classes, arquetipos, cartas, inimigos, eventos) mais o que o usuário tem desbloqueado. Uma chamada só no carregamento. |
| POST | `/api/run/start.php` | Cria run, gera seed, sorteia as 5 cartas iniciais. |
| POST | `/api/run/save.php` | Grava o snapshot do estado atual. |
| GET | `/api/run/load.php` | Devolve a run ativa, se existir. |
| POST | `/api/run/finish.php` | Fecha a run (vitória ou derrota), calcula pontos, avalia objetivos, devolve o que foi desbloqueado. |
| GET | `/api/meta/profile.php` | Estatísticas, recordes e desbloqueios. |
| GET | `/api/meta/objectives.php` | Lista de objetivos com progresso. |

## 5. Estado da run

Snapshot em JSON, gravado numa coluna `estado_json`. Formato inicial:

```json
{
  "versao": 1,
  "classe": "capimaga",
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
  perde aquele combate, não a run.
- `versao` existe para migrar saves quando o formato mudar.
- A ordem dos andares não é salva, e **derivada da seed**, o que mantém o snapshot pequeno e
  garante que a torre seja a mesma ao retomar.

## 6. Formato de efeito de carta

Cartas não guardam código, guardam dados. Um interpretador em `effects.js` executa. Exemplo:

```json
[
  { "op": "dano",    "alvo": "inimigo",  "valor": 6 },
  { "op": "invocar", "valor": 1 },
  { "op": "estado",  "alvo": "inimigo",  "estado": "fragilidade", "valor": 2 }
]
```

Operações previstas na primeira versão: `dano`, `dano_por_lacaio`, `bloco`, `bloco_por_lacaio`,
`estado`, `invocar`, `consumir_lacaios`, `comprar`, `ganhar_acao`, `curar`, `repetir`. A Fase 3
acrescentou `dano_defesa` (dano igual ao Bloco atual), `manter_bloco` (Bloco não zera no fim do
turno), `espalhar_veneno`, `poder` (registra um poder persistente, ex: Vala Comum) e `se`
(condicional, com uma lista de efeitos que só resolve se a condição bater), todas para cobrir o
vocabulário que as 20 cartas da Capimaga usam de verdade (`flet_mvp/capitower/cards.py`).

Vantagem: cartas novas entram por linha no banco, sem tocar em JavaScript. Limite conhecido:
efeitos muito exóticos vão acabar precisando de uma operação própria, e tudo bem.

## 7. Segurança mínima

- `password_hash` com `PASSWORD_DEFAULT`, nunca MD5 ou SHA1.
- Toda query com PDO preparado, sem concatenação de string.
- `htmlspecialchars` na saída de qualquer texto que venha do usuário.
- `app/` protegido por `.htaccess` com `Deny from all`, e cada arquivo em `app/` checa uma
  constante definida no ponto de entrada, para o caso do host ignorar o `.htaccess`.
- Sessão com `httponly` e `samesite=Lax`.
- Rate limit simples no login (contador por IP em tabela).

## 8. Convenções de código

- PHP: PSR-12 no espírito, classes em PascalCase, métodos em camelCase.
- JS: módulos ES nativos, `const` por padrão, sem classes onde função resolve.
- Banco: tabelas no plural e em português sem acento, colunas em snake_case.
- Textos de jogo ficam no banco, não no código.
