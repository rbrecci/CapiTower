<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Auth.php';

Auth::iniciarSessao();
Request::exigirMetodo('POST');

Auth::encerrarSessao();
Response::ok([]);
