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
    $perfil = Meta::perfil($usuarioId);
    if ($perfil['usuario'] !== false && $perfil['usuario'] !== null) {
        $perfil['usuario']['usuario'] = Request::escapar($perfil['usuario']['usuario']);
    }
    Response::ok($perfil);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel carregar o perfil', 500);
}
