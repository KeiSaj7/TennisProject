from fastapi import FastAPI
from database.manage import add_to_season_competitors, add_competitor_profile, get_all_competitors_names, get_competitor_full_data, get_competitor_id_by_name, get_h2h_data, calc_every_rating_for_all_competitors
from scraper import get_H2H_stats

app = FastAPI()

""" Collector Section"""
@app.post("/SeasonCompetitors")
async def refresh_SeasonCompetitors(data: list[dict] ):
    add_to_season_competitors(data)
    return {"message": "[Controller] SeasonCompetitors data refreshed successfully"}

@app.post("/CompetitorProfile")
async def refresh_CompetitorProfile(data: dict):
    add_competitor_profile(data)
    return {"message": "[Controller] CompetitorProfile data refreshed successfully"}

@app.get("/calc_elo")
async def calculate_elo():
    calc_every_rating_for_all_competitors()
    return {"message": "[Controller] ELO ratings calculated for all competitors successfully"}

""" GUI Section"""
@app.get("/competitors")
async def get_competitors() -> list[str]:
    competitors = get_all_competitors_names()
    return competitors

@app.get("/full_data")
async def get_full_data(name: str):
    player, periods, surface_data = get_competitor_full_data(name)
    return player, periods, surface_data

@app.get("/competitor_id")
async def get_competitor_id(name: str):
    id = get_competitor_id_by_name(name)
    return id

@app.get("/h2h_stats")
async def get_h2h_stats(player1: str, player2: str):
    h2h_stats = get_H2H_stats(player1, player2)
    return h2h_stats

@app.get("/h2h_data")
async def get_h2h(player1: str, player2: str):
    h2h_data = get_h2h_data(player1, player2)
    return h2h_data