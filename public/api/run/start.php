<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';
require_once __DIR__ . '/../../../app/models/Catalog.php';
require_once __DIR__ . '/../../../app/models/Run.php';

Auth::iniciarSessao();
Request::exigirMetodo('POST');
$usuarioId = Auth::exigirLogin();

// Unica classe pronta ate a Fase 6 (Brutamontes e Ligeira ainda nao tem cartas no banco).
$classeSlug = 'capimaga';

try {
    $classeId = Catalog::classeIdPorSlug($classeSlug);
    if ($classeId === null) {
        Response::erro('CATALOGO_VAZIO', 'Catalogo nao foi semeado no banco', 500);
    }

    $hpInicial = Catalog::hpInicialDaClasse($classeId);
    $seed = random_int(0, 4294967295);

    $run = Run::criar($usuarioId, $classeId, $seed, $hpInicial, $classeSlug);
    Response::ok(['run' => $run], 201);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel comecar a run', 500);
}
