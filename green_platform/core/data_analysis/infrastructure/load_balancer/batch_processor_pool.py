from typing import Dict, List, Optional, Type
from uuid import UUID
from datetime import datetime
from ...domain.batch_processing import BatchProcessor
from .round_robin import RoundRobinBalancer, WorkerMetrics

class BatchProcessorPool:
    """Пул обработчиков батчей с балансировкой нагрузки"""

    def __init__(self, processor_class: Type[BatchProcessor], pool_size: int = 3):
        self.balancer = RoundRobinBalancer[BatchProcessor]()
        self.processor_class = processor_class
        self.initialize_pool(pool_size)

    def initialize_pool(self, size: int) -> None:
        """Инициализация пула обработчиков"""
        for i in range(size):
            processor = self.processor_class()
            worker_id = f"{processor_class.__name__}_{i}"
            self.balancer.add_worker(processor, worker_id)

    async def process_batch(self, batch_id: UUID) -> bool:
        """Обработка батча с использованием балансировки нагрузки"""
        processor = self.balancer.get_next_worker()
        if not processor:
            return False

        worker_id = next(
            wid for wid, metrics in self.balancer.get_metrics().items()
            if id(processor) == int(wid.split('_')[-1])
        )

        start_time = datetime.utcnow()
        try:
            result = await processor.process(batch_id)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.balancer.update_metrics(worker_id, processing_time, result)
            return result
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.balancer.update_metrics(worker_id, processing_time, False)
            raise e

    def get_pool_metrics(self) -> Dict[str, WorkerMetrics]:
        """Получение метрик всех обработчиков в пуле"""
        return self.balancer.get_metrics()

    def adjust_pool_size(self, new_size: int) -> None:
        """Изменение размера пула обработчиков"""
        current_size = len(self.balancer.workers)
        
        if new_size > current_size:
            # Добавление новых обработчиков
            for i in range(current_size, new_size):
                processor = self.processor_class()
                worker_id = f"{self.processor_class.__name__}_{i}"
                self.balancer.add_worker(processor, worker_id)
        elif new_size < current_size:
            # Удаление лишних обработчиков
            workers_to_remove = sorted(
                self.balancer.get_metrics().items(),
                key=lambda x: (x[1].total_processed, x[1].avg_processing_time)
            )[:current_size - new_size]
            
            for worker_id, _ in workers_to_remove:
                self.balancer.remove_worker(worker_id)