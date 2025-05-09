from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from asyncpg import Pool
from ...domain.entities import TreeData, AnalysisResult
from .transaction_manager import TransactionManager, TransactionStep
from .postgres_config import PostgresConfig

class TreeRepository:
    """Репозиторий для работы с данными о деревьях с поддержкой версионирования"""
    
    def __init__(self, pool: Pool, transaction_manager: TransactionManager):
        self.pool = pool
        self.transaction_manager = transaction_manager
    
    async def add_tree_data(self, tree_data: TreeData) -> str:
        """Добавление новых данных о дереве с версионированием"""
        async with self.transaction_manager.transaction() as connection:
            # Создание новой версии записи
            version_id = await connection.fetchval("""
                INSERT INTO tree_versions (tree_id, version_number, created_at)
                VALUES ($1, (
                    SELECT COALESCE(MAX(version_number), 0) + 1
                    FROM tree_versions
                    WHERE tree_id = $1
                ), $2)
                RETURNING version_id
            """, str(tree_data.id), datetime.utcnow())
            
            # Сохранение данных дерева
            await connection.execute("""
                INSERT INTO trees (tree_id, version_id, location, height, species, health_status)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, str(tree_data.id), version_id, tree_data.location,
                tree_data.height, tree_data.species, tree_data.health_status)
            
            return version_id
    
    async def get_tree_data(self, tree_id: str, version_id: Optional[str] = None) -> Optional[TreeData]:
        """Получение данных о дереве с учетом версии"""
        async with self.pool.acquire() as connection:
            if version_id:
                query = """
                    SELECT t.*, v.version_number, v.created_at
                    FROM trees t
                    JOIN tree_versions v ON t.version_id = v.version_id
                    WHERE t.tree_id = $1 AND v.version_id = $2
                """
                row = await connection.fetchrow(query, tree_id, version_id)
            else:
                query = """
                    SELECT t.*, v.version_number, v.created_at
                    FROM trees t
                    JOIN tree_versions v ON t.version_id = v.version_id
                    WHERE t.tree_id = $1
                    ORDER BY v.version_number DESC
                    LIMIT 1
                """
                row = await connection.fetchrow(query, tree_id)
            
            return TreeData(**row) if row else None
    
    async def save_analysis_result(self, tree_id: str, result: AnalysisResult) -> bool:
        """Сохранение результатов анализа с использованием Saga"""
        steps = [
            TransactionStep(
                execute=lambda: self._save_analysis_data(tree_id, result),
                compensate=lambda: self._cleanup_analysis_data(tree_id, result.id),
                name="save_analysis"
            ),
            TransactionStep(
                execute=lambda: self._update_tree_status(tree_id, result.status),
                compensate=lambda: self._restore_tree_status(tree_id),
                name="update_status"
            )
        ]
        
        return await self.transaction_manager.execute_saga(steps)
    
    async def get_analysis_history(self, tree_id: str) -> List[Dict[str, Any]]:
        """Получение истории анализов дерева"""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch("""
                SELECT a.*, v.version_number
                FROM analysis_results a
                JOIN tree_versions v ON a.tree_id = v.tree_id
                WHERE a.tree_id = $1
                ORDER BY a.created_at DESC
            """, tree_id)
            
            return [dict(row) for row in rows]
    
    async def _save_analysis_data(self, tree_id: str, result: AnalysisResult) -> None:
        """Сохранение данных анализа"""
        async with self.pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO analysis_results 
                (analysis_id, tree_id, status, details, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """, str(result.id), tree_id, result.status,
                result.details, datetime.utcnow())
    
    async def _cleanup_analysis_data(self, tree_id: str, analysis_id: str) -> None:
        """Очистка данных анализа при откате"""
        async with self.pool.acquire() as connection:
            await connection.execute("""
                DELETE FROM analysis_results
                WHERE tree_id = $1 AND analysis_id = $2
            """, tree_id, analysis_id)
    
    async def _update_tree_status(self, tree_id: str, status: str) -> None:
        """Обновление статуса дерева"""
        async with self.pool.acquire() as connection:
            await connection.execute("""
                UPDATE trees
                SET health_status = $1
                WHERE tree_id = $2
            """, status, tree_id)
    
    async def _restore_tree_status(self, tree_id: str) -> None:
        """Восстановление предыдущего статуса дерева"""
        async with self.pool.acquire() as connection:
            previous_status = await connection.fetchval("""
                SELECT health_status
                FROM trees
                WHERE tree_id = $1
                ORDER BY version_id DESC
                LIMIT 1 OFFSET 1
            """, tree_id)
            
            if previous_status:
                await connection.execute("""
                    UPDATE trees
                    SET health_status = $1
                    WHERE tree_id = $2
                """, previous_status, tree_id)