print("SCRAPER STARTING")

import pandas as pd
import requests
import time
from io import StringIO

STAT_CATEGORIES = {
    "assists": 480,
    "draw_controls": 262,
    "free_position": 1082,
    "shots_on_goal": 1162,
    "shots_per_game": 1160,
    "goals": 246,
    "caused_turnovers": 264
}

def scrape_stat(stat_id):

    base_url = f"https://www.ncaa.com/stats/lacrosse-women/d1/current/team/{stat_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    pages = []
    page = 1

    while True:

        url = base_url if page == 1 else f"{base_url}/p{page}"
        print("Scraping:", url)

        try:
            r = requests.get(url, headers=headers)

            tables = pd.read_html(StringIO(r.text))

            if len(tables) == 0:
                break

            df = tables[0]

            if df.empty:
                break

            pages.append(df)

            page += 1
            time.sleep(2)

        except ValueError:
            break

    return pd.concat(pages, ignore_index=True)


def build_dataset():

    master = None

    for stat, stat_id in STAT_CATEGORIES.items():

        df = scrape_stat(stat_id)

        df.columns = df.columns.str.lower().str.replace(" ", "_")

        stat_col = df.columns[-1]

        df = df[["team", stat_col]]
        df = df.rename(columns={stat_col: stat})

        if master is None:
            master = df
        else:
            master = master.merge(df, on="team")

    return master


def main():

    df = build_dataset()

    df.to_csv(
        "data/ncaa_womens_lacrosse_team_stats_2026.csv",
        index=False
    )

    print("Dataset updated successfully")


if __name__ == "__main__":
    main()