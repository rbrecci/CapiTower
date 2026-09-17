# 06. Roadmap

Ordem pensada para que exista algo jogavel o mais cedo possivel, e para que o balanceamento
comece com dado real e nao com planilha.

## Fase 0: fundacao (atual)

- [x] Documentacao de design e tecnica
- [x] Esqueleto de pastas
- [x] Schema do banco
- [x] Fechar as questoes abertas de `07-decisoes.md` (D01 a D25)
- [x] Definir as classes 2 e 3 no brainstorm (Brutamontes e Ligeira, aprovadas)

## Fase 1: prototipo de combate (sem banco, sem conta)

O objetivo aqui e responder uma pergunta: o combate e divertido?

- [ ] `index.php` servindo uma tela so
- [ ] Motor de combate em `combat.js`: turno, Acao, compra, descarte, reembaralhamento
- [ ] Interpretador de efeitos em `effects.js`
- [ ] Estados compartilhados (Bloco, Forca, Fragilidade, Fraqueza, Veneno)
- [ ] Sistema de lacaios como contador
- [ ] 5 cartas de teste e 1 inimigo com intencao telegrafada, tudo em JSON local
- [ ] Interface de carta jogavel com clique

Criterio de saida: da para jogar um combate inteiro e perder de proposito.

## Fase 2: a torre

- [ ] `rng.js` com seed deterministica
- [ ] `tower.js` gerando os 5 blocos com ordem embaralhada
- [ ] Tipos de sala: combate, elite, evento, descanso, desafio, chefe
- [ ] Tela de recompensa com a escolha carta contra habilidade
- [ ] Modificadores de run vindos do desafio opcional
- [ ] HP persistente entre andares
- [ ] Fim de run: vitoria e derrota

Criterio de saida: da para subir do andar 1 ao 51 numa sentada.

## Fase 3: conteudo da primeira classe

- [ ] As 20 cartas da Capimaga escritas e balanceadas no papel
- [ ] Os 10 niveis da habilidade Legiao
- [ ] Bestiario dos 5 blocos
- [ ] Os 5 chefes com fases
- [ ] Soberana Gertrudes com 3 fases
- [ ] 8 a 12 eventos

Criterio de saida: uma run completa com identidade propria, sem placeholder de mecanica.

## Fase 4: banco e conta

- [ ] `Database.php`, `Response.php`, `Auth.php`
- [ ] Registro, login, logout, sessao
- [ ] `schema.sql` e `seeds.sql` no ar
- [ ] Migrar o catalogo do JSON local para o banco
- [ ] `bootstrap.php` servindo o catalogo
- [ ] Save e load da run entre andares
- [ ] Retomar run ativa ao entrar

Criterio de saida: fechar a aba no andar 30 e voltar no dia seguinte no andar 30.

## Fase 5: meta progressao

- [ ] Tabela de objetivos e avaliacao no `finish.php`
- [ ] Pool inicial reduzido de cartas
- [ ] Desbloqueios por objetivo
- [ ] Tela de perfil com estatisticas e recordes
- [ ] Formula de pontos de meta

Criterio de saida: perder uma run gera progresso visivel.

## Fase 6: classes 2 e 3

- [x] Conceito, mecanica exclusiva e 4 arquetipos de cada
- [ ] 20 cartas de cada
- [ ] Habilidade com 10 niveis de cada
- [ ] Passe de balanceamento comparando as tres

Criterio de saida: tres classes que vencem a torre por caminhos diferentes.

## Fase 7: acabamento

- [x] Arte gerada por IA substituindo os placeholders
- [x] Animacao de carta, dano e invocacao
- [x] Som
- [x] Tela de tutorial ou primeira run guiada
- [x] Responsivo para tela menor
- [ ] Deploy na InfinityFree (precisa da conta/credenciais do dono do projeto, ver docs/09)

## Depois, se fizer sentido

- Dificuldade ascendente (modificadores para quem ja venceu)
- Run diaria com seed compartilhada
- Historia completa e cutscenes de bloco
- Quarta classe
