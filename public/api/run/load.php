<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';
require_once __DIR__ . '/../../../app/models/Run.php';

Auth::iniciarSessao();
$usuarioId = Auth::exigirLogin();

try {
    $run = Run::ativa($usuarioId);
    Response::ok(['run' => $run]);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel carregar a run', 500);
}
