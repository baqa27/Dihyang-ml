"""
DITA Services Package
"""

from .realtime_scheduler import get_scheduler
from .auto_retrain import get_retrainer

__all__ = ["get_scheduler", "get_retrainer"]
