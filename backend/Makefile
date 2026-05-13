.PHONY: help install scrape train test run clean

help:
	@echo "DITA Backend - Available Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make scrape     - Scrape weather data"
	@echo "  make train      - Train ML models"
	@echo "  make run        - Run FastAPI server"
	@echo "  make clean      - Clean cache files"

install:
	pip install -r requirements.txt

scrape:
	python scraper/scrape.py
	python scraper/scrape.py --realtime

train:
	python -m app.models.train_weather_model
	python -m app.models.train_route_model

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
