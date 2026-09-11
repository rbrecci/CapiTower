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

## 3. Classe 1: Capivárias (definida)

**Status: conceito aprovado, cartas a detalhar.**

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
variacoes de Capivárias.

| Classe | Onde mora o poder | Quando o poder aparece | Ritmo |
| --- | --- | --- | --- |
| Capivárias | No campo (lacaios) | Cresce ao longo do combate | Fraca cedo, vence por atrito |
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
| Engenhoca (estruturas que disparam depois) | Mora no mesmo vertice de Capivárias (campo, recurso persistente). Viraria lacaio com outro nome. |
| Bardo (manipular a intencao inimiga) | Interessante, mas exige que todo inimigo do jogo seja desenhado pensando nisso. Custo de conteudo alto demais. |

## 5. Classe 2: Brutamontes

**Status: conceito aprovado, cartas a detalhar.**

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

| # | Arquetipo | Papel | Como usa Adrenalina | Carta exemplo |
| --- | --- | --- | --- | --- |
| 1 | **Suor** | Acumulo | Gera Adrenalina de proposito, inclusive pagando vida por ela | Bufo (0): perde 3 de vida, ganha 2 de Adrenalina, compra 1 carta |
| 2 | **Estouro** | Gasto explosivo | Consome Adrenalina num golpe unico que escala com ela | Cabecada Final (2): consome ate 6 de Adrenalina, causa 8 mais 3 por ponto consumido |
| 3 | **Couro** | Defensivo | Converte Adrenalina em Bloco e mitigacao | Costado (1): ganha 5 de Bloco, mais 1 por Adrenalina acumulada (limite 8) |
| 4 | **Troco** | Alternativo | Retaliacao. Ganha por ser atingida, nao por atacar | Nao Faz Isso (1): ganha Retaliacao 4 por 2 turnos |

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

**Status: conceito aprovado, cartas a detalhar.**

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

| # | Arquetipo | Papel | Como usa Impulso | Carta exemplo |
| --- | --- | --- | --- | --- |
| 1 | **Corrente** | Acumulo | Cartas de custo 0 e compra, para esticar o turno | Passo Curto (0): causa 3 de dano, compra 1 carta |
| 2 | **Estocada** | Gasto explosivo | Finalizadores que escalam com o Impulso ja acumulado | Ponto Cego (1): causa 4 de dano por carta jogada antes desta neste turno (limite 5 cartas) |
| 3 | **Fumaca** | Defensivo | Evasao e negacao de golpe | Banho de Lama (1): ganha 1 de Evasao, ou 2 se ja jogou 2 cartas neste turno |
| 4 | **Contrabando** | Alternativo | Mexe no descarte e na ordem de compra, da consistencia | Pega de Volta (1): devolve a mao a ultima carta jogada neste turno (nao alcanca carta de custo 0) |

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
| Classe | Capivárias |
| Arquetipo | Enxame |
| Custo | 1 Acao |
| Tipo | Ataque, Defesa, Poder ou Utilidade |
| Texto | Causa 6 de dano. Invoca 1 lacaio. |
| Efeitos | lista estruturada, ver `docs/05-banco-de-dados.md` |
| Arte | caminho do placeholder |

Cartas de **Poder** ficam em campo pelo resto do combate e nao voltam ao deck.
