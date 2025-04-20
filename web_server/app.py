from flask import Flask, render_template, request, redirect
from database.manage import get_all_competitors_names, get_competitor_full_data
from scraper import get_H2H_stats

app = Flask(__name__)

@app.route('/')
async def home():
    return render_template('index.html', active_tab="search")  

@app.route('/search')
async def search():
    query = request.args.get("player", "").lower()
    search_matches = [c for c in COMPETITORS if query in c.lower()]
    return render_template('suggestions.html', matches = search_matches)

@app.route('/player/<name>')
async def player(name: str):
    player, periods, surface_data = get_competitor_full_data(name)
    #return redirect(f"https://tennisstats.com/players/{name}")
    return render_template('player.html', player=player, periods=periods, surface_data=surface_data, name=name)

@app.route('/h2h')
def h2h():
    return render_template('h2h.html', active_tab ="h2h")

@app.route('/h2h/<player1>/<player2>')
def h2h_compare(player1: str, player2: str ):
    h2h_stats = get_H2H_stats(player1.replace('-', ", "), player2.replace('-', ", "))
    if h2h_stats is None:
        return render_template(
            'h2h_comparison.html',
            player1=player1.replace('-', ' '),
            player2=player2.replace('-', ' '),
            error="No H2H score found for these players."
        )
    
    names = list(h2h_stats.keys())
    return render_template('h2h_comparison.html', player1=player1.replace('-', ' '), player2=player2.replace('-', ' '), stats1 = h2h_stats[names[0]] , stats2 = h2h_stats[names[1]])

def start_app():
    global COMPETITORS
    COMPETITORS = get_all_competitors_names()
    app.run(debug=True)
    