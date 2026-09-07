from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
import random
from unidecode import unidecode

load_dotenv()

app = Flask(__name__, template_folder="../templetes")

API_BASE_URL = "https://api.restcountries.com/countries/v5"
API_KEY = os.getenv("API_KEY")
COUNTRY_NAME = None
HINTS = []
SHOWN_HINTS = []

def api_request(query_params):
    url = f"{API_BASE_URL}?{query_params}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers, timeout=10)
    return response.json() 



@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/game")
def construct_game():

    global COUNTRY_NAME, HINTS
    COUNTRY_OBJ = random_country()
    COUNTRY_NAME = COUNTRY_OBJ['names']['common']

    neighbour_isos = COUNTRY_OBJ['borders']
    if neighbour_isos:
        example_neighbour_iso = random.choice(neighbour_isos)
        example_neighbour = api_request(
            f"codes.alpha_3={example_neighbour_iso}"
        )["data"]["objects"][0]["names"]["common"]
    else:
        example_neighbour = "No neighbouring countries"

    capital_list = []
    for capital in COUNTRY_OBJ['capitals']:
        capital_list.append(capital['name'])
    capitals_text = ", ".join(capital_list)

    languages_list = []
    for language in COUNTRY_OBJ['languages']:
        languages_list.append(language['name'])
    languages_text = ", ".join(languages_list)

    HINTS = [
        "Hint 1: The country is located in " + str(COUNTRY_OBJ['region']),
        "Hint 2: The country has a population of " + str(COUNTRY_OBJ['population']),
        "Hint 3: The country has a capital city called " + capitals_text,
        "Hint 4: The country has " + str(example_neighbour) + " as a neighbouring country",
        "Hint 5: The country has a land area of " + str(COUNTRY_OBJ['area']['kilometers']) + " square kilometers",
        "Hint 6: The country has the following languages spoken: " + languages_text
    ]

    SHOWN_HINTS.clear()
    SHOWN_HINTS.append(HINTS.pop(0))
    
    return render_template("game.html", guesses=0, hints=SHOWN_HINTS, country_name=COUNTRY_NAME)

@app.route("/guess", methods=["POST"])
def guess():

    guess = request.form.get("guess")
    guesses_count = int(request.form.get("guesses"))
    normalized_guess = unidecode(guess).lower()
    normalized_country_name = unidecode(COUNTRY_NAME).lower()

    if normalized_guess == normalized_country_name:
        return render_template("winner.html", country_name=COUNTRY_NAME)
    if not HINTS:
        return render_template("loser.html", country_name=COUNTRY_NAME)

    SHOWN_HINTS.append(HINTS.pop(0)) if HINTS else None
    return render_template("game.html", 
                               message="Incorrect guess. Try again.", 
                               guesses=guesses_count + 1,
                               hints=SHOWN_HINTS)

def random_country():

    number = random.randint(0, 248)
    json = api_request(f"limit=1&offset={number}")
    print(json)
    country = json['data']['objects'][0]
    return country
    

if __name__ == '__main__':
    app.run(debug=True)