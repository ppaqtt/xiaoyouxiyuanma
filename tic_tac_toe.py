def print_board(board):
    for row in board:
        print(" | ".join(row))
        print("-" * 9)

def check_winner(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False

def is_board_full(board):
    return all(cell != " " for row in board for cell in row)

def tic_tac_toe():
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"
    
    print("欢迎来到井字棋游戏！")
    print_board(board)
    
    while True:
        try:
            row = int(input(f"玩家 {current_player}，请输入行号 (1-3): ")) - 1
            col = int(input(f"玩家 {current_player}，请输入列号 (1-3): ")) - 1
            
            if 0 <= row < 3 and 0 <= col < 3:
                if board[row][col] == " ":
                    board[row][col] = current_player
                    print_board(board)
                    
                    if check_winner(board, current_player):
                        print(f"恭喜玩家 {current_player} 获胜！")
                        break
                    elif is_board_full(board):
                        print("平局！")
                        break
                    
                    current_player = "O" if current_player == "X" else "X"
                else:
                    print("这个位置已经被占用了！")
            else:
                print("请输入有效的行号和列号 (1-3)！")
        except ValueError:
            print("请输入有效的数字！")

if __name__ == "__main__":
    tic_tac_toe()