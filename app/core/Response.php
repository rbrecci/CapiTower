<?php
defined('CAPITOWER') or exit('Acesso negado');

// Envelope JSON padrao de toda a API (docs/04-arquitetura.md secao 4).
class Response
{
    public static function ok(array $data = [], int $status = 200): void
    {
        self::enviar($status, ['ok' => true, 'data' => $data]);
    }

    public static function erro(string $codigo, string $mensagem, int $status = 400): void
    {
        self::enviar($status, ['ok' => false, 'error' => ['code' => $codigo, 'message' => $mensagem]]);
    }

    private static function enviar(int $status, array $corpo): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($corpo, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit;
    }
}
