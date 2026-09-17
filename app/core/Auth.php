<?php
defined('CAPITOWER') or exit('Acesso negado');

require_once __DIR__ . '/Database.php';

// Sessao PHP por cookie, cadastro com password_hash e rate limit de login por IP
// (docs/04-arquitetura.md secao 7). Sem JWT, sem token em localStorage.
class Auth
{
    private static array $config;
    private static bool $sessaoIniciada = false;

    private static function config(): array
    {
        if (!isset(self::$config)) {
            self::$config = require __DIR__ . '/../config/config.php';
        }
        return self::$config;
    }

    public static function iniciarSessao(): void
    {
        if (self::$sessaoIniciada || session_status() === PHP_SESSION_ACTIVE) {
            self::$sessaoIniciada = true;
            return;
        }

        $sessao = self::config()['sessao'];
        session_name($sessao['nome']);
        session_set_cookie_params([
            'lifetime' => 0,
            'path' => '/',
            'httponly' => $sessao['httponly'],
            'samesite' => $sessao['samesite'],
            'secure' => $sessao['secure'],
        ]);
        session_start();
        self::$sessaoIniciada = true;
    }

    public static function usuarioId(): ?int
    {
        self::iniciarSessao();
        return $_SESSION['usuario_id'] ?? null;
    }

    public static function usuarioLogado(): bool
    {
        return self::usuarioId() !== null;
    }

    public static function exigirLogin(): int
    {
        $id = self::usuarioId();
        if ($id === null) {
            Response::erro('AUTH_REQUIRED', 'Faca login', 401);
        }
        return $id;
    }

    public static function abrirSessaoPara(int $usuarioId): void
    {
        self::iniciarSessao();
        session_regenerate_id(true);
        $_SESSION['usuario_id'] = $usuarioId;
    }

    public static function encerrarSessao(): void
    {
        self::iniciarSessao();
        $_SESSION = [];
        session_destroy();
    }

    // ------------------------------------------------------------------ rate limit de login

    public static function limiteExcedido(string $ip): bool
    {
        $login = self::config()['login'];
        $pdo = Database::conexao();
        $stmt = $pdo->prepare(
            'SELECT COUNT(*) FROM login_tentativas
             WHERE ip = :ip AND sucesso = 0 AND criado_em >= (NOW() - INTERVAL :janela SECOND)'
        );
        $stmt->execute(['ip' => $ip, 'janela' => $login['janela_segundos']]);
        return (int) $stmt->fetchColumn() >= $login['max_tentativas'];
    }

    public static function registrarTentativa(string $ip, ?string $usuario, bool $sucesso): void
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare(
            'INSERT INTO login_tentativas (ip, usuario, sucesso) VALUES (:ip, :usuario, :sucesso)'
        );
        $stmt->execute(['ip' => $ip, 'usuario' => $usuario, 'sucesso' => $sucesso ? 1 : 0]);
    }

    // ------------------------------------------------------------------------- cadastro/login

    public static function registrar(string $usuario, string $email, string $senha): array
    {
        $pdo = Database::conexao();
        $hash = password_hash($senha, PASSWORD_DEFAULT);

        $stmt = $pdo->prepare(
            'INSERT INTO usuarios (usuario, email, senha_hash) VALUES (:usuario, :email, :hash)'
        );
        $stmt->execute(['usuario' => $usuario, 'email' => $email, 'hash' => $hash]);
        $id = (int) $pdo->lastInsertId();

        $pdo->prepare('INSERT INTO usuario_estatisticas (usuario_id) VALUES (:id)')
            ->execute(['id' => $id]);

        return ['id' => $id, 'usuario' => $usuario, 'email' => $email];
    }

    public static function buscarPorUsuarioOuEmail(string $identificador): ?array
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare('SELECT * FROM usuarios WHERE usuario = :usuario OR email = :email LIMIT 1');
        $stmt->execute(['usuario' => $identificador, 'email' => $identificador]);
        $linha = $stmt->fetch();
        return $linha ?: null;
    }

    public static function usuarioExiste(string $usuario, string $email): bool
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare('SELECT COUNT(*) FROM usuarios WHERE usuario = :usuario OR email = :email');
        $stmt->execute(['usuario' => $usuario, 'email' => $email]);
        return (int) $stmt->fetchColumn() > 0;
    }

    public static function marcarUltimoLogin(int $usuarioId): void
    {
        $pdo = Database::conexao();
        $pdo->prepare('UPDATE usuarios SET ultimo_login = NOW() WHERE id = :id')
            ->execute(['id' => $usuarioId]);
    }
}
