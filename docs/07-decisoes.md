# 07. Decisões e pontos em aberto

## 1. Decisões fechadas

Registradas na entrevista de design de 10/09/2026.

| # | Tema | Decisão |
| --- | --- | --- |
| D01 | Recurso de turno | Energia por turno, chamada **Ação**. Reseta a cada turno. |
| D02 | Formato da torre | Linear, 50 andares, ordem dos tipos de encontro embaralhada por run. |
| D03 | Backend | Conta e save da run, meta progressão e catálogo de conteúdo no MySQL. |
| D04 | Validação | Sem validação autoritativa. Combate roda no cliente. |
| D05 | Upgrade | Cartas não evoluem. Só a habilidade de classe sobe de nível. |
| D06 | Deck | Enxuto. Sem remoção, sem upgrade, sem lixo. Tamanho final definido em D18. |
| D07 | Vida | HP persiste entre andares, cura escassa (só descanso e evento). |
| D08 | Encontros | Combate comum, elite, evento narrativo, descanso, desafio opcional. |
| D09 | Economia | **Não existe moeda.** Sem loja, sem ouro, sem tesouro. Recompensa é sempre direta. |
| D10 | Inimigos | Varia por sala: grupo em combate comum, duelo com fases em elite e chefe. |
| D11 | Lacaios | Aparecem em campo, mas **não são alvejáveis**. São contadores, não unidades. |
| D12 | Derrota | Permadeath, com bônus de meta proporcional ao andar alcançado. |
| D13 | Desbloqueio | Por objetivos e conquistas nomeadas. Sem XP passivo, sem moeda de meta. |
| D14 | Classe 1 | Capimaga (conjuradora necromante), com os 4 arquétipos girando em torno dos lacaios. |
| D15 | Arte | Placeholder agora, arte gerada por IA depois. |
| D16 | Ambiente | XAMPP para desenvolver, InfinityFree para hospedar. Sem build, sem Node, sem Composer. |
| D17 | Tema | Fantasia com humor. Capivaras de esteroide, Soberana Gertrudes no topo. |
| D18 | Deck inicial | Cada uma das 5 cartas sorteadas entra em **2 cópias**. Deck começa com 10 e termina com até 20. Resolve Q1. |
| D19 | Sorteio inicial | As 5 cartas sorteadas são **sempre distintas**. Resolve Q2. |
| D20 | Tipos de encontro | Fechado em 6: combate comum, elite, evento, descanso, desafio opcional e chefe. Não haverá um sétimo. Resolve Q6. |
| D21 | Pontos de recompensa | 10 por run: **5 elites + 5 chefes**. O chefão do andar 51 não dá ponto. Resolve Q3. |
| D22 | Personagem jogável | O jogador também é uma capivara. Lore detalhada fica para depois das mecânicas. Resolve Q5. |
| D23 | Lacaios entre combates | **Não persistem.** Zeram ao fim de todo combate, sem exceção nem privilégio de habilidade. Resolve Q7. |
| D24 | Nome | O projeto se chama **CapiTower**, pasta local e repositório. Resolve Q8. |
| D25 | Desafio opcional | Fica. Vencer dá um **modificador de run** permanente e pequeno, escolhido entre 2 sorteados. Máximo de 5 por run. Resolve Q4. |
| D26 | Nomes das classes | **Capimaga** (conjuradora), **Brutamontes** (Adrenalina) e **Ligeira** (Impulso). A classe 1 foi Conjuradora e Capivarias antes de fechar em Capimaga. |
| D27 | Classes 2 e 3 | Conceitos aprovados: Brutamontes e Ligeira, com mecânica, habilidade, estado exclusivo e 4 arquétipos cada. |
| D28 | Composição de arquétipo | Arquétipo é um **nicho** dentro do jeito de jogar da classe, não uma função no deck. Cada um tem 5 cartas com pelo menos 1 Ataque, 1 Defesa, 1 Poder e 1 Utilidade. Resolve Q9. |

## 2. Questões em aberto

**Todas resolvidas.** Ficam registradas abaixo com o histórico do raciocínio que levou a cada
decisão, para não refazer a mesma discussão daqui a três meses.

---

### Q1. Deck de 5 cartas com mão de 5 elimina a variância inicial (RESOLVIDA, ver D18)

**Problema.** No andar 1 o deck tem 5 cartas e a mão compra 5. O jogador compra o deck inteiro
todo turno, sempre. Não existe sorte de compra, não existe decisão de sequenciamento, e isso dura
até a primeira recompensa. Com o modelo de 10 recompensas, o deck só chega a 10 cartas na metade
da torre.

**Opções.**

| Opção | Efeito |
| --- | --- |
| **A. Duas cópias de cada carta inicial** | Deck começa com 10 (5 cartas x 2 cópias), termina com 20. Variância desde o andar 1, e a build inicial fica mais consistente porque a carta sorteada aparece mais. |
| **B. Mão menor** | Compra 3 por turno em vez de 5. Mantém o deck de 15, mas deixa o combate mais lento e reduz o teto de combo. |
| **C. Aceitar** | Os 10 primeiros andares são determinísticos e funcionam como tutorial. Barato, mas 10 andares é muito tempo sem variância. |
| **D. Cartas básicas neutras** | Deck começa com as 5 sorteadas mais 5 cartas básicas genéricas. Resolve a variância, mas contraria o pilar de não ter carta de lixo no deck. |

**Decidido: A.** É a única que resolve o problema sem ferir nenhum pilar. Deck final de 20
continua enxuto para o gênero, e duplicar as cartas iniciais reforça exatamente a intenção do
desenho: começar com 3 cartas de um arquétipo passa a significar 6 cópias, uma identidade de build
forte desde o primeiro combate.

Consequência a vigiar no playtest: com 2 cópias de cada inicial, combos de duas cartas ficam bem
mais fáceis de montar no começo da run. Se algum par sair forte demais no bloco 1, o ajuste é no
número da carta, não na regra de duplicação.

---

### Q3. De onde vem os 10 pontos de recompensa (RESOLVIDA, ver D21)

**Problema.** O desenho pedia 10 recompensas e um chefe a cada 10 andares. São 5 chefes mais o
chefão, o que dá 5 ou 6 pontos, não 10.

**Opções.**

| Opção | Efeito |
| --- | --- |
| **A. Elite também dá ponto** | 5 chefes + 5 elites = 10. Um elite garantido por bloco. |
| **B. Chefe dá 2 pontos** | 5 chefes x 2 = 10. Menos momentos de decisão, cada um mais pesado. |
| **C. Recompensa a cada 5 andares** | Andares 5, 10, 15... 50 = 10 pontos, independente do tipo de sala. Regular, mas desconecta a recompensa do desafio. |

**Decidido: A.** Amarra recompensa a dificuldade, distribui as decisões ao longo do bloco e dá
função ao elite, que senão seria só um combate mais duro sem motivo para existir.

---

### Q2. Carta repetida no sorteio inicial (RESOLVIDA, ver D19)

O sorteio das 5 iniciais pode entregar a mesma carta duas vezes?

**Decidido: não pode.** As 5 são sempre distintas. Como D18 já entrega 2 cópias de cada, permitir
repetição criaria decks iniciais com 4 cópias da mesma carta, o que estreita demais a run logo na
largada e piora a leitura da tela de sorteio.

---

### Q4. Recompensa do desafio opcional (RESOLVIDA, ver D25)

Não podia dar ponto de recompensa (quebraria a conta de 10) nem moeda (não existe).

**Decidido: modificador de run.** Bônus permanente e pequeno que vale até o fim da run, escolhido
entre 2 sorteados, no máximo 5 por run. Não infla o deck, não mexe na economia de recompensa e dá
uma segunda dimensão de crescimento para quem gosta de arriscar.

Restrições que vieram junto, detalhadas em `01-gdd.md` seção 3.3: modificadores são sempre
aditivos e de valor fixo, e nenhum deles pode tocar na mecânica exclusiva de uma única classe.
Sem isso, o desafio opcional viraria uma sala que vale mais para a Capimaga que para as
outras duas, e a paridade entre classes iria junto.

---

### Q5. Quem é o jogador (RESOLVIDA, ver D22)

**Decidido: também capivara.** O resto (por que sobe, qual o vínculo com a família da Soberana,
história de cada classe) entra numa passada de lore dedicada, depois que as mecânicas fecharem.
Nada no design mecânico depende dessa história.

---

### Q6. O sexto tipo de encontro (RESOLVIDA, ver D20)

Na entrevista foi marcado um tipo de encontro adicional que não chegou a ser nomeado.

**Decidido: não haverá.** Os seis tipos atuais (combate, elite, evento, descanso, desafio e chefe)
já preenchem os 10 andares de cada bloco e cobrem o ritmo pretendido. Candidatos avaliados e
descartados: sala de troca de carta, altar de arquétipo, emboscada e pedágio.

Fica registrado o buraco que esses candidatos preencheriam, caso o playtest mostre que ele
incomoda: **nada fora das recompensas mexe no deck**, então quem recebe um sorteio inicial ruim
não tem ferramenta para corrigir o rumo antes do primeiro elite.

---

### Q7. Lacaios persistem entre combates? (RESOLVIDA, ver D23)

**Decidido: não persistem.** Zeram ao fim de todo combate, sem exceção. Persistir criaria bola de
neve entre andares e exigiria um teto artificial para o bloco 5 não virar passeio.

Consequência: o nível 9 da habilidade Legião, que carregava metade dos lacaios para o combate
seguinte, foi substituído por uma rede de segurança dentro do combate (uma vez por combate, ao
ficar sem lacaios, invoca 2). Isso serve principalmente ao arquétipo Sacrifício, que fica exposto
logo depois de gastar tudo.

---

### Q8. Nome do projeto (RESOLVIDA, ver D24)

**Decidido: CapiTower.** A pasta local foi renomeada de `BrecciTower` para `CapiTower`, ficando
igual ao repositório e a documentação.

---

### Q9. Arquétipo é função ou nicho? (RESOLVIDA, ver D28)

Registrada em 11/09/2026, a partir do primeiro playtest do MVP em Flet.

**Problema.** Com 3 cartas por arquétipo, cinco arquétipos eram 100% de um tipo só: Estouro e
Estocada só Ataque, Couro e Fumaça só Defesa, Contrabando só Utilidade. A raiz estava na própria
documentação: as tabelas de arquétipo de Brutamontes e Ligeira em `02-classes-e-arquetipos.md`
tinham uma coluna "Papel" com valores "Acúmulo / Gasto explosivo / Defensivo / Alternativo", que é
exatamente função dentro do deck, e induzia a montar cada arquétipo como um tipo de carta.

**Decidido: nicho.** Arquétipo é um nicho dentro do jeito de jogar da classe, não uma função no
deck. Cada arquétipo tem 5 cartas, com pelo menos 1 Ataque, 1 Defesa, 1 Poder e 1 Utilidade; a 5a
é livre. A coluna "Papel" virou "Nicho" nas tabelas de `02`.

**Consequências.** Cartas que mudaram para cumprir a regra:

| Carta | Classe | Mudança |
| --- | --- | --- |
| Soco de Sobra | Brutamontes | Saiu de Estouro e foi para Couro (dano por Adrenalina acumulada, sem gastar). |
| Pele de Bicho | Brutamontes | Saiu de Couro e foi para Estouro (consome Adrenalina por Defesa). |
| Esquiva | Ligeira (Fumaça) | Removida: era Defesa genérica e falhava no teste de identidade da seção 2.3 de `02`. |
| Rasteira | Ligeira (Estocada) | Deixou de ser Ataque e virou Utilidade (só aplica Fragilidade). |
| Troca Rápida | Ligeira (Contrabando) | Deixou de ser Utilidade e virou Defesa (ganhou 4 de Defesa, mantém o redraw). |

Entraram 8 poderes novos no motor, 1 por arquétipo que não tinha: Vala Comum (Enxame), Banquete
(Sacrifício), Pavio Curto (Estouro), Calo (Couro), Segundo Fôlego (Corrente), Golpe de Vista
(Estocada), Rastro de Lama (Fumaça) e Bolso Fundo (Contrabando). O catálogo completo está na
seção 9 de `02-classes-e-arquetipos.md`.
