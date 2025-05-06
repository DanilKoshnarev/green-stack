from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from .entities import TreeAnalysis, AnalysisResult

class TreeAnalysisRepository(ABC):
    """Интерфейс репозитория для работы с анализом деревьев"""
    
    @abstractmethod
    async def save(self, tree_analysis: TreeAnalysis) -> TreeAnalysis:
        """Сохранить анализ дерева"""
        pass

    @abstractmethod
    async def get_by_id(self, analysis_id: UUID) -> Optional[TreeAnalysis]:
        """Получить анализ по ID"""
        pass

    @abstractmethod
    async def get_all(self) -> List[TreeAnalysis]:
        """Получить все анализы"""
        pass

    @abstractmethod
    async def update(self, tree_analysis: TreeAnalysis) -> TreeAnalysis:
        """Обновить анализ дерева"""
        pass

    @abstractmethod
    async def delete(self, analysis_id: UUID) -> bool:
        """Удалить анализ по ID"""
        pass

class AnalysisResultRepository(ABC):
    """Интерфейс репозитория для работы с результатами анализа"""
    
    @abstractmethod
    async def save_result(self, result: AnalysisResult) -> AnalysisResult:
        """Сохранить результат анализа"""
        pass

    @abstractmethod
    async def get_result_by_id(self, result_id: UUID) -> Optional[AnalysisResult]:
        """Получить результат по ID"""
        pass

    @abstractmethod
    async def get_results_by_date_range(self, start_date: str, end_date: str) -> List[AnalysisResult]:
        """Получить результаты за период"""
        pass

    @abstractmethod
    async def update_result(self, result: AnalysisResult) -> AnalysisResult:
        """Обновить результат анализа"""
        pass