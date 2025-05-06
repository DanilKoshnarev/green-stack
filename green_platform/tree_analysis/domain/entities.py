from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

@dataclass
class TreeCharacteristics:
    """Основные характеристики дерева"""
    height: float  # высота в метрах
    trunk_diameter: float  # диаметр ствола в сантиметрах
    crown_density: float  # плотность кроны (0-1)
    age: int  # возраст в годах
    species: str  # вид дерева
    location_latitude: float  # широта
    location_longitude: float  # долгота
    health_condition: str  # состояние здоровья
    co2_absorption: float  # поглощение CO2 в кг/год
    biomass: float  # биомасса в кг
    leaf_area: Optional[float] = None  # площадь листвы в м²
    root_system_depth: Optional[float] = None  # глубина корневой системы в метрах

@dataclass
class TreeAnalysis:
    """Анализ дерева с уникальным идентификатором и временем измерения"""
    id: UUID = uuid4()
    characteristics: TreeCharacteristics
    measurement_date: datetime
    notes: Optional[str] = None
    environmental_impact_score: Optional[float] = None

@dataclass
class AnalysisResult:
    """Результаты анализа группы деревьев"""
    analysis_id: UUID = uuid4()
    trees: List[TreeAnalysis]
    total_co2_absorption: float
    average_health_score: float
    biodiversity_index: float
    analysis_date: datetime
    recommendations: Optional[str] = None