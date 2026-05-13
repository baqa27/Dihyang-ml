"""
DITA Auto-Retrain Service
Otomatis retrain model dengan data terbaru setiap minggu.
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "models" / "saved"
DATA_DIR = Path(__file__).parent.parent / "data"
SCRAPER_PATH = Path(__file__).parent.parent.parent / "scraper" / "scrape.py"
TRAIN_SCRIPT = Path(__file__).parent.parent / "models" / "train_weather_model.py"

class AutoRetrainer:
    def __init__(self, retrain_interval_days=7):
        self.interval_days = retrain_interval_days
        self.last_retrain = self._load_last_retrain()
        
    def _load_last_retrain(self):
        """Load timestamp last retrain dari file."""
        marker_file = MODEL_DIR / "last_retrain.json"
        if marker_file.exists():
            with open(marker_file, "r") as f:
                data = json.load(f)
                return datetime.fromisoformat(data["timestamp"])
        return None
    
    def _save_last_retrain(self):
        """Save timestamp retrain ke file."""
        marker_file = MODEL_DIR / "last_retrain.json"
        with open(marker_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }, f, indent=2)
    
    def should_retrain(self):
        """Check apakah sudah waktunya retrain."""
        if self.last_retrain is None:
            return True
        
        days_since = (datetime.now() - self.last_retrain).days
        return days_since >= self.interval_days
    
    def scrape_latest_data(self):
        """Scrape data 30 hari terakhir."""
        print("[AutoRetrain] Scraping latest 30 days data...")
        try:
            result = subprocess.run(
                ["python", str(SCRAPER_PATH), "--latest"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("[AutoRetrain] ✅ Scraping berhasil")
                return True
            else:
                print(f"[AutoRetrain] ❌ Scraping gagal: {result.stderr}")
                return False
        except Exception as e:
            print(f"[AutoRetrain] ❌ Error: {e}")
            return False
    
    def merge_latest_to_combined(self):
        """Merge data 30 hari terakhir ke combined dataset."""
        print("[AutoRetrain] Merging latest data to combined...")
        
        combined_file = DATA_DIR / "dieng_historical_combined.json"
        latest_file = DATA_DIR / "dieng_historical_latest_30d.json"
        
        if not latest_file.exists():
            print("[AutoRetrain] ❌ Latest data tidak ada")
            return False
        
        try:
            # Load latest data
            with open(latest_file, "r") as f:
                latest = json.load(f)
            
            # Load atau create combined
            if combined_file.exists():
                with open(combined_file, "r") as f:
                    combined = json.load(f)
            else:
                # Jika belum ada combined, gunakan latest sebagai base
                combined = latest
                with open(combined_file, "w") as f:
                    json.dump(combined, f, separators=(",", ":"))
                print("[AutoRetrain] ✅ Created new combined dataset")
                return True
            
            # Merge: append data baru, remove duplicates by timestamp
            hourly_combined = combined.get("hourly", {})
            hourly_latest = latest.get("hourly", {})
            
            # Get existing timestamps
            existing_times = set(hourly_combined.get("time", []))
            
            # Append new data
            new_count = 0
            for i, time in enumerate(hourly_latest.get("time", [])):
                if time not in existing_times:
                    # Append ke semua keys
                    for key in hourly_latest.keys():
                        if key not in hourly_combined:
                            hourly_combined[key] = []
                        hourly_combined[key].append(hourly_latest[key][i])
                    new_count += 1
            
            combined["hourly"] = hourly_combined
            combined["total_records"] = len(hourly_combined.get("time", []))
            
            # Save
            with open(combined_file, "w") as f:
                json.dump(combined, f, separators=(",", ":"))
            
            print(f"[AutoRetrain] ✅ Merged {new_count} new records")
            return True
            
        except Exception as e:
            print(f"[AutoRetrain] ❌ Merge error: {e}")
            return False
    
    def retrain_models(self):
        """Retrain semua model dengan data terbaru."""
        print("[AutoRetrain] Retraining models...")
        try:
            result = subprocess.run(
                ["python", "-m", "app.models.train_weather_model"],
                capture_output=True,
                text=True,
                timeout=600,  # 10 menit max
                cwd=str(Path(__file__).parent.parent.parent)
            )
            
            if result.returncode == 0:
                print("[AutoRetrain] ✅ Retraining berhasil")
                print(result.stdout[-500:])  # Print last 500 chars
                return True
            else:
                print(f"[AutoRetrain] ❌ Retraining gagal: {result.stderr}")
                return False
        except Exception as e:
            print(f"[AutoRetrain] ❌ Error: {e}")
            return False
    
    def run_full_retrain(self):
        """Jalankan full retrain pipeline."""
        print("\n" + "="*60)
        print("DITA AUTO-RETRAIN PIPELINE")
        print("="*60)
        print(f"Started at: {datetime.now()}")
        
        # Step 1: Scrape latest data
        if not self.scrape_latest_data():
            print("[AutoRetrain] ❌ Pipeline failed at scraping")
            return False
        
        # Step 2: Merge to combined
        if not self.merge_latest_to_combined():
            print("[AutoRetrain] ❌ Pipeline failed at merging")
            return False
        
        # Step 3: Retrain models
        if not self.retrain_models():
            print("[AutoRetrain] ❌ Pipeline failed at retraining")
            return False
        
        # Step 4: Save timestamp
        self._save_last_retrain()
        self.last_retrain = datetime.now()
        
        print("\n" + "="*60)
        print("✅ AUTO-RETRAIN PIPELINE SELESAI")
        print(f"Completed at: {datetime.now()}")
        print(f"Next retrain: {datetime.now() + timedelta(days=self.interval_days)}")
        print("="*60)
        
        return True
    
    def get_status(self):
        """Status auto-retrain."""
        next_retrain = None
        if self.last_retrain:
            next_retrain = self.last_retrain + timedelta(days=self.interval_days)
        
        return {
            "last_retrain": self.last_retrain.isoformat() if self.last_retrain else None,
            "next_retrain": next_retrain.isoformat() if next_retrain else "pending",
            "interval_days": self.interval_days,
            "should_retrain": self.should_retrain(),
        }


# Singleton instance
_retrainer = None

def get_retrainer(interval_days=7):
    global _retrainer
    if _retrainer is None:
        _retrainer = AutoRetrainer(interval_days)
    return _retrainer


if __name__ == "__main__":
    # Manual trigger untuk testing
    retrainer = get_retrainer()
    retrainer.run_full_retrain()
