from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class TreeData:
    """Сущность данных о дереве"""
    id: str
    species: str
    height: float
    diameter: float
    health_status: str
    location_coordinates: tuple[float, float]
    last_inspection_date: datetime
    notes: Optional[str] = None

@dataclass
class AnalysisResult:
    """Сущность результатов анализа"""
    tree_id: str
    analysis_date: datetime
    metrics: dict
    recommendations: List[str]
    confidence_score: float