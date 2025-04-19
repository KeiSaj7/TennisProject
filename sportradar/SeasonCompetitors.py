import requests
from database.manage import add_to_season_competitors

def SeasonCompetitors(API_KEY: str) -> None:
    base_url = "https://api.sportradar.com/tennis/trial/v3/en/seasons/sr%3Aseason%3A115101/competitors.json"

    params = {
        "api_key": API_KEY
    }
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url=base_url, params=params).json()
        data = response["season_competitors"]
        print("[API] SeasonCompetitors data fetched successfully.")
        add_to_season_competitors(data)
    except requests.exceptions.RequestException as e:
        print(f"[API] An error occurred: {e}")
