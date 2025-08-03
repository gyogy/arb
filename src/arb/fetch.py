import os
import requests
from typing import Any, Dict, List


def fetch_odds(sport: str, regions: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("ODDS_API_KEY")

    if not api_key:
        raise RuntimeError("API key not found in environment.")

    response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{sport}/odds',
        params={
            'api_key': api_key,
            'regions': regions,
            'markets': 'h2h',
            'oddsFormat': 'decimal',
            'dateFormat': 'iso',
        }
    )
    response.raise_for_status()

    print('Remaining requests:', response.headers.get('x-requests-remaining'))
    print('Used requests:', response.headers.get('x-requests-used'))

    return response.json()

