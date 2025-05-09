-- Создание таблицы для батчей данных
CREATE TABLE IF NOT EXISTS data_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tree_id UUID NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- Тип данных (tree_data, analysis_result)
    batch_data JSONB NOT NULL, -- Данные в формате JSON
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    error_details TEXT
);

-- Создание индексов для оптимизации работы с батчами
CREATE INDEX IF NOT EXISTS idx_data_batches_tree_id ON data_batches(tree_id);
CREATE INDEX IF NOT EXISTS idx_data_batches_status ON data_batches(status);
CREATE INDEX IF NOT EXISTS idx_data_batches_created_at ON data_batches(created_at);

-- Создание функции для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_batch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера для автоматического обновления updated_at
CREATE TRIGGER trigger_update_batch_updated_at
    BEFORE UPDATE ON data_batches
    FOR EACH ROW
    EXECUTE FUNCTION update_batch_updated_at();

-- Создание функции для очистки успешно обработанных батчей
CREATE OR REPLACE FUNCTION cleanup_completed_batches(p_days_to_keep INTEGER)
RETURNS void AS $$
BEGIN
    DELETE FROM data_batches
    WHERE status = 'completed'
    AND created_at < NOW() - (p_days_to_keep || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;