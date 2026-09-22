# 06. Roadmap

Ordem pensada para que exista algo jogável o mais cedo possível, e para que o balanceamento
comece com dado real e não com planilha.

## Fase 0: fundação (atual)

- [x] Documentação de design e técnica
- [x] Esqueleto de pastas
- [x] Schema do banco
- [x] Fechar as questões abertas de `07-decisoes.md` (D01 a D25)
- [x] Definir as classes 2 e 3 no brainstorm (Brutamontes e Ligeira, aprovadas)

## Fase 1: protótipo de combate (sem banco, sem conta)

O objetivo aqui é responder uma pergunta: o combate é divertido?

- [ ] `index.php` servindo uma tela só
- [ ] Motor de combate em `combat.js`: turno, Ação, compra, descarte, reembaralhamento
- [ ] Interpretador de efeitos em `effects.js`
- [ ] Estados compartilhados (Bloco, Força, Fragilidade, Fraqueza, Veneno)
- [ ] Sistema de lacaios como contador
- [ ] 5 cartas de teste e 1 inimigo com intenção telegrafada, tudo em JSON local
- [ ] Interface de carta jogável com clique

Critério de saída: dá para jogar um combate inteiro e perder de propósito.

## Fase 2: a torre

- [ ] `rng.js` com seed determinística
- [ ] `tower.js` gerando os 5 blocos com ordem embaralhada
- [ ] Tipos de sala: combate, elite, evento, descanso, desafio, chefe
- [ ] Tela de recompensa com a escolha carta contra habilidade
- [ ] Modificadores de run vindos do desafio opcional
- [ ] HP persistente entre andares
- [ ] Fim de run: vitória e derrota

Critério de saída: dá para subir do andar 1 ao 51 numa sentada.

## Fase 3: conteúdo da primeira classe

- [ ] As 20 cartas da Capimaga escritas e balanceadas no papel
- [ ] Os 10 níveis da habilidade Legião
- [ ] Bestiário dos 5 blocos
- [ ] Os 5 chefes com fases
- [ ] Soberana Gertrudes com 3 fases
- [ ] 8 a 12 eventos

Critério de saída: uma run completa com identidade própria, sem placeholder de mecânica.

## Fase 4: banco e conta

- [ ] `Database.php`, `Response.php`, `Auth.php`
- [ ] Registro, login, logout, sessão
- [ ] `schema.sql` e `seeds.sql` no ar
- [ ] Migrar o catálogo do JSON local para o banco
- [ ] `bootstrap.php` servindo o catálogo
- [ ] Save e load da run entre andares
- [ ] Retomar run ativa ao entrar

Critério de saída: fechar a aba no andar 30 e voltar no dia seguinte no andar 30.

## Fase 5: meta progressão

- [ ] Tabela de objetivos e avaliação no `finish.php`
- [ ] Pool inicial reduzido de cartas
- [ ] Desbloqueios por objetivo
- [ ] Tela de perfil com estatísticas e recordes
- [ ] Fórmula de pontos de meta

Critério de saída: perder uma run gera progresso visível.

## Fase 6: classes 2 e 3

- [x] Conceito, mecânica exclusiva e 4 arquétipos de cada
- [ ] 20 cartas de cada
- [ ] Habilidade com 10 níveis de cada
- [ ] Passe de balanceamento comparando as três

Critério de saída: três classes que vencem a torre por caminhos diferentes.

## Fase 7: acabamento

- [x] Arte gerada por IA substituindo os placeholders
- [x] Animação de carta, dano e invocação
- [x] Som
- [x] Tela de tutorial ou primeira run guiada
- [x] Responsivo para tela menor
- [ ] Deploy na InfinityFree (precisa da conta/credenciais do dono do projeto, ver docs/09)

## Depois, se fizer sentido

- Dificuldade ascendente (modificadores para quem já venceu)
- Run diária com seed compartilhada
- História completa e cutscenes de bloco
- Quarta classe
