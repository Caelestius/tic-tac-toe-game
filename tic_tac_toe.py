import tkinter as tk
from tkinter import ttk  # For creating tabs
import pygame
import sys
import os
import random
import json

# Initialize pygame for music control
pygame.mixer.init()

# Global variables
board = [" " for _ in range(9)]
current_player = "X"
player_name = ""
music_on = True
game_over = False
ai_difficulty = "Easy"
game_mode = "Best of 5"  # Default game mode
player_score = 0
ai_score = 0  # Initialize ai_score here globally
rounds_played = 0
max_rounds = None

# Set the AI difficulty level
def set_difficulty(level):
    global ai_difficulty
    ai_difficulty = level
    print(f"Difficulty set to: {ai_difficulty}")

# High score file path
high_score_file = "high_scores.json"

# Tkinter root window
root = tk.Tk()
root.title("Tic-Tac-Toe - Made by Fulmen Factor")
root.geometry("800x800")

# Ensure high score file exists and is formatted correctly
def ensure_high_score_file():
    if not os.path.exists(high_score_file):
        with open(high_score_file, 'w') as file:
            json.dump({"Best of 5": [], "Best of 10": [], "Best of 20": []}, file)

# Load high scores
def load_high_scores():
    ensure_high_score_file()
    try:
        with open(high_score_file, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"Best of 5": [], "Best of 10": [], "Best of 20": []}

# Save high score based on game mode and difficulty
def save_high_score(name, score, difficulty):
    print(f"Saving high score: {name}, {score}, Difficulty: {difficulty}")  # Debugging print
    scores = load_high_scores()

    # Ensure the current game mode exists in the scores dictionary
    if game_mode not in scores:
        scores[game_mode] = []

    # Add player's score with difficulty
    scores[game_mode].append({"name": name, "score": score, "difficulty": difficulty})

    # Sort the scores in descending order by score
    scores[game_mode] = sorted(scores[game_mode], key=lambda x: x['score'], reverse=True)

    # Write updated scores to file
    try:
        with open(high_score_file, 'w') as file:
            json.dump(scores, file)
    except IOError as e:
        print(f"Error saving high scores: {e}")

# Helper function to get the correct path for bundled files
def resource_path(relative_path):
    """ Get the absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Start music with corrected path
def start_music():
    music_file = resource_path("background_music.mp3")  # Adjust to correct path
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)

# Toggle music
def toggle_music():
    global music_on
    if music_on:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    music_on = not music_on

# Show high scores in a separate window with tabs
def show_high_scores():
    scores_window = tk.Toplevel(root)
    scores_window.title("High Scores")
    scores_window.geometry("500x600")

    scores = load_high_scores()

    notebook = ttk.Notebook(scores_window)
    notebook.pack(expand=True, fill='both')

    for mode in ["Best of 5", "Best of 10", "Best of 20"]:
        frame = tk.Frame(notebook)
        notebook.add(frame, text=mode)

        if mode in scores and scores[mode]:
            score_text = "\n".join([f"{entry['name']}: {entry['score']} (Difficulty: {entry['difficulty']})" for entry in scores[mode]])
        else:
            score_text = "No scores yet."

        label = tk.Label(frame, text=score_text, font=("Lucida", 14))
        label.pack(pady=20)

# Reset the board for a new game
def restart_game():
    global board, current_player, game_over
    board = [" " for _ in range(9)]
    current_player = "X"
    game_over = False
    for button in buttons:
        button.config(text="", bg="SystemButtonFace")

# Quit to the initial menu
def quit_to_menu():
    global rounds_played, player_score, ai_score
    rounds_played = 0
    player_score = 0
    ai_score = 0
    for widget in root.winfo_children():
        widget.destroy()
    player_name_input()

# Board setup
buttons = []

# Add a basic label for player's name input
def player_name_input():
    root.geometry("510x800")

    name_label = tk.Label(root, text="Enter Player Name:", font=("Lucida", 16))
    name_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

    name_entry = tk.Entry(root, font=("Lucida", 16))
    name_entry.place(relx=0.5, rely=0.10, anchor=tk.CENTER)

    def save_name():
        global player_name
        player_name = name_entry.get()
        start_game()

    submit_button = tk.Button(root, text="Start Game", command=save_name, font=("Lucida", 16))
    submit_button.place(relx=0.5, rely=0.20, anchor=tk.CENTER)

    # High scores button
    toggle_score_button = tk.Button(root, text="Show High Scores", command=show_high_scores, font=("Lucida", 16))
    toggle_score_button.place(relx=0.5, rely=0.30, anchor=tk.CENTER)

    # Music toggle button
    music_button = tk.Button(root, text="Music On/Off", command=toggle_music, font=("Lucida", 16))
    music_button.place(relx=0.5, rely=0.40, anchor=tk.CENTER)

    # Game mode selection
    mode_label = tk.Label(root, text="Select Game Mode:", font=("Lucida", 16))
    mode_label.place(relx=0.5, rely=0.50, anchor=tk.CENTER)

    best_of_5_button = tk.Button(root, text="Best of 5", command=lambda: set_game_mode("Best of 5"), font=("Lucida", 14))
    best_of_5_button.place(relx=0.3, rely=0.60, anchor=tk.CENTER)

    best_of_10_button = tk.Button(root, text="Best of 10", command=lambda: set_game_mode("Best of 10"), font=("Lucida", 14))
    best_of_10_button.place(relx=0.5, rely=0.60, anchor=tk.CENTER)

    best_of_20_button = tk.Button(root, text="Best of 20", command=lambda: set_game_mode("Best of 20"), font=("Lucida", 14))
    best_of_20_button.place(relx=0.71, rely=0.60, anchor=tk.CENTER)

    # Difficulty settings
    difficulty_label = tk.Label(root, text="Select AI Difficulty:", font=("Lucida", 16))
    difficulty_label.place(relx=0.5, rely=0.70, anchor=tk.CENTER)

    easy_button = tk.Button(root, text="Easy", command=lambda: set_difficulty("Easy"), font=("Lucida", 14))
    easy_button.place(relx=0.3, rely=0.80, anchor=tk.CENTER)

    medium_button = tk.Button(root, text="Medium", command=lambda: set_difficulty("Medium"), font=("Lucida", 14))
    medium_button.place(relx=0.5, rely=0.80, anchor=tk.CENTER)

    hard_button = tk.Button(root, text="Hard", command=lambda: set_difficulty("Hard"), font=("Lucida", 14))
    hard_button.place(relx=0.7, rely=0.80, anchor=tk.CENTER)

    # Add the maker's mark to the main menu
    maker_label = tk.Label(root, text="Made by Fulmen Factor - Music by orangiromusik via Pixabay", font="Lucida 12 italic")
    maker_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

# Set game mode and rounds based on selection
def set_game_mode(mode):
    global game_mode, max_rounds
    game_mode = mode
    if mode == "Best of 5":
        max_rounds = 5
    elif mode == "Best of 10":
        max_rounds = 10
    elif mode == "Best of 20":  # Replacing Unlimited with Best of 20
        max_rounds = 20
    print(f"Game mode set to: {game_mode}")

# Start game after name input
def start_game():
    global rounds_played, player_score, ai_score
    # Reset scores and rounds
    rounds_played = 0
    player_score = 0
    ai_score = 0

    # Clear input widgets and set up the game board
    for widget in root.winfo_children():
        widget.destroy()

    create_board()

def create_board():
    global buttons, rounds_played_label, results_label
    buttons = []

    rounds_played_label = tk.Label(root, text=f"Round {rounds_played + 1} of {max_rounds}", font=("Lucida", 16))
    rounds_played_label.grid(row=0, column=0, columnspan=3)

    for i in range(3):
        for j in range(3):
            button = tk.Button(root, text="", font="Lucida 25 bold", width=8, height=4,  # Bigger buttons for better fit
                               command=lambda i=i, j=j: handle_click(i, j))
            button.grid(row=i+1, column=j)
            buttons.append(button)

    # Restart button
    restart_button = tk.Button(root, text="Reset Board", command=restart_game, font=("Lucida", 16))
    restart_button.grid(row=5, column=0, columnspan=3)

    # Quit button
    quit_button = tk.Button(root, text="Quit to Menu", command=quit_to_menu, font=("Lucida", 16))
    quit_button.grid(row=6, column=0, columnspan=3)

    # Music toggle button
    music_button = tk.Button(root, text="Music On/Off", command=toggle_music, font=("Lucida", 16))
    music_button.grid(row=7, column=0, columnspan=3)

    # Results label
    results_label = tk.Label(root, text=f"Player: {player_score} | AI: {ai_score}", font=("Lucida", 16))
    results_label.grid(row=8, column=0, columnspan=3)

# Handle player and computer moves
def handle_click(row, col):
    global current_player, game_over, rounds_played, player_score

    index = row * 3 + col
    if board[index] == " " and not game_over:
        board[index] = current_player
        buttons[index].config(text=current_player)
        if check_winner():
            game_over = True
            if current_player == "X":
                player_score += 1  # Player score is incremented here
            results_label.config(text=f"Player: {player_score} | AI: {ai_score}")
            highlight_winning_line(check_winning_combo())
            root.after(1500, update_rounds)  # Wait 1.5 seconds before starting next round
            return
        if " " not in board:  # Handle tie
            game_over = True
            root.after(1500, update_rounds)  # Move to the next round in case of a tie
            return
        current_player = "O" if current_player == "X" else "X"
        if current_player == "O":
            computer_move()

# Update AI move logic to correctly update AI score
def computer_move():
    global current_player, game_over, ai_score
    if ai_difficulty == "Easy":
        random_move()
    elif ai_difficulty == "Medium":
        if not block_player():
            random_move()
    else:
        best_move()

    # After AI move, check if AI has won
    if check_winner():
        game_over = True
        ai_score += 1  # Increment AI's score when it wins
        results_label.config(text=f"Player: {player_score} | AI: {ai_score}")  # Update display with AI score
        highlight_winning_line(check_winning_combo())
        root.after(1500, update_rounds)  # Wait 1.5 seconds before starting next round
        return
    if " " not in board:  # Handle tie
        game_over = True
        root.after(1500, update_rounds)  # Move to the next round in case of a tie
        return
    current_player = "X"

# Update rounds and reset board after each session
def update_rounds():
    global rounds_played
    rounds_played += 1
    if max_rounds and rounds_played >= max_rounds:  # Game ends after the set number of rounds
        save_high_score(player_name, player_score, ai_difficulty)  # Save player score with difficulty
        quit_to_menu()  # Return to the main menu
    else:
        rounds_played_label.config(text=f"Round {rounds_played + 1} of {max_rounds}")
        reset_board()  # Reset the board at the start of each new round

# Reset the game board
def reset_board():
    global board, current_player, game_over
    board = [" " for _ in range(9)]  # Clear the board
    current_player = "X"  # Reset to player's turn
    game_over = False  # Reset game over state
    for button in buttons:
        button.config(text="", bg="SystemButtonFace")  # Reset button appearance

# Easy AI: Random move
def random_move():
    empty_spots = [i for i in range(9) if board[i] == " "]
    if empty_spots:
        index = random.choice(empty_spots)
        board[index] = current_player
        buttons[index].config(text=current_player)

# Medium AI: Block player if they're about to win, otherwise random move
def block_player():
    for combo in winning_combinations:
        block_index = check_for_blocking_opportunity(combo)
        if block_index is not None:
            board[block_index] = current_player
            buttons[block_index].config(text=current_player)
            return True
    return False

# Check for blocking opportunity
def check_for_blocking_opportunity(combo):
    x_count = sum(1 for i in combo if board[i] == "X")
    empty_count = sum(1 for i in combo if board[i] == " ")
    if x_count == 2 and empty_count == 1:
        return next(i for i in combo if board[i] == " ")
    return None

# Hard AI: Best move (using Minimax)
def best_move():
    best_score = float('-inf')
    move = -1
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            score = minimax(board, False, "O")
            board[i] = " "
            if score > best_score:
                best_score = score
                move = i
    if move != -1:
        board[move] = "O"
        buttons[move].config(text=current_player)

# Minimax algorithm for Hard AI
def minimax(board_state, is_maximizing, player):
    winner = check_winner_for_minimax(board_state)
    if winner:
        return 1 if winner == "O" else -1
    if " " not in board_state:
        return 0

    if is_maximizing:
        best_score = float('-inf')
        for i in range(9):
            if board_state[i] == " ":
                board_state[i] = "O"
                score = minimax(board_state, False, "X")
                board_state[i] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board_state[i] == " ":
                board_state[i] = "X"
                score = minimax(board_state, True, "O")
                board_state[i] = " "
                best_score = min(score, best_score)
        return best_score

# Winning combinations
winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                        (0, 3, 6), (1, 4, 7), (2, 5, 8),
                        (0, 4, 8), (2, 4, 6)]

# Check if there is a winner in the actual game
def check_winner():
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
            return True
    return False

# Get winning combination
def check_winning_combo():
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
            return combo
    return None

# Check for winner specifically for minimax function
def check_winner_for_minimax(board_state):
    for combo in winning_combinations:
        if board_state[combo[0]] == board_state[combo[1]] == board_state[combo[2]] != " ":
            return board_state[combo[0]]
    return None

def highlight_winning_line(combo):
    for index in combo:
        buttons[index].config(bg="lightgreen")

# Start player name input and music
player_name_input()
start_music()

root.mainloop()
