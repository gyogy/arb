import json
import os
import requests


API_KEY = os.getenv("ODDS_API_KEY")
SPORT = 'boxing_boxing'
REGIONS = 'eu'
MARKETS = 'h2h' 
ODDS_FORMAT = 'decimal'
DATE_FORMAT = 'iso'


odds_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
    params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    }
)

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    with open("data.json", "w") as f:
        json.dump(odds_json, f, indent=2)

    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
