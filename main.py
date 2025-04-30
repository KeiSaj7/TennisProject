import os
from dotenv import load_dotenv
from sportradar import CompetitorProfile, SeasonCompetitors
from database import manage as db
from scraper import get_H2H_stats
from web_server.app import start_app

load_dotenv()
API_KEY = os.getenv("API_KEY")

def Refresh():
    ids = db.get_competitors_ids()
    SeasonCompetitors.SeasonCompetitors()
    CompetitorProfile.CompetitorProfile(API_KEY, ids)
    db.calc_every_rating_for_all_competitors()
    
    

if __name__ == "__main__":
    print("Tennis Predictor v1.0")
    db.get_h2h_ratings('sr:competitor:407573', 'sr:competitor:14882')
    #start_app()

    
    
    
