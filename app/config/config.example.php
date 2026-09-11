<?php
/**
 * Modelo de configuracao do CapiTower.
 *
 * Copie este arquivo para config.php e ajuste os valores.
 * config.php esta no .gitignore e nunca deve ser versionado.
 */

// Bloqueia acesso direto pelo navegador caso o .htaccess seja ignorado pelo host.
defined('CAPITOWER') or exit('Acesso negado');

return [
    'db' => [
        'host'    => 'localhost',
        'nome'    => 'capitower',
        'usuario' => 'root',
        'senha'   => '',
        'charset' => 'utf8mb4',
    ],

    'app' => [
        // 'dev' mostra erro na tela, 'prod' esconde e grava em log.
        'ambiente' => 'dev',
        'nome'     => 'CapiTower',
        'versao'   => '0.1.0',
    ],

    'sessao' => [
        'nome'     => 'capitower_sid',
        'httponly' => true,
        'samesite' => 'Lax',
        // true apenas em producao com HTTPS
        'secure'   => false,
    ],

    'login' => [
        // Tentativas por IP dentro da janela, antes de bloquear.
        'max_tentativas'  => 8,
        'janela_segundos' => 900,
    ],
];
