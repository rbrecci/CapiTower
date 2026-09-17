<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';
require_once __DIR__ . '/../../../app/models/Run.php';

Auth::iniciarSessao();
Request::exigirMetodo('POST');
$usuarioId = Auth::exigirLogin();

$runId = Request::inteiro('run_id');
$estadoJson = Request::campo('estado_json');

if ($runId === null || !is_array($estadoJson)) {
    Response::erro('VALIDACAO', 'run_id e estado_json sao obrigatorios', 422);
}

try {
    $run = Run::salvar($usuarioId, $runId, $estadoJson);
    if ($run === null) {
        Response::erro('RUN_INVALIDA', 'Run nao encontrada ou ja finalizada', 404);
    }
    Response::ok(['run' => $run]);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel salvar a run', 500);
}
