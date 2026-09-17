<?php
defined('CAPITOWER') or exit('Acesso negado');

require_once __DIR__ . '/../core/Database.php';

// Meta progressao (docs/04-arquitetura.md secao 4, docs/06-roadmap.md Fase 5,
// docs/07-decisoes.md D12/D13). perfil() devolve as estatisticas acumuladas por Run::finalizar;
// objetivos() devolve a lista real com progresso por usuario; avaliarObjetivos() e chamado por
// run/finish.php depois que a run termina, para travar os objetivos batidos por essa run.
class Meta
{
    public static function perfil(int $usuarioId): array
    {
        $pdo = Database::conexao();

        $stmtUsuario = $pdo->prepare('SELECT usuario, criado_em, ultimo_login FROM usuarios WHERE id = :id');
        $stmtUsuario->execute(['id' => $usuarioId]);
        $usuario = $stmtUsuario->fetch();

        $stmtStats = $pdo->prepare('SELECT * FROM usuario_estatisticas WHERE usuario_id = :id');
        $stmtStats->execute(['id' => $usuarioId]);
        $stats = $stmtStats->fetch();

        if (!$stats) {
            $stats = [
                'runs_totais' => 0, 'vitorias' => 0, 'andar_recorde' => 0,
                'pontos_meta_total' => 0, 'chefes_derrotados' => 0,
            ];
        } else {
            unset($stats['usuario_id'], $stats['atualizado_em']);
        }

        return ['usuario' => $usuario, 'estatisticas' => $stats];
    }

    public static function objetivos(int $usuarioId): array
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare(
            'SELECT o.slug, o.nome, o.descricao, o.condicao, o.recompensa_tipo, o.recompensa_ref, o.oculto,
                    uo.progresso, uo.concluido_em
             FROM objetivos o
             LEFT JOIN usuario_objetivos uo ON uo.objetivo_id = o.id AND uo.usuario_id = :usuario_id
             WHERE o.oculto = 0 OR uo.concluido_em IS NOT NULL
             ORDER BY o.ordem'
        );
        $stmt->execute(['usuario_id' => $usuarioId]);
        return $stmt->fetchAll();
    }

    // Monta o contexto que condicaoBatida() precisa a partir do que o cliente ja manda em
    // estado_json (docs/04-arquitetura.md secao 5) mais o resultado e o andar maximo que
    // Run::finalizar acabou de gravar. deck_arquetipos_distintos ignora copias temporarias do
    // evento Vestiario, que nao contam como parte do baralho de verdade do jogador.
    public static function contextoDaRun(array $estadoJson, string $resultado, int $andarMaximo): array
    {
        $pdo = Database::conexao();

        $deckPermanente = array_values(array_filter(
            $estadoJson['deck'] ?? [],
            static fn(array $carta): bool => empty($carta['temporaria'])
        ));
        $ids = array_values(array_unique(array_column($deckPermanente, 'id')));

        $arquetiposDistintos = 0;
        if ($ids !== []) {
            $marcadores = implode(',', array_fill(0, count($ids), '?'));
            $stmt = $pdo->prepare("SELECT COUNT(DISTINCT arquetipo_id) FROM cartas WHERE slug IN ($marcadores)");
            $stmt->execute($ids);
            $arquetiposDistintos = (int) $stmt->fetchColumn();
        }

        return [
            'resultado' => $resultado,
            'andar_maximo' => $andarMaximo,
            'chefes_derrotados' => is_array($estadoJson['chefes_derrotados'] ?? null)
                ? $estadoJson['chefes_derrotados'] : [],
            'recompensas_habilidade' => (int) ($estadoJson['recompensas_habilidade'] ?? 0),
            'deck_arquetipos_distintos' => $arquetiposDistintos,
        ];
    }

    // Avalia os objetivos ainda nao concluidos pelo usuario contra o contexto desta run e trava
    // (usuario_objetivos + usuario_desbloqueios) os que bateram. Devolve o que foi desbloqueado
    // agora, para o cliente mostrar na tela de fim de run. Idempotente: rodar duas vezes para a
    // mesma run (ou para runs diferentes que ja bateram o mesmo objetivo) nao desbloqueia de
    // novo, porque so avalia objetivo sem concluido_em e usuario_desbloqueios tem chave primaria
    // composta (usuario_id, tipo, ref).
    public static function avaliarObjetivos(int $usuarioId, array $contexto): array
    {
        $pdo = Database::conexao();

        $stmt = $pdo->prepare(
            'SELECT o.id, o.slug, o.nome, o.descricao, o.condicao, o.recompensa_tipo, o.recompensa_ref
             FROM objetivos o
             LEFT JOIN usuario_objetivos uo ON uo.objetivo_id = o.id AND uo.usuario_id = :usuario_id
             WHERE uo.concluido_em IS NULL
             ORDER BY o.ordem'
        );
        $stmt->execute(['usuario_id' => $usuarioId]);
        $pendentes = $stmt->fetchAll();

        $desbloqueados = [];
        foreach ($pendentes as $objetivo) {
            $condicao = json_decode($objetivo['condicao'], true);
            if (!is_array($condicao) || !self::condicaoBatida($condicao, $contexto)) {
                continue;
            }

            $pdo->prepare(
                'INSERT INTO usuario_objetivos (usuario_id, objetivo_id, progresso, concluido_em)
                 VALUES (:usuario_id, :objetivo_id, 1, NOW())
                 ON DUPLICATE KEY UPDATE
                   progresso = 1,
                   concluido_em = COALESCE(concluido_em, NOW())'
            )->execute(['usuario_id' => $usuarioId, 'objetivo_id' => $objetivo['id']]);

            $pdo->prepare(
                'INSERT IGNORE INTO usuario_desbloqueios (usuario_id, tipo, ref, origem)
                 VALUES (:usuario_id, :tipo, :ref, :origem)'
            )->execute([
                'usuario_id' => $usuarioId,
                'tipo' => $objetivo['recompensa_tipo'],
                'ref' => $objetivo['recompensa_ref'],
                'origem' => $objetivo['slug'],
            ]);

            $desbloqueados[] = [
                'slug' => $objetivo['slug'],
                'nome' => $objetivo['nome'],
                'descricao' => $objetivo['descricao'],
                'recompensa_tipo' => $objetivo['recompensa_tipo'],
                'recompensa_ref' => $objetivo['recompensa_ref'],
            ];
        }

        return $desbloqueados;
    }

    private static function condicaoBatida(array $condicao, array $contexto): bool
    {
        switch ($condicao['tipo'] ?? null) {
            case 'andar_alcancado':
                return $contexto['andar_maximo'] >= $condicao['valor'];
            case 'vitoria':
                return $contexto['resultado'] === 'vitoria';
            case 'chefe_derrotado':
                return in_array($condicao['slug'], $contexto['chefes_derrotados'], true);
            case 'vitoria_sem_habilidade':
                return $contexto['resultado'] === 'vitoria' && $contexto['recompensas_habilidade'] === 0;
            case 'baralho_arquetipo_unico':
                return $contexto['deck_arquetipos_distintos'] === 1;
            case 'derrota_precoce':
                return $contexto['resultado'] === 'derrota' && $contexto['andar_maximo'] <= $condicao['andar_maximo'];
            default:
                return false;
        }
    }
}
