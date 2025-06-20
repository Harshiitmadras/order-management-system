
import time
import threading
from datetime import datetime
from collections import deque

# --- Data Structures ---

class Logon:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Logout:
    def __init__(self, username):
        self.username = username

class OrderRequest:
    def __init__(self, symbol_id, price, qty, side, order_id, request_type):
        self.m_symbolId = symbol_id
        self.m_price = price
        self.m_qty = qty
        self.m_side = side  # 'B' or 'S'
        self.m_orderId = order_id
        self.request_type = request_type
        self.timestamp = datetime.now()

class OrderResponse:
    def __init__(self, order_id, response_type):
        self.m_orderId = order_id
        self.m_responseType = response_type

class RequestType:
    Unknown = 0
    New = 1
    Modify = 2
    Cancel = 3

class ResponseType:
    Unknown = 0
    Accept = 1
    Reject = 2

# --- Order Management System ---

class OrderManagement:
    def __init__(self, start_time_str, end_time_str, throttle_limit):
        self.queue = deque()
        self.sent_orders = {}
        self.queue_lock = threading.Lock()
        self.latency_log_file = open("responses.log", "w")

        self.limit_per_sec = throttle_limit
        self.sent_this_sec = 0
        self.last_sec = int(time.time())

        self.start_time = datetime.strptime(start_time_str, "%H:%M").time()
        self.end_time = datetime.strptime(end_time_str, "%H:%M").time()

        self.logon_done = False
        self.logout_done = False
        self.username = "user1"
        self.password = "pass"

        self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.sender_thread.start()

    def _in_market_hours(self):
        now = datetime.now().time()
        return self.start_time <= now <= self.end_time

    def sendLogon(self):
        print("[Logon] Exchange logon sent")
        self.logon_done = True

    def sendLogout(self):
        print("[Logout] Exchange logout sent")
        self.logout_done = True

    def send(self, request):
        print(f"[Sent] OrderID {request.m_orderId} sent to exchange")
        self.sent_orders[request.m_orderId] = datetime.now()

    def onData(self, request):
        with self.queue_lock:
            if not self._in_market_hours():
                print(f"[Rejected] Order {request.m_orderId} outside trading hours")
                return

            if not self.logon_done:
                self.sendLogon()

            if request.request_type == RequestType.New:
                self.queue.append(request)
            elif request.request_type == RequestType.Modify:
                for order in self.queue:
                    if order.m_orderId == request.m_orderId:
                        order.m_price = request.m_price
                        order.m_qty = request.m_qty
                        break
            elif request.request_type == RequestType.Cancel:
                self.queue = deque(o for o in self.queue if o.m_orderId != request.m_orderId)

    def onDataResponse(self, response):
        order_id = response.m_orderId
        send_time = self.sent_orders.pop(order_id, None)
        if send_time:
            latency = (datetime.now() - send_time).total_seconds()
            log_entry = f"OrderID: {order_id}, Response: {response.m_responseType.name}, Latency: {latency:.6f}s\n"
            self.latency_log_file.write(log_entry)
            self.latency_log_file.flush()
            print(f"[Response] {log_entry.strip()}")

    def _sender_loop(self):
        while True:
            current_sec = int(time.time())
            if current_sec != self.last_sec:
                self.sent_this_sec = 0
                self.last_sec = current_sec

            if not self._in_market_hours():
                if self.logon_done and not self.logout_done:
                    self.sendLogout()
                time.sleep(1)
                continue

            with self.queue_lock:
                while self.queue and self.sent_this_sec < self.limit_per_sec:
                    order = self.queue.popleft()
                    self.send(order)
                    self.sent_this_sec += 1

            time.sleep(0.01)

    def close(self):
        self.latency_log_file.close()
