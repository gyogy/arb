import os
from typing import Any, Dict, List

import requests


def fetch_odds(sport: str, regions: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("ODDS_API_KEY")

    if not api_key:
        raise RuntimeError("API key not found in environment.")

    base_url = (
        "https://api.the-odds-api.com/v4/sports/{sport}/odds"
        "?api_key={api_key}"
        "&regions={regions}"
        "&markets={markets}"
        "&oddsFormat={odds_format}"
        "&dateFormat={date_format}"
    )
    url = base_url.format(
        sport=sport,
        api_key=api_key,
        regions=regions,
        markets="h2h",
        odds_format="decimal",
        date_format="iso",
    )

    response = requests.get(url)
    response.raise_for_status()

    print("Remaining requests:", response.headers.get("x-requests-remaining"))
    print("Used requests:", response.headers.get("x-requests-used"))

    return response.json()
