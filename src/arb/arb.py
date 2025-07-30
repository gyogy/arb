import copy
from typing import Any, Dict

def leave_best(odds: list[tuple[str, float]]) -> tuple[float, list]:
    
    if odds:
        best = max(odds, key=lambda x: x[1])[1]
        books = [x[0] for x in odds if x[1] == best]
    
        return (best, books)
    else:
        return (1, [])


def find_arb_in(bout: Dict, include_draws: bool = False) -> Dict:
    d = copy.deepcopy(bout)

    for k, v in d.items():
        if isinstance(v, str):
            continue
        d[k] = leave_best(v)

    inverse_sum = 1 / d["home"][0] + 1 / d["away"][0]
    if include_draws:
        inverse_sum += 1 / d["draw"][0]

    bout["arb"] = (1 - inverse_sum) > 0
    if bout["arb"]:
        bout["arb_size"] = f"{(1 - inverse_sum) * 100:.1f}%"
        bout["home_stake"] = f'{((1 / d["home"][0]) / inverse_sum) * 100:.2f}%'
        bout["away_stake"] = f'{((1 / d["away"][0]) / inverse_sum) * 100:.2f}%'
        bout["bet_home_at"] = d["home"]
        bout["bet_away_at"] = d["away"]

    return bout


def extract_odds_from(d: Dict[str, Any]) -> Dict[str, Any]:
    odds = {
        "id": f'{d["home_team"]} vs {d["away_team"]}',
        "home": [],
        "away": [],
        "draw": []
    }

    if d["bookmakers"] == []:
        return odds

    for b in d["bookmakers"]:
        book = b["key"]

        for m in b["markets"]:

            if m["key"] == "h2h_lay":
                continue

            for o in m["outcomes"]:
                side = o["name"]

                if side == d["home_team"]:
                    key = "home"
                elif side == d["away_team"]:
                    key = "away"
                else:
                    key = "draw"
                    
                odds[key].append((book, o["price"]))

    return odds


if __name__ == "__main__":
    import json

    with open("data.json", "r") as f:
        data = json.load(f)

    for d in data:
        test = extract_odds_from(d)
        test = find_arb_in(test)
        if test["arb"]:
            print(test["id"])
            print(test["arb_size"])
            print(test["home_stake"])
            print(test["away_stake"])
            print(test["bet_home_at"])
            print(test["bet_away_at"])
            print()

