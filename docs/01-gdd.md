# 01. Game design

> Numeros marcados como `[ajustar]` sao pontos de partida para playtest, nao valores finais.

## 1. Loop principal

```
Menu -> escolher classe -> sortear 5 cartas iniciais (1 re-roll) -> entrar na torre
  -> [ andar: encontro sorteado -> resolver -> proximo andar ] x50
     -> a cada elite e chefe: escolher recompensa (carta nova OU +1 nivel de habilidade)
  -> andar 51: Soberana Gertrudes
  -> vitoria ou derrota -> converter progresso em meta -> desbloqueios -> nova run
```

## 2. Combate

### 2.1 Recurso: Acao

O recurso de turno se chama **Acao**. O jogador comeca com **3 Acao** por turno `[ajustar]`, e o
valor reseta no inicio de cada turno (nao acumula). O custo das cartas fica na faixa de 0 a 3.

### 2.2 Estrutura do turno

1. **Inicio do turno do jogador**: Bloco restante zera, efeitos de duracao caem 1, compra ate a mao.
2. **Fase de acoes**: joga cartas gastando Acao, em qualquer ordem, ate acabar a Acao ou passar.
3. **Fim do turno**: cartas restantes na mao vao para o descarte.
4. **Turno inimigo**: cada inimigo executa a intencao que estava telegrafada.
5. Volta ao passo 1.

Quando o deck de compra esvazia, o descarte e embaralhado e vira o novo deck.

### 2.3 Mao e compra

- Mao padrao: **5 cartas** `[ajustar]`.
- Sem limite de mao alem do que a compra entrega.
- Cartas jogadas vao para o descarte, salvo texto em contrario.

O deck comeca com 10 cartas justamente para que a mao de 5 nunca compre o deck inteiro (ver 4.1).
No pior caso, o jogador ve metade do deck por turno, o que preserva sorte de compra e decisao de
sequenciamento desde o andar 1.

### 2.4 Inimigos por sala

Definido por tipo de sala:

| Tipo | Formato |
| --- | --- |
| Combate comum | 1 a 3 inimigos, todos alvejaveis |
| Elite | 1 inimigo forte, as vezes com apoios alvejaveis que buffam ou atrapalham |
| Chefe | duelo unico com multiplas fases, muda de padrao conforme perde vida |

Todo inimigo telegrafa a intencao do proximo turno (icone + valor).

### 2.5 Lacaios

Lacaios da classe Capivárias **aparecem em campo como elemento visual e nao sao alvejaveis**.
Nao possuem HP, nao recebem dano e nao ocupam espaco de alvo. Mecanicamente sao contadores
persistentes que disparam efeitos (dano no fim do turno, bloco, gatilhos), representados na
interface como capivaras esqueleto acumulando ao lado do jogador.

Consequencia de design: lacaio nunca e removido pelo inimigo por dano, apenas por efeitos que
digam explicitamente "consome" ou "dissipa". Isso deixa a fantasia de exercito viavel sem
precisar de um sistema de unidades no campo, e evita o problema classico de o inimigo limpar o
tabuleiro e apagar a build inteira do jogador.

### 2.6 Estados compartilhados

Vocabulario unico para as tres classes, para manter a leitura previsivel:

| Estado | Efeito |
| --- | --- |
| Bloco | Absorve dano. Zera no inicio do seu turno. |
| Forca | +X de dano por ataque. |
| Fragilidade | Alvo recebe +50% de dano `[ajustar]`, dura N turnos. |
| Fraqueza | Alvo causa -25% de dano `[ajustar]`, dura N turnos. |
| Veneno | Perde X de vida no fim do turno, X cai 1 depois. |
| Atordoamento | Pula a proxima intencao. Raro e caro por design. |

Cada classe adiciona no maximo **um** estado exclusivo proprio:

| Estado | Classe | Efeito |
| --- | --- | --- |
| Retaliacao | Brutamontes | Todo ataque recebido devolve X de dano ao atacante. |
| Evasao | Ligeira | Anula por completo o proximo ataque, uma instancia por ponto. |

Capivárias nao tem estado exclusivo: os lacaios ja cumprem esse papel.
Detalhes em `docs/02-classes-e-arquetipos.md`.

## 3. A torre

### 3.1 Estrutura

- 50 andares em linha reta, sem ramificacao de rota.
- Divididos em **5 blocos de 10 andares**. O andar 10 de cada bloco e sempre um chefe.
- Andar 51: Soberana Gertrudes, chefao final.
- A **ordem dos encontros dentro de cada bloco e embaralhada** por run, a partir de uma seed
  guardada no banco (permite reproduzir a run em caso de bug).

### 3.2 Composicao de um bloco `[ajustar]`

Cada bloco de 10 andares contem:

| Quantidade | Encontro |
| --- | --- |
| 5 | Combate comum |
| 1 | Elite (posicao sorteada entre os andares 3 e 8 do bloco) |
| 1 | Evento narrativo com escolha |
| 1 | Descanso |
| 1 | Desafio opcional |
| 1 | Chefe (sempre o ultimo andar do bloco) |

Os 9 primeiros sao embaralhados dentro do bloco, o chefe fica fixo na posicao 10. Isso garante
ritmo (sempre um descanso e um elite por bloco) sem tornar a ordem previsivel.

### 3.3 Tipos de encontro

**Combate comum.** Base do jogo. Sem recompensa de deck, apenas progresso.

**Elite.** Bem mais dificil que o comum. **Da um ponto de recompensa.**

**Chefe.** Fim de bloco, duelo com fases. **Da um ponto de recompensa.**

**Evento narrativo.** Texto curto com 2 ou 3 escolhas e consequencia imediata (vida, estado
persistente, carta temporaria, risco x recompensa). Nunca da ponto de recompensa.

**Descanso.** Recupera **30% do HP maximo** `[ajustar]`. Unica cura confiavel do jogo.

**Desafio opcional.** O jogador pode pular sem custo nenhum. Aceitando, enfrenta um combate mais
duro com uma condicao extra (limite de turnos, inimigo com buff, comecar sem Bloco). Vencendo,
ganha um **modificador de run**: um bonus permanente e pequeno que vale ate o fim da run.

Sao no maximo 5 modificadores por run, um por bloco. Pool inicial `[ajustar]`:

| Modificador | Efeito |
| --- | --- |
| Casco Duro | +1 de Bloco toda vez que ganhar Bloco |
| Musculo Teimoso | +1 de Forca permanente |
| Folego | +5 de HP maximo, e cura os 5 na hora |
| Largada | +1 Acao no primeiro turno de cada combate |
| Mao Firme | Compra +1 carta no primeiro turno de cada combate |

Regras do pool:
- Todo modificador e **aditivo e de valor fixo**. Nada percentual, nada multiplicativo, porque com
  5 acumulados o efeito composto sai do controle.
- Nenhum modificador pode interagir com a mecanica exclusiva de uma classe so, senao o desafio
  vale mais para uma classe que para as outras e quebra a paridade.
- O jogador escolhe 1 entre 2 sorteados, nao recebe aleatorio.

### 3.4 Escalada de dificuldade

Por bloco, nao continua. Cada bloco tem seu proprio pool de inimigos, com HP e dano proprios.
Isso mantem o balanceamento legivel: um inimigo pertence ao bloco 3 e ponto final, sem formula de
escala global para depurar depois.

## 4. Deck

### 4.1 Deck inicial

- Ao escolher a classe, o jogo sorteia **5 cartas distintas** entre as 20 da classe (apenas as
  desbloqueadas). O sorteio **nunca repete carta**.
- Cada carta sorteada entra no deck em **2 copias**. Deck inicial: **10 cartas**.
- O jogador pode **re-roletar 1 das 5**, uma unica vez. A troca leva as duas copias junto, e a
  carta trocada nao volta ao sorteio.

O sorteio e a fonte de variedade entre runs. Comecar com 3 cartas do mesmo arquetipo significa 6
copias dele no deck, uma identidade de build forte desde o primeiro combate, e um convite a
especializar. Comecar com 5 arquetipos diferentes e um convite a generalizar.

A duplicacao existe por dois motivos: garante que a mao de 5 nao compre o deck inteiro, e faz o
sorteio inicial pesar de verdade na identidade da run.

### 4.2 Crescimento

10 pontos de recompensa por run (5 elites + 5 chefes). Em cada um, o jogador escolhe **uma** opcao:

- **Carta nova**: escolhe 1 entre 3 cartas sorteadas da propria classe (nunca oferece carta que ja
  esta no deck), e ela entra em **1 copia**, ou
- **+1 nivel de habilidade** da classe.

Deck no fim de uma run completa: **10 iniciais + ate 10 de recompensa = 20 cartas**, e menos que
isso se o jogador investir na habilidade.

Sem remocao de carta. Sem upgrade de carta. Sem loja. Sem moeda.

### 4.3 A decisao central

| Estilo | Como se forma | Ganho |
| --- | --- | --- |
| Especialista | Sorteio ja entregou 3 ou mais cartas de um arquetipo. Sobra recompensa para a habilidade. | Habilidade em nivel alto, combos consistentes, deck previsivel. |
| Generalista | Sorteio veio espalhado. Gasta recompensas fechando arquetipos. | Mais respostas para situacoes diferentes, habilidade fraca. |

Como a habilidade tem **nivel maximo 10** e comeca no **nivel 1**, existem no maximo **9**
aprimoramentos possiveis. Com 10 pontos de recompensa, pelo menos **1 ponto sempre vira carta**.
Nao existe build 100% habilidade, e isso e proposital.

## 5. Vida e derrota

- HP inicial: **70** `[ajustar]`, igual para as tres classes. A diferenca entre classes vem das
  cartas e da habilidade, nunca de vida base.
- HP persiste entre andares. Cura so em descanso e em eventos.
- **Permadeath**: morreu, a run acabou. Nao ha checkpoint nem ressurreicao.
- **Bonus de derrota**: o progresso de meta e proporcional ao andar alcancado, entao subir mais
  alto sempre vale a pena mesmo perdendo.

Formula inicial de pontos de meta `[ajustar]`:

```
pontos = andar_alcancado + (chefes_derrotados * 10) + bonus_vitoria
bonus_vitoria = 50 se venceu, 0 se nao
```

## 6. Meta progressao

### 6.1 O que persiste entre runs

- Personagens desbloqueados (comeca com 1).
- Cartas desbloqueadas por classe (comeca com um subconjunto, ver 6.2).
- Habilidades alternativas de classe (fase pos MVP).
- Objetivos cumpridos, estatisticas e recordes.

### 6.2 Pool inicial

O jogador nao comeca com as 20 cartas de uma classe disponiveis no sorteio. Comeca com um pool
reduzido `[ajustar: 10 cartas, 2 ou 3 de cada arquetipo]` e desbloqueia o resto cumprindo
objetivos. Isso serve a dois propositos: reduz a carga cognitiva do primeiro contato e da funcao
real ao sistema de conquistas.

### 6.3 Desbloqueios

Todo desbloqueio vem de **objetivo nomeado**, nunca de acumulo passivo de moeda ou XP. Exemplos:

| Objetivo | Recompensa |
| --- | --- |
| Alcancar o andar 20 | Carta do arquetipo X |
| Vencer um chefe sem tomar dano | Carta do arquetipo Y |
| Terminar uma run com um arquetipo completo | Nova carta |
| Vencer a torre pela primeira vez | Segunda classe |
| Vencer com a habilidade no nivel 10 | Terceira classe |

Os pontos de meta acumulados servem como estatistica e como criterio de alguns objetivos, nunca
como moeda gasta em loja.
