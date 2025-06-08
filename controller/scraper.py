from bs4 import BeautifulSoup
import cloudscraper
from itertools import permutations

scraper = cloudscraper.create_scraper()

def try_url(player1: str, player2: str):
    url = f"https://tennisstats.com/h2h/{player1}-vs-{player2}"
    print(url)
    
    try:
        response = scraper.get(url= url)
    except Exception as e:
        print(f"[API] An error occurred: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Scrap the H2H score
    score = soup.find("p", class_="bold h2h-record-max-font")
    if score is None:
        return (None, None)
    return score, soup

def check_name_length(name: list[str]):
    if len(name) != 2:
        perms = permutations(name)
        names = []
        for perm in perms:
            name = ''.join(p + '-' for p in perm)[:-1]
            names.append(name)
        return names
    return name[1] + '-' + name[0]

def check_permutations(player1, player2):
    if type(player1) != list:
        # Only player2 can be a list
        if type(player2) == list:
            for perm in player2:
                score, soup = try_url(player1, perm)
                if score is not None: return score, soup
                score, soup = try_url(perm, player1)
                if score is not None: return score, soup
            return score, soup
        # Both players are str
        score, soup = try_url(player1, player2)
        if score is not None: return score, soup
        score, soup = try_url(player2, player1)
        if score is not None: return score, soup
        return score, soup
    else:
        # Both players or only player1 can be a list
        if type(player2) == list:
            #Both players are a list
            for perm1 in player1:
                for perm2 in player2:
                    score, soup = try_url(perm1, perm2)
                    if score is not None: return score, soup
                    score, soup = try_url(perm2, perm1)
                    if score is not None: return score, soup
            return score, soup
        else:
            # Only player1 is a list
            for perm in player1:
                score, soup = try_url(player2, perm)
                if score is not None: return score, soup
                score, soup = try_url(perm, player2)
                if score is not None: return score, soup
            return score, soup


def get_H2H_stats(player1: str, player2: str) -> dict:
    player1_name = player1.lower().replace(", ", "-")
    player2_name = player2.lower().replace(", ", "-")
    
    player1 = player1.lower().replace(" ", "").split(",")
    player2 = player2.lower().replace(" ", "").split(",")


    player1 = check_name_length(player1)
    player2 = check_name_length(player2)
    
    score, soup = check_permutations(player1, player2)
    
    if score is None:
        print(f"[SCRAPER] No H2H score found for {player1_name} vs {player2_name}.")
        return None

    
    print(f"[SCRAPER] Scraping H2H stats")
    stats = {
        player1_name : {"H2H wins": None, "Form score": None, "Hardcourt wins": None, "Clay wins": None, "Grass wins": None},
        player2_name : {"H2H wins": None, "Form score": None, "Hardcourt wins": None, "Clay wins": None, "Grass wins": None}
    }
    
        
    score = score.get_text(strip=True).replace(" ","") 
    score = score.split("-")
    score = [int(s) for s in score]
    stats[player1_name]["H2H wins"] = score[0]
    stats[player2_name]["H2H wins"] = score[1]

    # Scrap players form score
    form_scores = soup.find_all("span", class_=["form-box", "fa-adjust-h2 big"])
    form_scores = [int(player_form.get_text(strip=True)) for player_form in form_scores]
    stats[player1_name]["Form score"] = form_scores[0]
    stats[player2_name]["Form score"] = form_scores[1]

    # Scrap the H2H score on various surfaces
    sufraces = soup.find("div", class_="main_feed h2h-stats")

    # Hard surface
    hard_div = sufraces.find("div", class_="main_feed_c hard-surfaces cf toggle-hidden")
    hard_div_wins = hard_div.select_one("div.data-table-row.row.cf")
    hard_div_wins = hard_div_wins.find_all("span")

    player1_hard_wins = hard_div_wins[2].get_text(strip=True)
    player2_hard_wins = hard_div_wins[4].get_text(strip=True)

    stats[player1_name]["Hardcourt wins"] = player1_hard_wins
    stats[player2_name]["Hardcourt wins"] = player2_hard_wins

    # Clay surface
    clay_div = sufraces.find("div", class_="main_feed_c clay-surfaces cf toggle-hidden")
    clay_div_wins = clay_div.select_one("div.data-table-row.row.cf")
    clay_div_wins = clay_div_wins.find_all("span")

    player1_clay_wins = clay_div_wins[2].get_text(strip=True)
    player2_clay_wins = clay_div_wins[4].get_text(strip=True)

    stats[player1_name]["Clay wins"] = player1_clay_wins
    stats[player2_name]["Clay wins"] = player2_clay_wins

    # Grass surface
    grass_div = sufraces.find("div", class_="main_feed_c grass-surfaces cf toggle-hidden")
    grass_div_wins = grass_div.select_one("div.data-table-row.row.cf")
    grass_div_wins = grass_div_wins.find_all("span")

    player1_grass_wins = grass_div_wins[2].get_text(strip=True)
    player2_grass_wins = grass_div_wins[4].get_text(strip=True)

    stats[player1_name]["Grass wins"] = player1_grass_wins
    stats[player2_name]["Grass wins"] = player2_grass_wins

    return stats