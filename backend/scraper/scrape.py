import requests
import json
import time

def get_dieng_historical_weather():
    print("Scraping historical weather from Open-Meteo for Dieng...")
    # Koordinat Dieng
    lat = -7.2125
    lon = 109.9100
    
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2023-01-01&end_date=2023-12-31&hourly=temperature_2m,precipitation&timezone=Asia/Jakarta"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Save to JSON
        with open("dieng_historical_2023.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Success! Data saved to dieng_historical_2023.json")
    except Exception as e:
        print(f"Error scraping weather: {e}")

def scrape_destinations_data():
    print("Scraping destinations data (Simulated)...")
    time.sleep(1)
    
    # In a real scenario, you'd use BeautifulSoup to scrape an official tourism site.
    # Because there's no single API for Dieng tickets, we structure the mock data here.
    
    destinations = [
        { "name": "Kawah Sikidang", "retribusi_lokal": 20000, "retribusi_asing": 50000 },
        { "name": "Candi Arjuna", "retribusi_lokal": 15000, "retribusi_asing": 30000 },
        { "name": "Bukit Sikunir", "retribusi_lokal": 15000, "retribusi_asing": 15000 },
    ]
    
    with open("dieng_retribusi.json", "w") as f:
        json.dump(destinations, f, indent=4)
    print("Success! Data saved to dieng_retribusi.json")

if __name__ == "__main__":
    get_dieng_historical_weather()
    scrape_destinations_data()
