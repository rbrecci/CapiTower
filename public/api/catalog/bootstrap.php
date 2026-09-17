<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';
require_once __DIR__ . '/../../../app/models/Catalog.php';

Auth::iniciarSessao();

try {
    Response::ok(Catalog::bootstrap(Auth::usuarioId()));
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel carregar o catalogo', 500);
}
