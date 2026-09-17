<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';
require_once __DIR__ . '/../../../app/models/Run.php';
require_once __DIR__ . '/../../../app/models/Meta.php';

Auth::iniciarSessao();
Request::exigirMetodo('POST');
$usuarioId = Auth::exigirLogin();

$runId = Request::inteiro('run_id');
$resultado = Request::texto('resultado');
$estadoJson = Request::campo('estado_json');

if ($runId === null || !in_array($resultado, ['vitoria', 'derrota'], true) || !is_array($estadoJson)) {
    Response::erro('VALIDACAO', 'run_id, resultado (vitoria|derrota) e estado_json sao obrigatorios', 422);
}

try {
    $run = Run::finalizar($usuarioId, $runId, $resultado, $estadoJson);
    if ($run === null) {
        Response::erro('RUN_INVALIDA', 'Run nao encontrada ou ja finalizada', 404);
    }

    $contexto = Meta::contextoDaRun($estadoJson, $resultado, (int) $run['andar_maximo']);
    $desbloqueios = Meta::avaliarObjetivos($usuarioId, $contexto);

    Response::ok(['run' => $run, 'desbloqueios' => $desbloqueios]);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel finalizar a run', 500);
}
