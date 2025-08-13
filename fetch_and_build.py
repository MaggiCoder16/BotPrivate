import chess.pgn
from io import StringIO

INPUT_PGN = "fetched_games.pgn"
OUTPUT_PGN = "fetched_games.pgn"
BOT_NAMES = set([
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
])
MIN_RATING = 3050
MIN_MOVES = 10
DUPLICATE_PLY = 12
MAX_GAMES = 3000

def game_starting_moves(game, max_ply):
    board = game.board()
    moves = []
    for i, move in enumerate(game.mainline_moves()):
        if i >= max_ply:
            break
        moves.append(board.san(move))
        board.push(move)
    return " ".join(moves)

def is_bot_in_game(game):
    white = game.headers.get("White", "")
    black = game.headers.get("Black", "")
    return white in BOT_NAMES or black in BOT_NAMES

def rating_ok(game):
    white = game.headers.get("White", "")
    black = game.headers.get("Black", "")
    try:
        white_elo = int(game.headers.get("WhiteElo", "0"))
        black_elo = int(game.headers.get("BlackElo", "0"))
    except:
        return False
    if white in BOT_NAMES and white_elo < MIN_RATING:
        return False
    if black in BOT_NAMES and black_elo < MIN_RATING:
        return False
    return True

def game_too_short(game):
    move_count = game.end().ply() // 2
    return move_count < MIN_MOVES

def remove_comments_and_variations(game):
    exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
    return game.accept(exporter)

def main():
    cleaned_games = []
    seen_openings = set()
    with open(INPUT_PGN, encoding="utf-8") as f:
        while True:
            if len(cleaned_games) >= MAX_GAMES:
                break
            game = chess.pgn.read_game(f)
            if game is None:
                break
            if not is_bot_in_game(game):
                continue
            if not rating_ok(game):
                continue
            if game_too_short(game):
                continue
            opening_key = game_starting_moves(game, DUPLICATE_PLY)
            if opening_key in seen_openings:
                continue
            seen_openings.add(opening_key)
            pgn_text = remove_comments_and_variations(game)
            cleaned_games.append(pgn_text)

    with open(OUTPUT_PGN, "w", encoding="utf-8") as out:
        out.write("\n\n\n".join(cleaned_games))
    print(f"Cleaned PGN saved to {OUTPUT_PGN}, total games: {len(cleaned_games)}")

if __name__ == "__main__":
    main()
