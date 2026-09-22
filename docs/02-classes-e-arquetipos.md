# 02. Classes e arquétipos

## 1. Anatomia de uma classe

Toda classe tem exatamente a mesma estrutura, o que torna o balanceamento comparável:

| Elemento | Regra |
| --- | --- |
| Habilidade | 1 habilidade ativa ou passiva, com 10 níveis. Começa no nível 1. |
| Mecânica exclusiva | 1 sistema próprio que só aquela classe usa. |
| Estado exclusivo | No máximo 1 estado além do vocabulário comum. |
| Arquétipos | 4. Cada um é um **nicho** dentro do jeito de jogar da classe, não uma função no deck. Tem 5 cartas, com pelo menos 1 Ataque, 1 Defesa, 1 Poder e 1 Utilidade (D28). |
| Cartas | 20, sendo 5 por arquétipo. |
| HP inicial | 70, igual para todas. |
| Ação por turno | 3, igual para todas. |

Cada arquétipo precisa ser jogável sozinho e ter pelo menos uma ponte com outro arquétipo da
mesma classe, para que builds híbridas façam sentido.

## 2. Regras de balanceamento

### 2.1 Orçamento de carta

Referência base para custo, usada para comparar cartas entre classes `[ajustar]`:

| Custo em Ação | Dano puro | Bloco puro |
| --- | --- | --- |
| 0 | 3 | 3 |
| 1 | 6 | 5 |
| 2 | 13 | 11 |
| 3 | 21 | 18 |

Cartas com efeito adicional pagam com números abaixo da linha. Cartas condicionais (só valem
dentro do arquétipo) podem passar da linha, porque o custo real é ter as outras cartas do
arquétipo no deck.

### 2.2 Paridade entre classes

As três classes precisam bater aproximadamente os mesmos números nestes eixos, por caminhos
diferentes:

| Eixo | Alvo |
| --- | --- |
| Dano por turno com arquétipo fechado, bloco 3 | comparável entre as três |
| Mitigação por turno | comparável entre as três |
| Turnos até matar o chefe do bloco 5 | comparável entre as três |
| Velocidade de arranque (blocos 1 e 2) | pode variar, e parte da identidade |

Assimetria permitida: **quando** a classe fica forte. Uma pode ser forte cedo e estável, outra
fraca cedo e explosiva no fim. Assimetria proibida: o teto de poder.

### 2.3 Teste de identidade

Antes de aprovar qualquer carta: se essa carta fosse movida para outra classe, faria sentido?
Se sim, ela é genérica demais e não deveria existir.

## 3. Classe 1: Capimaga (definida)

**Status: conceito aprovado, 20 cartas no MVP (`flet_mvp/capitower/cards.py`).**

Capivara necromante. A única classe cuja força está fora do próprio corpo.

### 3.1 Mecânica exclusiva: Lacaios

Lacaios são **contadores persistentes**, não unidades. Aparecem em campo como capivaras esqueleto
empilhando ao lado do jogador, mas **não são alvejáveis, não tem HP e não recebem dano**.

- Persistem entre turnos dentro do mesmo combate.
- **Zeram ao fim do combate**, sempre. Nenhuma carta e nenhum nível de habilidade carrega lacaio
  para o andar seguinte (decisão D23).
- Limite máximo de lacaios em campo: `[ajustar: 10]`, só para não quebrar a interface.
- Só somem por efeito que diga "consome" ou "dissipa".

### 3.2 Habilidade: Legião (níveis 1 a 10)

Começa cada combate com N lacaios em campo. Proposta de curva `[ajustar]`:

| Nível | Efeito |
| --- | --- |
| 1 | Começa o combate com 1 lacaio |
| 2 a 4 | +1 lacaio inicial a cada nível |
| 5 | Ao invocar, 20% de chance de invocar 1 a mais |
| 6 a 8 | +1 lacaio inicial a cada nível |
| 9 | Uma vez por combate, ao ficar sem lacaios em campo, invoca 2 imediatamente |
| 10 | Começa o combate com o dobro de lacaios iniciais |

A curva precisa ser desenhada de forma que o nível 10 seja forte sem tornar as cartas de invocação
irrelevantes, senão a build especialista se auto sabota.

### 3.3 Arquétipos

| # | Arquétipo | Fantasia | Como usa lacaios |
| --- | --- | --- | --- |
| 1 | Enxame | Quantidade acima de qualidade | Invoca muito e barato. Cartas escalam com o **número** de lacaios em campo. |
| 2 | Sacrifício | Poder imediato com custo | **Consome** lacaios para efeitos grandes e instantâneos. Alto risco, alto retorno. |
| 3 | Ossada | Muralha de ossos | Lacaios geram **Bloco** e mitigação passiva. Vence por atrito, ganha o combate no turno 15. |
| 4 | Putrefação | Decadência lenta | Lacaios aplicam **Veneno** e estados. Não precisa atacar para vencer. |

Pontes entre arquétipos: Enxame alimenta Sacrifício (precisa de corpo para gastar). Ossada
alimenta Putrefação (sobreviver é o que dá tempo para o veneno matar). Enxame e Ossada escalam
com o mesmo recurso e brigam pelo mesmo espaço de deck, o que é proposital: força escolha.

### 3.4 Perigo conhecido

O arquétipo Sacrifício combinado com habilidade em nível alto pode virar combo de um turno
(começa com muitos lacaios, gasta todos de uma vez). Isso precisa de teto: efeitos de Sacrifício
devem ter limite de escala ou consumir um número fixo, nunca "consome todos, dano por lacaio"
sem trava.

## 4. O eixo que separa as três classes

**Onde mora o poder do jogador.** Esse é o critério que impede as classes 2 e 3 de virarem
variações da Capimaga.

| Classe | Onde mora o poder | Quando o poder aparece | Ritmo |
| --- | --- | --- | --- |
| Capimaga | No campo (lacaios) | Cresce ao longo do combate | Fraca cedo, vence por atrito |
| Brutamontes | No próprio corpo (vida perdida) | Reage ao que o inimigo faz | Forte cedo, precisa de combustível |
| Ligeira | No deck e na mão (sequência) | Acontece dentro de um único turno | Variância alta, picos explosivos |

Referência assumida: o triângulo tabuleiro / corpo / deck do Slay the Spire (Defect, Ironclad,
Silent). O triângulo é emprestado de propósito, porque funciona e porque cada vértice puxa o
jogador para um tipo de decisão diferente. O conteúdo dentro de cada vértice é nosso.

### Alternativas consideradas e descartadas

| Direção | Por que ficou de fora |
| --- | --- |
| Postura (estilo Watcher) | Vistosa, mas o teto de poder de dançar entre posturas é historicamente difícil de conter. Feriria o pilar de paridade. |
| Alquimista (transformar cartas) | Mora no mesmo vértice de Ligeira (deck). Duas classes brigando pelo mesmo espaço de design. |
| Engenhoca (estruturas que disparam depois) | Mora no mesmo vértice da Capimaga (campo, recurso persistente). Viraria lacaio com outro nome. |
| Bardo (manipular a intenção inimiga) | Interessante, mas exige que todo inimigo do jogo seja desenhado pensando nisso. Custo de conteúdo alto demais. |

## 5. Classe 2: Brutamontes

**Status: conceito aprovado, 20 cartas no MVP (`flet_mvp/capitower/cards.py`).**

Capivara que nunca chegou perto do poço de esteroides e faz questão de dizer isso. Tudo que ela
tem veio de teimosia, e ela leva esse fato mais a sério do que qualquer um gostaria.

### 5.1 Mecânica exclusiva: Adrenalina

**Dano recebido vira recurso.** Toda vez que Brutamontes perde vida (dano que passou pelo Bloco), ela
ganha **1 de Adrenalina**, no máximo 1 por instância de dano.

- Acumula durante o combate, teto de **10** `[ajustar]`.
- Zera ao fim do combate, igual aos lacaios (D23).
- Cartas gastam Adrenalina ou escalam com a quantidade acumulada.

A tensão central da classe cabe em uma frase: **bloquear perfeitamente deixa o tanque vazio.**
Como a cura é escassa (D07), Brutamontes vive negociando vida por poder, e errar essa conta custa a
run. Nenhuma outra classe tem esse dilema.

### 5.2 Habilidade: Casca Grossa (níveis 1 a 10)

Curva proposta `[ajustar]`:

| Nível | Efeito |
| --- | --- |
| 1 | Começa cada combate com 2 de Adrenalina |
| 2 | +1 de Adrenalina inicial (3) |
| 3 | +1 de Adrenalina inicial (4) |
| 4 | A primeira vez que perde vida em cada combate rende 2 de Adrenalina em vez de 1 |
| 5 | Ganha 1 de Adrenalina também quando o Bloco absorve um ataque inteiro |
| 6 | +1 de Adrenalina inicial (5) |
| 7 | O teto de Adrenalina sobe de 10 para 15 |
| 8 | +1 de Adrenalina inicial (6) |
| 9 | Ao cair para metade da vida ou menos, ganha 3 de Adrenalina na hora (uma vez por combate) |
| 10 | Toda Adrenalina ganha e dobrada |

O nível 5 é o degrau mais importante da curva: é ele que desfaz a tensão entre bloquear e
acumular. Por isso precisa vir no meio, e nunca cedo.

### 5.3 Estado exclusivo: Retaliação

Enquanto tiver Retaliação X, todo ataque recebido devolve X de dano ao atacante. Dura N turnos.
É o único estado do jogo que transforma o turno do inimigo em dano do jogador.

### 5.4 Arquétipos

| # | Arquétipo | Nicho | Como usa Adrenalina | Carta exemplo |
| --- | --- | --- | --- | --- |
| 1 | **Suor** | Gerar Adrenalina de propósito, pagando vida | Gera Adrenalina de propósito, inclusive pagando vida por ela | Bufo (0): perde 2 de vida, ganha 2 de Adrenalina, compra 1 carta |
| 2 | **Estouro** | Gastar Adrenalina de uma vez | Consome Adrenalina num golpe único que escala com ela | Cabeçada Final (2): consome até 6 de Adrenalina, causa 10 mais 3 por ponto consumido |
| 3 | **Couro** | Adrenalina acumulada, sem gastar | Converte Adrenalina em Bloco e mitigação | Costado (1): ganha 6 de Bloco, mais 1 por Adrenalina acumulada (limite 8) |
| 4 | **Troco** | Retaliação: ganhar por ser atingida | Retaliação. Ganha por ser atingida, não por atacar | Não Faz Isso (1): ganha Retaliação 4 por 2 turnos |

Pontes: Suor alimenta Estouro (precisa encher para gastar). Couro sustenta Troco (sobreviver é o
que dá tempo de devolver). A briga proposital é **Suor contra Couro**: um quer perder vida, o
outro quer não perder. Escolher entre os dois é escolher como Brutamontes joga.

### 5.5 Perigos conhecidos

- **Estouro com Casca Grossa no nível 10** pode virar golpe único que mata chefe. Trava: consumo
  sempre limitado a um número fixo (o "até 6" do exemplo), nunca "consome toda a Adrenalina".
- **Suor pagando vida com cura escassa** pode virar armadilha para jogador novo. O custo em vida
  precisa ficar bem abaixo do valor de um descanso, senão o arquétipo só funciona para quem já
  decorou a torre.

## 6. Classe 3: Ligeira

**Status: conceito aprovado, 20 cartas no MVP (`flet_mvp/capitower/cards.py`).**

Capivara pequena e encharcada, impossível de segurar. Rápida a ponto de ofender as leis da
natureza e a reputação da própria espécie.

### 6.1 Mecânica exclusiva: Impulso

**Contador de cartas jogadas no turno atual.** Zera no fim de todo turno.

- Não acumula entre turnos, e essa é a diferença fundamental: lacaios e Adrenalina crescem ao
  longo do combate, o Impulso é construído e gasto dentro do mesmo turno.
- Cartas consultam o Impulso ("para cada carta jogada antes desta neste turno").
- Com 3 de Ação e mão de 5, chegar a um Impulso alto exige cartas de custo 0 e geração de Ação.
  Ou seja: o arquétipo de acúmulo da Ligeira não acumula recurso, acumula **tempo dentro do turno**.

### 6.2 Habilidade: Ligeireza (níveis 1 a 10)

Curva proposta `[ajustar]`. Ativa **uma vez por turno**, e esse limite é o que impede loop infinito:

| Nível | Efeito |
| --- | --- |
| 1 | Ao jogar a 5a carta do turno, ganha +1 Ação |
| 2 | Passa a ativar na 4a carta |
| 3 | A ativação também compra 1 carta |
| 4 | Passa a ativar na 3a carta |
| 5 | Começa cada combate com +1 Ação no primeiro turno |
| 6 | A ativação passa a dar +2 Ação |
| 7 | Passa a ativar na 2a carta |
| 8 | A ativação compra 2 cartas |
| 9 | Ativa duas vezes por turno (a segunda exige o dobro de cartas) |
| 10 | A primeira carta de cada turno custa 0 |

### 6.3 Estado exclusivo: Evasão

Anula **completamente** o próximo ataque recebido, uma instância por ponto de Evasão. Não absorve
valor como o Bloco, cancela o golpe inteiro.

Contrapartida embutida: contra inimigo que ataca duas vezes com valores baixos, a Evasão morre
barata. Contra golpe único e pesado, é a melhor defesa do jogo. É uma defesa que exige leitura de
intenção, não aritmética.

### 6.4 Arquétipos

| # | Arquétipo | Nicho | Como usa Impulso | Carta exemplo |
| --- | --- | --- | --- | --- |
| 1 | **Corrente** | Esticar o turno: custo 0 e compra | Cartas de custo 0 e compra, para esticar o turno | Passo Curto (0): causa 2 de dano, compra 1 carta |
| 2 | **Estocada** | Finalizador que escala com o Impulso | Finalizadores que escalam com o Impulso já acumulado | Ponto Cego (1): causa 3 de dano por carta jogada antes desta neste turno (limite 5 cartas) |
| 3 | **Fumaça** | Evasão e negação de golpe | Evasão e negação de golpe | Banho de Lama (1): ganha 1 de Evasão, ou 2 se já jogou 3 cartas neste turno |
| 4 | **Contrabando** | Mexer na mão e no descarte | Mexe no descarte e na ordem de compra, da consistência | Pega de Volta (1): devolve a mão a última carta jogada neste turno (não alcança carta de custo 0) |

Pontes: Contrabando recicla Corrente, Corrente arma Estocada. Fumaça compra os turnos necessários
para o combo se montar. A tensão proposital é que **Fumaça gasta Ação em defesa**, exatamente o
recurso que os outros três arquétipos querem para esticar o turno.

### 6.5 Perigos conhecidos

- **Loop infinito**: Contrabando devolvendo uma carta de custo 0 que se devolve de novo. Regra
  dura do design: nenhum efeito de recursão pode alcançar carta de custo 0. Já está escrita dentro
  da carta exemplo, de propósito.
- **Variância de mão**: a classe pode simplesmente não funcionar num turno em que a mão veio
  errada. A duplicação do deck inicial (D18) ajuda, mas o arquétipo Contrabando precisa existir
  como remédio para isso, e não como luxo.
- **Ligeireza nível 9 com nível 10** precisa de teste pesado. É a única combinação do jogo que
  gera Ação mais de uma vez no mesmo turno.

## 7. Matriz de pressão: chefes contra classes

Cada chefe existe para testar uma competência. Esta matriz é o instrumento de balanceamento: se
uma linha não tiver ninguém sofrendo, o chefe não está testando nada. Se uma classe nunca sofrer,
ela está forte demais.

| Chefe | O que testa | Quem se dá bem | Quem sofre |
| --- | --- | --- | --- |
| Dorival Supino | Golpe único e pesado, telegrafado | Fumaça, a Evasão anula o golpe inteiro | Enxame, que ainda não montou o exército no bloco 1 |
| Marlene Cardio | Duas ações por turno, valores baixos | Suor e Troco, dois gatilhos por turno | Fumaça, a Evasão morre barata |
| Helio Whey | Estados e buff próprio | Putrefação, joga o mesmo jogo melhor | Corrente, um turno de mão ruim e um turno perdido |
| Gêmeos Rosca Direta | Dano concentrado, o irmão herda o buff | Estouro e Estocada, matam antes da herança | Ossada, vence por atrito e o atrito joga a favor dele |
| Sargento Capitolino | Bloco alto todo turno | Estouro e Estocada, um golpe grande fura Bloco | Corrente e Enxame, muitos ataques pequenos morrem no Bloco |
| Soberana Gertrudes | Três fases, uma pressão diferente em cada | Builds generalistas, com resposta para tudo | Especialistas de nicho único |

Observação de design que sai dessa matriz: **Gertrudes é a única luta que favorece o generalista**,
e isso é o contrapeso do caminho especialista. A habilidade em nível alto precisa ser boa o
bastante para pagar essa desvantagem final, senão o jogo passa a ter uma resposta certa e a
decisão central da run vira decoração. Esse é o primeiro número a conferir no playtest.

## 8. Formato de carta

Toda carta tem:

| Campo | Exemplo |
| --- | --- |
| Nome | Costela Solta |
| Classe | Capimaga |
| Arquétipo | Enxame |
| Custo | 1 Ação |
| Tipo | Ataque, Defesa, Poder ou Utilidade |
| Texto | Causa 7 de dano. Invoca 1 lacaio. |
| Efeitos | lista estruturada, ver `docs/05-banco-de-dados.md` |
| Arte | caminho do placeholder |

Cartas de **Poder** ficam em campo pelo resto do combate e não voltam ao deck.

## 9. Catálogo do MVP

Fonte da verdade: `flet_mvp/capitower/cards.py`. A composição segue D28 (cada arquétipo com 5
cartas, pelo menos 1 de cada tipo). Os números são ponto de partida para playtest, todos
`[ajustar]`.

### 9.1 Capimaga

| Arquétipo | Carta | Custo | Tipo | Texto |
| --- | --- | --- | --- | --- |
| Enxame | Costela Solta | 1 | Ataque | Causa 7 de dano. Invoca 1 lacaio. |
| Enxame | Amontoado | 1 | Defesa | Ganha 3 de Defesa. Invoca 2 lacaios. |
| Enxame | Vala Comum | 2 | Poder | No início do seu turno, invoca 1 lacaio. |
| Enxame | Chamado da Vala | 1 | Utilidade | Invoca 3 lacaios. |
| Enxame | Marcha dos Ossos | 2 | Ataque | Causa 4 de dano por lacaio em campo. |
| Sacrifício | Explosão Óssea | 1 | Ataque | Consome até 2 lacaios. Causa 6 de dano por lacaio consumido. |
| Sacrifício | Escudo de Carne | 1 | Defesa | Consome até 2 lacaios. Ganha 3 de Defesa, +4 por lacaio consumido. |
| Sacrifício | Banquete | 2 | Poder | Sempre que consumir pelo menos 1 lacaio, compra 1 carta. |
| Sacrifício | Oferenda | 0 | Utilidade | Consome 1 lacaio. Se consumiu, ganha 1 Ação e compra 1 carta. |
| Sacrifício | Ritual Ganancioso | 2 | Ataque | Consome até 3 lacaios. Causa 4 de dano a todos os inimigos por lacaio consumido. |
| Ossada | Ariete de Costelas | 1 | Ataque | Causa dano igual a sua Defesa atual (limite 10). |
| Ossada | Muralha de Costelas | 1 | Defesa | Ganha 4 de Defesa, +1 por lacaio em campo (limite 8). |
| Ossada | Ossos Firmes | 2 | Poder | No fim do seu turno, ganha 1 de Defesa por lacaio em campo. |
| Ossada | Cimento de Osso | 1 | Utilidade | Ganha 2 de Defesa. A sua Defesa não se perde no fim deste turno. |
| Ossada | Escudo de Cranios | 1 | Defesa | Ganha 5 de Defesa. Invoca 1 lacaio. |
| Putrefação | Baforada Podre | 1 | Ataque | Aplica 5 de Veneno. |
| Putrefação | Pus Endurecido | 1 | Defesa | Ganha 4 de Defesa. Aplica 2 de Veneno. |
| Putrefação | Peste Óssea | 2 | Poder | No fim do seu turno, aplica 2 de Veneno a todos os inimigos. |
| Putrefação | Contágio | 1 | Utilidade | Espalha o Veneno do alvo para os outros inimigos. Compra 1 carta. |
| Putrefação | Mordida Gangrenada | 1 | Ataque | Causa 6 de dano. Se o alvo está envenenado, invoca 1 lacaio e aplica Fraqueza 1. |

### 9.2 Brutamontes

| Arquétipo | Carta | Custo | Tipo | Texto |
| --- | --- | --- | --- | --- |
| Suor | Peitada | 1 | Ataque | Causa 10 de dano. Perde 2 de vida. |
| Suor | Sangue Frio | 1 | Defesa | Perde 2 de vida. Ganha 9 de Defesa. |
| Suor | Rugido | 1 | Poder | Sempre que perder vida, ganha 1 de Adrenalina extra. |
| Suor | Bufo | 0 | Utilidade | Perde 2 de vida. Ganha 2 de Adrenalina. Compra 1 carta. |
| Suor | Mais Uma Série | 1 | Utilidade | Perde 3 de vida. Ganha 1 Ação e 2 de Adrenalina. |
| Estouro | Cabeçada Final | 2 | Ataque | Consome até 6 de Adrenalina. Causa 10 de dano, +3 por ponto consumido. |
| Estouro | Pele de Bicho | 2 | Defesa | Consome até 4 de Adrenalina. Ganha 6 de Defesa, +3 por ponto consumido. |
| Estouro | Pavio Curto | 2 | Poder | Sempre que gastar Adrenalina, causa 1 de dano a todos os inimigos por ponto gasto. |
| Estouro | Explosão de Fôlego | 0 | Utilidade | Consome até 2 de Adrenalina. Ganha 1 Ação por ponto consumido. |
| Estouro | Estampido | 2 | Ataque | Consome até 3 de Adrenalina. Causa 6 de dano a todos, +2 por ponto consumido. |
| Couro | Soco de Sobra | 1 | Ataque | Causa 7 de dano, +1 por Adrenalina acumulada (limite 8). |
| Couro | Costado | 1 | Defesa | Ganha 6 de Defesa, +1 por Adrenalina acumulada (limite 8). |
| Couro | Calo | 2 | Poder | No início do seu turno, ganha Defesa igual a metade da Adrenalina acumulada. |
| Couro | Fôlego Guardado | 1 | Utilidade | Compra 2 cartas. Se tem 5+ de Adrenalina, ganha 1 Ação. |
| Couro | Fincar Pé | 1 | Defesa | Ganha 8 de Defesa. Se tem 5+ de Adrenalina, ganha 1 de Força. |
| Troco | Cotovelada | 1 | Ataque | Causa 6 de dano. Ganha Retaliação 2 por 1 turno. |
| Troco | Não Faz Isso | 1 | Defesa | Ganha Retaliação 4 por 2 turnos. |
| Troco | Olho por Olho | 2 | Poder | Sempre que perder vida para um ataque, causa 3 de dano ao atacante. |
| Troco | Provocar | 0 | Utilidade | Ganha 4 de Defesa e Retaliação 2 por 1 turno. |
| Troco | Queixo de Ferro | 2 | Defesa | Ganha 8 de Defesa e Retaliação 3 por 2 turnos. |

### 9.3 Ligeira

| Arquétipo | Carta | Custo | Tipo | Texto |
| --- | --- | --- | --- | --- |
| Corrente | Passo Curto | 0 | Ataque | Causa 2 de dano. Compra 1 carta. |
| Corrente | Rolamento | 0 | Defesa | Ganha 3 de Defesa. Compra 1 carta. |
| Corrente | Segundo Fôlego | 1 | Poder | Sempre que jogar a 3a carta do turno, compra 1 carta. |
| Corrente | Respiro | 0 | Utilidade | Compra 1 carta. Se já jogou 3 cartas neste turno, ganha 1 Ação. |
| Corrente | Cambalhota | 1 | Ataque | Causa 4 de dano duas vezes. |
| Estocada | Ponto Cego | 1 | Ataque | Causa 3 de dano por carta jogada antes desta neste turno (limite 5). |
| Estocada | Finta | 1 | Defesa | Ganha 4 de Defesa, +2 por carta jogada antes desta neste turno (limite 3). |
| Estocada | Golpe de Vista | 2 | Poder | Sempre que jogar a 4a carta do turno, causa 6 de dano ao alvo. |
| Estocada | Rasteira | 1 | Utilidade | Aplica Fragilidade 2. Se já jogou 3 cartas neste turno, compra 1 carta. |
| Estocada | Dentada Rápida | 1 | Ataque | Causa 6 de dano. Se já jogou 2 cartas neste turno, causa 4 a mais. |
| Fumaça | Bote da Nevoa | 1 | Ataque | Causa 5 de dano. Se tem Evasão, causa 5 a mais. |
| Fumaça | Banho de Lama | 1 | Defesa | Ganha 1 de Evasão, ou 2 se já jogou 3 cartas neste turno. |
| Fumaça | Rastro de Lama | 1 | Poder | Sempre que a Evasão anular um ataque, compra 1 carta. |
| Fumaça | Truque de Fumaça | 1 | Utilidade | Compra 1 carta. Se tem Evasão, ganha 1 Ação. |
| Fumaça | Cortina de Lama | 2 | Defesa | Ganha 1 de Evasão. Aplica Fraqueza 2 a todos os inimigos. |
| Contrabando | Golpe Baixo | 1 | Ataque | Causa 5 de dano. A próxima carta jogada neste turno custa 0. |
| Contrabando | Troca Rápida | 1 | Defesa | Ganha 4 de Defesa. Descarta a mão e compra o mesmo número de cartas. |
| Contrabando | Bolso Fundo | 1 | Poder | No fim do seu turno, guarda 1 carta aleatória da mão em vez de descarta-la. |
| Contrabando | Pega de Volta | 1 | Utilidade | Devolve a mão a última carta jogada neste turno (não alcança carta de custo 0). |
| Contrabando | Baralho Marcado | 1 | Utilidade | Compra 1 carta. A próxima carta jogada neste turno custa 0. |
