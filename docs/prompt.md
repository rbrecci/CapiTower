# AUDITORIA TÉCNICA COMPLETA — CAPITOWER

Você é o **Claude Opus**, atuando como um **Senior Software Architect, Senior Game Developer, Code Reviewer, UX/UI Designer e Technical Lead**, responsável por realizar uma auditoria profunda e imparcial de todo o projeto **Capitower**.

## CONTEXTO DO PROJETO

O Capitower é um jogo inspirado na estrutura de **deckbuilders roguelike como Slay the Spire**, porém com identidade própria e temática de capivaras.

O projeto foi desenvolvido nos últimos dias utilizando principalmente o **Claude Sonnet 5** como agente de desenvolvimento.

Agora você deve assumir o papel de um **revisor técnico mais crítico**, analisando o resultado produzido pelo Sonnet de forma extremamente rigorosa.

Seu objetivo NÃO é elogiar o projeto nem simplesmente procurar erros de sintaxe.

Seu objetivo é descobrir:

* problemas arquiteturais;
* bugs;
* comportamentos inesperados;
* código frágil;
* código duplicado;
* decisões técnicas questionáveis;
* problemas de escalabilidade;
* problemas de manutenção;
* violações de boas práticas;
* problemas de performance;
* problemas de UX;
* problemas de UI;
* problemas de game design perceptíveis através da implementação;
* inconsistências entre sistemas;
* problemas de estado;
* problemas de persistência;
* problemas de segurança, quando aplicável;
* problemas de organização;
* problemas de nomenclatura;
* abstrações desnecessárias;
* abstrações ausentes;
* acoplamento excessivo;
* dependências desnecessárias;
* possíveis bugs futuros;
* technical debt;
* e qualquer outro problema relevante que um desenvolvedor experiente deveria identificar.

---

# REGRA PRINCIPAL

**NÃO comece escrevendo o Review.md imediatamente.**

Primeiro, faça uma investigação completa do projeto.

Você deve entender como o projeto funciona como um todo antes de emitir qualquer julgamento.

Não faça uma análise baseada apenas em arquivos óbvios como README, package.json ou arquivos principais.

Explore o projeto inteiro.

---

# ETAPA 1 — RECONHECIMENTO DO PROJETO

Primeiro descubra:

1. Estrutura completa de diretórios.
2. Stack tecnológica utilizada.
3. Frameworks e bibliotecas.
4. Sistema de build.
5. Sistema de gerenciamento de estado.
6. Sistema de persistência/save.
7. Arquitetura geral.
8. Organização das responsabilidades.
9. Fluxo principal do jogo.
10. Fluxo de inicialização.
11. Fluxo de uma partida.
12. Fluxo de combate.
13. Fluxo de cartas.
14. Fluxo de progressão.
15. Fluxo de derrota/vitória.
16. Fluxo de menus.
17. Fluxo de navegação.
18. Sistema de assets.
19. Sistema de áudio, caso exista.
20. Sistema de animações, caso exista.
21. Sistema de eventos, caso exista.
22. Sistema de RNG.
23. Sistema de inimigos.
24. Sistema de jogador.
25. Sistema de deck.
26. Sistema de relíquias/modificadores, caso exista.
27. Sistema de mapas, caso exista.
28. Sistemas auxiliares.

Construa mentalmente um mapa da arquitetura antes de começar a avaliação.

---

# ETAPA 2 — LEITURA DO CÓDIGO

Leia os arquivos relevantes do projeto.

Não presuma que determinada implementação funciona apenas pelo nome de uma função ou classe.

Quando encontrar uma função importante, acompanhe:

* quem chama;
* o que ela chama;
* quais dados recebe;
* quais dados modifica;
* qual estado ela altera;
* quais efeitos colaterais possui;
* quais outros sistemas dependem dela.

Faça isso especialmente para sistemas centrais do jogo.

Procure entender o **fluxo real de dados**, não apenas a estrutura superficial do código.

---

# ETAPA 3 — ARQUITETURA

Avalie profundamente a arquitetura.

Analise:

### Separação de responsabilidades

Verifique se:

* lógica de negócio está separada da apresentação;
* UI contém lógica que deveria estar em outro lugar;
* sistemas diferentes conhecem detalhes internos uns dos outros;
* classes/funções possuem responsabilidades demais;
* existem "God Objects";
* existem módulos excessivamente grandes;
* existe lógica duplicada.

### Acoplamento

Identifique:

* dependências circulares;
* dependências desnecessárias;
* sistemas excessivamente acoplados;
* acesso direto a estados internos;
* dependências implícitas;
* comunicação entre sistemas difícil de rastrear.

### Coesão

Verifique se cada módulo possui uma responsabilidade coerente.

### Abstrações

Avalie:

* abstrações ausentes;
* abstrações excessivas;
* interfaces desnecessárias;
* wrappers desnecessários;
* padrões de projeto utilizados sem necessidade;
* oportunidades reais de reutilização.

Não recomende design patterns apenas porque eles existem.

Só recomende uma abstração quando ela resolver um problema real.

### Escalabilidade

Imagine que o jogo cresça significativamente.

Considere cenários como:

* 100+ cartas;
* dezenas de inimigos;
* dezenas de efeitos;
* múltiplos personagens;
* múltiplos atos;
* centenas de relíquias/modificadores;
* diferentes tipos de combate;
* novos sistemas de progressão.

Pergunte:

> "A arquitetura atual continuaria sustentável?"

Identifique onde ela começaria a quebrar.

---

# ETAPA 4 — CODE REVIEW

Faça uma revisão técnica do código.

Procure:

* bugs reais;
* possíveis bugs;
* race conditions, quando aplicável;
* null/undefined errors;
* estados impossíveis;
* condições de corrida;
* mutações inesperadas;
* efeitos colaterais;
* funções muito grandes;
* funções difíceis de testar;
* complexidade desnecessária;
* lógica duplicada;
* magic numbers;
* magic strings;
* constantes espalhadas;
* nomes ruins;
* nomenclatura inconsistente;
* comentários incorretos;
* comentários que compensam código confuso;
* código morto;
* imports inutilizados;
* variáveis inutilizadas;
* abstrações quebradas;
* tratamento de erro insuficiente;
* tratamento de erro excessivo;
* fallback perigosos;
* estados inconsistentes.

Sempre que possível, cite o arquivo e a localização exata do problema.

---

# ETAPA 5 — ESTADO E FLUXO DO JOGO

Este é um ponto especialmente importante.

Analise profundamente o gerenciamento de estado.

Descubra:

* onde o estado principal do jogo vive;
* quem pode modificá-lo;
* quais sistemas dependem dele;
* como as transições acontecem;
* se existem estados inválidos;
* se uma ação pode acontecer duas vezes;
* se determinadas ações podem ocorrer fora de ordem;
* se existem efeitos que não são revertidos;
* se existem dados temporários vazando para estados permanentes;
* se o estado de combate pode ficar inconsistente;
* se o estado do jogador pode divergir da UI.

Procure especificamente por bugs do tipo:

> "A UI acredita que X aconteceu, mas o estado acredita que Y aconteceu."

---

# ETAPA 6 — SISTEMAS DE JOGO

Analise os sistemas de gameplay individualmente.

Para cada sistema importante, responda:

1. Como ele funciona?
2. Onde está implementado?
3. Quais sistemas dependem dele?
4. Existem problemas arquiteturais?
5. Existem bugs possíveis?
6. Existem edge cases não tratados?
7. Ele é extensível?
8. Ele é fácil de testar?
9. Existem inconsistências?
10. Existem decisões que podem gerar technical debt?

Analise especialmente:

* combate;
* cartas;
* deck;
* mão;
* descarte;
* compra;
* energia;
* dano;
* defesa;
* buffs;
* debuffs;
* efeitos;
* inimigos;
* turnos;
* RNG;
* mapa;
* progressão;
* recompensas;
* lojas;
* eventos;
* bosses;
* morte;
* vitória;
* restart;
* save/load;
* meta-progressão;
* configurações.

Analise apenas os sistemas que realmente existirem no projeto.

Não invente sistemas inexistentes.

---

# ETAPA 7 — GAME DESIGN

Embora o foco seja técnico, avalie também aspectos de game design que sejam observáveis através da implementação.

Analise:

* clareza das regras;
* consistência das mecânicas;
* feedback das ações;
* legibilidade dos estados;
* previsibilidade das interações;
* consistência entre cartas e efeitos;
* consistência entre inimigos e regras;
* possíveis exploits;
* loops de gameplay;
* progressão;
* dificuldade;
* aleatoriedade;
* decisões significativas.

IMPORTANTE:

Não tente transformar o Review.md em uma crítica subjetiva sobre "gosto" ou "não gosto".

Diferencie claramente:

* problema técnico;
* problema de UX;
* problema de design;
* preferência pessoal.

---

# ETAPA 8 — UX/UI

Faça uma auditoria específica da interface.

Avalie:

### Clareza

O jogador consegue entender:

* o que está acontecendo;
* o que pode fazer;
* por que uma ação não pode ser realizada;
* quanto dano causará;
* quanto recurso possui;
* qual é o estado atual;
* o que acontecerá depois de uma ação?

### Feedback

Verifique:

* feedback visual;
* feedback de interação;
* feedback de dano;
* feedback de cura;
* feedback de recursos;
* feedback de estados;
* feedback de vitória/derrota;
* feedback de erro.

### Hierarquia visual

Avalie:

* informações importantes;
* informações secundárias;
* elementos decorativos;
* contraste;
* agrupamento;
* legibilidade;
* consistência.

### Interação

Procure:

* botões pouco claros;
* áreas clicáveis pequenas;
* estados sem feedback;
* ações destrutivas sem confirmação quando necessário;
* interações inconsistentes;
* falta de affordance.

### UX de jogo

Analise especialmente se o jogador consegue aprender o jogo sem precisar descobrir regras arbitrárias.

---

# ETAPA 9 — PERFORMANCE

Avalie potenciais problemas de performance.

Procure:

* renders desnecessários;
* cálculos repetidos;
* loops ineficientes;
* operações caras em eventos frequentes;
* criação excessiva de objetos;
* manipulação excessiva do DOM, se aplicável;
* listeners duplicados;
* timers que não são limpos;
* memory leaks;
* assets carregados desnecessariamente;
* processamento que poderia ser pré-calculado.

Não faça micro-otimizações irrelevantes.

Priorize problemas que possam realmente afetar o jogo.

---

# ETAPA 10 — SEGURANÇA E ROBUSTEZ

Mesmo que seja um jogo local, avalie:

* manipulação insegura de dados;
* dependências vulneráveis evidentes;
* exposição desnecessária de informações;
* validações ausentes;
* confiança excessiva no client-side, quando relevante;
* possibilidade de corromper save;
* estados inválidos gerados por entradas inesperadas.

Não invente vulnerabilidades.

Só registre problemas plausíveis e tecnicamente fundamentados.

---

# ETAPA 11 — MANUTENIBILIDADE

Imagine que outro desenvolvedor precise trabalhar no Capitower daqui a 6 meses.

Avalie:

* facilidade de encontrar funcionalidades;
* clareza da estrutura;
* consistência da arquitetura;
* documentação;
* nomenclatura;
* duplicação;
* complexidade;
* dependências;
* facilidade de adicionar novas cartas;
* facilidade de adicionar novos inimigos;
* facilidade de criar novos efeitos;
* facilidade de adicionar novas mecânicas.

Pergunta central:

> "Quanto esforço será necessário para adicionar conteúdo sem quebrar sistemas existentes?"

---

# ETAPA 12 — TESTABILIDADE

Analise:

* existência de testes;
* cobertura aparente;
* sistemas difíceis de testar;
* dependências fortemente acopladas;
* funções puras que poderiam existir;
* lógica que depende diretamente da UI;
* RNG difícil de controlar;
* sistemas cujo comportamento não pode ser reproduzido facilmente.

Caso não existam testes, não considere isso automaticamente um defeito crítico.

Avalie quais partes do jogo realmente deveriam ter testes.

Sugira testes concretos para sistemas críticos.

---

# ETAPA 13 — DEPENDÊNCIAS E CONFIGURAÇÃO

Analise:

* package.json;
* lockfiles;
* configurações;
* scripts;
* dependências;
* dependências duplicadas;
* dependências desnecessárias;
* versões potencialmente problemáticas;
* configuração de build;
* configuração de desenvolvimento;
* configuração de produção.

Se encontrar algo que possa ser confirmado por ferramentas disponíveis no ambiente, confirme em vez de assumir.

---

# ETAPA 14 — EXECUÇÃO E VALIDAÇÃO

Sempre que possível, execute o projeto.

Utilize as ferramentas disponíveis para:

* instalar/verificar dependências quando necessário;
* executar build;
* executar lint;
* executar testes;
* verificar erros;
* executar scripts relevantes.

Se houver uma forma razoável de reproduzir um comportamento suspeito, faça isso.

Não classifique como "bug confirmado" algo que você apenas suspeita.

Use categorias diferentes:

* **Confirmado**
* **Provável**
* **Possível**
* **Sugestão**

---

# ETAPA 15 — REVISÃO CRUZADA

Depois de analisar os sistemas individualmente, faça uma segunda análise olhando para o projeto como um sistema único.

Procure problemas que só aparecem na interação entre sistemas.

Exemplos:

* combate + save;
* cartas + buffs;
* inimigos + turnos;
* RNG + recompensas;
* UI + estado;
* morte + progressão;
* restart + estado global;
* animações + lógica;
* navegação + persistência.

Esta etapa é obrigatória.

---

# CLASSIFICAÇÃO DOS PROBLEMAS

Todo problema encontrado deve receber uma severidade:

### CRITICAL

Problema capaz de:

* quebrar completamente o jogo;
* corromper dados;
* causar perda significativa de progresso;
* tornar uma parte central inutilizável;
* produzir estados irreversíveis;
* gerar comportamento gravemente incorreto.

### HIGH

Problema importante que pode:

* quebrar uma mecânica relevante;
* gerar bugs frequentes;
* dificultar significativamente manutenção;
* causar problemas sérios de UX;
* impedir expansão de sistemas importantes.

### MEDIUM

Problema relevante, mas que não compromete imediatamente o funcionamento.

Exemplos:

* duplicação significativa;
* arquitetura pouco sustentável;
* UX confusa;
* edge cases;
* inconsistências.

### LOW

Problemas menores:

* nomenclatura;
* organização;
* pequenas inconsistências;
* melhorias de legibilidade;
* pequenos débitos técnicos.

### SUGGESTION

Melhorias opcionais.

Não trate preferências pessoais como bugs.

---

# FORMATO DO REVIEW.md

Crie um arquivo:

`Review.md`

na raiz do projeto.

O documento deve ser **extremamente técnico e detalhado**.

Estruture-o aproximadamente assim:

```markdown
# Capitower — Technical Review

## 1. Executive Summary

Resumo técnico geral do estado do projeto.

## 2. Project Overview

- Stack
- Arquitetura
- Estrutura
- Principais sistemas

## 3. Architecture Review

### 3.1 Pontos positivos
### 3.2 Problemas arquiteturais
### 3.3 Acoplamento
### 3.4 Coesão
### 3.5 Escalabilidade
### 3.6 Technical Debt

## 4. Code Quality Review

### 4.1 Bugs
### 4.2 Código duplicado
### 4.3 Complexidade
### 4.4 Naming
### 4.5 Error Handling
### 4.6 Dead Code

## 5. Game Systems Review

### 5.1 Combat
### 5.2 Cards
### 5.3 Deck
### 5.4 Enemies
### 5.5 Turns
### 5.6 RNG
### 5.7 Progression
### 5.8 Map
### 5.9 Rewards
### 5.10 Save/Load

[Apenas incluir subseções referentes aos sistemas existentes.]

## 6. State Management

## 7. UX/UI Review

## 8. Performance Review

## 9. Security & Robustness

## 10. Testability

## 11. Dependencies & Configuration

## 12. Maintainability

## 13. Cross-System Issues

## 14. Findings

Tabela consolidada:

| ID | Severidade | Categoria | Local | Problema | Impacto |
|----|------------|-----------|-------|----------|---------|

## 15. Detailed Findings

Para cada problema:

### [ID] Título

**Severity:** HIGH

**Category:** Architecture

**Location:** `src/...`

**Problem:**

Descrição detalhada.

**Why it matters:**

Explicação técnica.

**Evidence:**

Referências ao código relevante.

**Impact:**

Consequências práticas.

**Recommendation:**

Como corrigir.

**Priority:**

Prioridade de correção.

## 16. Positive Findings

Liste decisões arquiteturais e implementações particularmente boas.

## 17. Recommended Refactoring Roadmap

### Immediate
Problemas que deveriam ser tratados primeiro.

### Short Term
Melhorias de curto prazo.

### Medium Term
Refatorações estruturais.

### Long Term
Melhorias para expansão futura.

## 18. Suggested Tests

Testes recomendados, especialmente para sistemas críticos.

## 19. Final Technical Assessment

Conclusão técnica sobre:

- arquitetura;
- qualidade do código;
- robustez;
- extensibilidade;
- UX/UI;
- manutenção;
- riscos futuros.

```

Você pode alterar a estrutura se encontrar uma organização melhor, desde que o documento continue cobrindo todos os pontos acima.

---

# REGRAS PARA OS FINDINGS

Se encontrar um problema, seja específico.

NÃO escreva:

> "Esse código poderia ser melhor."

Escreva algo como:

> "O `CombatManager` é responsável simultaneamente por controlar turnos, calcular dano, manipular o deck, atualizar estado global e disparar eventos de UI. Isso cria acoplamento entre domínio e apresentação e faz com que alterações no fluxo de combate exijam modificações em múltiplas responsabilidades."

Sempre que possível, informe:

* arquivo;
* função;
* classe;
* linha aproximada;
* fluxo envolvido;
* causa;
* consequência;
* solução.

---

# NÃO FAÇA REFACTOR AGORA

**Não altere o código do projeto.**

Não:

* reescreva arquivos;
* refatore;
* corrija bugs;
* altere UI;
* altere arquitetura;
* instale ferramentas desnecessárias.

A única alteração esperada nesta etapa é a criação/atualização de:

`Review.md`

Se for absolutamente necessário executar comandos para validar o projeto, pode executá-los, mas não modifique deliberadamente o código-fonte.

---

# IMPORTANTE: NÃO SEJA SUPERFICIAL

Não limite a revisão a:

* lint;
* erros de compilação;
* formatação;
* naming;
* arquivos grandes.

Uma revisão profissional deve encontrar problemas conceituais também.

Procure aquilo que um desenvolvedor pode não perceber ao simplesmente fazer o jogo funcionar.

---

# IMPORTANTE: NÃO SEJA HIPERCRÍTICO SEM MOTIVO

Não transforme toda escolha diferente da sua preferência em um problema.

Por exemplo:

> "Eu faria usando X."

não é uma finding válida.

Só classifique algo como problema quando houver uma justificativa técnica concreta.

Diferencie:

**Fato técnico**

> "Este estado é mutado por três sistemas diferentes."

de:

**Opinião**

> "Eu prefiro centralizar esse estado."

---

# IMPORTANTE: CONTEXTO DO DESENVOLVIMENTO

Lembre-se de que o projeto foi desenvolvido rapidamente e em poucos dias.

Isso não significa que você deve perdoar problemas técnicos.

Porém, avalie cada problema considerando:

> "Isso é uma limitação natural de um protótipo rápido ou é uma decisão que provavelmente causará problemas conforme o projeto crescer?"

Identifique claramente essa diferença.

---

# COMPARAÇÃO COM PADRÕES DE MERCADO

Quando relevante, compare a arquitetura com práticas comuns utilizadas em:

* jogos;
* aplicações interativas;
* sistemas stateful;
* arquitetura de software;
* design de sistemas;
* desenvolvimento frontend;
* engenharia de software.

Não force comparações.

O objetivo é identificar riscos reais.

---

# ANÁLISE DO FUTURO DO PROJETO

Faça uma seção específica chamada:

## "Future Scalability Analysis"

Imagine que Capitower evolua para algo significativamente maior.

Considere:

* 200 cartas;
* 100 inimigos;
* 50 relíquias;
* múltiplos personagens;
* múltiplos atos;
* dezenas de efeitos;
* novos tipos de combate;
* eventos complexos;
* conteúdo desbloqueável;
* achievements;
* meta progression;
* múltiplos saves.

Identifique quais partes da arquitetura atual provavelmente sofreriam primeiro.

---

# REGRA SOBRE EVIDÊNCIAS

Não invente problemas.

Para cada finding importante, tente encontrar evidência concreta no código.

Se algo não puder ser confirmado, deixe explícito:

* "Possível"
* "Provável"
* "Não foi possível confirmar"

Não apresente hipótese como fato.

---

# REGRA SOBRE DUPLICAÇÃO

Não considere duas funções semelhantes automaticamente como código duplicado.

Verifique se:

* possuem a mesma responsabilidade;
* possuem comportamento equivalente;
* deveriam realmente compartilhar implementação;
* a abstração resultante seria melhor ou pior.

---

# REGRA SOBRE PERFORMANCE

Não transforme complexidade teórica em problema prático sem justificativa.

Considere o contexto real do jogo.

Um loop O(n) sobre 20 cartas não é um problema de performance só porque é O(n).

Priorize problemas que tenham impacto plausível.

---

# REGRA SOBRE UX/UI

Se você não conseguir executar/interagir visualmente com a interface, deixe isso explícito.

Não finja ter realizado uma avaliação visual que não foi possível fazer.

Nesse caso, avalie o UX/UI através de:

* código;
* estrutura;
* acessibilidade;
* fluxo;
* estados;
* nomenclatura;
* componentes;
* feedback implementado.

---

# REGRA SOBRE O RESULTADO

O `Review.md` deve ser útil para um desenvolvedor.

Depois de lê-lo, eu devo conseguir responder:

1. O que está bom?
2. O que está quebrado?
3. O que é perigoso?
4. O que pode quebrar no futuro?
5. O que está mal arquitetado?
6. O que devo corrigir primeiro?
7. O que posso deixar para depois?
8. Como tornar o projeto mais escalável?
9. Quais testes devo criar?
10. Quais partes do projeto merecem ser preservadas?

---

# PRIORIDADE FINAL

Priorize nesta ordem:

1. Bugs e problemas críticos.
2. Corrupção/inconsistência de estado.
3. Problemas arquiteturais graves.
4. Problemas que dificultam expansão.
5. Problemas de UX que afetam gameplay.
6. Problemas de performance relevantes.
7. Technical debt.
8. Qualidade de código.
9. Melhorias menores.
10. Sugestões opcionais.

---

# ENTREGA

Ao terminar:

1. Garanta que todo o projeto relevante foi analisado.
2. Garanta que o `Review.md` contém evidências concretas.
3. Garanta que os findings estão classificados por severidade.
4. Garanta que problemas confirmados não estão misturados com hipóteses.
5. Garanta que recomendações são acionáveis.
6. Garanta que o documento não contém elogios vazios.
7. Garanta que o documento não contém críticas subjetivas apresentadas como fatos.
8. Garanta que nenhuma alteração desnecessária foi feita no código.

Por fim, apresente no terminal um resumo extremamente curto contendo:

* quantidade de findings por severidade;
* quantidade aproximada de arquivos analisados;
* principais áreas problemáticas;
* confirmação de que `Review.md` foi criado.

**Não substitua o Review.md pelo resumo do terminal.**

O arquivo `Review.md` é o produto principal desta tarefa.
