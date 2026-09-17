<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';
require_once __DIR__ . '/../../../app/models/Meta.php';

Auth::iniciarSessao();
$usuarioId = Auth::exigirLogin();

try {
    Response::ok(['objetivos' => Meta::objetivos($usuarioId)]);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel carregar os objetivos', 500);
}
