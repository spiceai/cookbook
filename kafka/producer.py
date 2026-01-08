import os, time, json
from confluent_kafka import Producer
import random
import uuid
from datetime import datetime

BOOTSTRAP = os.getenv("BOOTSTRAP_SERVERS", "broker:29092")
TOPIC = os.getenv("TOPIC", "orders_events")
MPS = float(os.getenv("MPS", "1"))

p = Producer({"bootstrap.servers": BOOTSTRAP})

interval = 1.0 / MPS if MPS > 0 else 0.0

# Heartbeat tracking
message_count = 0
last_heartbeat = time.time()
heartbeat_interval = 10.0

print(f"Starting to produce test messages to topic '{TOPIC}' at rate {MPS} msg/sec")

def generate_item():
    # Generate random IDs for order, customer, part, supplier
    order_id = str(uuid.uuid4())
    custkey = random.randint(1, 1000)
    partkey = random.randint(1, 500)
    suppkey = random.randint(1, 300)
    quantity = random.randint(1, 100)
    unit_price = round(random.uniform(10.0, 1000.0), 2)
    order_ts = time.time()

    return {
        "order_id": order_id,
        "custkey": custkey,
        "partkey": partkey,
        "suppkey": suppkey,
        "quantity": quantity,
        "unit_price": unit_price,
        "order_ts": order_ts
    }

try:
    while True:  # replay forever
        json_data = generate_item()
        payload = json.dumps(json_data).encode("utf-8")
        p.produce(TOPIC, value=payload)
        p.poll(0)
        message_count += 1
        
        # Heartbeat every 10 seconds
        current_time = time.time()
        if current_time - last_heartbeat >= heartbeat_interval:
            print(f"Produced {message_count} messages so far")
            last_heartbeat = current_time
        
        if interval:
            time.sleep(interval)
except KeyboardInterrupt:
    pass
finally:
    p.flush()
    print(f"Total messages produced: {message_count}")