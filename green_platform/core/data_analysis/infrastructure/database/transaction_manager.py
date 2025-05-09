from typing import List, Callable, Any, Optional
from contextlib import asynccontextmanager
from asyncpg import Connection, Pool
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class TransactionState(Enum):
    STARTED = "started"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"

@dataclass
class TransactionStep:
    execute: Callable
    compensate: Callable
    name: str

class TransactionManager:
    """Менеджер транзакций с поддержкой Saga и двухфазного коммита"""
    
    def __init__(self, pool: Pool):
        self.pool = pool
        self._current_transaction: Optional[Connection] = None
        self._prepared_transactions: List[str] = []
    
    @asynccontextmanager
    async def transaction(self):
        """Контекстный менеджер для транзакций"""
        async with self.pool.acquire() as connection:
            self._current_transaction = connection
            try:
                async with connection.transaction():
                    yield connection
            finally:
                self._current_transaction = None
    
    async def execute_saga(self, steps: List[TransactionStep]) -> bool:
        """Выполнение распределенной транзакции с использованием паттерна Saga"""
        executed_steps: List[TransactionStep] = []
        
        try:
            for step in steps:
                await step.execute()
                executed_steps.append(step)
            return True
        except Exception as e:
            # Компенсация в случае ошибки
            for step in reversed(executed_steps):
                try:
                    await step.compensate()
                except Exception as comp_error:
                    # Логирование ошибки компенсации
                    print(f"Compensation error in step {step.name}: {comp_error}")
            return False
    
    async def prepare_transaction(self, transaction_id: str) -> bool:
        """Подготовка транзакции (первая фаза 2PC)"""
        if not self._current_transaction:
            return False
            
        try:
            await self._current_transaction.execute(f"PREPARE TRANSACTION '{transaction_id}'")
            self._prepared_transactions.append(transaction_id)
            return True
        except Exception as e:
            print(f"Error preparing transaction {transaction_id}: {e}")
            return False
    
    async def commit_prepared(self, transaction_id: str) -> bool:
        """Фиксация подготовленной транзакции (вторая фаза 2PC)"""
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(f"COMMIT PREPARED '{transaction_id}'")
                self._prepared_transactions.remove(transaction_id)
                return True
        except Exception as e:
            print(f"Error committing prepared transaction {transaction_id}: {e}")
            return False
    
    async def rollback_prepared(self, transaction_id: str) -> bool:
        """Откат подготовленной транзакции"""
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(f"ROLLBACK PREPARED '{transaction_id}'")
                self._prepared_transactions.remove(transaction_id)
                return True
        except Exception as e:
            print(f"Error rolling back prepared transaction {transaction_id}: {e}")
            return False
    
    async def get_prepared_transactions(self) -> List[str]:
        """Получение списка подготовленных транзакций"""
        return self._prepared_transactions.copy()