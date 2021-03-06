import csv
import bz2
import time
import urllib.request
import chess
import chess.pgn
import random

NUM_WINS = 50000

def generate_dataset():
    """
    Generates a csv file with result,white_elo,black_elo,board fields.

    result is an array [1, 0] for white wins and [0, 1] for black wins.

    board is an array of integers with the first 64 values being the board and the 5 values following being the turn to move and castling rights.
    """
    filelisturl = "https://database.lichess.org/standard/list.txt"
    filelist = []

    with urllib.request.urlopen(filelisturl) as fil:
        for line in fil:
            filelist.append(line.decode("utf-8").strip())

    random.shuffle(filelist)

    with open("test.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["result","white_elo","black_elo","board"])
        rows = []
        white_wins = 0
        black_wins = 0
    
        for gamefile in filelist:
            if white_wins >= NUM_WINS and black_wins >= NUM_WINS:
                break

            with bz2.open(urllib.request.urlopen(gamefile), "rt") as reader:
                chessgame = None
                while True:
                    if white_wins >= NUM_WINS and black_wins >= NUM_WINS:
                        break

                    try:
                        chessgame = chess.pgn.read_game(reader)
                    except EOFError:
                        break
                    if chessgame == None:
                        break

                    # Filtering data
                    if chessgame.headers['Result'] == '1-0' and white_wins >= NUM_WINS:
                        continue
                    if chessgame.headers['Result'] == '0-1' and black_wins >= NUM_WINS:
                        continue
                    if chessgame.headers['Result'] == '1/2-1/2':
                        continue
                    if not chessgame.headers['WhiteElo'].isnumeric() or not chessgame.headers['BlackElo'].isnumeric():
                        continue
                    if int(chessgame.headers['WhiteElo']) < 2000 or int(chessgame.headers['BlackElo']) < 2000:
                        continue
                    if '+' not in chessgame.headers['TimeControl']:
                        continue
                    if int(chessgame.headers['TimeControl'].split('+')[0]) < 1200:
                        continue

                    # Make sure the game lasts at least 10 moves
                    last_move = str(chessgame.end()).split('.')[0]
                    if not last_move.isnumeric():
                        continue
                    if int(last_move) < 10:
                        continue

                    last_move = int(last_move)

                    # Play moves past move 10
                    board = chessgame.board()
                    num_moves = random.randint(22, last_move * 2 + 2)
                    i = 0
                    for move in chessgame.mainline_moves():
                        board.push(move)
                        if i == num_moves:
                            break
                        i += 1
                    
                    # Convert board to our representation
                    board_position = fen_to_inputarray(board.fen())
                    result = [int(res) for res in chessgame.headers['Result'].split('-')]

                    if result[0] == 1 and white_wins < NUM_WINS:
                        rows.append([result, chessgame.headers['WhiteElo'], chessgame.headers['BlackElo'], board_position])
                        white_wins += 1
                    elif result[0] == 0 and black_wins < NUM_WINS:
                        rows.append([result, chessgame.headers['WhiteElo'], chessgame.headers['BlackElo'], board_position])
                        black_wins += 1
                        

                writer.writerows(rows)
                rows = []




def fen_to_inputarray(board_fen):
    """
    Takes a board FEN respresentation

    Converts it all to an array of length 64 + 5 for the board + turn and castling rights (in that order)
    """
    board_map = {
        'P': [1],
        'N': [2],
        'B': [3],
        'R': [4],
        'Q': [5],
        'K': [6],
        'p': [7],
        'n': [8],
        'b': [9],
        'r': [10],
        'q': [11],
        'k': [12],
        '1': [0 for _ in range(1)],
        '2': [0 for _ in range(2)],
        '3': [0 for _ in range(3)],
        '4': [0 for _ in range(4)],
        '5': [0 for _ in range(5)],
        '6': [0 for _ in range(6)],
        '7': [0 for _ in range(7)],
        '8': [0 for _ in range(8)],
    }

    board, castling_rights, turn = board_fen.split(' ')[0], board_fen.split(' ')[2], board_fen.split(' ')[1]
    board_repr = []
    board = board.replace('/','')
    for char in board:
        board_repr.extend(board_map[char])

    if turn == 'w':
        board_repr.append(1)
    else:
        board_repr.append(0)

    board_repr.extend([0,0,0,0])
    if 'K' in castling_rights:
        board_repr[-4] = 1
    if 'Q' in castling_rights:
        board_repr[-3] = 1
    if 'k' in castling_rights:
        board_repr[-2] = 1
    if 'q' in castling_rights:
        board_repr[-1] = 1


    return board_repr
                    
                    

if __name__ == "__main__":
    start_time = time.time() 
    # generate_dataset()
    fen_to_inputarray("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    print ("Done --- %s seconds ---" % (time.time() - start_time))