import unittest
from green_platform.core.data_analysis.infrastructure.metrics.batch_metrics import BatchMetricsCollector

class TestSystem(unittest.TestCase):
    def setUp(self):
        self.collector = BatchMetricsCollector(window_size=60)

    def test_system_behavior(self):
        # Simulate batch processing
        self.collector.record_batch_processing(5.0, True)
        self.collector.record_batch_processing(10.0, False, error_type='timeout')
        self.collector.record_batch_processing(7.0, True)

        # Check metrics
        metrics = self.collector.get_current_metrics()
        self.assertEqual(metrics['general']['total_batches'], 3)
        self.assertEqual(metrics['general']['completed_batches'], 2)
        self.assertEqual(metrics['general']['failed_batches'], 1)
        self.assertEqual(metrics['error_distribution']['timeout'], 1)

if __name__ == '__main__':
    unittest.main()