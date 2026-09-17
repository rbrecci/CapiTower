<?php
defined('CAPITOWER') or exit('Acesso negado');

require_once __DIR__ . '/../core/Database.php';

class User
{
    public static function porId(int $id): ?array
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare(
            'SELECT id, usuario, email, criado_em, ultimo_login FROM usuarios WHERE id = :id'
        );
        $stmt->execute(['id' => $id]);
        $linha = $stmt->fetch();
        return $linha ?: null;
    }
}
