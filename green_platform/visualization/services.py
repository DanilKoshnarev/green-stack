from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from ..tree_analysis.domain.entities import TreeAnalysis, AnalysisResult

class VisualizationService:
    """Сервис для создания визуализаций данных о деревьях"""

    @staticmethod
    def create_growth_chart(trees: List[TreeAnalysis]) -> Dict[str, Any]:
        """Создает график роста деревьев"""
        df = pd.DataFrame([
            {
                'height': tree.characteristics.height,
                'age': tree.characteristics.age,
                'species': tree.characteristics.species
            } for tree in trees
        ])

        fig = px.scatter(df, x='age', y='height', color='species',
                        title='Зависимость высоты деревьев от возраста',
                        labels={'age': 'Возраст (лет)',
                                'height': 'Высота (м)',
                                'species': 'Вид дерева'})
        return fig.to_dict()

    @staticmethod
    def create_co2_absorption_chart(result: AnalysisResult) -> Dict[str, Any]:
        """Создает график поглощения CO2"""
        df = pd.DataFrame([
            {
                'species': tree.characteristics.species,
                'co2': tree.characteristics.co2_absorption
            } for tree in result.trees
        ])

        fig = px.bar(df.groupby('species').sum().reset_index(),
                     x='species', y='co2',
                     title='Поглощение CO2 по видам деревьев',
                     labels={'species': 'Вид дерева',
                             'co2': 'Поглощение CO2 (кг/год)'})
        return fig.to_dict()

    @staticmethod
    def create_biodiversity_chart(result: AnalysisResult) -> Dict[str, Any]:
        """Создает круговую диаграмму биоразнообразия"""
        species_count = pd.Series([tree.characteristics.species for tree in result.trees])\
            .value_counts()

        fig = go.Figure(data=[go.Pie(labels=species_count.index,
                                    values=species_count.values,
                                    title='Распределение видов деревьев')])
        return fig.to_dict()

    @staticmethod
    def create_health_distribution(trees: List[TreeAnalysis]) -> Dict[str, Any]:
        """Создает диаграмму распределения состояния здоровья деревьев"""
        health_count = pd.Series([tree.characteristics.health_condition for tree in trees])\
            .value_counts()

        fig = px.bar(x=health_count.index, y=health_count.values,
                     title='Распределение состояния здоровья деревьев',
                     labels={'x': 'Состояние здоровья',
                             'y': 'Количество деревьев'})
        return fig.to_dict()

    @staticmethod
    def create_environmental_impact_map(trees: List[TreeAnalysis]) -> Dict[str, Any]:
        """Создает карту экологического влияния деревьев"""
        df = pd.DataFrame([
            {
                'lat': tree.characteristics.location_latitude,
                'lon': tree.characteristics.location_longitude,
                'impact': tree.characteristics.co2_absorption,
                'species': tree.characteristics.species
            } for tree in trees
        ])

        fig = px.scatter_mapbox(df,
                               lat='lat',
                               lon='lon',
                               color='impact',
                               size='impact',
                               hover_data=['species'],
                               title='Карта экологического влияния деревьев',
                               mapbox_style='carto-positron')
        return fig.to_dict()