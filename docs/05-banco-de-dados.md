# 05. Banco de dados

Estrutura completa em [`database/schema.sql`](../database/schema.sql). Este documento explica o
porque de cada decisao de modelagem.

## 1. Principio

**Conteudo de jogo mora no banco, nao no codigo.** Carta, inimigo, evento, objetivo e nivel de
habilidade sao linhas de tabela. Balancear o jogo vira um `UPDATE`, e nao um deploy.

O preco disso e um interpretador de efeitos no cliente (`effects.js`). Vale a pena: sem isso, cada
ajuste de dano exigiria mexer em JavaScript e subir arquivo por FTP.

## 2. Grupos de tabelas

| Grupo | Tabelas | Muda quando |
| --- | --- | --- |
| Contas | `usuarios`, `login_tentativas` | O jogador se cadastra |
| Catalogo de classe | `classes`, `habilidade_niveis`, `arquetipos`, `cartas` | O designer balanceia |
| Catalogo de mundo | `inimigos`, `inimigo_acoes`, `encontros`, `eventos` | O designer adiciona conteudo |
| Run | `runs`, `run_cartas` | O jogador joga |
| Meta | `objetivos`, `usuario_objetivos`, `usuario_desbloqueios`, `usuario_estatisticas` | O jogador progride |

## 3. Decisoes que merecem explicacao

### 3.1 Por que `slug` em tudo

Toda entidade de catalogo tem `slug` unico alem do `id`. O codigo e os seeds referenciam slug,
nunca id numerico. Isso permite recriar o banco do zero sem quebrar referencias e deixa o SQL
legivel: `carta = 'costela-solta'` diz mais que `carta_id = 47`.

### 3.2 Por que `run_cartas` alem do `estado_json`

O deck aparece nos dois lugares de proposito:

- `estado_json` e a fonte de verdade para **retomar a run**. Snapshot rapido, uma leitura so.
- `run_cartas` e a fonte de verdade para **analisar o jogo**. Com ela da para perguntar ao banco
  quais cartas aparecem em runs vencedoras e quais nunca sao escolhidas. Isso e o dado que vai
  guiar o balanceamento depois.

Se as duas divergirem, `estado_json` ganha e `run_cartas` e reescrita no proximo save.

### 3.3 Por que a ordem dos andares nao e salva

A torre e gerada a partir da `seed` da run com um RNG deterministico (mulberry32). Mesma seed,
mesma torre. Guardar a seed em vez da lista de andares mantem o save pequeno e serve de rede de
seguranca: com a seed da para reproduzir exatamente a run de um bug reportado.

Cuidado: qualquer mudanca no algoritmo de geracao invalida as runs ativas. Por isso `estado_json`
tem campo `versao`.

### 3.4 Por que `inimigo_acoes` e tabela separada

Chefes tem fases, e fase e so um conjunto diferente de acoes. Modelar acao como linha permite:
- ciclo fixo (`ordem` > 0) para inimigos previsiveis, que ensinam o jogador,
- sorteio por peso (`ordem` = 0) para inimigos comuns,
- condicao em JSON (`{"hp_abaixo_de": 50}`) para mudanca de fase.

Tudo sem uma linha de codigo por inimigo.

### 3.5 Por que nao existe tabela de partida ou de turno

Combate e do cliente. O servidor nunca ve turno, jogada ou dano. Guardar isso exigiria enviar
telemetria a cada acao, o que multiplica requisicoes num host gratuito por nenhum ganho real.

### 3.6 Por que `usuario_estatisticas` e tabela e nao consulta

Poderia ser derivada de `runs` com agregacao, mas em host compartilhado consulta agregada em
tabela que so cresce e o primeiro lugar que fica lento. Uma linha por usuario atualizada no
`finish.php` resolve.

## 4. Seeds

`database/seeds.sql` carrega o conteudo do jogo. Ordem obrigatoria por causa das chaves
estrangeiras:

```
classes -> habilidade_niveis -> arquetipos -> cartas
inimigos -> inimigo_acoes -> encontros
eventos
objetivos
```

Regra: o seed e reexecutavel. Usa `INSERT ... ON DUPLICATE KEY UPDATE` com base no slug, de forma
que rodar de novo atualiza os valores em vez de duplicar linhas. E assim que o balanceamento vai
para producao.

## 5. Convencoes

- Nomes de tabela no plural, em portugues sem acento.
- Colunas em `snake_case`.
- Toda tabela de conteudo tem `slug` unico.
- Chave estrangeira sempre nomeada `fk_<tabela>_<referencia>`.
- Indice sempre nomeado `ix_<tabela>_<colunas>`.
- Datas em `DATETIME`, nunca em `TIMESTAMP` (fuso do host gratuito nao e confiavel).
