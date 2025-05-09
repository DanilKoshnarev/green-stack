from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class BatchProcessingMetrics:
    """Метрики обработки батчей"""
    total_batches: int = 0
    completed_batches: int = 0
    failed_batches: int = 0
    avg_processing_time: float = 0.0
    batches_per_minute: float = 0.0
    error_rate: float = 0.0

class BatchMetricsCollector:
    """Коллектор метрик обработки батчей"""

    def __init__(self, window_size: int = 60):
        self.window_size = window_size  # размер окна для расчета метрик в секундах
        self.processing_times: List[float] = []
        self.completion_timestamps: List[datetime] = []
        self.error_counts = defaultdict(int)
        self.current_metrics = BatchProcessingMetrics()

    def record_batch_processing(self, processing_time: float, success: bool,
                              error_type: Optional[str] = None) -> None:
        """Запись метрик обработки батча"""
        now = datetime.utcnow()
        self.processing_times.append(processing_time)
        self.completion_timestamps.append(now)
        
        # Обновление основных метрик
        self.current_metrics.total_batches += 1
        if success:
            self.current_metrics.completed_batches += 1
        else:
            self.current_metrics.failed_batches += 1
            if error_type:
                self.error_counts[error_type] += 1

        # Очистка устаревших данных
        self._cleanup_old_data(now)
        
        # Пересчет агрегированных метрик
        self._recalculate_metrics(now)

    def get_current_metrics(self) -> Dict:
        """Получение текущих метрик"""
        return {
            'general': self.current_metrics.__dict__,
            'error_distribution': dict(self.error_counts)
        }

    def _cleanup_old_data(self, current_time: datetime) -> None:
        """Очистка устаревших данных из окна"""
        window_start = current_time - timedelta(seconds=self.window_size)
        
        # Удаление старых временных меток и соответствующих данных
        while self.completion_timestamps and self.completion_timestamps[0] < window_start:
            self.completion_timestamps.pop(0)
            self.processing_times.pop(0)

    def _recalculate_metrics(self, current_time: datetime) -> None:
        """Пересчет агрегированных метрик"""
        if not self.processing_times:
            return

        # Расчет среднего времени обработки
        self.current_metrics.avg_processing_time = sum(self.processing_times) / len(self.processing_times)

        # Расчет батчей в минуту
        window_start = current_time - timedelta(seconds=self.window_size)
        recent_completions = sum(1 for ts in self.completion_timestamps if ts >= window_start)
        self.current_metrics.batches_per_minute = (recent_completions * 60) / self.window_size

        # Расчет процента ошибок
        total = self.current_metrics.completed_batches + self.current_metrics.failed_batches
        self.current_metrics.error_rate = (
            (self.current_metrics.failed_batches / total * 100)
            if total > 0 else 0.0
        )