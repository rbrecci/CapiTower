# 00. Visao geral

## Pitch

CapiTower e um tower crawler roguelike de deck building para navegador. O jogador escolhe uma das
tres classes, monta um deck enxuto de 15 cartas ao longo de 50 andares e enfrenta os capangas da
Soberana Gertrudes a cada 10 andares.

O diferencial esta na escolha entre **largura** e **profundidade**: a cada recompensa o jogador
decide entre ganhar uma carta nova (largura, mais opcoes de nicho) ou subir o nivel da habilidade
da classe (profundidade, build especializada). Como o deck comeca aleatorio, cada run oferece um
ponto de partida diferente para essa decisao.

## Pilares de design

**1. As tres classes sao igualmente fortes, so que diferentes.**
Nenhuma classe e a escolha "certa". Escolher classe e escolher estilo de jogo, nunca poder bruto.
Toda proposta de carta ou habilidade passa pelo teste: isso quebra a paridade entre as classes?

**2. Deck pequeno, decisao grande.**
15 cartas no fim da run. Sem remocao, sem upgrade de carta, sem lixo. Cada carta ganha e cerca de
7% do deck, entao toda recompensa importa e o jogador nunca precisa "consertar" o deck.

**3. A run conta uma historia de build.**
O deck inicial aleatorio define a pergunta da run, e as 10 recompensas definem a resposta.
Comecou com 3 cartas do mesmo arquetipo? Especialize. Comecou espalhado? Vire generalista.

**4. Perder tambem avanca.**
Permadeath, mas o andar alcancado vira progresso de meta. Nenhuma run e desperdicio.

**5. Humor sem piada burra.**
Capivaras bombadas levadas a serio dentro do proprio universo. O tom e leve, as mecanicas nao.

## Publico e sessao

- Sessao alvo de uma run completa: 30 a 45 minutos.
- Jogador de deck builder que conhece o genero, mas o onboarding assume que nao conhece.
- Desktop primeiro. Layout responsivo fica para depois do MVP.

## Escopo do MVP

Dentro:
- 1 classe jogavel completa (20 cartas em 4 arquetipos, habilidade com 10 niveis).
- Motor de combate por turnos com o recurso Acao.
- Torre de 50 andares com ordem de encontros embaralhada.
- Conta, save da run e retomada.
- Placeholders visuais, sem arte final.

Fora do MVP:
- Classes 2 e 3.
- Sistema de objetivos e desbloqueios completo.
- Eventos narrativos alem de um punhado de exemplos.
- Arte, som e animacao.
- Qualquer forma de ranking ou competicao.

## Nao objetivos

Deixado de fora por decisao, nao por falta de tempo:

- **Economia de moeda e loja.** Recompensas sao sempre diretas.
- **Remocao e upgrade de cartas.** A curva de poder vem da habilidade de classe.
- **Validacao autoritativa de combate no servidor.** O jogo e single player, cheat prejudica apenas
  quem cheata. Isso so seria revisto se algum dia existir ranking.
- **Lacaios alvejaveis.** Lacaios sao presenca visual e efeito mecanico, nunca unidades no campo.
