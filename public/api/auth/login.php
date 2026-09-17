<?php
define('CAPITOWER', true);
require_once __DIR__ . '/../../../app/core/Response.php';
require_once __DIR__ . '/../../../app/core/Request.php';
require_once __DIR__ . '/../../../app/core/Database.php';
require_once __DIR__ . '/../../../app/core/Auth.php';

Auth::iniciarSessao();
Request::exigirMetodo('POST');

$identificador = Request::texto('usuario');
$senha = Request::texto('senha');
$ip = Request::ip();

if ($identificador === '' || $senha === '') {
    Response::erro('VALIDACAO', 'Informe usuario e senha', 422);
}

try {
    if (Auth::limiteExcedido($ip)) {
        Response::erro('RATE_LIMIT', 'Muitas tentativas de login. Tente de novo mais tarde.', 429);
    }

    $linha = Auth::buscarPorUsuarioOuEmail($identificador);
    $senhaCorreta = $linha !== null && password_verify($senha, $linha['senha_hash']);

    Auth::registrarTentativa($ip, $identificador, $senhaCorreta);

    if (!$senhaCorreta) {
        Response::erro('CREDENCIAIS_INVALIDAS', 'Usuario ou senha invalidos', 401);
    }

    Auth::marcarUltimoLogin((int) $linha['id']);
    Auth::abrirSessaoPara((int) $linha['id']);

    Response::ok([
        'usuario' => [
            'id' => (int) $linha['id'],
            'usuario' => Request::escapar($linha['usuario']),
            'email' => Request::escapar($linha['email']),
        ],
    ]);
} catch (PDOException $e) {
    Response::erro('ERRO_INTERNO', 'Nao foi possivel entrar', 500);
}
