from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from ..domain.entities import TreeData, AnalysisResult
from .services import TreeAnalysisApplicationService

router = APIRouter(prefix="/api/v1/analysis", tags=["tree-analysis"])

class TreeAnalysisAPI:
    """API для анализа данных о деревьях"""
    
    def __init__(self, analysis_service: TreeAnalysisApplicationService):
        self.analysis_service = analysis_service
        
    async def register_routes(self, router: APIRouter) -> None:
        """Регистрация маршрутов API"""
        
        @router.post("/trees")
        async def add_tree_data(tree_data: TreeData):
            """Добавление новых данных о дереве"""
            try:
                await self.analysis_service.add_tree_data(tree_data)
                return {"status": "success", "message": "Tree data added successfully"}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @router.post("/trees/{tree_id}/analyze")
        async def analyze_tree(tree_id: str):
            """Запуск анализа дерева"""
            try:
                result = await self.analysis_service.analyze_tree(tree_id)
                if not result:
                    raise HTTPException(status_code=404, detail="Tree not found")
                return result
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @router.get("/trees/{tree_id}/history")
        async def get_analysis_history(tree_id: str):
            """Получение истории анализов дерева"""
            try:
                history = await self.analysis_service.get_tree_analysis_history(tree_id)
                return history
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))