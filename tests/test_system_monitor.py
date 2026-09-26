import unittest
from system.monitor import SystemMonitorWorker

class TestSystemMonitor(unittest.TestCase):
    def test_worker_initialization(self):
        worker = SystemMonitorWorker()
        self.assertTrue(worker.running)
        # We won't start the thread in test to avoid blocking, just test it constructs
        worker.stop()
        self.assertFalse(worker.running)

if __name__ == '__main__':
    unittest.main()
