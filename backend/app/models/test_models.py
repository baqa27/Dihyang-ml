"""
DITA ML Test Script — Validasi Model Pasca-Retrain
===================================================
Menguji semua model ML setelah re-training dengan data 2022-2026.
Jalankan: python -m app.models.test_models
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from app.models.predict import DiengPredictor
from datetime import datetime
import json

def test_all():
    print("=" * 60)
    print("DITA ML Test Suite — Validasi Model Pasca-Retrain")
    print("=" * 60)
    
    p = DiengPredictor()
    
    if not p.models_loaded:
        print("\n❌ GAGAL: Model tidak bisa dimuat!")
        return False
    
    print("\n✅ Semua model berhasil dimuat\n")
    
    # Test scenarios
    now = datetime.now()
    h = now.hour
    mo = now.month
    doy = now.timetuple().tm_yday
    
    tests_passed = 0
    tests_total = 0
    
    # ── Test 1: Temperature Prediction ──
    print("-" * 50)
    print("TEST 1: Temperature Prediction")
    print("-" * 50)
    tests_total += 1
    try:
        result = p.predict_temperature(
            hour=h, month=mo, day_of_year=doy,
            current_temp=14.5, current_precip=0.0,
            temp_3h_ago=13.0, temp_6h_ago=11.0, temp_24h_ago=12.0,
            humidity=85.0, windspeed=8.0, cloudcover=60.0, visibility_km=5.0
        )
        print(f"  Suhu sekarang   : {result['current_temperature']}°C")
        print(f"  Prediksi 1 jam  : {result['predicted_temperature']}°C")
        print(f"  Perubahan       : {result['change']}°C")
        print(f"  Model           : {result['model']}")
        print(f"  Advisory        : {result['advisory'][:100]}")
        
        # Validasi: prediksi harus dalam range wajar Dieng (0-25°C)
        assert 0 <= result['predicted_temperature'] <= 30, f"Suhu di luar range: {result['predicted_temperature']}"
        assert result['model'] != 'Rule-based Fallback', "Model fallback, bukan ML"
        print("  ✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # ── Test 2: Rain Prediction ──
    print("\n" + "-" * 50)
    print("TEST 2: Rain Prediction")
    print("-" * 50)
    tests_total += 1
    try:
        result = p.predict_rain(
            hour=15, month=5, day_of_year=132,
            current_temp=16.0, current_precip=0.5,
            humidity=92.0, windspeed=5.0, cloudcover=80.0, visibility_km=3.0
        )
        print(f"  Akan hujan?     : {'Ya' if result['will_rain'] else 'Tidak'}")
        print(f"  Probabilitas    : {result['rain_probability']}%")
        print(f"  Model           : {result['model']}")
        print(f"  Advisory        : {result['advisory']}")
        
        assert 0 <= result['rain_probability'] <= 100, f"Probabilitas di luar range: {result['rain_probability']}"
        assert result['model'] != 'Rule-based Fallback', "Model fallback"
        print("  ✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # ── Test 3: Risk Classification ──
    print("\n" + "-" * 50)
    print("TEST 3: Risk Classification — Kondisi Normal")
    print("-" * 50)
    tests_total += 1
    try:
        result = p.predict_risk_level(
            hour=10, month=5, day_of_year=130,
            current_temp=16.0, current_precip=0.0,
            humidity=75.0, windspeed=8.0, cloudcover=40.0, visibility_km=8.0
        )
        print(f"  Risk level      : {result['risk_level']} ({result['risk_label']})")
        print(f"  Confidence      : Aman {result['confidence']['aman']}% | Waspada {result['confidence']['waspada']}% | Bahaya {result['confidence']['bahaya']}%")
        print(f"  Model           : {result['model']}")
        print(f"  Advisory        : {result['advisory'][:100]}")
        
        assert result['risk_level'] in [0, 1, 2], f"Risk level invalid: {result['risk_level']}"
        assert result['model'] != 'Rule-based Fallback', "Model fallback"
        print("  ✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # ── Test 4: Risk Classification — Kondisi Ekstrem ──
    print("\n" + "-" * 50)
    print("TEST 4: Risk Classification — Kondisi Ekstrem")
    print("-" * 50)
    tests_total += 1
    try:
        result = p.predict_risk_level(
            hour=3, month=7, day_of_year=185,
            current_temp=5.0, current_precip=3.0,
            humidity=98.0, windspeed=15.0, cloudcover=100.0, visibility_km=0.3
        )
        print(f"  Risk level      : {result['risk_level']} ({result['risk_label']})")
        print(f"  Confidence      : Aman {result['confidence']['aman']}% | Waspada {result['confidence']['waspada']}% | Bahaya {result['confidence']['bahaya']}%")
        print(f"  Advisory        : {result['advisory'][:100]}")
        
        # Kondisi ekstrem seharusnya Waspada atau Bahaya
        assert result['risk_level'] >= 1, f"Seharusnya Waspada/Bahaya, bukan Aman"
        print("  ✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # ── Test 5: Route Safety ──
    print("\n" + "-" * 50)
    print("TEST 5: Route Safety — Tanjakan Sikarim (Motor)")
    print("-" * 50)
    tests_total += 1
    try:
        result = p.predict_route_safety(
            gradient=45, width=3.0, visibility=2.0,
            guardrail=0, surface='aspal', elevation=1800,
            curve_count=15, lighting=0,
            vehicle='motorcycle', weather='kabut'
        )
        print(f"  Safety class    : {result['safety_class']} ({result['safety_label']})")
        print(f"  Confidence      : Aman {result['confidence']['aman']}% | Waspada {result['confidence']['waspada']}% | Bahaya {result['confidence']['bahaya']}%")
        print(f"  Model           : {result['model']}")
        
        # Sikarim + motor + kabut harus Bahaya (class 2)
        assert result['safety_class'] == 2, f"Seharusnya Bahaya(2), bukan {result['safety_class']}"
        print("  ✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # ── Test 6: Route Safety — Jalur Aman ──
    print("\n" + "-" * 50)
    print("TEST 6: Route Safety — Wonosobo-Kejajar (Mobil, Cerah)")
    print("-" * 50)
    tests_total += 1
    try:
        result = p.predict_route_safety(
            gradient=8, width=6.0, visibility=8.0,
            guardrail=1, surface='aspal', elevation=1200,
            curve_count=5, lighting=1,
            vehicle='car', weather='cerah'
        )
        print(f"  Safety class    : {result['safety_class']} ({result['safety_label']})")
        print(f"  Confidence      : Aman {result['confidence']['aman']}% | Waspada {result['confidence']['waspada']}% | Bahaya {result['confidence']['bahaya']}%")
        
        # Jalur utama cerah + mobil harus Aman (class 0)
        assert result['safety_class'] == 0, f"Seharusnya Aman(0), bukan {result['safety_class']}"
        print("  ✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # ── Test 7: Model Info ──
    print("\n" + "-" * 50)
    print("TEST 7: Model Info / Evaluation Report")
    print("-" * 50)
    tests_total += 1
    try:
        info = p.get_model_info()
        print(f"  Project         : {info.get('project', 'N/A')}")
        print(f"  Team            : {info.get('team', 'N/A')}")
        if 'dataset' in info:
            ds = info['dataset']
            print(f"  Dataset records : {ds.get('total_records', 'N/A')}")
            print(f"  Features        : {ds.get('features_engineered', 'N/A')}")
        if 'models' in info:
            for mname, mdata in info['models'].items():
                metrics = mdata.get('metrics', {})
                metric_str = ", ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in metrics.items())
                print(f"  {mname}: {metric_str}")
        
        assert 'models' in info, "Evaluation report tidak punya field 'models'"
        print("  ✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    # ── Summary ──
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {tests_passed}/{tests_total} passed")
    if tests_passed == tests_total:
        print("🎉 SEMUA TEST BERHASIL!")
    else:
        print(f"⚠️ {tests_total - tests_passed} test gagal")
    print("=" * 60)
    
    return tests_passed == tests_total


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
