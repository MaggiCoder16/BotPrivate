import requests
import time

BOTS = [
    "NimsiluBot",
    "MaggiChess16",
    "NNUE_Drift",
    "Endogenetic-Bot",
    "Exogenetic-Bot",
    "InvinxibleFlxsh",
    "NecroMindX",
    "Classic_BOT-v2",
    "BOT_Stockfish13",
    "IndianGuyPlayz",
    "Sooraj_Kumar_P_S"
]

OUTPUT_PGN = "filtered_standard_bots_2200plus.pgn"

def fetch_full_games(bot):
    url = f"https://lichess.org/api/games/user/{bot}"
    headers = {
        "Accept": "application/x-chess-pgn"
    }
    
    all_pgn = ""
    until = None

    while True:
        params = {
            "max": 3000,
            "variant": "standard",
            "perfType": "standard",
            "rated": "true",
            "analysed": "false",
            "opening": "false",
            "clocks": "false",
            "evals": "false"
        }
        if until:
            params["until"] = until

        print(f"Fetching games for {bot} (until={until})...")
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"  Failed for {bot} - {response.status_code}")
            break

        text = response.text.strip()
        print(f"  Fetched {len(text)} characters for {bot}")

        if not text:
            break

        all_pgn += "\n\n\n" + text if all_pgn else text

        next_until = response.headers.get("X-Next-Until")
        if not next_until or next_until == until:
            break
        until = next_until

        time.sleep(2)  

    return all_pgn

def filter_games(pgn_data):
    games = pgn_data.strip().split("\n\n\n")
    valid_games = []

    for game in games:
        lines = game.split("\n")
        tags = {line.split(" ")[0][1:]: line for line in lines if line.startswith("[")}
        
        variant_tag = tags.get("Variant", "")
        if variant_tag and variant_tag.lower() != "standard":
            continue
        
        w_rating_line = tags.get("WhiteElo", "")
        b_rating_line = tags.get("BlackElo", "")
        w_prov = "WhiteRatingDiff" not in tags
        b_prov = "BlackRatingDiff" not in tags

        def extract_rating(line):
            try:
                return int(line.split('"')[1])
            except:
                return 0

        wr = extract_rating(w_rating_line)
        br = extract_rating(b_rating_line)

        if (w_prov or wr >= 3050) and (b_prov or br >= 3050):
            valid_games.append(game.strip())

    return valid_games

def main():
    all_games = []
    for bot in BOTS:
        pgn_data = fetch_full_games(bot)
        time.sleep(2)
        filtered = filter_games(pgn_data)
        print(f"  → {len(filtered)} valid games for {bot}")
        all_games.extend(filtered)

    print(f"\nTotal games collected: {len(all_games)}")
    with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
        f.write("\n\n\n".join(all_games))
    print(f"PGN saved to {OUTPUT_PGN}")

if __name__ == "__main__":
    main()
