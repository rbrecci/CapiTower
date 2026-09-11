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

## 2. Questoes em aberto

Ordenadas por impacto. Q3 trava o design do MVP, o resto pode esperar.
Q1, Q2 e Q6 ja foram resolvidas e ficam registradas abaixo com o historico do raciocinio.

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

### Q3. De onde vem os 10 pontos de recompensa

**Problema.** O desenho pedia 10 recompensas e um chefe a cada 10 andares. Sao 5 chefes mais o
chefao, o que da 5 ou 6 pontos, nao 10.

**Opcoes.**

| Opcao | Efeito |
| --- | --- |
| **A. Elite tambem da ponto** | 5 chefes + 5 elites = 10. Um elite garantido por bloco. |
| **B. Chefe da 2 pontos** | 5 chefes x 2 = 10. Menos momentos de decisao, cada um mais pesado. |
| **C. Recompensa a cada 5 andares** | Andares 5, 10, 15... 50 = 10 pontos, independente do tipo de sala. Regular, mas desconecta a recompensa do desafio. |

**Recomendacao: A.** Ja esta escrita no GDD. Amarra recompensa a dificuldade, distribui as
decisoes ao longo do bloco e da funcao ao elite, que senao seria so um combate mais duro sem
motivo para existir.

---

### Q2. Carta repetida no sorteio inicial (RESOLVIDA, ver D19)

O sorteio das 5 iniciais pode entregar a mesma carta duas vezes?

**Decidido: nao pode.** As 5 sao sempre distintas. Como D18 ja entrega 2 copias de cada, permitir
repeticao criaria decks iniciais com 4 copias da mesma carta, o que estreita demais a run logo na
largada e piora a leitura da tela de sorteio.

---

### Q4. Recompensa do desafio opcional

Nao pode dar ponto de recompensa (quebraria a conta de 10) e nao pode dar moeda (nao existe).
Candidatos: cura grande, carta temporaria ate o proximo chefe, modificador permanente da run
(tipo +1 Forca), ou escolher uma das 3 cartas que apareceriam na proxima recompensa.

**Recomendacao: modificador permanente pequeno da run.** Nao infla o deck, nao mexe na economia
de recompensa e da uma segunda dimensao de crescimento para quem gosta de arriscar.

---

### Q5. Quem e o jogador

O jogador tambem e uma capivara (do ramo que nao caiu no poco) ou e outra coisa que sobe a torre?
Isso decide se o bestiario de personagens jogaveis e capivara ou nao, e afeta as classes 2 e 3.

**Recomendacao: tambem capivara.** Economiza direcao de arte, explica a capivara necromante e da
uma piada estrutural de graca (a familia que ficou de fora da bonanca).

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

### Q7. Lacaios persistem entre combates?

Zerar ao fim do combate e o padrao seguro. Persistir cria uma fantasia forte (o exercito cresce
andar apos andar) mas exige teto rigido, senao o bloco 5 vira passeio. O nivel 9 da habilidade
Legiao ja flerta com isso ao carregar metade dos lacaios.

**Recomendacao: zera por padrao, e persistir vira privilegio da habilidade em nivel alto.**

---

### Q8. Nome do projeto

A pasta local se chama `BrecciTower` e o repositorio se chama `CapiTower`. A documentacao adotou
**CapiTower**, que combina com o tema. Vale renomear a pasta local para evitar confusao.
