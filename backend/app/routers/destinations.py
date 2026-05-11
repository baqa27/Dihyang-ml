import json
import os
from fastapi import APIRouter

router = APIRouter()

# Load data from the scraped file
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "dieng_retribusi.json")

def get_destinations_from_file():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

@router.get("/")
def get_destinations():
    return get_destinations_from_file()
