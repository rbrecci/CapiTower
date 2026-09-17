<?php
defined('CAPITOWER') or exit('Acesso negado');

// Conexao PDO unica por requisicao (docs/04-arquitetura.md secao 3 e 7). Toda query do
// projeto passa por aqui, sempre com prepared statements.
class Database
{
    private static ?PDO $instancia = null;

    public static function conexao(): PDO
    {
        if (self::$instancia !== null) {
            return self::$instancia;
        }

        $config = require __DIR__ . '/../config/config.php';
        $db = $config['db'];

        $dsn = "mysql:host={$db['host']};dbname={$db['nome']};charset={$db['charset']}";

        self::$instancia = new PDO($dsn, $db['usuario'], $db['senha'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);

        return self::$instancia;
    }
}
