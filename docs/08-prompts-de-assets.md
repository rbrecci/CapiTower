# 08. Prompts de assets: inimigos do MVP Flet

> Prompts para gerar a arte dos 26 inimigos que hoje são silhueta com ícone (`ENEMY_ICONS` em
> `flet_mvp/capitower/ui.py`). Gerados no app do Gemini (gemini.google.com), um por vez, com a
> `capimaga.png` anexada como referência de estilo. Saída: `flet_mvp/assets/<id>.png` em 512px
> e entrada em `ENEMY_ART`.

## Estilo-casa (derivado de capimaga.png e gertrudes.png)

Mascote cartoon: contorno preto grosso e limpo, cel shading chapado com pouco gradiente, pelo
marrom-alaranjado, formas simples e legíveis, corpo inteiro em pé, fundo branco liso, sem texto.
Tudo que não é capivara (sapo, rato, halter, frasco, bolha, sobremesa, vaso) segue o mesmo traço.

**Bloco de estilo** (vai no começo de todo prompt, com a `capimaga.png` anexada na mesma mensagem):

```
Generate an image in the exact same art style as the attached reference character: cartoon game mascot illustration, clean thick black outlines, flat cel shading with minimal soft gradients, simple readable shapes, full body standing pose, slight 3/4 view, isolated on a plain pure white background, no text, no watermark, no scenery. Same line weight, same fur rendering and same proportions logic as the reference.
```

**Fechamento** (vai no fim de todo prompt):

```
Single character only, centered, whole body visible with margin around it, square composition.
```

**Se o Gemini sair do traço:** repetir "same art style as the attached reference" e pedir "no
realistic shading, no 3D render". Se sair com cenário, pedir "plain white background only".

**Negativo** (o app do Gemini não tem campo negativo; usar em texto se precisar corrigir):
realistic, 3D render, photo, painterly, sketch lines, text, watermark, background scenery,
multiple characters, cropped body.

## Ordem de geração

Chefes -> elites -> monstros comuns. Gertrudes já tem arte e fica fora.

---

## Chefes

### dorival (Dorival Supino, andar 10)
```
[estilo] A male capybara bodybuilder boss who only trains chest and never legs: enormous inflated pectorals and arms, absurdly thin skinny legs, wearing a black stringer tank top and lifting belt, a loaded barbell resting across his shoulders, smug proud grin, chin up. Warm brown fur. [fechamento]
```

### marlene (Marlene Cardio, andar 20)
```
[estilo] A lean athletic female capybara boss who never stops moving: pink headband, matching wristbands, bright running shoes, sporty crop top and shorts, caught mid-run with one knee high and arms pumping, sweat drops flying, intense energetic wide-eyed expression, small motion lines. Warm brown fur. [fechamento]
```

### helio (Professor Helio Whey, andar 30)
```
[estilo] A mad scientist capybara boss, the family chemist: white lab coat over a tight gym shirt showing muscles, round goggles pushed up on his forehead, wild tufts of fur, holding up a protein shaker bottle overflowing with bubbling glowing green liquid, other hand holding a test tube, manic grin. Warm brown fur. [fechamento]
```

### gemeo_a (Gêmeo Rosca, esquerdo, andar 40)
```
[estilo] A muscular capybara bodybuilder twin doing a bicep curl: huge round biceps, red sweatband on the head, red sleeveless gym shirt with a bold letter-free logo shape, curling a heavy dumbbell with his LEFT arm while flexing, cocky wink, body turned slightly to the viewer's left. Warm brown fur. [fechamento]
```

### gemeo_b (Gêmeo Rosca, direito, andar 40)
Espelho horizontal de `gemeo_a` feito no Pillow (eles "treinam em espelho"), não se gera. Se
quiser distinguir, trocar a cor da faixa pra azul na edição.

### capitolino (Sargento Capitolino, andar 50)
```
[estilo] A stern military capybara sergeant boss, the Sovereign's personal guard: broad square build, olive-green dress uniform with gold epaulettes and buttons, a beret with a small pink flower pin, a whistle on a cord, standing at rigid attention holding a tall riot shield painted with a flower emblem, thick eyebrows, serious frown, chin scar. Warm brown fur. [fechamento]
```

---

## Elites

### elite1 (Capivara de Pulso, bloco O Poço)
```
[estilo] An elite capybara fighter with gigantic forearms and wrists far bigger than the rest of the body, white wrist wraps, damp fur with water drops, squeezing a steel hand-gripper until it bends, veins popping on the forearm, gritted teeth, slightly hunched stance. Warm brown fur. [fechamento]
```

### elite2 (Instrutora de Cross, bloco A Academia)
```
[estilo] An elite female capybara cross-training instructor: athletic build, high ponytail of fur, whistle in mouth, stopwatch hanging from the neck, fingerless gloves, black leggings and a neon-yellow sports top, holding a heavy kettlebell in one hand and pointing at the viewer with the other, bossy commanding expression. Warm brown fur. [fechamento]
```

### elite3 (Cobaia Alfa, bloco O Laboratório)
```
[estilo] An elite mutated lab-test capybara: asymmetric body with one massively oversized arm, patches of glowing toxic-green fur, a yellow ear tag reading nothing (blank tag), a few thin transparent tubes taped to the back leaking green drops, cracked stitches, one eye bigger than the other, unsettling toothy grin. Warm brown fur with green patches. [fechamento]
```

### elite4 (Chef de Cozinha, bloco O Refeitório)
```
[estilo] An elite fat and muscular capybara chef: big round belly over thick arms, tall white chef toque, white double-breasted chef jacket with the sleeves rolled up, red neckerchief, curly mustache, holding a giant ladle like a club and a frying pan as a shield, furious red-faced yelling expression. Warm brown fur. [fechamento]
```

### elite5 (Capita da Guarda, bloco O Jardim Suspenso)
```
[estilo] An elite female capybara guard captain: ornate silver plate armor engraved with flower motifs, a short pink cape, helmet with a tall white plume held under one arm, a halberd in the other hand, a rose tucked in the breastplate, proud disciplined posture, calm confident expression. Warm brown fur. [fechamento]
```

---

## Monstros comuns

### capivarinha (Capivarinha Encharcada, bloco 1)
```
[estilo] A tiny soaked baby capybara: small chubby body, fur plastered down and dripping water, puddle at its feet, big shiny angry eyes, tiny bared teeth, fists clenched, trying hard to look threatening and failing. Warm brown fur, slightly darker because wet. [fechamento]
```

### sapo (Sapo Musculoso, bloco 1)
```
[estilo] A hulking muscular green toad: massive shoulders and arms, warty slimy skin, bulging yellow eyes, wide flat mouth in a grumpy frown, wearing purple gym shorts and a lifting belt, crouched in a squat guard stance with fists up. Cartoon toad in the same style as the capybara reference. [fechamento]
```

### rato (Rato de Academia, bloco 1)
```
[estilo] A skinny sneaky grey gym rat: long thin tail, oversized sweatband, baggy tank top, clutching a stolen protein bar in one paw and a small sack over the shoulder, shifty narrowed eyes, sly grin, tiptoeing pose. Cartoon rat in the same style as the capybara reference. [fechamento]
```

### halter (Halter Vivo, bloco 2)
```
[estilo] A living iron dumbbell monster: heavy black cast-iron dumbbell with two big round weight plates, a grumpy face on the bar between the plates, stubby little arms and legs sticking out of the plates, cracks and scratches on the metal, standing in a heavy stomp pose. Cartoon object monster in the same style as the capybara reference. [fechamento]
```

### spinning (Capivara do Spinning, bloco 2)
```
[estilo] A capybara riding a stationary spinning bike at full speed: aerodynamic cycling helmet, sports goggles, tight cycling jersey, legs a blur with motion lines, sweat flying, gritted determined face leaning over the handlebars. The bike is part of the character, drawn in the same cartoon style. Warm brown fur. [fechamento]
```

### personal (Personal Trainer, bloco 2)
```
[estilo] A capybara personal trainer: fit build, tight polo shirt with a collar, whistle around the neck, clipboard in one hand, other hand raised pointing upward shouting encouragement, cap worn backwards, motivational over-enthusiastic smile, sport shoes. Warm brown fur. [fechamento]
```

### frasco (Frasco Ambulante, bloco 3)
```
[estilo] A walking glass flask monster: round-bottom laboratory flask filled with bubbling purple poison liquid, a cork on top, a mischievous face visible through the glass, two stubby legs and two thin arms, small green drips falling from the rim, wobbling pose. Cartoon object monster in the same style as the capybara reference. [fechamento]
```

### experimental (Capivara Experimental, bloco 3)
```
[estilo] A patched-up experimental capybara: body covered in stitched square patches of different fur tones, two metal bolts on the neck, electrodes with short wires on the head, one arm mechanical and oversized, mismatched eyes, dazed dangerous expression, unbalanced stance. Warm brown fur with grey patches. [fechamento]
```

### bolha (Bolha de Soro, bloco 3)
```
[estilo] A big blob of translucent glowing blue serum: round jelly bubble body with soft highlights and a faint reflection, a simple sleepy face with droopy eyes and a small mouth, two little jelly arms, a small IV drip needle stuck in its top, sitting like a dome on the floor. Cartoon blob monster in the same style as the capybara reference. [fechamento]
```

### marmita (Capivara de Marmita, bloco 4)
```
[estilo] A fat lazy capybara hugging a huge aluminum lunchbox: round belly, food stains on a white shirt, a fork in one hand, mouth full with cheeks puffed out, greasy happy half-closed eyes, sitting heavily on the ground. Warm brown fur. [fechamento]
```

### garcom (Garçom Bombado, bloco 4)
```
[estilo] A gigantic bodybuilder capybara waiter: towering muscular build, black vest and bow tie over a white shirt stretched by the muscles, a white cloth over one forearm, balancing a silver serving tray with a cloche dome high on one hand, other fist clenched, calm polite smile that looks threatening. Warm brown fur. [fechamento]
```

### sobremesa (Sobremesa Viva, bloco 4)
```
[estilo] A living dessert monster: a tall wobbly caramel flan pudding with a swirl of whipped cream and a red cherry on top, an angry face with furrowed brows on the front, two short arms made of pudding, caramel sauce dripping down, sitting on a small plate. Cartoon food monster in the same style as the capybara reference. [fechamento]
```

### guarda (Guarda de Avental, bloco 5)
```
[estilo] A capybara royal guard wearing a floral pink apron over chainmail and shoulder plates: round helmet with a small flower on it, a tall kite shield painted with a rose, a spear in the other hand, standing firm and stoic, serious face. Warm brown fur. [fechamento]
```

### jardineira (Jardineira Furiosa, bloco 5)
```
[estilo] A furious female capybara gardener: wide straw hat, dirt-stained green overalls, gardening gloves, brandishing giant hedge shears with both hands, teeth bared in rage, eyebrows sharp, a few petals flying around, aggressive forward-leaning stance. Warm brown fur. [fechamento]
```

### vaso (Vaso Sentinela, bloco 5)
```
[estilo] A living flower vase sentinel: an ornate white ceramic vase with pink patterns, a big pink glowing flower blooming on top with a calm serene face in its center, thick roots coming out of the bottom acting as legs, small leaves as arms raised in a healing gesture, soft glow around the flower. Cartoon plant monster in the same style as the capybara reference. [fechamento]
```
