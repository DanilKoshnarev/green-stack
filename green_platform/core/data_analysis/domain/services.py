from abc import ABC, abstractmethod
from typing import List
from .entities import TreeData, AnalysisResult

class TreeAnalysisService(ABC):
    """Сервис для анализа данных о деревьях"""
    
    @abstractmethod
    async def analyze_tree_health(self, tree_data: TreeData) -> AnalysisResult:
        """Анализ состояния здоровья дерева"""
        pass
    
    @abstractmethod
    async def generate_recommendations(self, analysis_result: AnalysisResult) -> List[str]:
        """Генерация рекомендаций по уходу за деревом"""
        pass
    
    @abstractmethod
    async def calculate_growth_metrics(self, tree_data: TreeData) -> dict:
        """Расчет метрик роста дерева"""
        pass

class DataValidationService(ABC):
    """Сервис для валидации данных"""
    
    @abstractmethod
    def validate_tree_data(self, tree_data: TreeData) -> bool:
        """Проверка корректности данных о дереве"""
        pass
    
    @abstractmethod
    def validate_analysis_result(self, result: AnalysisResult) -> bool:
        """Проверка корректности результатов анализа"""
        pass