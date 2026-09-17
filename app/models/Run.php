<?php
defined('CAPITOWER') or exit('Acesso negado');

require_once __DIR__ . '/../core/Database.php';

// Save/load da run (docs/04-arquitetura.md secao 5). O servidor nao entende o conteudo do
// snapshot, so guarda; quem monta e le estado_json e o cliente (docs secao 2).
//
// Desvio documentado do exemplo da secao 5: "deck" aqui e uma lista de objetos
// {"id":"cm_costela","temporaria":false} em vez de ids numericos soltos, porque as cartas
// reais usam slug (string) como id, e uma copia temporaria do evento Vestiario (D03) precisa
// ficar marcavel individualmente mesmo quando o baralho tem duas copias do mesmo id.
class Run
{
    public static function ativa(int $usuarioId): ?array
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare(
            "SELECT r.*, c.slug AS classe_slug FROM runs r
             JOIN classes c ON c.id = r.classe_id
             WHERE r.usuario_id = :usuario_id AND r.estado = 'ativa'
             ORDER BY r.id DESC LIMIT 1"
        );
        $stmt->execute(['usuario_id' => $usuarioId]);
        $linha = $stmt->fetch();
        return $linha ? self::formatar($linha) : null;
    }

    public static function porIdDoUsuario(int $usuarioId, int $runId): ?array
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare(
            'SELECT r.*, c.slug AS classe_slug FROM runs r
             JOIN classes c ON c.id = r.classe_id
             WHERE r.id = :id AND r.usuario_id = :usuario_id'
        );
        $stmt->execute(['id' => $runId, 'usuario_id' => $usuarioId]);
        $linha = $stmt->fetch();
        return $linha ? self::formatar($linha) : null;
    }

    public static function criar(int $usuarioId, int $classeId, int $seed, int $hpInicial, string $classeSlug): array
    {
        $pdo = Database::conexao();

        // Uma run ativa por usuario. Comecar uma nova abandona a anterior, se existir.
        $pdo->prepare("UPDATE runs SET estado = 'abandonada' WHERE usuario_id = :id AND estado = 'ativa'")
            ->execute(['id' => $usuarioId]);

        $estadoJson = [
            'versao' => 1,
            'classe' => $classeSlug,
            'seed' => $seed,
            'andar' => 0,
            'hp' => $hpInicial,
            'hp_max' => $hpInicial,
            'forca_permanente' => 0,
            'nivel_habilidade' => 1,
            'deck' => [],
            'modificadores' => [],
            'pontos_recompensa' => 0,
            'status' => 'jogando',
            'fraqueza_proximo_combate' => 0,
            'cura_diferida' => 0,
        ];

        $stmt = $pdo->prepare(
            'INSERT INTO runs (usuario_id, classe_id, seed, estado, andar_atual, andar_maximo,
                                hp_atual, hp_max, nivel_habilidade, estado_json)
             VALUES (:usuario_id, :classe_id, :seed, "ativa", 0, 0, :hp_atual, :hp_max, 1, :estado_json)'
        );
        $stmt->execute([
            'usuario_id' => $usuarioId,
            'classe_id' => $classeId,
            'seed' => $seed,
            'hp_atual' => $hpInicial,
            'hp_max' => $hpInicial,
            'estado_json' => json_encode($estadoJson, JSON_UNESCAPED_UNICODE),
        ]);

        $runId = (int) $pdo->lastInsertId();
        return self::porIdDoUsuario($usuarioId, $runId);
    }

    // Grava o snapshot. So aceita se a run for do usuario e ainda estiver ativa (uma run
    // terminada nao recebe mais save).
    public static function salvar(int $usuarioId, int $runId, array $estadoJson): ?array
    {
        $pdo = Database::conexao();
        $atual = self::porIdDoUsuario($usuarioId, $runId);
        if ($atual === null || $atual['estado'] !== 'ativa') {
            return null;
        }

        $andar = max(0, (int) ($estadoJson['andar'] ?? 0));
        $hp = max(0, (int) ($estadoJson['hp'] ?? $atual['hp_max']));
        $hpMax = max(1, (int) ($estadoJson['hp_max'] ?? $atual['hp_max']));
        $nivelHabilidade = max(1, (int) ($estadoJson['nivel_habilidade'] ?? 1));

        $stmt = $pdo->prepare(
            'UPDATE runs SET
                estado_json = :estado_json,
                andar_atual = :andar,
                andar_maximo = GREATEST(andar_maximo, :andar2),
                hp_atual = :hp,
                hp_max = :hp_max,
                nivel_habilidade = :nivel
             WHERE id = :id AND usuario_id = :usuario_id'
        );
        $stmt->execute([
            'estado_json' => json_encode($estadoJson, JSON_UNESCAPED_UNICODE),
            'andar' => $andar,
            'andar2' => $andar,
            'hp' => $hp,
            'hp_max' => $hpMax,
            'nivel' => $nivelHabilidade,
            'id' => $runId,
            'usuario_id' => $usuarioId,
        ]);

        return self::porIdDoUsuario($usuarioId, $runId);
    }

    public static function finalizar(int $usuarioId, int $runId, string $resultado, array $estadoJson): ?array
    {
        $pdo = Database::conexao();
        $atual = self::porIdDoUsuario($usuarioId, $runId);
        if ($atual === null || $atual['estado'] !== 'ativa') {
            return null;
        }

        $andarMaximo = max($atual['andar_maximo'], (int) ($estadoJson['andar'] ?? 0));
        $pontosRecompensa = (int) ($estadoJson['pontos_recompensa'] ?? 0);
        $pontosMeta = $andarMaximo * 10 + $pontosRecompensa * 5 + ($resultado === 'vitoria' ? 100 : 0);
        $chefesDerrotados = is_array($estadoJson['chefes_derrotados'] ?? null)
            ? count($estadoJson['chefes_derrotados']) : 0;

        $stmt = $pdo->prepare(
            "UPDATE runs SET
                estado = :estado,
                estado_json = :estado_json,
                andar_maximo = :andar_maximo,
                pontos_meta = :pontos_meta,
                finalizado_em = NOW()
             WHERE id = :id AND usuario_id = :usuario_id"
        );
        $stmt->execute([
            'estado' => $resultado,
            'estado_json' => json_encode($estadoJson, JSON_UNESCAPED_UNICODE),
            'andar_maximo' => $andarMaximo,
            'pontos_meta' => $pontosMeta,
            'id' => $runId,
            'usuario_id' => $usuarioId,
        ]);

        $pdo->prepare(
            'INSERT INTO usuario_estatisticas
                (usuario_id, runs_totais, vitorias, andar_recorde, pontos_meta_total, chefes_derrotados)
             VALUES (:usuario_id, 1, :vitoria, :andar_maximo, :pontos_meta, :chefes)
             ON DUPLICATE KEY UPDATE
               runs_totais = runs_totais + 1,
               vitorias = vitorias + VALUES(vitorias),
               andar_recorde = GREATEST(andar_recorde, VALUES(andar_recorde)),
               pontos_meta_total = pontos_meta_total + VALUES(pontos_meta_total),
               chefes_derrotados = chefes_derrotados + VALUES(chefes_derrotados)'
        )->execute([
            'usuario_id' => $usuarioId,
            'vitoria' => $resultado === 'vitoria' ? 1 : 0,
            'andar_maximo' => $andarMaximo,
            'pontos_meta' => $pontosMeta,
            'chefes' => $chefesDerrotados,
        ]);

        return self::porIdDoUsuario($usuarioId, $runId);
    }

    private static function formatar(array $linha): array
    {
        $linha['estado_json'] = json_decode($linha['estado_json'], true);
        return $linha;
    }
}
