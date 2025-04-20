from flask import Flask, render_template, request, redirect
from database.manage import get_all_competitors_names, get_competitor_full_data

app = Flask(__name__)

@app.route('/')
async def home():
    return render_template('index.html')  

@app.route('/search')
async def search():
    query = request.args.get("player", "").lower()
    search_matches = [c for c in COMPETITORS if query in c.lower()]
    return render_template('suggestions.html', matches = search_matches)

@app.route('/player/<name>')
async def player(name):
    player, periods, surface_data = get_competitor_full_data(name)
    #return redirect(f"https://tennisstats.com/players/{name}")
    return render_template('player.html', player=player, periods=periods, surface_data=surface_data, name=name)

def start_app():
    global COMPETITORS
    COMPETITORS = get_all_competitors_names()
    app.run(debug=True)
    