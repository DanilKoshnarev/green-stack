from typing import List, Optional
from ..domain.entities import TreeData, AnalysisResult
from ..domain.repositories import TreeDataRepository, AnalysisResultRepository
from ..domain.services import TreeAnalysisService, DataValidationService

class TreeAnalysisApplicationService:
    """Сервис приложения для анализа данных о деревьях"""
    
    def __init__(
        self,
        tree_repository: TreeDataRepository,
        analysis_repository: AnalysisResultRepository,
        analysis_service: TreeAnalysisService,
        validation_service: DataValidationService
    ):
        self.tree_repository = tree_repository
        self.analysis_repository = analysis_repository
        self.analysis_service = analysis_service
        self.validation_service = validation_service
    
    async def analyze_tree(self, tree_id: str) -> Optional[AnalysisResult]:
        """Анализ дерева по его ID"""
        # Получение данных о дереве
        tree_data = await self.tree_repository.get_by_id(tree_id)
        if not tree_data:
            return None
            
        # Валидация данных
        if not self.validation_service.validate_tree_data(tree_data):
            raise ValueError("Invalid tree data")
            
        # Проведение анализа
        analysis_result = await self.analysis_service.analyze_tree_health(tree_data)
        
        # Валидация результатов
        if not self.validation_service.validate_analysis_result(analysis_result):
            raise ValueError("Invalid analysis result")
            
        # Сохранение результатов
        await self.analysis_repository.save(analysis_result)
        
        return analysis_result
    
    async def get_tree_analysis_history(self, tree_id: str) -> List[AnalysisResult]:
        """Получение истории анализов для дерева"""
        return await self.analysis_repository.get_by_tree_id(tree_id)
    
    async def add_tree_data(self, tree_data: TreeData) -> None:
        """Добавление новых данных о дереве"""
        if not self.validation_service.validate_tree_data(tree_data):
            raise ValueError("Invalid tree data")
            
        await self.tree_repository.save(tree_data)