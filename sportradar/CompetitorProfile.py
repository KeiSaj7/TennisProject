import requests
import time
from database.manage import add_competitor_profile

def CompetitorProfile(API_KEY: str, competitors_ids : list[str]) -> None:
    params = {
        "api_key": API_KEY
    }
    headers = {"accept": "application/json"}
    
    for competitor_id in competitors_ids:
        base_url = f"https://api.sportradar.com/tennis/trial/v3/en/competitors/{competitor_id}/profile.json"
        try:
            response = requests.get(url=base_url, params=params).json()
            print(f"[API] CompetitorProfile data for {competitor_id} fetched successfully. {len(competitors_ids) - competitors_ids.index(competitor_id) - 1} left.")
            add_competitor_profile(response)
        except requests.exceptions.RequestException as e:
            print(f"[API] An error occurred: {e}")
        finally:
            time.sleep(1.1)
    print("[API] CompetitorProfile data fetched successfully.")