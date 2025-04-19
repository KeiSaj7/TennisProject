import sqlite3

con = sqlite3.connect('tennis.db')
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
        cur.row_factory = sqlite3.Row
        competitors_ids = cur.execute(f"SELECT id FROM {table}").fetchall()
        return [row["id"] for row in competitors_ids]
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return ["Error"]

def get_competitor_name_by_id(competitor_id: str) -> str:
    table="SeasonCompetitors"
    try:
        cur.row_factory = sqlite3.Row
        competitor_name: str = cur.execute(f"SELECT name FROM {table} WHERE id = ?", (competitor_id,)).fetchone()
        return competitor_name["name"] if competitor_name else None
    except sqlite3.Error as e:
        print(f"[DB] An error occurred: {e}")
        return None
    
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
