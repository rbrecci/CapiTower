# CapiTower

Tower crawler roguelike com deck building, jogado no navegador.

Uma familia de capivaras caiu num poco de esteroides e virou uma trupe maligna de super capivaras.
A torre delas tem 50 andares, e no topo esta a Soberana Gertrudes, uma SUPER capivara bombada de
avental de flores. Voce sobe, elas nao gostam.

## Stack

Sem build, sem Node, sem Composer. O projeto roda direto em qualquer host com PHP e MySQL.

| Camada | Tecnologia |
| --- | --- |
| Front | HTML, CSS e JavaScript (ES modules) puro |
| Back | PHP 8 com PDO |
| Banco | MySQL / MariaDB |
| Dev | XAMPP (Apache + PHP + MySQL) |
| Producao | InfinityFree |

## Estado atual

Fase de planejamento e documentacao. Nao ha codigo de jogo ainda, apenas o esqueleto de pastas
e o design documentado em `docs/`.

## Documentacao

| Arquivo | Conteudo |
| --- | --- |
| [docs/00-visao-geral.md](docs/00-visao-geral.md) | Pitch, pilares de design e escopo |
| [docs/01-gdd.md](docs/01-gdd.md) | Game design: combate, run, deck, progressao |
| [docs/02-classes-e-arquetipos.md](docs/02-classes-e-arquetipos.md) | Estrutura de classe, arquetipos e balanceamento |
| [docs/03-conteudo.md](docs/03-conteudo.md) | Inimigos, chefes, eventos e tema |
| [docs/04-arquitetura.md](docs/04-arquitetura.md) | Estrutura de pastas, API e fluxo cliente/servidor |
| [docs/05-banco-de-dados.md](docs/05-banco-de-dados.md) | Modelagem das tabelas |
| [docs/06-roadmap.md](docs/06-roadmap.md) | Fases de desenvolvimento |
| [docs/07-decisoes.md](docs/07-decisoes.md) | Registro de decisoes e pontos em aberto |

## Rodando localmente

1. Clone o repositorio dentro de `C:\xampp\htdocs\`.
2. Suba Apache e MySQL pelo painel do XAMPP.
3. Importe `database/schema.sql` no phpMyAdmin.
4. Copie `app/config/config.example.php` para `app/config/config.php` e ajuste as credenciais.
5. Acesse `http://localhost/CapiTower/public/`.

## Estrutura

```
CapiTower/
  app/          codigo PHP que nao e servido diretamente (config, core, models)
  database/     schema e seeds SQL
  docs/         documentacao de design e tecnica
  public/       raiz web (index, assets, endpoints da API)
```
