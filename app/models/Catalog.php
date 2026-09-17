<?php
defined('CAPITOWER') or exit('Acesso negado');

require_once __DIR__ . '/../core/Database.php';

// Monta o catalogo inteiro a partir do banco, no mesmo formato que
// public/assets/js/data/{cards,enemy,events,challenges}.json ja usavam como arquivo estatico
// (docs/04-arquitetura.md secao 4), para o cliente trocar a fonte sem mudar a leitura dos dados.
class Catalog
{
    private const NOMES_BLOCO = [
        1 => 'Bloco 1, O Poco',
        2 => 'Bloco 2, A Academia',
        3 => 'Bloco 3, O Laboratorio',
        4 => 'Bloco 4, O Refeitorio',
        5 => 'Bloco 5, O Jardim Suspenso',
    ];

    public static function bootstrap(?int $usuarioId = null): array
    {
        return [
            'classes' => self::classes(),
            'cartas' => self::cartas($usuarioId),
            'inimigos' => self::inimigos(),
            'eventos' => self::eventos(),
            'desafios' => self::desafios(),
        ];
    }

    private static function classes(): array
    {
        $pdo = Database::conexao();
        $linhas = $pdo->query(
            'SELECT slug, nome, descricao, mecanica_nome, mecanica_descricao,
                    habilidade_nome, habilidade_descricao, hp_inicial, acao_por_turno, inicial
             FROM classes ORDER BY ordem'
        )->fetchAll();

        foreach ($linhas as &$classe) {
            $niveis = $pdo->prepare(
                'SELECT hn.nivel, hn.descricao FROM habilidade_niveis hn
                 JOIN classes c ON c.id = hn.classe_id WHERE c.slug = :slug ORDER BY hn.nivel'
            );
            $niveis->execute(['slug' => $classe['slug']]);
            $classe['habilidade_niveis'] = $niveis->fetchAll();
        }
        return $linhas;
    }

    // O pool inicial (Fase 5, D18) e "carta com inicial = 1" mais o que o usuario logado ja
    // destravou em usuario_desbloqueios: uma carta especifica (tipo 'carta') ou o arquetipo
    // inteiro dela de uma vez (tipo 'arquetipo', ver app/models/Meta.php::avaliarObjetivos).
    private static function cartas(?int $usuarioId): array
    {
        $pdo = Database::conexao();
        $sql = 'SELECT c.slug AS id, c.nome, cl.slug AS classe, a.nome AS arquetipo,
                       c.custo, c.tipo, c.texto, c.efeitos
                FROM cartas c
                JOIN arquetipos a ON a.id = c.arquetipo_id
                JOIN classes cl ON cl.id = a.classe_id
                WHERE c.inicial = 1';
        $parametros = [];
        if ($usuarioId !== null) {
            $sql .= ' OR EXISTS (
                        SELECT 1 FROM usuario_desbloqueios ud
                        WHERE ud.usuario_id = :usuario_id
                          AND ((ud.tipo = "carta" AND ud.ref = c.slug)
                            OR (ud.tipo = "arquetipo" AND ud.ref = a.slug))
                      )';
            $parametros['usuario_id'] = $usuarioId;
        }
        $sql .= ' ORDER BY c.id';

        $stmt = $pdo->prepare($sql);
        $stmt->execute($parametros);
        $linhas = $stmt->fetchAll();

        return array_map(static function (array $carta): array {
            $carta['tipo'] = ucfirst($carta['tipo']);
            $carta['efeitos'] = json_decode($carta['efeitos'], true);
            return $carta;
        }, $linhas);
    }

    private static function inimigos(): array
    {
        $pdo = Database::conexao();
        $linhasInimigos = $pdo->query('SELECT * FROM inimigos')->fetchAll();

        $dicionario = [];
        $finalId = null;
        $fasesFinal = null;
        foreach ($linhasInimigos as $linha) {
            $entrada = [
                'nome' => $linha['nome'],
                'hp' => (int) $linha['hp'],
            ];
            if ($linha['nota'] !== null) {
                $entrada['nota'] = $linha['nota'];
            }
            if ($linha['flags'] !== null) {
                $entrada['flags'] = json_decode($linha['flags'], true);
            }
            $entrada['padrao'] = json_decode($linha['padrao'], true);
            $dicionario[$linha['slug']] = $entrada;

            if ($linha['tipo'] === 'chefao') {
                $finalId = $linha['slug'];
                $fasesFinal = $linha['fases'] !== null ? json_decode($linha['fases'], true) : [];
            }
        }

        $blocos = [];
        for ($bloco = 1; $bloco <= 5; $bloco++) {
            $stmtCombates = $pdo->prepare(
                "SELECT composicao FROM encontros WHERE bloco = :bloco AND tipo = 'comum' ORDER BY ordem"
            );
            $stmtCombates->execute(['bloco' => $bloco]);
            $combates = array_map(
                static fn(array $l) => json_decode($l['composicao'], true),
                $stmtCombates->fetchAll()
            );

            $stmtElite = $pdo->prepare(
                "SELECT composicao FROM encontros WHERE bloco = :bloco AND tipo = 'elite' LIMIT 1"
            );
            $stmtElite->execute(['bloco' => $bloco]);
            $eliteComposicao = json_decode($stmtElite->fetchColumn(), true);

            $stmtChefe = $pdo->prepare(
                "SELECT composicao FROM encontros WHERE bloco = :bloco AND tipo = 'chefe' LIMIT 1"
            );
            $stmtChefe->execute(['bloco' => $bloco]);
            $chefeComposicao = json_decode($stmtChefe->fetchColumn(), true);

            $blocos[] = [
                'nome' => self::NOMES_BLOCO[$bloco],
                'combates' => $combates,
                'eliteId' => $eliteComposicao[0] ?? null,
                'chefeIds' => $chefeComposicao ?? [],
            ];
        }

        return [
            'inimigos' => $dicionario,
            'blocos' => $blocos,
            'finalId' => $finalId,
            'fasesFinal' => $fasesFinal,
        ];
    }

    private static function eventos(): array
    {
        $pdo = Database::conexao();
        $linhas = $pdo->query('SELECT slug, titulo, texto, opcoes FROM eventos ORDER BY id')->fetchAll();
        return array_map(static function (array $evento): array {
            return [
                'id' => $evento['slug'],
                'titulo' => $evento['titulo'],
                'texto' => $evento['texto'],
                'escolhas' => json_decode($evento['opcoes'], true),
            ];
        }, $linhas);
    }

    private static function desafios(): array
    {
        $pdo = Database::conexao();
        $linhas = $pdo->query('SELECT slug, nome, texto, efeito FROM desafios ORDER BY ordem')->fetchAll();
        return array_map(static function (array $desafio): array {
            return [
                'id' => $desafio['slug'],
                'nome' => $desafio['nome'],
                'texto' => $desafio['texto'],
                'efeito' => json_decode($desafio['efeito'], true),
            ];
        }, $linhas);
    }

    public static function classeIdPorSlug(string $slug): ?int
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare('SELECT id FROM classes WHERE slug = :slug');
        $stmt->execute(['slug' => $slug]);
        $id = $stmt->fetchColumn();
        return $id !== false ? (int) $id : null;
    }

    public static function hpInicialDaClasse(int $classeId): int
    {
        $pdo = Database::conexao();
        $stmt = $pdo->prepare('SELECT hp_inicial FROM classes WHERE id = :id');
        $stmt->execute(['id' => $classeId]);
        return (int) $stmt->fetchColumn();
    }
}
