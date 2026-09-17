<?php
// Shell estatico (docs/06-roadmap.md): uma pagina so, sem logica de servidor.
// Toda a torre roda no cliente, em assets/js (docs/04-arquitetura.md secao 2).
// Fase 1 tinha um combate avulso; Fase 2 acrescenta a torre inteira, orquestrada por
// assets/js/ui/screens.js, sem mudar esse contrato.
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CapiTower</title>
  <link rel="stylesheet" href="assets/css/base.css">
  <link rel="stylesheet" href="assets/css/layout.css">
  <link rel="stylesheet" href="assets/css/combat.css">
  <link rel="stylesheet" href="assets/css/cards.css">
  <link rel="stylesheet" href="assets/css/tower.css">
</head>
<body>
  <div id="fundo-cenario"></div>
  <div id="app"></div>
  <script type="module" src="assets/js/main.js"></script>
</body>
</html>
