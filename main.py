import os
from dotenv import load_dotenv
from sportradar import CompetitorProfile, SeasonCompetitors
from database import manage as db
from scraper import get_H2H_stats
from web_server.app import start_app

load_dotenv()
API_KEY = os.getenv("API_KEY")

if __name__ == "__main__":
    print("Tennis Predictor v1.0")
    start_app()
    #SeasonCompetitors(API_KEY)
    #competitors_ids = db.get_competitors_ids()
    #name1 = db.get_competitor_name_by_id("sr:competitor:429603")
    #name2 = db.get_competitor_name_by_id("sr:competitor:23581")
    #print(get_H2H_stats(db.get_competitor_name_by_id(competitors_ids[4]), db.get_competitor_name_by_id(competitors_ids[8])))
    #print(get_H2H_stats(db.get_competitor_name_by_id(competitors_ids[12]), db.get_competitor_name_by_id(competitors_ids[47])))
    #print(get_H2H_stats(db.get_competitor_name_by_id(competitors_ids[56]), db.get_competitor_name_by_id(competitors_ids[23])))
    
    
    
