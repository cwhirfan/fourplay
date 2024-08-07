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
WHITE = (255, 255, 255)

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
HOST = 'SERVER IP ADDRESS'
PORT = 65432

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
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
            # Receive messages from the server
            message = client.recv(1024).decode()

              # To assign the player's symbol and color based on the received message just now
            if message == 'R' or message == 'Y':
                symbol = message
                color = 'Red' if symbol == 'R' else 'Yellow'
                my_turn = (symbol == 'R')

                  # This to show a message indicating whose turn it is
                if my_turn:
                    display_message("It's your turn (" + color + ")")
                else:
                    display_message("Waiting for opponent's turn")
            else:

                 # This will check if the message indicates a win
                if message.startswith('WIN:'):
                    player_symbol, col = message[4:].split(':')
                    col = int(col)
                    for row in range(5, -1, -1):
                        if board[row][col] == ' ':
                            board[row][col] = player_symbol
                            break
                    winner = True

                    # Display a win or lose message
                    if player_symbol == symbol:
                        display_message("You win!")
                    else:
                        display_message("You lose!")
                    pygame.quit()
                    sys.exit()

                # Update the board with the opponent move
                player_symbol, col = message.split(':')
                col = int(col)
                for row in range(5, -1, -1):
                    if board[row][col] == ' ':
                        board[row][col] = player_symbol
                        break
                draw_board(board)

                  # If it's the opponent's move, this will set my_turn to True
                if player_symbol != symbol:
                    my_turn = True
                    display_message("It's your turn (" + color + ")")
                else:
                    display_message("Waiting for opponent's turn")
        except Exception as e:
            print(f"Error: {e}")
            client.close()
            break


def send_move(col):
    #This is for sending move to server
    client.sendall(f'{col}'.encode())


#This is to create new thread, to receive the messages from the server, (parallel processing with threading)
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

draw_board(board)

# Game loop
while True:
    for event in pygame.event.get():
        #Handle the quit event to close the game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # This is for to handle mouse movement to draw the player's piece above the board    
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            if symbol == 'R':
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

        # Handle mouse click event to make a move
        if event.type == pygame.MOUSEBUTTONDOWN:
            if my_turn and not winner:
                posx = event.pos[0] # Get the x-coordinate of the mouse click position
                col = int(posx // SQUARESIZE) # Determine the column based on the x-coordinate from the mouse position before
                send_move(col) # Send the move to the server
                my_turn = False  # Set my_turn to False after making a move
