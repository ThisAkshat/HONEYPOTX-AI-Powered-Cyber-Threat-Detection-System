# Use of model.py → Defines the structure/schema of stored data (attack logs, user activity, payloads).

def log_schema(data):
    return {
        "ip": data.get("ip"),
        "endpoint": data.get("endpoint"),
        "payload": data.get("payload"),
        "attack_type": data.get("attack_type"),
        "risk": data.get("risk")
    }