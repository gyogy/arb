from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Event:
    id: str
    sport: str
    commence_time: str
    home: str
    away: str


@dataclass
class Odds:
    event_id: str
    book: str
    market_type: str
    last_update: str
    home_odds: Optional[float]
    away_odds: Optional[float]
    draw_odds: Optional[float]


def flatten(d: Dict[str, Any]) -> Tuple[List[Event], List[Odds]]:
    odds = []
    event = Event(
        id=d["id"],
        sport=d["sport_key"],
        commence_time=d["commence_time"],
        home=d["home_team"],
        away=d["away_team"],
    )

    if not d.get("bookmakers"):
        return [], []

    for b in d["bookmakers"]:
        bk = b["key"]
        lupd = b["last_update"]

        for m in b["markets"]:
            mtype = m["key"]
            hodds = None
            aodds = None
            dodds = None

            for o in m["outcomes"]:
                if o["name"] == event.home:
                    hodds = o["price"]
                if o["name"] == event.away:
                    aodds = o["price"]
                if o["name"] == "Draw":
                    dodds = o["price"]

            odd = Odds(
                event_id=d["id"],
                book=bk,
                market_type=mtype,
                last_update=lupd,
                home_odds=hodds,
                away_odds=aodds,
                draw_odds=dodds,
            )

            odds.append(odd)

    for o in odds:
        print(o)

    return [event], odds
