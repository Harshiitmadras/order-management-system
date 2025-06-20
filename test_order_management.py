
import unittest
from order_management import OrderRequest, RequestType, OrderManagement

class TestOrderManagement(unittest.TestCase):
    def setUp(self):
        self.oms = OrderManagement("00:00", "23:59", throttle_limit=10)

    def test_new_order(self):
        req = OrderRequest(1, 100.0, 5, 'B', 101, RequestType.New)
        self.oms.onData(req)
        self.assertEqual(len(self.oms.queue), 1)

    def test_modify_order(self):
        req = OrderRequest(1, 100.0, 5, 'B', 102, RequestType.New)
        self.oms.onData(req)
        mod = OrderRequest(1, 105.0, 10, 'B', 102, RequestType.Modify)
        self.oms.onData(mod)
        self.assertEqual(self.oms.queue[0].m_price, 105.0)

    def test_cancel_order(self):
        req = OrderRequest(1, 100.0, 5, 'B', 103, RequestType.New)
        self.oms.onData(req)
        cancel = OrderRequest(1, 0.0, 0, 'B', 103, RequestType.Cancel)
        self.oms.onData(cancel)
        self.assertEqual(len(self.oms.queue), 0)

if __name__ == '__main__':
    unittest.main()
