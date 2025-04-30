from bs4 import BeautifulSoup
import cloudscraper
import requests

scraper = cloudscraper.create_scraper()

url = 'https://tennisstats.com/h2h/carlos-alcaraz-vs-novak-djokovic-43040'
response = scraper.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
score = soup.find("p", class_="bold h2h-record-max-font")


print(score)
