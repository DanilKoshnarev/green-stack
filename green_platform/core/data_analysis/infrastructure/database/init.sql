-- Создание таблицы версий деревьев
CREATE TABLE IF NOT EXISTS tree_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tree_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (tree_id, version_number)
);

-- Создание индекса для быстрого поиска версий
CREATE INDEX IF NOT EXISTS idx_tree_versions_tree_id ON tree_versions(tree_id);
CREATE INDEX IF NOT EXISTS idx_tree_versions_created_at ON tree_versions(created_at);

-- Создание таблицы деревьев
CREATE TABLE IF NOT EXISTS trees (
    tree_id UUID NOT NULL,
    version_id UUID NOT NULL REFERENCES tree_versions(version_id),
    location POINT NOT NULL,
    height DECIMAL NOT NULL,
    species VARCHAR(100) NOT NULL,
    health_status VARCHAR(50) NOT NULL,
    PRIMARY KEY (tree_id, version_id)
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_trees_version_id ON trees(version_id);
CREATE INDEX IF NOT EXISTS idx_trees_location ON trees USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_trees_species ON trees(species);
CREATE INDEX IF NOT EXISTS idx_trees_health_status ON trees(health_status);

-- Создание таблицы результатов анализа
CREATE TABLE IF NOT EXISTS analysis_results (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tree_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    details JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Создание индексов для анализа
CREATE INDEX IF NOT EXISTS idx_analysis_results_tree_id ON analysis_results(tree_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_results_status ON analysis_results(status);

-- Включение расширения для работы с UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Включение расширения для работы с геоданными
CREATE EXTENSION IF NOT EXISTS postgis;

-- Создание функции для очистки старых версий
CREATE OR REPLACE FUNCTION cleanup_old_versions(p_tree_id UUID, p_keep_versions INTEGER)
RETURNS void AS $$
BEGIN
    DELETE FROM tree_versions
    WHERE version_id IN (
        SELECT version_id
        FROM (
            SELECT version_id,
                   ROW_NUMBER() OVER (PARTITION BY tree_id ORDER BY version_number DESC) as rn
            FROM tree_versions
            WHERE tree_id = p_tree_id
        ) ranked
        WHERE ranked.rn > p_keep_versions
    );
END;
$$ LANGUAGE plpgsql;