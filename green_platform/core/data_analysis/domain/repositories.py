from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import TreeData, AnalysisResult

class TreeDataRepository(ABC):
    """Интерфейс репозитория для работы с данными деревьев"""
    
    @abstractmethod
    async def save(self, tree_data: TreeData) -> None:
        """Сохранить данные о дереве"""
        pass
    
    @abstractmethod
    async def get_by_id(self, tree_id: str) -> Optional[TreeData]:
        """Получить данные о дереве по ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[TreeData]:
        """Получить все данные о деревьях"""
        pass

class AnalysisResultRepository(ABC):
    """Интерфейс репозитория для работы с результатами анализа"""
    
    @abstractmethod
    async def save(self, result: AnalysisResult) -> None:
        """Сохранить результат анализа"""
        pass
    
    @abstractmethod
    async def get_by_tree_id(self, tree_id: str) -> List[AnalysisResult]:
        """Получить все результаты анализа для конкретного дерева"""
        pass