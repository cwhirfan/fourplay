import socket
import threading

#Server setup
HOST = "Server IP Address"
PORT = 65432

#Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Bind the socket to the specified host and port
server.bind((HOST, PORT))
#Enable the server to accept connections (Max 2)
server.listen(2)

clients = []
symbols = ['R', 'Y']
turn = 0
board = [[' ' for _ in range(7)] for _ in range(6)]

def check_winner(board, symbol):
    # Check horizontal locations for win
    for c in range(4):
        for r in range(6):
            if board[r][c] == board[r][c + 1] == board[r][c + 2] == board[r][c + 3] == symbol:
                return True
    # Check vertical locations for win
    for c in range(7):
        for r in range(3):
            if board[r][c] == board[r + 1][c] == board[r + 2][c] == board[r + 3][c] == symbol:
                return True
    # Check positively sloped diagonals
    for c in range(4):
        for r in range(3):
            if board[r][c] == board[r + 1][c + 1] == board[r + 2][c + 2] == board[r + 3][c + 3] == symbol:
                return True
    # Check negatively sloped diagonals
    for c in range(4):
        for r in range(3, 6):
            if board[r][c] == board[r - 1][c + 1] == board[r - 2][c + 2] == board[r - 3][c + 3] == symbol:
                return True
    return False



def handle_client(conn, player):
    global turn
    conn.sendall(f'{symbols[player]}'.encode())
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            col = int(data)
            if turn != player:
                continue
            for row in range(5, -1, -1):
                if board[row][col] == ' ':
                    board[row][col] = symbols[player]
                    break
            if check_winner(board, symbols[player]):
                for client in clients:
                    client.sendall(f'WIN:{symbols[player]}'.encode())
                break
            turn = (turn + 1) % 2
            for client in clients:
                client.sendall(f'{symbols[player]}:{col}'.encode())
        except Exception as e:
            print(f"Error: {e}")
            clients.remove(conn)
            conn.close()
            break

#Indicates that server was started
def start_server():
    print ("Server start")

   

#Start the server
start_server()
