<?php
defined('CAPITOWER') or exit('Acesso negado');

// Leitura e validacao de entrada (docs/04-arquitetura.md secao 3 e 7). Todo endpoint le o
// corpo da requisicao por aqui, nunca direto de $_POST/php://input.
class Request
{
    private static ?array $corpoJson = null;
    private static bool $corpoLido = false;

    private static function corpo(): array
    {
        if (!self::$corpoLido) {
            $bruto = file_get_contents('php://input');
            $decodificado = $bruto !== false && $bruto !== '' ? json_decode($bruto, true) : null;
            self::$corpoJson = is_array($decodificado) ? $decodificado : [];
            self::$corpoLido = true;
        }
        return self::$corpoJson;
    }

    public static function metodo(): string
    {
        return $_SERVER['REQUEST_METHOD'] ?? 'GET';
    }

    public static function exigirMetodo(string $esperado): void
    {
        if (self::metodo() !== $esperado) {
            Response::erro('METODO_INVALIDO', 'Metodo nao permitido', 405);
        }
    }

    // Le um campo do corpo JSON (POST) ou da query string (GET), nessa ordem de prioridade.
    public static function campo(string $nome, $padrao = null)
    {
        $corpo = self::corpo();
        if (array_key_exists($nome, $corpo)) {
            return $corpo[$nome];
        }
        if (array_key_exists($nome, $_GET)) {
            return $_GET[$nome];
        }
        return $padrao;
    }

    public static function texto(string $nome, string $padrao = ''): string
    {
        $valor = self::campo($nome, $padrao);
        return is_string($valor) ? trim($valor) : $padrao;
    }

    public static function inteiro(string $nome, ?int $padrao = null): ?int
    {
        $valor = self::campo($nome, $padrao);
        if ($valor === null || $valor === '') {
            return $padrao;
        }
        return filter_var($valor, FILTER_VALIDATE_INT) !== false ? (int) $valor : $padrao;
    }

    public static function ip(): string
    {
        return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    }

    // htmlspecialchars na saida de qualquer texto que venha do usuario (docs secao 7).
    public static function escapar(string $texto): string
    {
        return htmlspecialchars($texto, ENT_QUOTES, 'UTF-8');
    }
}
