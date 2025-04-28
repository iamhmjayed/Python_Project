# Project_9_The_Hangman_Game with Tkinter GUI
import random
import tkinter as tk
from tkinter import messagebox


class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game")

        # Game variables
        self.words = ['python', 'java', 'kotlin', 'javascript', 'hangman', 'programming']
        self.word = random.choice(self.words)
        self.word_letters = set(self.word)
        self.used_letters = set()
        self.lives = 6

        # Setup GUI
        self.create_widgets()
        self.disable_game_controls()

    def create_widgets(self):
        # Welcome section
        self.name_label = tk.Label(self.root, text="Enter your name:")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.start_button.pack()

        # Game display
        self.lives_label = tk.Label(self.root, text="")
        self.lives_label.pack()

        self.used_letters_label = tk.Label(self.root, text="")
        self.used_letters_label.pack()

        self.word_display = tk.Label(self.root, text="", font=('Arial', 24))
        self.word_display.pack()

        # Guess input
        self.letter_label = tk.Label(self.root, text="Guess a letter:")
        self.letter_label.pack()

        self.letter_entry = tk.Entry(self.root)
        self.letter_entry.pack()

        self.guess_button = tk.Button(self.root, text="Guess", command=self.process_guess)
        self.guess_button.pack()

    def disable_game_controls(self):
        self.lives_label.config(text="")
        self.used_letters_label.config(text="")
        self.word_display.config(text="")
        self.letter_label.config(state=tk.DISABLED)
        self.letter_entry.config(state=tk.DISABLED)
        self.guess_button.config(state=tk.DISABLED)

    def enable_game_controls(self):
        self.letter_label.config(state=tk.NORMAL)
        self.letter_entry.config(state=tk.NORMAL)
        self.guess_button.config(state=tk.NORMAL)

    def start_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter your name!")
            return

        # Hide the name entry widgets
        self.name_label.pack_forget()
        self.name_entry.pack_forget()
        self.start_button.pack_forget()

        # Enable game controls
        self.enable_game_controls()

        # Initialize game display
        self.lives_label.config(text=f"Lives left: {self.lives}")
        self.word_display.config(text="_ " * len(self.word))

        messagebox.showinfo("Game Started", f"Welcome {name}!\nThe word has {len(self.word)} letters.")

    def process_guess(self):
        user_letter = self.letter_entry.get().lower()
        self.letter_entry.delete(0, tk.END)

        # Validate input
        if len(user_letter) != 1 or not user_letter.isalpha():
            messagebox.showwarning("Invalid Input", "Please enter a single letter.")
            return

        if user_letter in self.used_letters:
            messagebox.showinfo("Already Used", "You've already guessed that letter.")
            return

        self.used_letters.add(user_letter)
        self.used_letters_label.config(text=f"Used letters: {' '.join(sorted(self.used_letters))}")

        if user_letter in self.word_letters:
            self.word_letters.remove(user_letter)
        else:
            self.lives -= 1
            self.lives_label.config(text=f"Lives left: {self.lives}")
            messagebox.showinfo("Incorrect", f"'{user_letter}' is not in the word.")

        # Update word display
        display_word = [letter if letter in self.used_letters else '_' for letter in self.word]
        self.word_display.config(text=' '.join(display_word))

        # Check game status
        if not self.word_letters:
            messagebox.showinfo("Congratulations!", f"You won! The word was '{self.word}'!")
            self.root.destroy()
        elif self.lives == 0:
            messagebox.showinfo("Game Over", f"You lost! The word was '{self.word}'.")
            self.root.destroy()


def main():
    root = tk.Tk()
    game = HangmanGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
