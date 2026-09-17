<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';

Auth::iniciarSessao();
Request::exigirMetodo('POST');

$usuario = Request::texto('usuario');
$email = Request::texto('email');
$senha = Request::texto('senha');

if (!preg_match('/^[a-zA-Z0-9_]{3,24}$/', $usuario)) {
    Response::erro('VALIDACAO', 'Usuario deve ter de 3 a 24 letras, numeros ou _', 422);
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 160) {
    Response::erro('VALIDACAO', 'E-mail invalido', 422);
}
if (strlen($senha) < 6) {
    Response::erro('VALIDACAO', 'Senha deve ter pelo menos 6 caracteres', 422);
}

try {
    if (Auth::usuarioExiste($usuario, $email)) {
        Response::erro('USUARIO_EXISTE', 'Usuario ou e-mail ja cadastrado', 409);
    }

    $novo = Auth::registrar($usuario, $email, $senha);
    Auth::abrirSessaoPara($novo['id']);

    Response::ok([
        'usuario' => [
            'id' => $novo['id'],
            'usuario' => Request::escapar($novo['usuario']),
            'email' => Request::escapar($novo['email']),
        ],
    ], 201);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel criar a conta', 500);
}
