#!/usr/bin/env python3

from wordle import Player, GameManager
from scipy.stats import entropy
from information import *
from wordlist import *
from random import *
import time

class RandomSolver(Player):
    def __init__(self):
        """
        Initialize the solver.
        """
        self.num_guesses = 0
        self.guesses = []
        self.wordlist = WordList("possible_words.txt")

    def make_guess(self):
        """
        the make_guess function makes a guess.

        Currently, it always guesses "salty". Write code here to improve your solver.
        """
        guess = self.wordlist.get_random_word()
        return guess

    def update_knowledge(self, info):
        """
        update_knowledge updates the solver's knowledge with an `info`
        info is an element of the `Information` class. See `information.py`
        """
        self.wordlist.refine(info)
        print(info)

class MattParkerSolver(Player):

    def __init__(self):
        """
        Initialize the solver.
        """
        self.num_guesses = 0
        self.guesses = []
        self.wordlist = WordList()
        self.five_words = ['fjord', 'gucks', 'nymph', 'vibex', 'waltz']
        self.index = -1

    def make_guess(self):
        """
        the make_guess function makes a guess.

        Currently, it always guesses "salty". Write code here to improve your solver.
        """
        self.num_guesses += 1
        self.index += 1
        if self.index >= 5 or len(self.wordlist) == 1:
            return self.wordlist.get_random_word()
        return self.five_words[self.index]
            
    def update_knowledge(self, info):
        """
        update_knowledge updates the solver's knowledge with an `info`
        info is an element of the `Information` class. See `information.py`
        """
        self.guesses.append(info.guess)
        self.wordlist.refine(info)
        print(info)

class EntropySolver(Player):
    def __init__(self):
        """
        Initialize the solver.
        """
        self.num_guesses = 0
        self.wordlist = WordList("possible_words.txt")
        self.all_patterns = patterns()

    def make_guess(self):
        """
        the make_guess function makes a guess.
        Currently, it always guesses "salty". Write code here to improve your solver.
        """
        max_entropy = 0
        guess = ""
        if 'lares' in self.wordlist:
            return 'lares'
        for word in self.wordlist:
            pk = []
            for pattern in self.all_patterns:
                num_words_for_pattern = len(self.wordlist.matching(pattern, word))
                pk.append(num_words_for_pattern/len(self.wordlist))
            ent = entropy(pk=pk)
            if ent >= max_entropy:
                max_entropy = ent
                guess = word
        # print("WORD:",word,"ENTROPY:",ent)
        return guess

    def update_knowledge(self, info):
        """
        update_knowledge updates the solver's knowledge with an `info`
        info is an element of the `Information` class. See `information.py`
        """
        self.wordlist.refine(info)
        print(info)

class OriginalSolver(Player):
    def __init__(self):
        """
        Initialize the solver.
        """
        self.num_guesses = 0
        self.wordlist = WordList("possible_words.txt")
        self.all_patterns = patterns()
        self.frequencies = [{}] * 5 # # of letters per position in the word
        self.fixed_letters = set()

    def make_guess(self):
        """
        the make_guess function makes a guess.
        Currently, it always guesses "salty". Write code here to improve your solver.
        """
        guess = ""

        if len(self.wordlist) == 1:
            return self.wordlist.words[0]

        # building the new frequency dict array (changes every guess)
        for word in self.wordlist:
            for i in range(len(word)): # 0 - 4 inclusive
                dict = self.frequencies[i]
                letter = word[i]
                if letter not in dict.keys():
                    dict[letter] = 1
                else:
                    dict[letter] += 1

        max_score = 0
        for word in self.wordlist:
            score = 0
            multiplier = 1

            # weight for # of vowels
            vowels = set()
            for letter in word:
                if letter == 'a' or letter == 'e' or letter == 'i' or letter == 'o' or letter == 'u':
                    vowels.add(letter)
            if 'a' not in self.fixed_letters and 'e' not in self.fixed_letters and 'i' not in self.fixed_letters and 'o' not in self.fixed_letters and 'u' not in self.fixed_letters:
                multiplier += len(vowels)/5

            # weight for distinct letters
            distinct = set()
            for i in range(len(word)):
                letter = word[i]
                score += self.frequencies[i][letter]
                distinct.add(letter)
            multiplier -= (5 - len(distinct)) / 5

            # update max!
            score *= multiplier
            if score > max_score:
                max_score = score
                guess = word
        return guess
    
    def update_knowledge(self, info):
        """
        update_knowledge updates the solver's knowledge with an `info`
        info is an element of the `Information` class. See `information.py`
        """
        self.wordlist.refine(info)
        for i in range(len(info.pat.pattern)):
            letter = info.pat.pattern[i]
            if letter == Code.hit:
                self.fixed_letters.add(info.guess[i])
        self.frequencies = [{}] * 5
        print(info)

class Solver(Player):
    """
    "Solving" Wordle

    Your task is to fill in this class to automatically play the game.
    Feel free to modify any of the starter code.

    You Should write at least three subclasses of Player.
    1. A Random Player -- guess a random word each time!
    2. A Player that uses Matt Parker's 5 Words. 
       2a. How do you leverage the info gained from these 5 words?
       2b. Do always you have to guess all of these words?
       2c. What order should you guess these words in?
    3. Entropy Player (You are welcome to use the scipy above)
    4. Better and Better Players!

    Your goal is not just to Write the BEST SOLVER YOU CAN, but scientifically
    show that your solver is better than the others. 

    Note that the GameManager class returns the number of guesses a player makes.
    Compute 3 statistics:
    (1) the average number of guesses
    (2) the max number of guesses
    (3) the minimum number of guesses
    Feel free to add more statistics if you'd like.

    Think deeply about how you should design this experiments. How should you select the
    experimental inputs? Is it better for the two algorithms youre comparing to have the
    same or different test sets between experiments? 
    
    Please use objects and inheritance to structure your experiments.

    Here's an outline of the rest of the code in this project.
    - wordle.py.
      Hit play when VSCode is focused on this file to play
      a game of wordle against the computer! There are 3 classes
      of interest to the Solver:
      +  `Wordle` manages the world game state itself
      +  `Player` Provides a Human interface at the CLI to play the game
          Your Solver exposes the same interface as this class       
      +  `Game Manager` runs the main control loop for Wordle

    - information.py
      This file defines how information is propagated to the player. The relevant
      classes are `Information` and `Pattern`.
      + Pattern records a list `pattern` that represents the outcomes. 
        For instance
            [hit, miss, miss, mem, hit]
        Means the first and last letters of a guess are correct, the second two
        are not in the word, and the penultimate is in the word but not
        in the right spot. These codes are defined in `Code`.

      + Pattern provides a useful method `pattern.matches(guess, word)` which
        checks that the current pattern is consistent with guessing `guess` when
        `word` is the goal word

      + Information is constructed by passing it a player-provided `guess` and
        the `goal` word. 
        
      + Information provides an important method `info.matches(word)` which 
        returns true if `info.pattern == Information(info.guess, word)`

      + IMPORTANT. The `patterns()` function returns a list of all 3^5 patterns.

    - `wordlist.py`
       This file defines the `WordList` class, which is not actually a `list`,
       but wraps a list, defining some helpful wordle-specific features.
       + wordlist.get_random_word() gets a random word from the wordlist
       + wordlist.refine(info) keeps only those words consistent with `info`
       + wordlist.matching(pattern, guess) produces a literal `list`
         of words that such that if they had been the goal word, would have 
         produced pattern in responds to a player guessing `guess.

    
    IN GENERAL. FEEL FREE TO MAKE ANY MODIFICATIONS/ADDITIONS TO THIS CODE.
    You shouldn't neeeed to but of course please do if it makes your solution
    more elegant
    """

    def __init__(self):
        """
        Initialize the solver.
        """
        self.num_guesses = 0

    def make_guess(self):
        """
        the make_guess function makes a guess.

        Currently, it always guesses "salty". Write code here to improve your solver.
        """
        return "salty"

    def update_knowledge(self, info):
        """
        update_knowledge updates the solver's knowledge with an `info`
        info is an element of the `Information` class. See `information.py`
        """
        print(info)

def main():
    wl = WordList("possible_words.txt")
    random_guesses = []
    parker_guesses = []
    original_guesses = []
    entropy_guesses = []
    for i in range(100):
        word = wl.get_random_word()
        solver  = RandomSolver()
        solver2 = MattParkerSolver()
        solver3 = OriginalSolver()
        # solver4 = EntropySolver()
        manager = GameManager(solver, word)
        n_guess = manager.play_game()
        random_guesses.append(n_guess)
        manager = GameManager(solver2, word)
        n_guess = manager.play_game()
        parker_guesses.append(n_guess)
        manager = GameManager(solver3, word)
        n_guess = manager.play_game()
        original_guesses.append(n_guess)
        # manager = GameManager(solver4, word)
        # n_guess = manager.play_game()
        # entropy_guesses.append(n_guess)
    print("RANDOM AVERAGE:",sum(random_guesses)/100,"guesses")
    print("PARKER AVERAGE:",sum(parker_guesses)/100,"guesses")
    print("Original AVERAGE:",sum(original_guesses)/100,'guesses')
    # print("Entropy AVERAGE:",sum(entropy_guesses)/100,'guesses')
    # print("you found the word in", n_guess, "guesses")
    # start_time = time.time()
    # solver = OriginalSolver()
    # manager = GameManager(solver)
    # n_guess = manager.play_game()
    # print("you found the word in", n_guess, "guesses")
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print("execution time:",execution_time)

if __name__ == "__main__": main()

# Ways to optimize OriginalSolver():
# limit the amount of times it has double letters (ex. eerie)
# limit the amount of times it guesses more words than necessary (ex. hussy puppy mummy funny)
# find different ways to weight the score

# TO DO:
# compare OriginalSolver() to EntropySolver() over the small_words file
