
# Order Management System

## Description
A backend order management system that:
- Accepts orders within a configurable time window
- Sends logon/logout based on trading hours
- Throttles X orders/second
- Supports Modify/Cancel logic in the queue
- Logs round-trip latency for exchange responses

## Files
- `order_management.py`: Core OMS logic
- `test_order_management.py`: Unit tests
- `simulator.py`: Sample runner and exchange simulation

## Run Tests
```bash
python3 -m unittest test_order_management.py
```

## Run Simulation
```bash
python3 simulator.py
```

## Assumptions
- All orders outside market time are rejected
- Logon sent once per day; logout after market closes
- Persistent logs are written to `responses.log`
