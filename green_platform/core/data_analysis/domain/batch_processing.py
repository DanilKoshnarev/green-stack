from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, TypeVar, Generic
from uuid import UUID
from datetime import datetime

T = TypeVar('T')

class BatchData(Protocol):
    """Протокол для данных батча"""
    tree_id: UUID
    data_type: str
    batch_data: Dict[str, Any]

class BatchProcessor(Protocol):
    """Протокол для обработчика батчей"""
    async def process(self, batch_id: UUID) -> bool:
        ...

class BatchFactory(ABC, Generic[T]):
    """Абстрактная фабрика для создания батчей и их обработчиков"""
    
    @abstractmethod
    def create_batch_data(self, tree_id: UUID, data: Dict[str, Any]) -> BatchData:
        """Создает данные батча"""
        pass
    
    @abstractmethod
    def create_processor(self) -> BatchProcessor:
        """Создает обработчик батча"""
        pass

class TreeDataBatch(BatchData):
    """Реализация батча данных о дереве"""
    def __init__(self, tree_id: UUID, data: Dict[str, Any]):
        self.tree_id = tree_id
        self.data_type = 'tree_data'
        self.batch_data = {
            'location': data['location'],
            'height': data['height'],
            'species': data['species'],
            'health_status': data['health_status']
        }

class AnalysisResultBatch(BatchData):
    """Реализация батча результатов анализа"""
    def __init__(self, tree_id: UUID, data: Dict[str, Any]):
        self.tree_id = tree_id
        self.data_type = 'analysis_result'
        self.batch_data = {
            'analysis_id': data['analysis_id'],
            'status': data['status'],
            'details': data['details']
        }