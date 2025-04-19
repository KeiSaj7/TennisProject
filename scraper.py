import requests
from bs4 import BeautifulSoup

def try_url(player1: str, player2: str):
    url = f"https://tennisstats.com/h2h/{player1}-vs-{player2}"
    
    try:
        response = requests.get(url= url)
    except requests.exceptions.RequestException as e:
        print(f"[API] An error occurred: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Scrap the H2H score
    score = soup.find("p", class_="bold h2h-record-max-font")
    if score is None:
        return (None, None)
    return score, soup

def get_H2H_stats(player1: str, player2: str) -> dict:
    player1 = player1.lower().replace(" ", "").split(",")
    player2 = player2.lower().replace(" ", "").split(",")
    player1 = player1[1] + '-' + player1[0]
    player2 = player2[1] + '-' + player2[0]
    stats = {
        player1 : {"H2H wins": None, "Form score": None, "Hardcourt wins": None, "Clay wins": None, "Grass wins": None},
        player2 : {"H2H wins": None, "Form score": None, "Hardcourt wins": None, "Clay wins": None, "Grass wins": None}
    }
    
    score, soup = try_url(player1, player2) 
    if score is None:
        score, soup = try_url(player2, player1)
        if score is None:
            print(f"[SCRAPER] No H2H score found for {player1} vs {player2}.")
            return None
        
    score = score.get_text(strip=True).replace(" ","") 
    score = score.split("-")
    score = [int(s) for s in score]
    stats[player1]["H2H wins"] = score[0]
    stats[player2]["H2H wins"] = score[1]

    # Scrap players form score
    form_scores = soup.find_all("span", class_=["form-box", "fa-adjust-h2 big"])
    form_scores = [int(player_form.get_text(strip=True)) for player_form in form_scores]
    stats[player1]["Form score"] = form_scores[0]
    stats[player2]["Form score"] = form_scores[1]

    # Scrap the H2H score on various surfaces
    sufraces = soup.find("div", class_="main_feed h2h-stats")

    # Hard surface
    hard_div = sufraces.find("div", class_="main_feed_c hard-surfaces cf toggle-hidden")
    hard_div_wins = hard_div.select_one("div.data-table-row.row.cf")
    hard_div_wins = hard_div_wins.find_all("span")

    player1_hard_wins = hard_div_wins[2].get_text(strip=True)
    player2_hard_wins = hard_div_wins[4].get_text(strip=True)

    stats[player1]["Hardcourt wins"] = player1_hard_wins
    stats[player2]["Hardcourt wins"] = player2_hard_wins

    # Clay surface
    clay_div = sufraces.find("div", class_="main_feed_c clay-surfaces cf toggle-hidden")
    clay_div_wins = clay_div.select_one("div.data-table-row.row.cf")
    clay_div_wins = clay_div_wins.find_all("span")

    player1_clay_wins = clay_div_wins[2].get_text(strip=True)
    player2_clay_wins = clay_div_wins[4].get_text(strip=True)

    stats[player1]["Clay wins"] = player1_clay_wins
    stats[player2]["Clay wins"] = player2_clay_wins

    # Grass surface
    grass_div = sufraces.find("div", class_="main_feed_c grass-surfaces cf toggle-hidden")
    grass_div_wins = grass_div.select_one("div.data-table-row.row.cf")
    grass_div_wins = grass_div_wins.find_all("span")

    player1_grass_wins = grass_div_wins[2].get_text(strip=True)
    player2_grass_wins = grass_div_wins[4].get_text(strip=True)

    stats[player1]["Grass wins"] = player1_grass_wins
    stats[player2]["Grass wins"] = player2_grass_wins

    return stats