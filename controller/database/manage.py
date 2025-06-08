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
    
def get_competitor_id_by_name(name: str) -> str:
    table="SeasonCompetitors"
    try:
        name_parts = name.split(sep=' ')
        competitor_id: str = cur.execute(f"SELECT id FROM {table} WHERE name LIKE ?", (f"%{name_parts[0]}%{name_parts[1]}%",)).fetchone()
        return competitor_id["id"] if competitor_id else None
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
table_id = 0

def add_competitor_profile(data: dict) -> None:
    try:
        global table_id
        competitor = data.get("competitor", {})
        info = data.get("info", {})
        rankings = data.get("competitor_rankings", [{}])
        
        for rank in rankings:
            if rank.get("type") == "singles" and rank.get("race_ranking") == False:
                competitor_rank = rank.get("rank")
                competitor_points = rank.get("points")
                break
            competitor_rank, competitor_points = None, None

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
                competitor_rank,
                competitor_points
            )
        )

        for period in data.get("periods", []):
            period_stats = period.get("statistics", {})
            cur.execute(
                """INSERT OR REPLACE INTO Periods 
                VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                (
                    table_id,
                    competitor.get("id"),
                    period.get("year"),
                    period_stats.get("competitions_played"),
                    period_stats.get("competitions_won"),
                    period_stats.get("matches_played"),
                    period_stats.get("matches_won"),
                )
            )

            for surface in period.get("surfaces", []):
                surface_stats = surface.get("statistics", {})
                cur.execute(
                    """INSERT OR REPLACE INTO Surfaces 
                    VALUES (?, ?, ?, ?, ?, ?)""", 
                    (
                        table_id,
                        surface.get("type"),
                        surface_stats.get("competitions_played"),
                        surface_stats.get("competitions_won"),
                        surface_stats.get("matches_played"),
                        surface_stats.get("matches_won"),
                    )
                )
            table_id +=1

        con.commit()
        print(f"[DB] Data inserted into CompetitorProfile table and its sub-tables successfully.")
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        
def get_competitor_full_data(name: str) -> dict:
    name = name.replace("-", " ")
    parts = name.split(" ")
    part1, part2 = parts[0], parts[1]
    try:
        competitor_profile = cur.execute(f"SELECT * FROM CompetitorProfile WHERE name LIKE ?", (f"%{parts[0]}%{parts[1]}%",)).fetchone()
        if competitor_profile:
            periods = cur.execute("SELECT * FROM Periods WHERE competitor_id = ? ORDER BY year DESC", (competitor_profile['id'],)).fetchall()
            
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

def get_competitor_rank(id: str):
    try:
        rank = cur.execute("SELECT rank FROM CompetitorProfile WHERE id = ?", (id,)).fetchone()
        return rank["rank"]
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None

def get_competitor_points(id: str):
    try:
        rank = cur.execute("SELECT points FROM CompetitorProfile WHERE id = ?", (id,)).fetchone()
        return rank["points"] if rank else 0
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
"""
    ELO RATINGS CALCULATIONS
""" 

# OVERALL ELO RATING
def calc_every_rating_for_all_competitors():
    try:
        print("[DB] Refreshing overall ratings...")
        ids = get_competitors_ids()
        for id in ids:
            overall_elo = 0
            years = get_competitor_period_years(id)
            points = get_competitor_points(id)
            if not points: points = 0
            surfaces = calc_surfaces_elo_for_given_years(id, years)
            for surface in surfaces:
                surfaces[surface] = round(surfaces[surface] + (points/1000), 2)
            for year in years:
                overall_elo += calc_overall_elo_for_year(id, year)
            overall_elo = round(overall_elo / (len(years)-1), 2)
            overall_elo = round(overall_elo + (points/1000), 2)
            add_competitor_overall_elo(id, overall_elo)
            add_competitor_surfaces_elo(id, surfaces)
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
        
def add_competitor_surfaces_elo(id: str, surfaces: dict):
    try:
        for surface in surfaces:
            cur.execute(f"UPDATE Ratings SET {surface} = ? WHERE competitor_id = ?", (surfaces[surface], id, ))
        con.commit()
        print(f"[DB] Added new surfaces rating for {id}")
        
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None  
        
def calc_overall_elo_for_year(id: str, year: int) -> float:
    try:
        elo = cur.execute(f"SELECT (matches_won * 1.0 / matches_played) + (competitions_won * 1.0 / competitions_played) FROM Periods WHERE competitor_id = ? AND year = ?", (id, year,)).fetchone()
        elo = elo[0]
        if elo is None:
            return 0
        return elo
    
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
    
def calc_surfaces_elo_for_given_years(id: str, years: list[str]) -> dict:
    try:
        periods = get_periods_based_on_years(id, years)
        surfaces = {"red_clay": 0, "hardcourt_outdoor": 0, "grass": 0}
        for period in periods:
            for surface in surfaces:
                elo = cur.execute("SELECT (matches_won * 1.0 / matches_played) + (competitions_won * 1.0 / competitions_played) FROM Surfaces WHERE period_id = ? AND type = ?", (period, surface)).fetchone()
                if elo: 
                    surfaces[surface] += round(elo[0], 2)
                    continue
                surfaces[surface] += round((surfaces[surface]/2), 2)
        return surfaces
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None 

def get_periods_based_on_years(id:str, years: list[str]) -> list[int]:
    try:
        periods = []
        for year in years:
            period = cur.execute("SELECT id FROM Periods WHERE competitor_id = ? AND year = ?", (id, year)).fetchone()
            periods.append(period["id"])
        return periods
        
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None


def get_competitor_period_years(id: str) -> list[str]:
    try:
        years = cur.execute("SELECT year FROM Periods WHERE competitor_id = ?", (id,)).fetchall()
        return [row['year'] for row in years][0:2]
    
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None

"""
    H2H DATA
"""

def get_h2h_data(player1, player2):
    player1 = get_competitor_id_by_name(player1)
    player2 = get_competitor_id_by_name(player2)
    ratings = get_h2h_ratings(player1, player2)
    winrates = get_h2h_winrates(player1, player2)
    winrates[player1].update({'ratings' : ratings[player1]})
    winrates[player2].update({'ratings' : ratings[player2]})
    return winrates

def get_h2h_ratings(player1, player2):
    try:
        ratings = cur.execute("SELECT * FROM Ratings WHERE competitor_id IN (?, ?)", (player1, player2,)).fetchall()
        print(ratings)
        ratings = {list(ratings[0])[0] : list(ratings[0])[1:], list(ratings[1])[0] : list(ratings[1])[1:]}
        return ratings
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
    
def get_h2h_winrates(player1, player2):
    try:
        winrates = cur.execute("SELECT competitor_id, ((matches_won * 1.0 )/matches_played), year, id FROM Periods WHERE competitor_id IN (?, ?) AND year IN (2024, 2025)", (player1, player2)).fetchall()
        h2h_winrates = {player1: {}, player2: {}}
        for r in winrates:
            h2h_winrates[r[0]][r[2]] = {'overall' : round(r[1], 2)}
            surfaces = cur.execute("SELECT type, (matches_won * 1.0/matches_played) FROM Surfaces WHERE period_id = ? AND type != 'unknown'", (r[3],)).fetchall()
            for s in surfaces:
                h2h_winrates[r[0]][r[2]].update({s[0] : round(s[1], 2)})
        return h2h_winrates
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None