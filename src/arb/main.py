from argparse import ArgumentParser
from dotenv import load_dotenv
from fetch import fetch_odds
from flatten import flatten


def main():
    load_dotenv(dotenv_path="/home/gyogy/cod/arb/.env")

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
    args = parser.parse_args()

    try:
        raw_data = fetch_odds(sport=args.sport, regions=args.regions)
    except Exception as e:
        print(f"Failed to fetch data:\n {e}")
        return

    if raw_data:
        events = []
        odds = []
        for d in raw_data:
            e, o = flatten(d)
            events.extend(e)
            odds.extend(o)


if __name__ == "__main__":
    main()

