"""
==============================================================================
DITA Model Versioning System
==============================================================================
Sistem untuk menyimpan dan manage berbagai versi model ML.
Memilih model terbaik berdasarkan metrics dan menyimpan history.

Features:
- Auto-save model dengan timestamp
- Comparison metrics antar versi
- Rollback ke versi sebelumnya
- Best model selection

Author: Tim PJK-GM067 (Ida Masruroh — AI Engineer)
==============================================================================
"""

import os
import json
import joblib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

MODEL_DIR = Path(__file__).parent / "saved"
ARCHIVE_DIR = MODEL_DIR / "archive"
ARCHIVE_DIR.mkdir(exist_ok=True)

class ModelVersionManager:
    """Manager untuk versioning model ML."""
    
    def __init__(self):
        self.model_dir = MODEL_DIR
        self.archive_dir = ARCHIVE_DIR
        self.version_file = self.archive_dir / "version_history.json"
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load version history dari file."""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save version history ke file."""
        with open(self.version_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def save_version(
        self,
        model_type: str,
        metrics: Dict[str, float],
        note: str = ""
    ) -> str:
        """
        Simpan versi model baru dengan metrics.
        
        Args:
            model_type: "temperature", "rain", "risk", "route"
            metrics: Dict metrics (e.g., {"r2": 0.9958, "mae": 0.088})
            note: Catatan versi
            
        Returns:
            version_id: ID versi yang tersimpan
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"{model_type}_v{timestamp}"
        
        # File mapping berdasarkan model type
        model_files = {
            "temperature": [
                "temperature_model.pkl",
                "temp_scaler.pkl"
            ],
            "rain": [
                "rain_classifier.pkl",
                "rain_scaler.pkl"
            ],
            "risk": [
                "risk_classifier.pkl",
                "risk_scaler.pkl"
            ],
            "route": [
                "route_safety_model.pkl",
                "route_scaler.pkl",
                "le_surface.pkl",
                "le_vehicle.pkl",
                "le_weather.pkl"
            ]
        }
        
        # Create version directory
        version_dir = self.archive_dir / version_id
        version_dir.mkdir(exist_ok=True)
        
        # Copy files ke archive
        files = model_files.get(model_type, [])
        for filename in files:
            src = self.model_dir / filename
            if src.exists():
                dst = version_dir / filename
                shutil.copy2(src, dst)
        
        # Save metadata
        metadata = {
            "version_id": version_id,
            "model_type": model_type,
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "metrics": metrics,
            "note": note,
            "files": files,
        }
        
        metadata_file = version_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update history
        self.history.append(metadata)
        self._save_history()
        
        print(f"✅ Model {model_type} disimpan sebagai {version_id}")
        print(f"   Metrics: {metrics}")
        
        return version_id
    
    def get_best_version(self, model_type: str, metric: str = "auto") -> Dict:
        """
        Ambil versi terbaik berdasarkan metric.
        
        Args:
            model_type: "temperature", "rain", "risk", "route"
            metric: metric yang dipakai ("auto", "r2", "accuracy", dll)
        
        Returns:
            metadata versi terbaik
        """
        # Filter by model type
        versions = [v for v in self.history if v["model_type"] == model_type]
        
        if not versions:
            return None
        
        # Auto-select metric berdasarkan model type
        if metric == "auto":
            metric_map = {
                "temperature": "r2",
                "rain": "f1",
                "risk": "accuracy",
                "route": "accuracy",
            }
            metric = metric_map.get(model_type, "accuracy")
        
        # Find best version
        best = max(
            versions,
            key=lambda v: v["metrics"].get(metric, 0)
        )
        
        return best
    
    def restore_version(self, version_id: str):
        """
        Restore model ke versi tertentu.
        
        Args:
            version_id: ID versi yang mau di-restore
        """
        version_dir = self.archive_dir / version_id
        
        if not version_dir.exists():
            raise ValueError(f"Version {version_id} tidak ditemukan!")
        
        # Load metadata
        metadata_file = version_dir / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Copy files kembali ke saved/
        for filename in metadata["files"]:
            src = version_dir / filename
            if src.exists():
                dst = self.model_dir / filename
                shutil.copy2(src, dst)
        
        print(f"✅ Model restored ke versi: {version_id}")
        print(f"   Metrics: {metadata['metrics']}")
    
    def list_versions(self, model_type: str = None) -> List[Dict]:
        """
        List semua versi yang tersimpan.
        
        Args:
            model_type: Filter by model type (optional)
        
        Returns:
            List metadata versions
        """
        if model_type:
            return [v for v in self.history if v["model_type"] == model_type]
        return self.history
    
    def compare_versions(
        self,
        version_id1: str,
        version_id2: str
    ) -> Dict:
        """
        Compare 2 versi model.
        
        Returns:
            Dict dengan comparison results
        """
        v1 = next((v for v in self.history if v["version_id"] == version_id1), None)
        v2 = next((v for v in self.history if v["version_id"] == version_id2), None)
        
        if not v1 or not v2:
            raise ValueError("Salah satu version ID tidak ditemukan!")
        
        comparison = {
            "version1": {
                "id": v1["version_id"],
                "datetime": v1["datetime"],
                "metrics": v1["metrics"],
            },
            "version2": {
                "id": v2["version_id"],
                "datetime": v2["datetime"],
                "metrics": v2["metrics"],
            },
            "diff": {}
        }
        
        # Calculate diff
        for metric in v1["metrics"]:
            if metric in v2["metrics"]:
                diff = v2["metrics"][metric] - v1["metrics"][metric]
                comparison["diff"][metric] = {
                    "absolute": diff,
                    "percentage": (diff / v1["metrics"][metric] * 100) if v1["metrics"][metric] != 0 else 0
                }
        
        return comparison
    
    def cleanup_old_versions(self, keep_last_n: int = 5):
        """
        Hapus versi lama, keep N versi terbaru per model type.
        
        Args:
            keep_last_n: Jumlah versi yang mau dipertahankan
        """
        model_types = set(v["model_type"] for v in self.history)
        
        for mtype in model_types:
            versions = [v for v in self.history if v["model_type"] == mtype]
            versions.sort(key=lambda v: v["timestamp"], reverse=True)
            
            # Delete old versions
            for old_version in versions[keep_last_n:]:
                version_dir = self.archive_dir / old_version["version_id"]
                if version_dir.exists():
                    shutil.rmtree(version_dir)
                    print(f"🗑️ Deleted old version: {old_version['version_id']}")
                
                # Remove from history
                self.history.remove(old_version)
        
        self._save_history()


# Singleton instance
_manager = None

def get_version_manager():
    global _manager
    if _manager is None:
        _manager = ModelVersionManager()
    return _manager
