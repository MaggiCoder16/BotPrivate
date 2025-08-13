import requests
import time
import chess.pgn
from io import StringIO

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

MAX_GAMES_TOTAL = 3000
MIN_RATING = 3050
OUTPUT_PGN = "fetched_games.pgn"

max_per_bot = MAX_GAMES_TOTAL // len(BOTS)

def fetch_games_for_bot(bot_name, max_games, min_rating):
    headers = {"Accept": "application/x-chess-pgn"}
    params = {"max": max_games * 3, "rated": "both", "perfType": "classical"}
    url = f"https://lichess.org/api/games/user/{bot_name}"
    try:
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
    except:
        return []

    pgn_text = response.text
    games = pgn_text.strip().split("\n\n\n")
    filtered_games = []
    for game_str in games:
        if len(filtered_games) >= max_games:
            break
        game_io = StringIO(game_str)
        try:
            game = chess.pgn.read_game(game_io)
        except:
            continue
        white_elo = game.headers.get("WhiteElo")
        black_elo = game.headers.get("BlackElo")
        if white_elo is None or black_elo is None:
            continue
        try:
            white_elo = int(white_elo)
            black_elo = int(black_elo)
        except:
            continue
        if game.headers.get("White") == bot_name and white_elo < min_rating:
            continue
        if game.headers.get("Black") == bot_name and black_elo < min_rating:
            continue
        filtered_games.append(game_str.strip())
    return filtered_games

def main():
    all_games = []
    for bot in BOTS:
        bot_games = fetch_games_for_bot(bot, max_per_bot, MIN_RATING)
        all_games.extend(bot_games)
        time.sleep(1)
        if len(all_games) >= MAX_GAMES_TOTAL:
            break
    with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
        f.write("\n\n\n".join(all_games[:MAX_GAMES_TOTAL]))

if __name__ == "__main__":
    main()
