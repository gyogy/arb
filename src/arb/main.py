import os
from argparse import ArgumentParser
from dotenv import load_dotenv
from .fetch import fetch_odds
from .flatten import flatten
from .db import OddsDatabase


def main():
    load_dotenv(dotenv_path="/home/gyogy/cod/arb/.env", override=True)

    parser = ArgumentParser(description="Fetch odds data and load to db.")
    parser.add_argument(
        '--sport', 
        default='boxing_boxing', 
        help='Check out https://the-odds-api.com/liveapi/guides/v4/ for avaliable sport keys.'
    )
    parser.add_argument(
        '--regions',
        default='eu',
        help='Check out https://the-odds-api.com/liveapi/guides/v4/ for avaliable region keys.'
    )
    parser.add_argument(
        '--db-path',
        default=os.getenv("ODDS_DB_PATH"),
        help='SQLite path (or :memory:) for storing odds. Defaults to odds.db in repo root.',
    )
    args = parser.parse_args()

    try:
        raw_data = fetch_odds(sport=args.sport, regions=args.regions)
    except Exception as e:
        print(f"Failed to fetch data:\n {e}")
        return

    if not raw_data:
        print("No data returned from API.")
        return

    ingested_events = 0
    ingested_odds = 0

    with OddsDatabase(db_path=args.db_path) as database:
        for d in raw_data:
            events, odds = flatten(d)
            if not events:
                continue

            for event in events:
                database.save_event(event)
                ingested_events += 1

            for odd in odds:
                if odd.market_type != "h2h":
                    continue
                database.save_odds(odd)
                ingested_odds += 1

        database.commit()

    print(f"Stored { ingested_events } events and { ingested_odds } odds rows.")


if __name__ == "__main__":
    main()
