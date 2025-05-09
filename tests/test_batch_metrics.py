import unittest
from datetime import datetime, timedelta
from green_platform.core.data_analysis.infrastructure.metrics.batch_metrics import BatchMetricsCollector

class TestBatchMetricsCollector(unittest.TestCase):
    def setUp(self):
        self.collector = BatchMetricsCollector(window_size=60)

    def test_record_batch_processing_success(self):
        self.collector.record_batch_processing(5.0, True)
        metrics = self.collector.get_current_metrics()
        self.assertEqual(metrics['general']['total_batches'], 1)
        self.assertEqual(metrics['general']['completed_batches'], 1)
        self.assertEqual(metrics['general']['failed_batches'], 0)

    def test_record_batch_processing_failure(self):
        self.collector.record_batch_processing(5.0, False, error_type='timeout')
        metrics = self.collector.get_current_metrics()
        self.assertEqual(metrics['general']['total_batches'], 1)
        self.assertEqual(metrics['general']['completed_batches'], 0)
        self.assertEqual(metrics['general']['failed_batches'], 1)
        self.assertEqual(metrics['error_distribution']['timeout'], 1)

    def test_cleanup_old_data(self):
        self.collector.record_batch_processing(5.0, True)
        self.collector.completion_timestamps[0] -= timedelta(seconds=61)
        self.collector._cleanup_old_data(datetime.utcnow())
        metrics = self.collector.get_current_metrics()
        self.assertEqual(metrics['general']['total_batches'], 0)

    def test_recalculate_metrics(self):
        self.collector.record_batch_processing(5.0, True)
        self.collector.record_batch_processing(10.0, True)
        self.collector._recalculate_metrics(datetime.utcnow())
        metrics = self.collector.get_current_metrics()
        self.assertAlmostEqual(metrics['general']['avg_processing_time'], 7.5)
        self.assertAlmostEqual(metrics['general']['batches_per_minute'], 2.0)

if __name__ == '__main__':
    unittest.main()