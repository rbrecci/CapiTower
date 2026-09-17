<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';
require_once __DIR__ . '/../../../app/models/User.php';

Auth::iniciarSessao();
$usuarioId = Auth::exigirLogin();

$usuario = User::porId($usuarioId);
if ($usuario === null) {
    Response::erro('NAO_ENCONTRADO', 'Usuario nao encontrado', 404);
}

$usuario['usuario'] = Request::escapar($usuario['usuario']);
$usuario['email'] = Request::escapar($usuario['email']);

Response::ok(['usuario' => $usuario]);
