from typing import Dict, Any
from uuid import UUID
from ...domain.batch_processing import (
    BatchFactory,
    BatchData,
    BatchProcessor,
    TreeDataBatch,
    AnalysisResultBatch
)
from .batch_repository import BatchRepository

class TreeDataBatchFactory(BatchFactory):
    """Фабрика для создания и обработки батчей данных о деревьях"""
    
    def __init__(self, repository: BatchRepository):
        self.repository = repository
    
    def create_batch_data(self, tree_id: UUID, data: Dict[str, Any]) -> BatchData:
        return TreeDataBatch(tree_id, data)
    
    def create_processor(self) -> BatchProcessor:
        return TreeDataBatchProcessor(self.repository)

class AnalysisResultBatchFactory(BatchFactory):
    """Фабрика для создания и обработки батчей результатов анализа"""
    
    def __init__(self, repository: BatchRepository):
        self.repository = repository
    
    def create_batch_data(self, tree_id: UUID, data: Dict[str, Any]) -> BatchData:
        return AnalysisResultBatch(tree_id, data)
    
    def create_processor(self) -> BatchProcessor:
        return AnalysisResultBatchProcessor(self.repository)

class TreeDataBatchProcessor(BatchProcessor):
    """Обработчик батчей данных о деревьях"""
    
    def __init__(self, repository: BatchRepository):
        self.repository = repository
    
    async def process(self, batch_id: UUID) -> bool:
        return await self.repository.process_tree_data_batch(batch_id)

class AnalysisResultBatchProcessor(BatchProcessor):
    """Обработчик батчей результатов анализа"""
    
    def __init__(self, repository: BatchRepository):
        self.repository = repository
    
    async def process(self, batch_id: UUID) -> bool:
        return await self.repository.process_analysis_result_batch(batch_id)