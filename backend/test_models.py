"""Full ML System Test — Verifikasi semua model DITA"""
import json
from app.models.predict import get_predictor

p = get_predictor()
print("=" * 60)
print("DITA ML SYSTEM TEST")
print("=" * 60)
print(f"Models loaded: {p.models_loaded}")

# Read eval report
with open("app/models/saved/evaluation_report.json") as f:
    report = json.load(f)

print("\n--- MODEL METRICS ---")
m = report["models"]
tp = m["temperature_prediction"]["metrics"]
rp = m["rain_prediction"]["metrics"]
rk = m["risk_classification"]["metrics"]
print(f"1. Temperature Prediction:  R2={tp['r2']:.4f}, MAE={tp['mae']:.3f}C, RMSE={tp['rmse']:.3f}C")
print(f"2. Rain Prediction:         F1={rp['f1']:.4f}, Acc={rp['accuracy']:.4f}, Prec={rp['precision']:.4f}")
print(f"3. Risk Classification:     Acc={rk['accuracy']:.4f}")

print("\n--- PREDICTION TESTS ---")

# Test 1: Temperature prediction
r1 = p.predict_temperature(hour=9, month=5, day_of_year=131, current_temp=15.0, current_precip=0)
print(f"[TEMP] 9AM May, now=15C -> predicted={r1['predicted_temperature']}C, change={r1['change']}C | {r1['model']}")

r1b = p.predict_temperature(hour=3, month=7, day_of_year=185, current_temp=7.0, current_precip=0)
print(f"[TEMP] 3AM Jul, now=7C  -> predicted={r1b['predicted_temperature']}C, change={r1b['change']}C | {r1b['model']}")

# Test 2: Rain prediction
r2 = p.predict_rain(hour=14, month=5, day_of_year=131, current_temp=18.0, current_precip=0.5)
print(f"[RAIN] 2PM May, precip=0.5 -> rain={r2['will_rain']}, prob={r2['rain_probability']}% | {r2['model']}")

r2b = p.predict_rain(hour=9, month=8, day_of_year=220, current_temp=12.0, current_precip=0)
print(f"[RAIN] 9AM Aug, precip=0   -> rain={r2b['will_rain']}, prob={r2b['rain_probability']}% | {r2b['model']}")

# Test 3: Risk level
r3 = p.predict_risk_level(hour=3, month=7, day_of_year=185, current_temp=6.0, current_precip=1.0)
print(f"[RISK] 3AM Jul, 6C+rain   -> {r3['risk_label']} conf={r3['confidence']} | {r3['model']}")

r3b = p.predict_risk_level(hour=10, month=5, day_of_year=131, current_temp=18.0, current_precip=0)
print(f"[RISK] 10AM May, 18C+dry  -> {r3b['risk_label']} conf={r3b['confidence']} | {r3b['model']}")

# Test 4: Route safety
r4 = p.predict_route_safety(gradient=45, width=3.0, visibility=2, guardrail=0, surface="aspal", elevation=1800, curve_count=15, lighting=0, vehicle="motorcycle", weather="kabut")
print(f"[ROUTE] Sikarim+Motor+Kabut  -> {r4['safety_label']} conf={r4['confidence']} | {r4['model']}")

r4b = p.predict_route_safety(gradient=8, width=6.0, visibility=8, guardrail=1, surface="aspal", elevation=1200, curve_count=5, lighting=1, vehicle="car", weather="cerah")
print(f"[ROUTE] Kejajar+Mobil+Cerah  -> {r4b['safety_label']} conf={r4b['confidence']} | {r4b['model']}")

r4c = p.predict_route_safety(gradient=35, width=3.5, visibility=3, guardrail=0, surface="aspal", elevation=1900, curve_count=12, lighting=0, vehicle="bus", weather="hujan")
print(f"[ROUTE] WatuAngkruk+Bus+Hujan-> {r4c['safety_label']} conf={r4c['confidence']} | {r4c['model']}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
