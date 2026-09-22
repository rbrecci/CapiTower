# 05. Banco de dados

Estrutura completa em [`database/schema.sql`](../database/schema.sql). Este documento explica o
porquê de cada decisão de modelagem.

## 1. Princípio

**Conteúdo de jogo mora no banco, não no código.** Carta, inimigo, evento, objetivo e nível de
habilidade são linhas de tabela. Balancear o jogo vira um `UPDATE`, e não um deploy.

O preço disso é um interpretador de efeitos no cliente (`effects.js`). Vale a pena: sem isso, cada
ajuste de dano exigiria mexer em JavaScript e subir arquivo por FTP.

## 2. Grupos de tabelas

| Grupo | Tabelas | Muda quando |
| --- | --- | --- |
| Contas | `usuarios`, `login_tentativas` | O jogador se cadastra |
| Catálogo de classe | `classes`, `habilidade_niveis`, `arquetipos`, `cartas` | O designer balanceia |
| Catálogo de mundo | `inimigos`, `inimigo_acoes`, `encontros`, `eventos` | O designer adiciona conteúdo |
| Run | `runs`, `run_cartas` | O jogador joga |
| Meta | `objetivos`, `usuario_objetivos`, `usuario_desbloqueios`, `usuario_estatisticas` | O jogador progride |

## 3. Decisões que merecem explicação

### 3.1 Por que `slug` em tudo

Toda entidade de catálogo tem `slug` único além do `id`. O código e os seeds referenciam slug,
nunca id numérico. Isso permite recriar o banco do zero sem quebrar referências e deixa o SQL
legível: `carta = 'costela-solta'` diz mais que `carta_id = 47`.

### 3.2 Por que `run_cartas` além do `estado_json`

O deck aparece nos dois lugares de propósito:

- `estado_json` é a fonte de verdade para **retomar a run**. Snapshot rápido, uma leitura só.
- `run_cartas` é a fonte de verdade para **analisar o jogo**. Com ela dá para perguntar ao banco
  quais cartas aparecem em runs vencedoras e quais nunca são escolhidas. Isso é o dado que vai
  guiar o balanceamento depois.

Se as duas divergirem, `estado_json` ganha e `run_cartas` é reescrita no próximo save.

### 3.3 Por que a ordem dos andares não é salva

A torre é gerada a partir da `seed` da run com um RNG determinístico (mulberry32). Mesma seed,
mesma torre. Guardar a seed em vez da lista de andares mantém o save pequeno e serve de rede de
segurança: com a seed dá para reproduzir exatamente a run de um bug reportado.

Cuidado: qualquer mudança no algoritmo de geração invalida as runs ativas. Por isso `estado_json`
tem campo `versao`.

### 3.4 Por que `inimigo_acoes` é tabela separada

Chefes têm fases, e fase é só um conjunto diferente de ações. Modelar ação como linha permite:
- ciclo fixo (`ordem` > 0) para inimigos previsíveis, que ensinam o jogador,
- sorteio por peso (`ordem` = 0) para inimigos comuns,
- condição em JSON (`{"hp_abaixo_de": 50}`) para mudança de fase.

Tudo sem uma linha de código por inimigo.

### 3.5 Por que não existe tabela de partida ou de turno

Combate é do cliente. O servidor nunca vê turno, jogada ou dano. Guardar isso exigiria enviar
telemetria a cada ação, o que multiplica requisições num host gratuito por nenhum ganho real.

### 3.6 Por que `usuario_estatisticas` é tabela e não consulta

Poderia ser derivada de `runs` com agregação, mas em host compartilhado consulta agregada em
tabela que só cresce e o primeiro lugar que fica lento. Uma linha por usuário atualizada no
`finish.php` resolve.

## 4. Seeds

`database/seeds.sql` carrega o conteúdo do jogo. Ordem obrigatória por causa das chaves
estrangeiras:

```
classes -> habilidade_niveis -> arquetipos -> cartas
inimigos -> inimigo_acoes -> encontros
eventos
objetivos
```

Regra: o seed é reexecutável. Usa `INSERT ... ON DUPLICATE KEY UPDATE` com base no slug, de forma
que rodar de novo atualiza os valores em vez de duplicar linhas. É assim que o balanceamento vai
para produção.

## 5. Convenções

- Nomes de tabela no plural, em português sem acento.
- Colunas em `snake_case`.
- Toda tabela de conteúdo tem `slug` único.
- Chave estrangeira sempre nomeada `fk_<tabela>_<referencia>`.
- Índice sempre nomeado `ix_<tabela>_<colunas>`.
- Datas em `DATETIME`, nunca em `TIMESTAMP` (fuso do host gratuito não é confiável).
