from datetime import datetime
from typing import Optional, List, Dict, Any, Protocol
from uuid import UUID
from asyncpg import Pool
from ...domain.entities import TreeData, AnalysisResult
from ...domain.batch_processing import BatchData, BatchProcessor, BatchFactory
from ..transaction import TransactionManager

class BatchRepositoryProtocol(Protocol):
    """Протокол репозитория для работы с батчами"""
    async def create_batch(self, batch_data: BatchData) -> str: ...
    async def get_pending_batches(self, limit: int) -> List[Dict[str, Any]]: ...
    async def update_batch_status(self, batch_id: UUID, status: str, error_details: Optional[str]) -> bool: ...
    async def cleanup_old_batches(self, days_to_keep: int) -> None: ...

class BatchRepository(BatchRepositoryProtocol):
    """Репозиторий для работы с батчами данных"""

    def __init__(self, pool: Pool, transaction_manager: TransactionManager):
        self.pool = pool
        self.transaction_manager = transaction_manager

    async def create_batch(self, batch_data: BatchData) -> str:
        """Создание нового батча данных"""
        async with self.pool.acquire() as connection:
            batch_id = await connection.fetchval("""
                INSERT INTO data_batches (tree_id, data_type, batch_data)
                VALUES ($1, $2, $3)
                RETURNING batch_id
            """, str(batch_data.tree_id), batch_data.data_type, batch_data.batch_data)
            return batch_id

    async def get_pending_batches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение списка необработанных батчей"""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch("""
                SELECT *
                FROM data_batches
                WHERE status = 'pending'
                AND retry_count < 3
                ORDER BY created_at ASC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]

    async def update_batch_status(self, batch_id: UUID, status: str, error_details: Optional[str] = None) -> bool:
        """Обновление статуса батча"""
        async with self.pool.acquire() as connection:
            result = await connection.execute("""
                UPDATE data_batches
                SET status = $1,
                    error_details = $2,
                    retry_count = CASE 
                        WHEN $1 = 'failed' THEN retry_count + 1
                        ELSE retry_count
                    END
                WHERE batch_id = $3
            """, status, error_details, str(batch_id))
            return result == 'UPDATE 1'

    async def process_tree_data_batch(self, batch_id: UUID) -> bool:
        """Обработка батча с данными о дереве"""
        async with self.transaction_manager.transaction() as connection:
            batch = await connection.fetchrow("""
                SELECT * FROM data_batches
                WHERE batch_id = $1 AND data_type = 'tree_data'
            """, str(batch_id))

            if not batch:
                return False

            try:
                version_id = await connection.fetchval("""
                    INSERT INTO tree_versions (tree_id, version_number, created_at)
                    VALUES ($1, (
                        SELECT COALESCE(MAX(version_number), 0) + 1
                        FROM tree_versions
                        WHERE tree_id = $1
                    ), $2)
                    RETURNING version_id
                """, batch['tree_id'], datetime.utcnow())

                tree_data = batch['batch_data']
                await connection.execute("""
                    INSERT INTO trees (tree_id, version_id, location, height, species, health_status)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, batch['tree_id'], version_id, tree_data['location'],
                    tree_data['height'], tree_data['species'], tree_data['health_status'])

                await self.update_batch_status(batch_id, 'completed')
                return True

            except Exception as e:
                await self.update_batch_status(batch_id, 'failed', str(e))
                return False

    async def process_analysis_result_batch(self, batch_id: UUID) -> bool:
        """Обработка батча с результатами анализа"""
        async with self.transaction_manager.transaction() as connection:
            batch = await connection.fetchrow("""
                SELECT * FROM data_batches
                WHERE batch_id = $1 AND data_type = 'analysis_result'
            """, str(batch_id))

            if not batch:
                return False

            try:
                result_data = batch['batch_data']
                await connection.execute("""
                    INSERT INTO analysis_results 
                    (analysis_id, tree_id, status, details, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                """, result_data['analysis_id'], batch['tree_id'],
                    result_data['status'], result_data['details'], datetime.utcnow())

                await self.update_batch_status(batch_id, 'completed')
                return True

            except Exception as e:
                await self.update_batch_status(batch_id, 'failed', str(e))
                return False

    async def cleanup_old_batches(self, days_to_keep: int = 7) -> None:
        """Очистка старых обработанных батчей"""
        async with self.pool.acquire() as connection:
            await connection.execute(
                'SELECT cleanup_completed_batches($1)',
                days_to_keep
            )