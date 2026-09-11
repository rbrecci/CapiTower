# 07. Decisoes e pontos em aberto

## 1. Decisoes fechadas

Registradas na entrevista de design de 10/09/2026.

| # | Tema | Decisao |
| --- | --- | --- |
| D01 | Recurso de turno | Energia por turno, chamada **Acao**. Reseta a cada turno. |
| D02 | Formato da torre | Linear, 50 andares, ordem dos tipos de encontro embaralhada por run. |
| D03 | Backend | Conta e save da run, meta progressao e catalogo de conteudo no MySQL. |
| D04 | Validacao | Sem validacao autoritativa. Combate roda no cliente. |
| D05 | Upgrade | Cartas nao evoluem. So a habilidade de classe sobe de nivel. |
| D06 | Deck | Enxuto. Sem remocao, sem upgrade, sem lixo. Tamanho final definido em D18. |
| D07 | Vida | HP persiste entre andares, cura escassa (so descanso e evento). |
| D08 | Encontros | Combate comum, elite, evento narrativo, descanso, desafio opcional. |
| D09 | Economia | **Nao existe moeda.** Sem loja, sem ouro, sem tesouro. Recompensa e sempre direta. |
| D10 | Inimigos | Varia por sala: grupo em combate comum, duelo com fases em elite e chefe. |
| D11 | Lacaios | Aparecem em campo, mas **nao sao alvejaveis**. Sao contadores, nao unidades. |
| D12 | Derrota | Permadeath, com bonus de meta proporcional ao andar alcancado. |
| D13 | Desbloqueio | Por objetivos e conquistas nomeadas. Sem XP passivo, sem moeda de meta. |
| D14 | Classe 1 | Conjuradora (necromante), com os 4 arquetipos girando em torno dos lacaios. |
| D15 | Arte | Placeholder agora, arte gerada por IA depois. |
| D16 | Ambiente | XAMPP para desenvolver, InfinityFree para hospedar. Sem build, sem Node, sem Composer. |
| D17 | Tema | Fantasia com humor. Capivaras de esteroide, Soberana Gertrudes no topo. |
| D18 | Deck inicial | Cada uma das 5 cartas sorteadas entra em **2 copias**. Deck comeca com 10 e termina com ate 20. Resolve Q1. |
| D19 | Sorteio inicial | As 5 cartas sorteadas sao **sempre distintas**. Resolve Q2. |
| D20 | Tipos de encontro | Fechado em 6: combate comum, elite, evento, descanso, desafio opcional e chefe. Nao havera um setimo. Resolve Q6. |
| D21 | Pontos de recompensa | 10 por run: **5 elites + 5 chefes**. O chefao do andar 51 nao da ponto. Resolve Q3. |
| D22 | Personagem jogavel | O jogador tambem e uma capivara. Lore detalhada fica para depois das mecanicas. Resolve Q5. |
| D23 | Lacaios entre combates | **Nao persistem.** Zeram ao fim de todo combate, sem excecao nem privilegio de habilidade. Resolve Q7. |
| D24 | Nome | O projeto se chama **CapiTower**, pasta local e repositorio. Resolve Q8. |
| D25 | Desafio opcional | Fica. Vencer da um **modificador de run** permanente e pequeno, escolhido entre 2 sorteados. Maximo de 5 por run. Resolve Q4. |

## 2. Questoes em aberto

**Todas resolvidas.** Ficam registradas abaixo com o historico do raciocinio que levou a cada
decisao, para nao refazer a mesma discussao daqui a tres meses.

---

### Q1. Deck de 5 cartas com mao de 5 elimina a variancia inicial (RESOLVIDA, ver D18)

**Problema.** No andar 1 o deck tem 5 cartas e a mao compra 5. O jogador compra o deck inteiro
todo turno, sempre. Nao existe sorte de compra, nao existe decisao de sequenciamento, e isso dura
ate a primeira recompensa. Com o modelo de 10 recompensas, o deck so chega a 10 cartas na metade
da torre.

**Opcoes.**

| Opcao | Efeito |
| --- | --- |
| **A. Duas copias de cada carta inicial** | Deck comeca com 10 (5 cartas x 2 copias), termina com 20. Variancia desde o andar 1, e a build inicial fica mais consistente porque a carta sorteada aparece mais. |
| **B. Mao menor** | Compra 3 por turno em vez de 5. Mantem o deck de 15, mas deixa o combate mais lento e reduz o teto de combo. |
| **C. Aceitar** | Os 10 primeiros andares sao deterministicos e funcionam como tutorial. Barato, mas 10 andares e muito tempo sem variancia. |
| **D. Cartas basicas neutras** | Deck comeca com as 5 sorteadas mais 5 cartas basicas genericas. Resolve a variancia, mas contraria o pilar de nao ter carta de lixo no deck. |

**Decidido: A.** E a unica que resolve o problema sem ferir nenhum pilar. Deck final de 20
continua enxuto para o genero, e duplicar as cartas iniciais reforca exatamente a intencao do
desenho: comecar com 3 cartas de um arquetipo passa a significar 6 copias, uma identidade de build
forte desde o primeiro combate.

Consequencia a vigiar no playtest: com 2 copias de cada inicial, combos de duas cartas ficam bem
mais faceis de montar no comeco da run. Se algum par sair forte demais no bloco 1, o ajuste e no
numero da carta, nao na regra de duplicacao.

---

### Q3. De onde vem os 10 pontos de recompensa (RESOLVIDA, ver D21)

**Problema.** O desenho pedia 10 recompensas e um chefe a cada 10 andares. Sao 5 chefes mais o
chefao, o que da 5 ou 6 pontos, nao 10.

**Opcoes.**

| Opcao | Efeito |
| --- | --- |
| **A. Elite tambem da ponto** | 5 chefes + 5 elites = 10. Um elite garantido por bloco. |
| **B. Chefe da 2 pontos** | 5 chefes x 2 = 10. Menos momentos de decisao, cada um mais pesado. |
| **C. Recompensa a cada 5 andares** | Andares 5, 10, 15... 50 = 10 pontos, independente do tipo de sala. Regular, mas desconecta a recompensa do desafio. |

**Decidido: A.** Amarra recompensa a dificuldade, distribui as decisoes ao longo do bloco e da
funcao ao elite, que senao seria so um combate mais duro sem motivo para existir.

---

### Q2. Carta repetida no sorteio inicial (RESOLVIDA, ver D19)

O sorteio das 5 iniciais pode entregar a mesma carta duas vezes?

**Decidido: nao pode.** As 5 sao sempre distintas. Como D18 ja entrega 2 copias de cada, permitir
repeticao criaria decks iniciais com 4 copias da mesma carta, o que estreita demais a run logo na
largada e piora a leitura da tela de sorteio.

---

### Q4. Recompensa do desafio opcional (RESOLVIDA, ver D25)

Nao podia dar ponto de recompensa (quebraria a conta de 10) nem moeda (nao existe).

**Decidido: modificador de run.** Bonus permanente e pequeno que vale ate o fim da run, escolhido
entre 2 sorteados, no maximo 5 por run. Nao infla o deck, nao mexe na economia de recompensa e da
uma segunda dimensao de crescimento para quem gosta de arriscar.

Restricoes que vieram junto, detalhadas em `01-gdd.md` secao 3.3: modificadores sao sempre
aditivos e de valor fixo, e nenhum deles pode tocar na mecanica exclusiva de uma unica classe.
Sem isso, o desafio opcional viraria uma sala que vale mais para a Conjuradora que para as
outras duas, e a paridade entre classes iria junto.

---

### Q5. Quem e o jogador (RESOLVIDA, ver D22)

**Decidido: tambem capivara.** O resto (por que sobe, qual o vinculo com a familia da Soberana,
historia de cada classe) entra numa passada de lore dedicada, depois que as mecanicas fecharem.
Nada no design mecanico depende dessa historia.

---

### Q6. O sexto tipo de encontro (RESOLVIDA, ver D20)

Na entrevista foi marcado um tipo de encontro adicional que nao chegou a ser nomeado.

**Decidido: nao havera.** Os seis tipos atuais (combate, elite, evento, descanso, desafio e chefe)
ja preenchem os 10 andares de cada bloco e cobrem o ritmo pretendido. Candidatos avaliados e
descartados: sala de troca de carta, altar de arquetipo, emboscada e pedagio.

Fica registrado o buraco que esses candidatos preencheriam, caso o playtest mostre que ele
incomoda: **nada fora das recompensas mexe no deck**, entao quem recebe um sorteio inicial ruim
nao tem ferramenta para corrigir o rumo antes do primeiro elite.

---

### Q7. Lacaios persistem entre combates? (RESOLVIDA, ver D23)

**Decidido: nao persistem.** Zeram ao fim de todo combate, sem excecao. Persistir criaria bola de
neve entre andares e exigiria um teto artificial para o bloco 5 nao virar passeio.

Consequencia: o nivel 9 da habilidade Legiao, que carregava metade dos lacaios para o combate
seguinte, foi substituido por uma rede de seguranca dentro do combate (uma vez por combate, ao
ficar sem lacaios, invoca 2). Isso serve principalmente ao arquetipo Sacrificio, que fica exposto
logo depois de gastar tudo.

---

### Q8. Nome do projeto (RESOLVIDA, ver D24)

**Decidido: CapiTower.** A pasta local foi renomeada de `BrecciTower` para `CapiTower`, ficando
igual ao repositorio e a documentacao.
