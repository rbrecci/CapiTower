# 01. Game design

> Números marcados como `[ajustar]` são pontos de partida para playtest, não valores finais.

## 1. Loop principal

```
Menu -> escolher classe -> sortear 5 cartas iniciais (1 re-roll) -> entrar na torre
  -> [ andar: encontro sorteado -> resolver -> proximo andar ] x50
     -> a cada elite e chefe: escolher recompensa (carta nova OU +1 nivel de habilidade)
  -> andar 51: Soberana Gertrudes
  -> vitoria ou derrota -> converter progresso em meta -> desbloqueios -> nova run
```

## 2. Combate

### 2.1 Recurso: Ação

O recurso de turno se chama **Ação**. O jogador começa com **3 Ação** por turno `[ajustar]`, e o
valor reseta no início de cada turno (não acumula). O custo das cartas fica na faixa de 0 a 3.

### 2.2 Estrutura do turno

1. **Início do turno do jogador**: Bloco restante zera, efeitos de duração caem 1, compra até a mão.
2. **Fase de ações**: joga cartas gastando Ação, em qualquer ordem, até acabar a Ação ou passar.
3. **Fim do turno**: cartas restantes na mão vão para o descarte.
4. **Turno inimigo**: cada inimigo executa a intenção que estava telegrafada.
5. Volta ao passo 1.

Quando o deck de compra esvazia, o descarte é embaralhado e vira o novo deck.

### 2.3 Mão e compra

- Mão padrão: **5 cartas** `[ajustar]`.
- Sem limite de mão além do que a compra entrega.
- Cartas jogadas vão para o descarte, salvo texto em contrário.

O deck começa com 10 cartas justamente para que a mão de 5 nunca compre o deck inteiro (ver 4.1).
No pior caso, o jogador vê metade do deck por turno, o que preserva sorte de compra e decisão de
sequenciamento desde o andar 1.

### 2.4 Inimigos por sala

Definido por tipo de sala:

| Tipo | Formato |
| --- | --- |
| Combate comum | 1 a 3 inimigos, todos alvejáveis |
| Elite | 1 inimigo forte, às vezes com apoios alvejáveis que buffam ou atrapalham |
| Chefe | duelo único com múltiplas fases, muda de padrão conforme perde vida |

Todo inimigo telegrafa a intenção do próximo turno (ícone + valor).

### 2.5 Lacaios

Lacaios da classe Capimaga **aparecem em campo como elemento visual e não são alvejáveis**.
Não possuem HP, não recebem dano e não ocupam espaço de alvo. Mecanicamente são contadores
persistentes que disparam efeitos (dano no fim do turno, bloco, gatilhos), representados na
interface como capivaras esqueleto acumulando ao lado do jogador.

Consequência de design: lacaio nunca é removido pelo inimigo por dano, apenas por efeitos que
digam explicitamente "consome" ou "dissipa". Isso deixa a fantasia de exército viável sem
precisar de um sistema de unidades no campo, e evita o problema clássico de o inimigo limpar o
tabuleiro e apagar a build inteira do jogador.

### 2.6 Estados compartilhados

Vocabulário único para as três classes, para manter a leitura previsível:

| Estado | Efeito |
| --- | --- |
| Bloco | Absorve dano. Zera no início do seu turno. |
| Força | +X de dano por ataque. |
| Fragilidade | Alvo recebe +50% de dano `[ajustar]`, dura N turnos. |
| Fraqueza | Alvo causa -25% de dano `[ajustar]`, dura N turnos. |
| Veneno | Perde X de vida no fim do turno, X cai 1 depois. |
| Atordoamento | Pula a próxima intenção. Raro e caro por design. |

Cada classe adiciona no máximo **um** estado exclusivo próprio:

| Estado | Classe | Efeito |
| --- | --- | --- |
| Retaliação | Brutamontes | Todo ataque recebido devolve X de dano ao atacante. |
| Evasão | Ligeira | Anula por completo o próximo ataque, uma instância por ponto. |

A Capimaga não tem estado exclusivo: os lacaios já cumprem esse papel.
Detalhes em `docs/02-classes-e-arquetipos.md`.

## 3. A torre

### 3.1 Estrutura

- 50 andares em linha reta, sem ramificação de rota.
- Divididos em **5 blocos de 10 andares**. O andar 10 de cada bloco é sempre um chefe.
- Andar 51: Soberana Gertrudes, chefão final.
- A **ordem dos encontros dentro de cada bloco é embaralhada** por run, a partir de uma seed
  guardada no banco (permite reproduzir a run em caso de bug).

### 3.2 Composição de um bloco `[ajustar]`

Cada bloco de 10 andares contem:

| Quantidade | Encontro |
| --- | --- |
| 5 | Combate comum |
| 1 | Elite (posição sorteada entre os andares 3 e 8 do bloco) |
| 1 | Evento narrativo com escolha |
| 1 | Descanso |
| 1 | Desafio opcional |
| 1 | Chefe (sempre o último andar do bloco) |

Os 9 primeiros são embaralhados dentro do bloco, o chefe fica fixo na posição 10. Isso garante
ritmo (sempre um descanso e um elite por bloco) sem tornar a ordem previsível.

### 3.3 Tipos de encontro

**Combate comum.** Base do jogo. Sem recompensa de deck, apenas progresso.

**Elite.** Bem mais difícil que o comum. **Dá um ponto de recompensa.**

**Chefe.** Fim de bloco, duelo com fases. **Dá um ponto de recompensa.**

**Evento narrativo.** Texto curto com 2 ou 3 escolhas e consequência imediata (vida, estado
persistente, carta temporária, risco x recompensa). Nunca dá ponto de recompensa.

**Descanso.** Recupera **30% do HP máximo** `[ajustar]`. Única cura confiável do jogo.

**Desafio opcional.** O jogador pode pular sem custo nenhum. Aceitando, enfrenta um combate mais
duro com uma condição extra (limite de turnos, inimigo com buff, começar sem Bloco). Vencendo,
ganha um **modificador de run**: um bônus permanente e pequeno que vale até o fim da run.

São no máximo 5 modificadores por run, um por bloco. Pool inicial `[ajustar]`:

| Modificador | Efeito |
| --- | --- |
| Casco Duro | +1 de Bloco toda vez que ganhar Bloco |
| Músculo Teimoso | +1 de Força permanente |
| Fôlego | +5 de HP máximo, e cura os 5 na hora |
| Largada | +1 Ação no primeiro turno de cada combate |
| Mão Firme | Compra +1 carta no primeiro turno de cada combate |

Regras do pool:
- Todo modificador é **aditivo e de valor fixo**. Nada percentual, nada multiplicativo, porque com
  5 acumulados o efeito composto sai do controle.
- Nenhum modificador pode interagir com a mecânica exclusiva de uma classe só, senão o desafio
  vale mais para uma classe que para as outras e quebra a paridade.
- O jogador escolhe 1 entre 2 sorteados, não recebe aleatório.

### 3.4 Escalada de dificuldade

Por bloco, não continua. Cada bloco tem seu próprio pool de inimigos, com HP e dano próprios.
Isso mantém o balanceamento legível: um inimigo pertence ao bloco 3 e ponto final, sem fórmula de
escala global para depurar depois.

## 4. Deck

### 4.1 Deck inicial

- Ao escolher a classe, o jogo sorteia **5 cartas distintas** entre as 20 da classe (apenas as
  desbloqueadas). O sorteio **nunca repete carta**.
- Cada carta sorteada entra no deck em **2 cópias**. Deck inicial: **10 cartas**.
- O jogador pode **re-roletar 1 das 5**, uma única vez. A troca leva as duas cópias junto, e a
  carta trocada não volta ao sorteio.

O sorteio é a fonte de variedade entre runs. Começar com 3 cartas do mesmo arquetipo significa 6
cópias dele no deck, uma identidade de build forte desde o primeiro combate, e um convite a
especializar. Começar com 5 arquetipos diferentes e um convite a generalizar.

A duplicação existe por dois motivos: garante que a mão de 5 não compre o deck inteiro, e faz o
sorteio inicial pesar de verdade na identidade da run.

### 4.2 Crescimento

10 pontos de recompensa por run (5 elites + 5 chefes). Em cada um, o jogador escolhe **uma** opção:

- **Carta nova**: escolhe 1 entre 3 cartas sorteadas da própria classe (nunca oferece carta que já
  está no deck), e ela entra em **1 cópia**, ou
- **+1 nível de habilidade** da classe.

Deck no fim de uma run completa: **10 iniciais + até 10 de recompensa = 20 cartas**, e menos que
isso se o jogador investir na habilidade.

Sem remoção de carta. Sem upgrade de carta. Sem loja. Sem moeda.

### 4.3 A decisão central

| Estilo | Como se forma | Ganho |
| --- | --- | --- |
| Especialista | Sorteio já entregou 3 ou mais cartas de um arquetipo. Sobra recompensa para a habilidade. | Habilidade em nível alto, combos consistentes, deck previsível. |
| Generalista | Sorteio veio espalhado. Gasta recompensas fechando arquetipos. | Mais respostas para situações diferentes, habilidade fraca. |

Como a habilidade tem **nível máximo 10** e começa no **nível 1**, existem no máximo **9**
aprimoramentos possíveis. Com 10 pontos de recompensa, pelo menos **1 ponto sempre vira carta**.
Não existe build 100% habilidade, e isso é proposital.

## 5. Vida e derrota

- HP inicial: **70** `[ajustar]`, igual para as três classes. A diferença entre classes vem das
  cartas e da habilidade, nunca de vida base.
- HP persiste entre andares. Cura só em descanso e em eventos.
- **Permadeath**: morreu, a run acabou. Não há checkpoint nem ressurreição.
- **Bônus de derrota**: o progresso de meta é proporcional ao andar alcançado, então subir mais
  alto sempre vale a pena mesmo perdendo.

Fórmula inicial de pontos de meta `[ajustar]`:

```
pontos = andar_alcancado + (chefes_derrotados * 10) + bonus_vitoria
bonus_vitoria = 50 se venceu, 0 se nao
```

## 6. Meta progressão

### 6.1 O que persiste entre runs

- Personagens desbloqueados (começa com 1).
- Cartas desbloqueadas por classe (começa com um subconjunto, ver 6.2).
- Habilidades alternativas de classe (fase pós MVP).
- Objetivos cumpridos, estatísticas e recordes.

### 6.2 Pool inicial

O jogador não começa com as 20 cartas de uma classe disponíveis no sorteio. Começa com um pool
reduzido `[ajustar: 10 cartas, 2 ou 3 de cada arquetipo]` e desbloqueia o resto cumprindo
objetivos. Isso serve a dois propósitos: reduz a carga cognitiva do primeiro contato e da função
real ao sistema de conquistas.

### 6.3 Desbloqueios

Todo desbloqueio vem de **objetivo nomeado**, nunca de acúmulo passivo de moeda ou XP. Exemplos:

| Objetivo | Recompensa |
| --- | --- |
| Alcançar o andar 20 | Carta do arquetipo X |
| Vencer um chefe sem tomar dano | Carta do arquetipo Y |
| Terminar uma run com um arquetipo completo | Nova carta |
| Vencer a torre pela primeira vez | Segunda classe |
| Vencer com a habilidade no nível 10 | Terceira classe |

Os pontos de meta acumulados servem como estatística e como critério de alguns objetivos, nunca
como moeda gasta em loja.
