
import time
from order_management import OrderRequest, OrderResponse, RequestType, ResponseType, OrderManagement

oms = OrderManagement("00:00", "23:59", throttle_limit=5)

# Submit 10 orders
for i in range(10):
    req = OrderRequest(101, 100 + i, 10 + i, 'B', 1000 + i, RequestType.New)
    oms.onData(req)
    time.sleep(0.05)

# Modify and cancel
oms.onData(OrderRequest(101, 150, 25, 'B', 1002, RequestType.Modify))
oms.onData(OrderRequest(101, 0, 0, 'B', 1004, RequestType.Cancel))

# Simulate exchange responses
time.sleep(2)
for i in range(10):
    resp = OrderResponse(1000 + i, ResponseType.Accept)
    oms.onDataResponse(resp)

oms.close()
