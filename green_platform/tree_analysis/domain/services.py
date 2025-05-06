from abc import ABC, abstractmethod
from typing import List, Protocol
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from .entities import TreeAnalysis, AnalysisResult, TreeCharacteristics

class DataProcessingStrategy(Protocol):
    """Протокол для стратегий обработки данных"""
    def process_data(self, data: np.ndarray) -> np.ndarray:
        pass

class AnalysisStrategy(Protocol):
    """Протокол для стратегий анализа"""
    def analyze(self, characteristics: List[TreeCharacteristics]) -> float:
        pass

class BatchProcessor:
    """Обработчик пакетных операций с данными"""
    def __init__(self, processing_strategy: DataProcessingStrategy):
        self.processing_strategy = processing_strategy

    def process_batch(self, data: List[TreeAnalysis]) -> np.ndarray:
        """Обработка пакета данных с использованием выбранной стратегии"""
        numpy_data = np.array([[t.characteristics.height,
                              t.characteristics.trunk_diameter,
                              t.characteristics.crown_density,
                              t.characteristics.co2_absorption] for t in data])
        return self.processing_strategy.process_data(numpy_data)

class TreeAnalysisService:
    """Сервис для анализа данных о деревьях"""
    def __init__(self, batch_processor: BatchProcessor):
        self.batch_processor = batch_processor
        self._ml_model = RandomForestRegressor()

    def calculate_environmental_impact(self, trees: List[TreeAnalysis]) -> float:
        """Расчет влияния на окружающую среду"""
        processed_data = self.batch_processor.process_batch(trees)
        return float(np.mean(processed_data[:, -1]))

    def predict_growth(self, tree: TreeAnalysis) -> float:
        """Прогнозирование роста дерева"""
        features = np.array([[tree.characteristics.height,
                            tree.characteristics.trunk_diameter,
                            tree.characteristics.crown_density,
                            tree.characteristics.age]])
        return float(self._ml_model.predict(features)[0])

    def create_analysis_result(self, trees: List[TreeAnalysis]) -> AnalysisResult:
        """Создание результата анализа группы деревьев"""
        total_co2 = sum(t.characteristics.co2_absorption for t in trees)
        avg_health = np.mean([1 if t.characteristics.health_condition == 'healthy' else 0
                            for t in trees])
        biodiversity = len(set(t.characteristics.species for t in trees)) / len(trees)

        return AnalysisResult(
            trees=trees,
            total_co2_absorption=total_co2,
            average_health_score=float(avg_health),
            biodiversity_index=float(biodiversity),
            analysis_date=datetime.now()
        )

class StandardDataProcessing(DataProcessingStrategy):
    """Стандартная стратегия обработки данных"""
    def process_data(self, data: np.ndarray) -> np.ndarray:
        return np.array(data)

class AdvancedDataProcessing(DataProcessingStrategy):
    """Продвинутая стратегия обработки с дополнительными вычислениями"""
    def process_data(self, data: np.ndarray) -> np.ndarray:
        # Нормализация данных
        normalized = (data - np.mean(data, axis=0)) / np.std(data, axis=0)
        # Добавление производных характеристик
        derived_features = np.column_stack([
            normalized,
            np.square(normalized),  # квадратичные характеристики
            np.exp(normalized)      # экспоненциальные характеристики
        ])
        return derived_features