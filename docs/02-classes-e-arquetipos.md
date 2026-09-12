# 02. Classes e arquetipos

## 1. Anatomia de uma classe

Toda classe tem exatamente a mesma estrutura, o que torna o balanceamento comparavel:

| Elemento | Regra |
| --- | --- |
| Habilidade | 1 habilidade ativa ou passiva, com 10 niveis. Comeca no nivel 1. |
| Mecanica exclusiva | 1 sistema proprio que so aquela classe usa. |
| Estado exclusivo | No maximo 1 estado alem do vocabulario comum. |
| Arquetipos | 4. Cada um e um **nicho** dentro do jeito de jogar da classe, nao uma funcao no deck. Tem 5 cartas, com pelo menos 1 Ataque, 1 Defesa, 1 Poder e 1 Utilidade (D28). |
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

## 3. Classe 1: Capimaga (definida)

**Status: conceito aprovado, 20 cartas no MVP (`flet_mvp/capitower/cards.py`).**

Capivara necromante. A unica classe cuja forca esta fora do proprio corpo.

### 3.1 Mecanica exclusiva: Lacaios

Lacaios sao **contadores persistentes**, nao unidades. Aparecem em campo como capivaras esqueleto
empilhando ao lado do jogador, mas **nao sao alvejaveis, nao tem HP e nao recebem dano**.

- Persistem entre turnos dentro do mesmo combate.
- **Zeram ao fim do combate**, sempre. Nenhuma carta e nenhum nivel de habilidade carrega lacaio
  para o andar seguinte (decisao D23).
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
| 9 | Uma vez por combate, ao ficar sem lacaios em campo, invoca 2 imediatamente |
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

## 4. O eixo que separa as tres classes

**Onde mora o poder do jogador.** Esse e o criterio que impede as classes 2 e 3 de virarem
variacoes da Capimaga.

| Classe | Onde mora o poder | Quando o poder aparece | Ritmo |
| --- | --- | --- | --- |
| Capimaga | No campo (lacaios) | Cresce ao longo do combate | Fraca cedo, vence por atrito |
| Brutamontes | No proprio corpo (vida perdida) | Reage ao que o inimigo faz | Forte cedo, precisa de combustivel |
| Ligeira | No deck e na mao (sequencia) | Acontece dentro de um unico turno | Variancia alta, picos explosivos |

Referencia assumida: o triangulo tabuleiro / corpo / deck do Slay the Spire (Defect, Ironclad,
Silent). O triangulo e emprestado de proposito, porque funciona e porque cada vertice puxa o
jogador para um tipo de decisao diferente. O conteudo dentro de cada vertice e nosso.

### Alternativas consideradas e descartadas

| Direcao | Por que ficou de fora |
| --- | --- |
| Postura (estilo Watcher) | Vistosa, mas o teto de poder de dancar entre posturas e historicamente dificil de conter. Feriria o pilar de paridade. |
| Alquimista (transformar cartas) | Mora no mesmo vertice de Ligeira (deck). Duas classes brigando pelo mesmo espaco de design. |
| Engenhoca (estruturas que disparam depois) | Mora no mesmo vertice da Capimaga (campo, recurso persistente). Viraria lacaio com outro nome. |
| Bardo (manipular a intencao inimiga) | Interessante, mas exige que todo inimigo do jogo seja desenhado pensando nisso. Custo de conteudo alto demais. |

## 5. Classe 2: Brutamontes

**Status: conceito aprovado, 20 cartas no MVP (`flet_mvp/capitower/cards.py`).**

Capivara que nunca chegou perto do poco de esteroides e faz questao de dizer isso. Tudo que ela
tem veio de teimosia, e ela leva esse fato mais a serio do que qualquer um gostaria.

### 5.1 Mecanica exclusiva: Adrenalina

**Dano recebido vira recurso.** Toda vez que Brutamontes perde vida (dano que passou pelo Bloco), ela
ganha **1 de Adrenalina**, no maximo 1 por instancia de dano.

- Acumula durante o combate, teto de **10** `[ajustar]`.
- Zera ao fim do combate, igual aos lacaios (D23).
- Cartas gastam Adrenalina ou escalam com a quantidade acumulada.

A tensao central da classe cabe em uma frase: **bloquear perfeitamente deixa o tanque vazio.**
Como a cura e escassa (D07), Brutamontes vive negociando vida por poder, e errar essa conta custa a
run. Nenhuma outra classe tem esse dilema.

### 5.2 Habilidade: Casca Grossa (niveis 1 a 10)

Curva proposta `[ajustar]`:

| Nivel | Efeito |
| --- | --- |
| 1 | Comeca cada combate com 2 de Adrenalina |
| 2 | +1 de Adrenalina inicial (3) |
| 3 | +1 de Adrenalina inicial (4) |
| 4 | A primeira vez que perde vida em cada combate rende 2 de Adrenalina em vez de 1 |
| 5 | Ganha 1 de Adrenalina tambem quando o Bloco absorve um ataque inteiro |
| 6 | +1 de Adrenalina inicial (5) |
| 7 | O teto de Adrenalina sobe de 10 para 15 |
| 8 | +1 de Adrenalina inicial (6) |
| 9 | Ao cair para metade da vida ou menos, ganha 3 de Adrenalina na hora (uma vez por combate) |
| 10 | Toda Adrenalina ganha e dobrada |

O nivel 5 e o degrau mais importante da curva: e ele que desfaz a tensao entre bloquear e
acumular. Por isso precisa vir no meio, e nunca cedo.

### 5.3 Estado exclusivo: Retaliacao

Enquanto tiver Retaliacao X, todo ataque recebido devolve X de dano ao atacante. Dura N turnos.
E o unico estado do jogo que transforma o turno do inimigo em dano do jogador.

### 5.4 Arquetipos

| # | Arquetipo | Nicho | Como usa Adrenalina | Carta exemplo |
| --- | --- | --- | --- | --- |
| 1 | **Suor** | Gerar Adrenalina de proposito, pagando vida | Gera Adrenalina de proposito, inclusive pagando vida por ela | Bufo (0): perde 2 de vida, ganha 2 de Adrenalina, compra 1 carta |
| 2 | **Estouro** | Gastar Adrenalina de uma vez | Consome Adrenalina num golpe unico que escala com ela | Cabecada Final (2): consome ate 6 de Adrenalina, causa 10 mais 3 por ponto consumido |
| 3 | **Couro** | Adrenalina acumulada, sem gastar | Converte Adrenalina em Bloco e mitigacao | Costado (1): ganha 6 de Bloco, mais 1 por Adrenalina acumulada (limite 8) |
| 4 | **Troco** | Retaliacao: ganhar por ser atingida | Retaliacao. Ganha por ser atingida, nao por atacar | Nao Faz Isso (1): ganha Retaliacao 4 por 2 turnos |

Pontes: Suor alimenta Estouro (precisa encher para gastar). Couro sustenta Troco (sobreviver e o
que da tempo de devolver). A briga proposital e **Suor contra Couro**: um quer perder vida, o
outro quer nao perder. Escolher entre os dois e escolher como Brutamontes joga.

### 5.5 Perigos conhecidos

- **Estouro com Casca Grossa no nivel 10** pode virar golpe unico que mata chefe. Trava: consumo
  sempre limitado a um numero fixo (o "ate 6" do exemplo), nunca "consome toda a Adrenalina".
- **Suor pagando vida com cura escassa** pode virar armadilha para jogador novo. O custo em vida
  precisa ficar bem abaixo do valor de um descanso, senao o arquetipo so funciona para quem ja
  decorou a torre.

## 6. Classe 3: Ligeira

**Status: conceito aprovado, 20 cartas no MVP (`flet_mvp/capitower/cards.py`).**

Capivara pequena e encharcada, impossivel de segurar. Rapida a ponto de ofender as leis da
natureza e a reputacao da propria especie.

### 6.1 Mecanica exclusiva: Impulso

**Contador de cartas jogadas no turno atual.** Zera no fim de todo turno.

- Nao acumula entre turnos, e essa e a diferenca fundamental: lacaios e Adrenalina crescem ao
  longo do combate, o Impulso e construido e gasto dentro do mesmo turno.
- Cartas consultam o Impulso ("para cada carta jogada antes desta neste turno").
- Com 3 de Acao e mao de 5, chegar a um Impulso alto exige cartas de custo 0 e geracao de Acao.
  Ou seja: o arquetipo de acumulo da Ligeira nao acumula recurso, acumula **tempo dentro do turno**.

### 6.2 Habilidade: Ligeireza (niveis 1 a 10)

Curva proposta `[ajustar]`. Ativa **uma vez por turno**, e esse limite e o que impede loop infinito:

| Nivel | Efeito |
| --- | --- |
| 1 | Ao jogar a 5a carta do turno, ganha +1 Acao |
| 2 | Passa a ativar na 4a carta |
| 3 | A ativacao tambem compra 1 carta |
| 4 | Passa a ativar na 3a carta |
| 5 | Comeca cada combate com +1 Acao no primeiro turno |
| 6 | A ativacao passa a dar +2 Acao |
| 7 | Passa a ativar na 2a carta |
| 8 | A ativacao compra 2 cartas |
| 9 | Ativa duas vezes por turno (a segunda exige o dobro de cartas) |
| 10 | A primeira carta de cada turno custa 0 |

### 6.3 Estado exclusivo: Evasao

Anula **completamente** o proximo ataque recebido, uma instancia por ponto de Evasao. Nao absorve
valor como o Bloco, cancela o golpe inteiro.

Contrapartida embutida: contra inimigo que ataca duas vezes com valores baixos, a Evasao morre
barata. Contra golpe unico e pesado, e a melhor defesa do jogo. E uma defesa que exige leitura de
intencao, nao aritmetica.

### 6.4 Arquetipos

| # | Arquetipo | Nicho | Como usa Impulso | Carta exemplo |
| --- | --- | --- | --- | --- |
| 1 | **Corrente** | Esticar o turno: custo 0 e compra | Cartas de custo 0 e compra, para esticar o turno | Passo Curto (0): causa 2 de dano, compra 1 carta |
| 2 | **Estocada** | Finalizador que escala com o Impulso | Finalizadores que escalam com o Impulso ja acumulado | Ponto Cego (1): causa 3 de dano por carta jogada antes desta neste turno (limite 5 cartas) |
| 3 | **Fumaca** | Evasao e negacao de golpe | Evasao e negacao de golpe | Banho de Lama (1): ganha 1 de Evasao, ou 2 se ja jogou 3 cartas neste turno |
| 4 | **Contrabando** | Mexer na mao e no descarte | Mexe no descarte e na ordem de compra, da consistencia | Pega de Volta (1): devolve a mao a ultima carta jogada neste turno (nao alcanca carta de custo 0) |

Pontes: Contrabando recicla Corrente, Corrente arma Estocada. Fumaca compra os turnos necessarios
para o combo se montar. A tensao proposital e que **Fumaca gasta Acao em defesa**, exatamente o
recurso que os outros tres arquetipos querem para esticar o turno.

### 6.5 Perigos conhecidos

- **Loop infinito**: Contrabando devolvendo uma carta de custo 0 que se devolve de novo. Regra
  dura do design: nenhum efeito de recursao pode alcancar carta de custo 0. Ja esta escrita dentro
  da carta exemplo, de proposito.
- **Variancia de mao**: a classe pode simplesmente nao funcionar num turno em que a mao veio
  errada. A duplicacao do deck inicial (D18) ajuda, mas o arquetipo Contrabando precisa existir
  como remedio para isso, e nao como luxo.
- **Ligeireza nivel 9 com nivel 10** precisa de teste pesado. E a unica combinacao do jogo que
  gera Acao mais de uma vez no mesmo turno.

## 7. Matriz de pressao: chefes contra classes

Cada chefe existe para testar uma competencia. Esta matriz e o instrumento de balanceamento: se
uma linha nao tiver ninguem sofrendo, o chefe nao esta testando nada. Se uma classe nunca sofrer,
ela esta forte demais.

| Chefe | O que testa | Quem se da bem | Quem sofre |
| --- | --- | --- | --- |
| Dorival Supino | Golpe unico e pesado, telegrafado | Fumaca, a Evasao anula o golpe inteiro | Enxame, que ainda nao montou o exercito no bloco 1 |
| Marlene Cardio | Duas acoes por turno, valores baixos | Suor e Troco, dois gatilhos por turno | Fumaca, a Evasao morre barata |
| Helio Whey | Estados e buff proprio | Putrefacao, joga o mesmo jogo melhor | Corrente, um turno de mao ruim e um turno perdido |
| Gemeos Rosca Direta | Dano concentrado, o irmao herda o buff | Estouro e Estocada, matam antes da heranca | Ossada, vence por atrito e o atrito joga a favor dele |
| Sargento Capitolino | Bloco alto todo turno | Estouro e Estocada, um golpe grande fura Bloco | Corrente e Enxame, muitos ataques pequenos morrem no Bloco |
| Soberana Gertrudes | Tres fases, uma pressao diferente em cada | Builds generalistas, com resposta para tudo | Especialistas de nicho unico |

Observacao de design que sai dessa matriz: **Gertrudes e a unica luta que favorece o generalista**,
e isso e o contrapeso do caminho especialista. A habilidade em nivel alto precisa ser boa o
bastante para pagar essa desvantagem final, senao o jogo passa a ter uma resposta certa e a
decisao central da run vira decoracao. Esse e o primeiro numero a conferir no playtest.

## 8. Formato de carta

Toda carta tem:

| Campo | Exemplo |
| --- | --- |
| Nome | Costela Solta |
| Classe | Capimaga |
| Arquetipo | Enxame |
| Custo | 1 Acao |
| Tipo | Ataque, Defesa, Poder ou Utilidade |
| Texto | Causa 7 de dano. Invoca 1 lacaio. |
| Efeitos | lista estruturada, ver `docs/05-banco-de-dados.md` |
| Arte | caminho do placeholder |

Cartas de **Poder** ficam em campo pelo resto do combate e nao voltam ao deck.

## 9. Catalogo do MVP

Fonte da verdade: `flet_mvp/capitower/cards.py`. A composicao segue D28 (cada arquetipo com 5
cartas, pelo menos 1 de cada tipo). Os numeros sao ponto de partida para playtest, todos
`[ajustar]`.

### 9.1 Capimaga

| Arquetipo | Carta | Custo | Tipo | Texto |
| --- | --- | --- | --- | --- |
| Enxame | Costela Solta | 1 | Ataque | Causa 7 de dano. Invoca 1 lacaio. |
| Enxame | Amontoado | 1 | Defesa | Ganha 3 de Defesa. Invoca 2 lacaios. |
| Enxame | Vala Comum | 2 | Poder | No inicio do seu turno, invoca 1 lacaio. |
| Enxame | Chamado da Vala | 1 | Utilidade | Invoca 3 lacaios. |
| Enxame | Marcha dos Ossos | 2 | Ataque | Causa 4 de dano por lacaio em campo. |
| Sacrificio | Explosao Ossea | 1 | Ataque | Consome ate 2 lacaios. Causa 6 de dano por lacaio consumido. |
| Sacrificio | Escudo de Carne | 1 | Defesa | Consome ate 2 lacaios. Ganha 3 de Defesa, +4 por lacaio consumido. |
| Sacrificio | Banquete | 2 | Poder | Sempre que consumir pelo menos 1 lacaio, compra 1 carta. |
| Sacrificio | Oferenda | 0 | Utilidade | Consome 1 lacaio. Se consumiu, ganha 1 Acao e compra 1 carta. |
| Sacrificio | Ritual Ganancioso | 2 | Ataque | Consome ate 3 lacaios. Causa 4 de dano a todos os inimigos por lacaio consumido. |
| Ossada | Ariete de Costelas | 1 | Ataque | Causa dano igual a sua Defesa atual (limite 10). |
| Ossada | Muralha de Costelas | 1 | Defesa | Ganha 4 de Defesa, +1 por lacaio em campo (limite 8). |
| Ossada | Ossos Firmes | 2 | Poder | No fim do seu turno, ganha 1 de Defesa por lacaio em campo. |
| Ossada | Cimento de Osso | 1 | Utilidade | Ganha 2 de Defesa. A sua Defesa nao se perde no fim deste turno. |
| Ossada | Escudo de Cranios | 1 | Defesa | Ganha 5 de Defesa. Invoca 1 lacaio. |
| Putrefacao | Baforada Podre | 1 | Ataque | Aplica 5 de Veneno. |
| Putrefacao | Pus Endurecido | 1 | Defesa | Ganha 4 de Defesa. Aplica 2 de Veneno. |
| Putrefacao | Peste Ossea | 2 | Poder | No fim do seu turno, aplica 2 de Veneno a todos os inimigos. |
| Putrefacao | Contagio | 1 | Utilidade | Espalha o Veneno do alvo para os outros inimigos. Compra 1 carta. |
| Putrefacao | Mordida Gangrenada | 1 | Ataque | Causa 6 de dano. Se o alvo esta envenenado, invoca 1 lacaio e aplica Fraqueza 1. |

### 9.2 Brutamontes

| Arquetipo | Carta | Custo | Tipo | Texto |
| --- | --- | --- | --- | --- |
| Suor | Peitada | 1 | Ataque | Causa 10 de dano. Perde 2 de vida. |
| Suor | Sangue Frio | 1 | Defesa | Perde 2 de vida. Ganha 9 de Defesa. |
| Suor | Rugido | 1 | Poder | Sempre que perder vida, ganha 1 de Adrenalina extra. |
| Suor | Bufo | 0 | Utilidade | Perde 2 de vida. Ganha 2 de Adrenalina. Compra 1 carta. |
| Suor | Mais Uma Serie | 1 | Utilidade | Perde 3 de vida. Ganha 1 Acao e 2 de Adrenalina. |
| Estouro | Cabecada Final | 2 | Ataque | Consome ate 6 de Adrenalina. Causa 10 de dano, +3 por ponto consumido. |
| Estouro | Pele de Bicho | 2 | Defesa | Consome ate 4 de Adrenalina. Ganha 6 de Defesa, +3 por ponto consumido. |
| Estouro | Pavio Curto | 2 | Poder | Sempre que gastar Adrenalina, causa 1 de dano a todos os inimigos por ponto gasto. |
| Estouro | Explosao de Folego | 0 | Utilidade | Consome ate 2 de Adrenalina. Ganha 1 Acao por ponto consumido. |
| Estouro | Estampido | 2 | Ataque | Consome ate 3 de Adrenalina. Causa 6 de dano a todos, +2 por ponto consumido. |
| Couro | Soco de Sobra | 1 | Ataque | Causa 7 de dano, +1 por Adrenalina acumulada (limite 8). |
| Couro | Costado | 1 | Defesa | Ganha 6 de Defesa, +1 por Adrenalina acumulada (limite 8). |
| Couro | Calo | 2 | Poder | No inicio do seu turno, ganha Defesa igual a metade da Adrenalina acumulada. |
| Couro | Folego Guardado | 1 | Utilidade | Compra 2 cartas. Se tem 5+ de Adrenalina, ganha 1 Acao. |
| Couro | Fincar Pe | 1 | Defesa | Ganha 8 de Defesa. Se tem 5+ de Adrenalina, ganha 1 de Forca. |
| Troco | Cotovelada | 1 | Ataque | Causa 6 de dano. Ganha Retaliacao 2 por 1 turno. |
| Troco | Nao Faz Isso | 1 | Defesa | Ganha Retaliacao 4 por 2 turnos. |
| Troco | Olho por Olho | 2 | Poder | Sempre que perder vida para um ataque, causa 3 de dano ao atacante. |
| Troco | Provocar | 0 | Utilidade | Ganha 4 de Defesa e Retaliacao 2 por 1 turno. |
| Troco | Queixo de Ferro | 2 | Defesa | Ganha 8 de Defesa e Retaliacao 3 por 2 turnos. |

### 9.3 Ligeira

| Arquetipo | Carta | Custo | Tipo | Texto |
| --- | --- | --- | --- | --- |
| Corrente | Passo Curto | 0 | Ataque | Causa 2 de dano. Compra 1 carta. |
| Corrente | Rolamento | 0 | Defesa | Ganha 3 de Defesa. Compra 1 carta. |
| Corrente | Segundo Folego | 1 | Poder | Sempre que jogar a 3a carta do turno, compra 1 carta. |
| Corrente | Respiro | 0 | Utilidade | Compra 1 carta. Se ja jogou 3 cartas neste turno, ganha 1 Acao. |
| Corrente | Cambalhota | 1 | Ataque | Causa 4 de dano duas vezes. |
| Estocada | Ponto Cego | 1 | Ataque | Causa 3 de dano por carta jogada antes desta neste turno (limite 5). |
| Estocada | Finta | 1 | Defesa | Ganha 4 de Defesa, +2 por carta jogada antes desta neste turno (limite 3). |
| Estocada | Golpe de Vista | 2 | Poder | Sempre que jogar a 4a carta do turno, causa 6 de dano ao alvo. |
| Estocada | Rasteira | 1 | Utilidade | Aplica Fragilidade 2. Se ja jogou 3 cartas neste turno, compra 1 carta. |
| Estocada | Dentada Rapida | 1 | Ataque | Causa 6 de dano. Se ja jogou 2 cartas neste turno, causa 4 a mais. |
| Fumaca | Bote da Nevoa | 1 | Ataque | Causa 5 de dano. Se tem Evasao, causa 5 a mais. |
| Fumaca | Banho de Lama | 1 | Defesa | Ganha 1 de Evasao, ou 2 se ja jogou 3 cartas neste turno. |
| Fumaca | Rastro de Lama | 1 | Poder | Sempre que a Evasao anular um ataque, compra 1 carta. |
| Fumaca | Truque de Fumaca | 1 | Utilidade | Compra 1 carta. Se tem Evasao, ganha 1 Acao. |
| Fumaca | Cortina de Lama | 2 | Defesa | Ganha 1 de Evasao. Aplica Fraqueza 2 a todos os inimigos. |
| Contrabando | Golpe Baixo | 1 | Ataque | Causa 5 de dano. A proxima carta jogada neste turno custa 0. |
| Contrabando | Troca Rapida | 1 | Defesa | Ganha 4 de Defesa. Descarta a mao e compra o mesmo numero de cartas. |
| Contrabando | Bolso Fundo | 1 | Poder | No fim do seu turno, guarda 1 carta aleatoria da mao em vez de descarta-la. |
| Contrabando | Pega de Volta | 1 | Utilidade | Devolve a mao a ultima carta jogada neste turno (nao alcanca carta de custo 0). |
| Contrabando | Baralho Marcado | 1 | Utilidade | Compra 1 carta. A proxima carta jogada neste turno custa 0. |
