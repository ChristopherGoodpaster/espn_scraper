import requests
import pandas as pd
import json
import time

# ✅ ESPN cookies (fresh and decoded)
COOKIES = {
    "SWID": "{55B78258-74C1-4D62-9AED-BBEEC28DE54A}",
    "espn_s2": "AEBsoQHA42+1szrmqFbOeeBjTyYLHYiE+Hcuvaog4xBgaqDYX7k4FI8dXUYpJ2CZZG3PlCHUNkin67EvfuoKiyCSlAVu9ypMLVeCB6cN6jMdiQmF7MphYzoe58Y5sq8wkn5iBPPhVDXWbXZtY80ie3KXKWGh1j2mHbqvHGlbaA7cgOsttCpj2GzQsdI7bWDasgwGJkgn/RwYvxDK+7L8yFa7RLgWcHe4gYVOWQ4yNDRGKARpFFWMHFV57agMYutP//LKKgEET7yL2sRLLnd5iXmi"
}

# ✅ Your ESPN league ID
LEAGUE_ID = '200045'

# Only testing 2022 to debug
START_YEAR = 2022
END_YEAR = 2022

# ESPN API views
COMMON_VIEWS = [
    "mMatchup",
    "mMatchupScore",
    "mRoster",
    "mSettings",
    "mTeam",
    "mPendingTransactions"
]

# File paths
SAVE_DIR = r"C:\Users\Chris\Desktop\project_espn\espn_scraper"
output_excel = rf"{SAVE_DIR}\espn_fantasy_history_2009_2022.xlsx"

# Fetch data from ESPN
def fetch_league_data(year, league_id, views, cookies):
    url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
    params = {"view": views}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, params=params, cookies=cookies, headers=headers, timeout=10)
        print(f"\n--- RAW RESPONSE for {year} ---")
        print(response.text[:500])
        print("--- END RESPONSE ---\n")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching data for {year}: {e}")
        return None

# Parse team-level summary
def parse_team_data(year, data):
    teams = []
    for team in data.get("teams", []):
        teams.append({
            "Year": year,
            "Team ID": team.get("id"),
            "Team Name": f"{team.get('location')} {team.get('nickname')}",
            "Wins": team.get("record", {}).get("overall", {}).get("wins"),
            "Losses": team.get("record", {}).get("overall", {}).get("losses"),
            "Points For": team.get("points", 0),
            "Points Against": team.get("pointsAgainst", 0)
        })
    return teams

# Write to Excel + JSON
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    for year in range(START_YEAR, END_YEAR + 1):
        print(f"📥 Fetching data for {year}...")
        data = fetch_league_data(year, LEAGUE_ID, COMMON_VIEWS, COOKIES)
        if data:
            # Save raw JSON
            json_path = rf"{SAVE_DIR}\espn_league_{LEAGUE_ID}_{year}.json"
            with open(json_path, "w") as jf:
                json.dump(data, jf, indent=2)
            print(f"🧾 Saved JSON: {json_path}")

            # Save to Excel
            parsed = parse_team_data(year, data)
            df = pd.DataFrame(parsed)
            df.to_excel(writer, sheet_name=str(year), index=False)
            print(f"📊 Added Excel sheet for {year}")

        time.sleep(1)

print(f"\n✅ All done! Excel saved to:\n{output_excel}")
