from typing import List, TypeVar, Generic, Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

T = TypeVar('T')

@dataclass
class WorkerMetrics:
    """Метрики работы обработчика"""
    worker_id: str
    total_processed: int
    success_count: int
    failure_count: int
    avg_processing_time: float
    last_processed: Optional[datetime]

class RoundRobinBalancer(Generic[T]):
    """Балансировщик нагрузки с алгоритмом Round Robin"""

    def __init__(self):
        self.workers: List[T] = []
        self.current_index = 0
        self.metrics: dict[str, WorkerMetrics] = {}

    def add_worker(self, worker: T, worker_id: str) -> None:
        """Добавление нового обработчика"""
        self.workers.append(worker)
        self.metrics[worker_id] = WorkerMetrics(
            worker_id=worker_id,
            total_processed=0,
            success_count=0,
            failure_count=0,
            avg_processing_time=0.0,
            last_processed=None
        )

    def remove_worker(self, worker_id: str) -> None:
        """Удаление обработчика"""
        if worker_id in self.metrics:
            worker_index = next(
                (i for i, w in enumerate(self.workers)
                 if id(w) == int(worker_id)), None
            )
            if worker_index is not None:
                self.workers.pop(worker_index)
                del self.metrics[worker_id]
                if self.current_index >= len(self.workers):
                    self.current_index = 0

    def get_next_worker(self) -> Optional[T]:
        """Получение следующего обработчика по алгоритму Round Robin"""
        if not self.workers:
            return None

        worker = self.workers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.workers)
        return worker

    def update_metrics(self, worker_id: str, processing_time: float, success: bool) -> None:
        """Обновление метрик обработчика"""
        if worker_id in self.metrics:
            metrics = self.metrics[worker_id]
            metrics.total_processed += 1
            if success:
                metrics.success_count += 1
            else:
                metrics.failure_count += 1

            # Обновление среднего времени обработки
            metrics.avg_processing_time = (
                (metrics.avg_processing_time * (metrics.total_processed - 1) + processing_time)
                / metrics.total_processed
            )
            metrics.last_processed = datetime.utcnow()

    def get_metrics(self, worker_id: Optional[str] = None) -> dict:
        """Получение метрик обработчиков"""
        if worker_id:
            return {worker_id: self.metrics[worker_id].__dict__} if worker_id in self.metrics else {}
        return {wid: metrics.__dict__ for wid, metrics in self.metrics.items()}