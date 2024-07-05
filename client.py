import socket
import threading
import pygame
import sys

# Pygame setup
pygame.init()

WIDTH, HEIGHT = 700, 600
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fourplay")


font = pygame.font.SysFont("monospace", 50)


def draw_board(board):
    for c in range(7):
        for r in range(6):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    for c in range(7):
        for r in range(6):
            if board[r][c] == 'R':
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), HEIGHT - int((5-r) * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 'Y':
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), HEIGHT - int((5-r) * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

def display_message(message):
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
    label = font.render(message, True, WHITE)
    screen.blit(label, (40, 10))
    pygame.display.update()

# Client setup
HOST = '192.168.1.100'
PORT = 65432

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

board = [[' ' for _ in range(7)] for _ in range(6)]
my_turn = False
symbol = ''
winner = False
color=''


# This function is to receive messages from the server
def receive_messages():
    global my_turn, symbol, winner
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'R' or message == 'Y':
                symbol = message
                color = 'Red' if symbol == 'R' else 'Yellow'
                my_turn = (symbol == 'R')
                if my_turn:
                    display_message("It's your turn (" + color + ")")
                winner = True
                if message[4:] == symbol:
                    print("You win!")
                else:
                    print("You lose!")
                pygame.quit()
                sys.exit()
            if message == 'R' or message == 'Y':
                symbol = message
                if symbol == 'R':
                    my_turn = True
            else:
                player_symbol, col = message.split(':')
                col = int(col)
                for row in range(5, -1, -1):
                    if board[row][col] == ' ':
                        board[row][col] = player_symbol
                        break
                draw_board(board)
                if player_symbol != symbol:
                    my_turn = True
        except Exception as e:
            print(f"Error: {e}")
            client.close()
            break

def send_move(col):
    client.sendall(f'{col}'.encode())

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

draw_board(board)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            if symbol == 'R':
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if my_turn and not winner:
                posx = event.pos[0]
                col = int(posx // SQUARESIZE)
                send_move(col)
                my_turn = False
