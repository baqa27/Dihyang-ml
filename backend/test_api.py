"""Test semua API endpoint ML"""
import urllib.request
import json

BASE = "http://127.0.0.1:8000/api"

def test_get(path):
    try:
        r = urllib.request.urlopen(f"{BASE}{path}", timeout=10)
        data = json.loads(r.read().decode())
        return True, data
    except Exception as e:
        return False, str(e)

def test_post(path, body):
    try:
        req = urllib.request.Request(
            f"{BASE}{path}",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"}
        )
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read().decode())
        return True, data
    except Exception as e:
        return False, str(e)

print("=" * 60)
print("API ENDPOINT TESTS")
print("=" * 60)

# 1. Model Info
ok, d = test_get("/ml/model-info")
print(f"\n[{'OK' if ok else 'FAIL'}] GET /api/ml/model-info")
if ok:
    print(f"  models_loaded: {d.get('models_loaded')}")

# 2. Quick prediction
ok, d = test_get("/ml/predict/quick")
print(f"\n[{'OK' if ok else 'FAIL'}] GET /api/ml/predict/quick")
if ok:
    print(f"  temp: {d.get('temperature', {}).get('predicted_temperature')}C")
    print(f"  rain: {d.get('rain', {}).get('rain_probability')}%")
    print(f"  risk: {d.get('risk', {}).get('risk_label')}")

# 3. Temperature prediction
body = {"hour": 9, "month": 5, "day_of_year": 131, "current_temp": 15.0, "current_precip": 0}
ok, d = test_post("/ml/predict/temperature", body)
print(f"\n[{'OK' if ok else 'FAIL'}] POST /api/ml/predict/temperature")
if ok:
    print(f"  predicted: {d.get('predicted_temperature')}C, model: {d.get('model')}")

# 4. Rain prediction
ok, d = test_post("/ml/predict/rain", body)
print(f"\n[{'OK' if ok else 'FAIL'}] POST /api/ml/predict/rain")
if ok:
    print(f"  rain: {d.get('will_rain')}, prob: {d.get('rain_probability')}%")

# 5. Risk prediction
ok, d = test_post("/ml/predict/risk", body)
print(f"\n[{'OK' if ok else 'FAIL'}] POST /api/ml/predict/risk")
if ok:
    print(f"  risk: {d.get('risk_label')}, confidence: {d.get('confidence')}")

# 6. Route safety
route_body = {"gradient": 45, "width": 3.0, "visibility": 2, "guardrail": 0, "surface": "aspal", "elevation": 1800, "curve_count": 15, "lighting": 0, "vehicle": "motorcycle", "weather": "kabut"}
ok, d = test_post("/ml/predict/route-safety", route_body)
print(f"\n[{'OK' if ok else 'FAIL'}] POST /api/ml/predict/route-safety")
if ok:
    print(f"  safety: {d.get('safety_label')}, conf: {d.get('confidence')}")

# 7. Chat (NLP)
chat_body = {"message": "berapa biaya masuk kawah sikidang?", "history": []}
ok, d = test_post("/chat", chat_body)
print(f"\n[{'OK' if ok else 'FAIL'}] POST /api/chat")
if ok:
    reply_preview = d.get("reply", "")[:120]
    print(f"  reply: {reply_preview}...")

print("\n" + "=" * 60)
print("API TESTS COMPLETE")
print("=" * 60)
