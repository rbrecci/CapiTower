# 02. Classes e arquetipos

## 1. Anatomia de uma classe

Toda classe tem exatamente a mesma estrutura, o que torna o balanceamento comparavel:

| Elemento | Regra |
| --- | --- |
| Habilidade | 1 habilidade ativa ou passiva, com 10 niveis. Comeca no nivel 1. |
| Mecanica exclusiva | 1 sistema proprio que so aquela classe usa. |
| Estado exclusivo | No maximo 1 estado alem do vocabulario comum. |
| Arquetipos | 4, com fantasias distintas entre si. |
| Cartas | 20, sendo 5 por arquetipo. |
| HP inicial | 70, igual para todas. |
| Acao por turno | 3, igual para todas. |

Cada arquetipo precisa ser jogavel sozinho e ter pelo menos uma ponte com outro arquetipo da
mesma classe, para que builds hibridas facam sentido.

## 2. Regras de balanceamento

### 2.1 Orcamento de carta

Referencia base para custo, usada para comparar cartas entre classes `[ajustar]`:

| Custo em Acao | Dano puro | Bloco puro |
| --- | --- | --- |
| 0 | 3 | 3 |
| 1 | 6 | 5 |
| 2 | 13 | 11 |
| 3 | 21 | 18 |

Cartas com efeito adicional pagam com numeros abaixo da linha. Cartas condicionais (so valem
dentro do arquetipo) podem passar da linha, porque o custo real e ter as outras cartas do
arquetipo no deck.

### 2.2 Paridade entre classes

As tres classes precisam bater aproximadamente os mesmos numeros nestes eixos, por caminhos
diferentes:

| Eixo | Alvo |
| --- | --- |
| Dano por turno com arquetipo fechado, bloco 3 | comparavel entre as tres |
| Mitigacao por turno | comparavel entre as tres |
| Turnos ate matar o chefe do bloco 5 | comparavel entre as tres |
| Velocidade de arranque (blocos 1 e 2) | pode variar, e parte da identidade |

Assimetria permitida: **quando** a classe fica forte. Uma pode ser forte cedo e estavel, outra
fraca cedo e explosiva no fim. Assimetria proibida: o teto de poder.

### 2.3 Teste de identidade

Antes de aprovar qualquer carta: se essa carta fosse movida para outra classe, faria sentido?
Se sim, ela e generica demais e nao deveria existir.

## 3. Classe 1: a Conjuradora (definida)

**Status: conceito aprovado, cartas a detalhar.**

Capivara necromante. A unica classe cuja forca esta fora do proprio corpo.

### 3.1 Mecanica exclusiva: Lacaios

Lacaios sao **contadores persistentes**, nao unidades. Aparecem em campo como capivaras esqueleto
empilhando ao lado do jogador, mas **nao sao alvejaveis, nao tem HP e nao recebem dano**.

- Persistem entre turnos dentro do mesmo combate.
- Zeram ao fim do combate `[ajustar: ou carregam para o proximo andar em alguma build]`.
- Limite maximo de lacaios em campo: `[ajustar: 10]`, so para nao quebrar a interface.
- So somem por efeito que diga "consome" ou "dissipa".

### 3.2 Habilidade: Legiao (niveis 1 a 10)

Comeca cada combate com N lacaios em campo. Proposta de curva `[ajustar]`:

| Nivel | Efeito |
| --- | --- |
| 1 | Comeca o combate com 1 lacaio |
| 2 a 4 | +1 lacaio inicial a cada nivel |
| 5 | Ao invocar, 20% de chance de invocar 1 a mais |
| 6 a 8 | +1 lacaio inicial a cada nivel |
| 9 | Lacaios sobrevivem ao fim do combate (metade, arredondado para baixo) |
| 10 | Comeca o combate com o dobro de lacaios iniciais |

A curva precisa ser desenhada de forma que o nivel 10 seja forte sem tornar as cartas de invocacao
irrelevantes, senao a build especialista se auto sabota.

### 3.3 Arquetipos

| # | Arquetipo | Fantasia | Como usa lacaios |
| --- | --- | --- | --- |
| 1 | Enxame | Quantidade acima de qualidade | Invoca muito e barato. Cartas escalam com o **numero** de lacaios em campo. |
| 2 | Sacrificio | Poder imediato com custo | **Consome** lacaios para efeitos grandes e instantaneos. Alto risco, alto retorno. |
| 3 | Ossada | Muralha de ossos | Lacaios geram **Bloco** e mitigacao passiva. Vence por atrito, ganha o combate no turno 15. |
| 4 | Putrefacao | Decadencia lenta | Lacaios aplicam **Veneno** e estados. Nao precisa atacar para vencer. |

Pontes entre arquetipos: Enxame alimenta Sacrificio (precisa de corpo para gastar). Ossada
alimenta Putrefacao (sobreviver e o que da tempo para o veneno matar). Enxame e Ossada escalam
com o mesmo recurso e brigam pelo mesmo espaco de deck, o que e proposital: forca escolha.

### 3.4 Perigo conhecido

O arquetipo Sacrificio combinado com habilidade em nivel alto pode virar combo de um turno
(comeca com muitos lacaios, gasta todos de uma vez). Isso precisa de teto: efeitos de Sacrificio
devem ter limite de escala ou consumir um numero fixo, nunca "consome todos, dano por lacaio"
sem trava.

## 4. Classes 2 e 3 (a definir)

**Status: nao definidas. A resolver na fase de brainstorm.**

Requisitos que ja fecham antes de escolher os conceitos:

- Nenhuma pode ser "a classe de dano" ou "a classe de defesa". Todas precisam de acesso aos dois.
- Cada uma precisa de uma mecanica exclusiva tao visivel quanto Lacaios, algo que o jogador
  aponte na tela e diga: e essa aqui.
- Cada uma precisa dos mesmos 4 arquetipos estruturais: um de acumulo, um de gasto explosivo, um
  defensivo e um alternativo (estados, manipulacao de deck, controle de turno).

Direcoes candidatas para avaliar no brainstorm (nenhuma escolhida ainda):

| Direcao | Mecanica exclusiva possivel |
| --- | --- |
| Bruta / musculo | Postura acumulada que converte dano recebido em dano devolvido |
| Agil / combo | Contador de cartas jogadas no turno, cartas de custo 0 encadeadas |
| Alquimista | Transformacao de cartas na mao, mistura de dois efeitos em um |
| Engenhoca | Estruturas que disparam no fim do turno, com tempo de preparo |
| Bardo / controle | Manipulacao da intencao do inimigo, atrasar e redirecionar |

## 5. Formato de carta

Toda carta tem:

| Campo | Exemplo |
| --- | --- |
| Nome | Costela Solta |
| Classe | Conjuradora |
| Arquetipo | Enxame |
| Custo | 1 Acao |
| Tipo | Ataque, Defesa, Poder ou Utilidade |
| Texto | Causa 6 de dano. Invoca 1 lacaio. |
| Efeitos | lista estruturada, ver `docs/05-banco-de-dados.md` |
| Arte | caminho do placeholder |

Cartas de **Poder** ficam em campo pelo resto do combate e nao voltam ao deck.
