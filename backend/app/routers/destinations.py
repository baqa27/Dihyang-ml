import json
import os
from fastapi import APIRouter
from ..models.knowledge_base import DESTINATIONS, RETRIBUSI_DATA

router = APIRouter()

@router.get("/")
def get_destinations():
    result = []
    # Gabungkan data DESTINATIONS dengan RETRIBUSI_DATA
    for dest in DESTINATIONS:
        name = dest.get("name")
        retribusi = RETRIBUSI_DATA.get(name, {})
        
        result.append({
            "name": name,
            "location": "Dieng, Wonosobo",
            "priceLocal": f"Rp {retribusi.get('lokal', 0):,}",
            "priceForeign": f"Rp {retribusi.get('asing', 0):,}",
            "hours": "07.00–17.00", # default
            "rating": 4.5,          # default
            "category": dest.get("type", "Alam"),
            "tip": dest.get("tips", dest.get("description", ""))
        })
    return result
