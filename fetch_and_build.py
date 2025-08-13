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
MIN_MOVES = 10
DUPLICATE_PLY = 12
OUTPUT_PGN = "fetched_games.pgn"
max_per_bot = MAX_GAMES_TOTAL // len(BOTS)

def game_starting_moves(game, max_ply):
    board = game.board()
    moves = []
    for i, move in enumerate(game.mainline_moves()):
        if i >= max_ply:
            break
        moves.append(board.san(move))
        board.push(move)
    return " ".join(moves)

def rating_ok(game, bot_name):
    try:
        white_elo = int(game.headers.get("WhiteElo", "0"))
        black_elo = int(game.headers.get("BlackElo", "0"))
    except:
        return False
    if game.headers.get("White") == bot_name and white_elo < MIN_RATING:
        return False
    if game.headers.get("Black") == bot_name and black_elo < MIN_RATING:
        return False
    return True

def game_too_short(game):
    move_count = game.end().ply() // 2
    return move_count < MIN_MOVES

def remove_comments_and_variations(game):
    exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
    return game.accept(exporter)

def fetch_and_filter_games(bot_name, max_games, seen_openings):
    headers = {"Accept": "application/x-chess-pgn", "User-Agent": "Mozilla/5.0"}
    params = {"max": max_games * 4, "rated": "both", "perfType": "classical"}
    url = f"https://lichess.org/api/games/user/{bot_name}"
    try:
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch for {bot_name}: {e}")
        return []

    pgn_text = response.text.strip()
    raw_games = pgn_text.split("\n\n\n")
    filtered_games = []

    for game_str in raw_games:
        if len(filtered_games) >= max_games:
            break
        game_io = StringIO(game_str)
        try:
            game = chess.pgn.read_game(game_io)
        except:
            continue
        if game is None:
            continue
        if not rating_ok(game, bot_name):
            continue
        if game_too_short(game):
            continue
        opening_key = game_starting_moves(game, DUPLICATE_PLY)
        if opening_key in seen_openings:
            continue
        seen_openings.add(opening_key)
        pgn_clean = remove_comments_and_variations(game)
        filtered_games.append(pgn_clean)
    print(f"{bot_name}: fetched {len(raw_games)} games, kept {len(filtered_games)} after filtering")
    return filtered_games

def main():
    all_games = []
    seen_openings = set()
    for bot in BOTS:
        bot_games = fetch_and_filter_games(bot, max_per_bot, seen_openings)
        all_games.extend(bot_games)
        print(f"Total games collected so far: {len(all_games)}")
        time.sleep(1)
        if len(all_games) >= MAX_GAMES_TOTAL:
            break

    all_games = all_games[:MAX_GAMES_TOTAL]
    with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
        f.write("\n\n\n".join(all_games))
    print(f"Finished. Total games saved to {len(all_games)} in {OUTPUT_PGN}")

if __name__ == "__main__":
    main()
