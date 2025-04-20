import sqlite3

con = sqlite3.connect('tennis.db', check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()

# SeaonCompetitors Table
def add_to_season_competitors(data: dict) -> None:
    table="SeasonCompetitors"
    try:
        cur.executemany(
            f"INSERT OR REPLACE INTO {table} VALUES (:id, :name, :short_name, :abbreviation)", data
        )
        con.commit()
        print(f"[DB] Data inserted into {table} table successfully.")
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")

def get_competitors_ids() -> list[str]:
    table="SeasonCompetitors"
    try:
        competitors_ids = cur.execute(f"SELECT id FROM {table}").fetchall()
        return [row["id"] for row in competitors_ids]
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return ["Error"]

def get_competitor_name_by_id(competitor_id: str) -> str:
    table="SeasonCompetitors"
    try:
        competitor_name: str = cur.execute(f"SELECT name FROM {table} WHERE id = ?", (competitor_id,)).fetchone()
        return competitor_name["name"] if competitor_name else None
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
    
def get_all_competitors_names() -> list[str]:
    table="SeasonCompetitors"
    try:
        competitors_names = cur.execute(f"SELECT name FROM {table}").fetchall()
        return [row["name"].replace(',', '') for row in competitors_names]
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return ["Error"]
    
# CompetitorProfile Table and it's sub-tables

def add_competitor_profile(data: dict) -> None:
    try:
        competitor = data.get("competitor", {})
        info = data.get("info", {})
        rankings = data.get("competitor_rankings", [{}])

        cur.execute(
            """INSERT OR REPLACE INTO CompetitorProfile 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            (                 
                competitor.get("id"),
                competitor.get("name"),
                competitor.get("country"),
                competitor.get("abbreviation"),
                info.get("pro_year"),
                info.get("handedness"),
                info.get("highest_singles_ranking"),
                info.get("weight"),
                info.get("height"),
                info.get("date_of_birth"),
                info.get("highest_singles_ranking_date"),
                rankings[0].get("rank"),
                rankings[0].get("points")
            )
        )

        for period in data.get("periods", []):
            period_stats = period.get("statistics", {})
            cur.execute(
                """INSERT OR REPLACE INTO Periods 
                (competitor_id, year, competitions_played, competitions_won, matches_played, matches_won) 
                VALUES (?, ?, ?, ?, ?, ?)""", 
                (
                    competitor.get("id"),
                    period.get("year"),
                    period_stats.get("competitions_played"),
                    period_stats.get("competitions_won"),
                    period_stats.get("matches_played"),
                    period_stats.get("matches_won"),
                )
            )
            period_id = cur.lastrowid

            for surface in period.get("surfaces", []):
                surface_stats = surface.get("statistics", {})
                cur.execute(
                    """INSERT OR REPLACE INTO Surfaces 
                    VALUES (?, ?, ?, ?, ?, ?)""", 
                    (
                        period_id,
                        surface.get("type"),
                        surface_stats.get("competitions_played"),
                        surface_stats.get("competitions_won"),
                        surface_stats.get("matches_played"),
                        surface_stats.get("matches_won"),
                    )
                )  

        con.commit()
        print(f"[DB] Data inserted into CompetitorProfile table and its sub-tables successfully.")
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        
def get_competitor_full_data(name: str) -> dict:
    name = name.replace("-", ", ")  
    try:
        competitor_profile = cur.execute(f"SELECT * FROM CompetitorProfile WHERE name = ?", (name,)).fetchone()
        if competitor_profile:
            periods = cur.execute("SELECT * FROM Periods WHERE competitor_id = ?", (competitor_profile['id'],)).fetchall()
            
            surface_data = {}
            for period in periods:
                surface_data[period['id']] = cur.execute("SELECT * FROM Surfaces WHERE period_id = ?", (period['id'],)).fetchall()
        else:
            periods = []
            surface_data = {}
        return competitor_profile, periods, surface_data
            
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
    
"""
    ELO RATINGS CALCULATIONS
""" 

# OVERALL ELO RATING
def calc_overall_elo_for_all_competitors():
    try:
        print("[DB] Refreshing overall ratings...")
        ids = get_competitors_ids()
        for id in ids:
            elo = 0
            years = get_competitor_period_years(id)
            for year in years:
                elo += calc_overall_elo_for_year(id, year)
            elo = round(elo / (len(years)-1), 2)
            add_competitor_overall_elo(id, elo)
            print(f"[DB] Competitors left: {len(ids)-1-ids.index(id)}")
        print("[DB] Finished refreshing competitors overall ratings")
                
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
        
def add_competitor_overall_elo(id: str, elo: float):
    try:
        cur.execute("INSERT OR REPLACE INTO Ratings (competitor_id, rating) VALUES (?, ?)", (id, elo,))
        con.commit()
        print(f"[DB] Added new overall rating for {id}: {elo} points")
        
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
        
def calc_overall_elo_for_year(id: str, year: int) -> float:
    # ( (matches_won * (1 + (0.1 * competitions_won) ) ) / (matches_played / competitions_played) ) * 10
    try:
        elo = cur.execute("SELECT ((matches_won * (1 + 0.1 * competitions_won)) / (matches_played / competitions_played)) * 10 FROM Periods WHERE competitor_id = ? AND year = ?", (id, year,)).fetchone()
        elo = elo[0]
        return elo
    
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None

def get_competitor_period_years(id: str) -> list[str]:
    try:
        years = cur.execute("SELECT year FROM Periods WHERE competitor_id = ?", (id,)).fetchall()
        return [row['year'] for row in years]
    
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
