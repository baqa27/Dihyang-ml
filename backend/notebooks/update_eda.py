"""
Script untuk update EDA dengan data terbaru (2022-2025)
Jalankan: python notebooks/update_eda.py
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Setup
DATA_DIR = Path(__file__).parent.parent / "app" / "data"
OUTPUT_DIR = Path(__file__).parent / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

print("="*60)
print("DITA EDA Update - Data 2022-2025")
print("="*60)

# Load combined data
print("\n1. Loading combined dataset...")
with open(DATA_DIR / "dieng_historical_combined.json", "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data["hourly"])
df["time"] = pd.to_datetime(df["time"])
df.set_index("time", inplace=True)

print(f"   Total records: {len(df):,}")
print(f"   Date range: {df.index.min()} to {df.index.max()}")
print(f"   Variables: {len(df.columns)}")

# Basic statistics
print("\n2. Basic Statistics:")
print(df[["temperature_2m", "precipitation", "relativehumidity_2m", "windspeed_10m"]].describe())

# Temperature analysis
print("\n3. Temperature Analysis:")
print(f"   Mean: {df['temperature_2m'].mean():.2f}°C")
print(f"   Min: {df['temperature_2m'].min():.2f}°C")
print(f"   Max: {df['temperature_2m'].max():.2f}°C")
print(f"   Std: {df['temperature_2m'].std():.2f}°C")

# Extreme cold events (< 5°C)
cold_events = df[df["temperature_2m"] < 5]
print(f"   Extreme cold events (<5°C): {len(cold_events):,} ({len(cold_events)/len(df)*100:.2f}%)")

# Rain analysis
print("\n4. Rain Analysis:")
rainy_hours = df[df["precipitation"] > 0]
print(f"   Rainy hours: {len(rainy_hours):,} ({len(rainy_hours)/len(df)*100:.2f}%)")
print(f"   Max precipitation: {df['precipitation'].max():.2f} mm")
print(f"   Mean (when raining): {rainy_hours['precipitation'].mean():.2f} mm")

# Visibility analysis
print("\n5. Visibility Analysis:")
low_vis = df[df["visibility"] < 2000]  # < 2 km
print(f"   Low visibility (<2km): {len(low_vis):,} ({len(low_vis)/len(df)*100:.2f}%)")
print(f"   Mean visibility: {df['visibility'].mean()/1000:.2f} km")

# Monthly patterns
print("\n6. Monthly Patterns:")
df["month"] = df.index.month
monthly = df.groupby("month").agg({
    "temperature_2m": "mean",
    "precipitation": "sum",
    "relativehumidity_2m": "mean"
})
print(monthly)

# Hourly patterns
print("\n7. Hourly Patterns:")
df["hour"] = df.index.hour
hourly = df.groupby("hour").agg({
    "temperature_2m": "mean",
    "precipitation": "sum"
})
print(f"   Coldest hour: {hourly['temperature_2m'].idxmin()}:00 ({hourly['temperature_2m'].min():.2f}°C)")
print(f"   Warmest hour: {hourly['temperature_2m'].idxmax()}:00 ({hourly['temperature_2m'].max():.2f}°C)")

# Risk hours (cold + rain)
print("\n8. Risk Analysis:")
risk_hours = df[(df["temperature_2m"] < 10) & (df["precipitation"] > 0)]
print(f"   High risk hours (cold+rain): {len(risk_hours):,} ({len(risk_hours)/len(df)*100:.2f}%)")

# Visualization
print("\n9. Creating visualizations...")

# Plot 1: Temperature distribution
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
plt.hist(df["temperature_2m"], bins=50, color="#00b4cc", alpha=0.7, edgecolor="black")
plt.axvline(df["temperature_2m"].mean(), color="red", linestyle="--", label=f"Mean: {df['temperature_2m'].mean():.1f}°C")
plt.xlabel("Temperature (°C)")
plt.ylabel("Frequency")
plt.title("Temperature Distribution (2022-2025)")
plt.legend()
plt.grid(alpha=0.3)

plt.subplot(1, 2, 2)
plt.hist(df["precipitation"], bins=50, color="#a78bfa", alpha=0.7, edgecolor="black")
plt.xlabel("Precipitation (mm)")
plt.ylabel("Frequency")
plt.title("Precipitation Distribution (2022-2025)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_distributions.png", dpi=150, bbox_inches="tight")
print(f"   Saved: {OUTPUT_DIR / '01_distributions.png'}")

# Plot 2: Monthly patterns
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
monthly["temperature_2m"].plot(kind="bar", color="#00b4cc", alpha=0.7)
plt.xlabel("Month")
plt.ylabel("Mean Temperature (°C)")
plt.title("Monthly Average Temperature")
plt.xticks(rotation=0)
plt.grid(alpha=0.3)

plt.subplot(1, 2, 2)
monthly["precipitation"].plot(kind="bar", color="#a78bfa", alpha=0.7)
plt.xlabel("Month")
plt.ylabel("Total Precipitation (mm)")
plt.title("Monthly Total Precipitation")
plt.xticks(rotation=0)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_monthly_patterns.png", dpi=150, bbox_inches="tight")
print(f"   Saved: {OUTPUT_DIR / '02_monthly_patterns.png'}")

# Plot 3: Hourly patterns
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
hourly["temperature_2m"].plot(color="#00b4cc", linewidth=2, marker="o")
plt.xlabel("Hour of Day")
plt.ylabel("Mean Temperature (°C)")
plt.title("Hourly Temperature Pattern")
plt.grid(alpha=0.3)

plt.subplot(1, 2, 2)
hourly["precipitation"].plot(kind="bar", color="#a78bfa", alpha=0.7)
plt.xlabel("Hour of Day")
plt.ylabel("Total Precipitation (mm)")
plt.title("Hourly Precipitation Pattern")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_hourly_patterns.png", dpi=150, bbox_inches="tight")
print(f"   Saved: {OUTPUT_DIR / '03_hourly_patterns.png'}")

# Plot 4: Correlation heatmap
plt.figure(figsize=(10, 8))
corr_vars = ["temperature_2m", "precipitation", "relativehumidity_2m", 
             "windspeed_10m", "visibility", "cloudcover", "surface_pressure"]
corr = df[corr_vars].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, 
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title("Feature Correlation Matrix")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_correlation.png", dpi=150, bbox_inches="tight")
print(f"   Saved: {OUTPUT_DIR / '04_correlation.png'}")

print("\n" + "="*60)
print("EDA Update Complete!")
print(f"Figures saved to: {OUTPUT_DIR}")
print("="*60)
