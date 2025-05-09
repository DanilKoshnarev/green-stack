from typing import Dict, Any
from pydantic import BaseSettings

class PostgresConfig(BaseSettings):
    """Конфигурация PostgreSQL с поддержкой репликации и двухфазного коммита"""
    
    # Основные настройки подключения
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/green_platform"
    MAX_CONNECTIONS: int = 100
    POOL_SIZE: int = 20
    
    # Настройки репликации
    REPLICATION_MODE: str = "synchronous"  # synchronous/asynchronous
    STANDBY_SERVERS: list[str] = [
        "postgresql://replica1:5432/green_platform",
        "postgresql://replica2:5432/green_platform"
    ]
    SYNCHRONOUS_COMMIT: str = "on"  # on/remote_write/remote_apply
    
    # Настройки двухфазного коммита
    MAX_PREPARED_TRANSACTIONS: int = 50
    PREPARE_THRESHOLD: int = 5
    
    # Настройки журналирования
    WAL_LEVEL: str = "replica"  # minimal/replica/logical
    WAL_KEEP_SIZE: str = "1GB"
    ARCHIVE_MODE: bool = True
    ARCHIVE_TIMEOUT: int = 300  # секунды
    
    # Настройки восстановления
    RECOVERY_TARGET_TIMELINE: str = "latest"
    RESTORE_COMMAND: str = "cp /path/to/archive/%f %p"
    
    class Config:
        env_file = ".env"
        
    def get_dsn(self) -> str:
        """Получение строки подключения к базе данных"""
        return self.DATABASE_URL
    
    def get_replication_settings(self) -> Dict[str, Any]:
        """Получение настроек репликации"""
        return {
            "mode": self.REPLICATION_MODE,
            "standby_servers": self.STANDBY_SERVERS,
            "synchronous_commit": self.SYNCHRONOUS_COMMIT
        }
    
    def get_two_phase_commit_settings(self) -> Dict[str, Any]:
        """Получение настроек двухфазного коммита"""
        return {
            "max_prepared_transactions": self.MAX_PREPARED_TRANSACTIONS,
            "prepare_threshold": self.PREPARE_THRESHOLD
        }