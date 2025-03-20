#!/usr/bin/env python3

from wordle import Player, GameManager
from scipy.stats import entropy
from information import *
from wordlist import *
from random import *
import time

class RandomSolver(Player):
    def __init__(self):
        self.num_guesses = 0
        self.guesses = []
        self.wordlist = WordList("possible_words.txt")

    def make_guess(self):
        guess = self.wordlist.get_random_word()
        return guess

    def update_knowledge(self, info):
        self.wordlist.refine(info)
        print(info)

class MattParkerSolver(Player):

    def __init__(self):
        self.num_guesses = 0
        self.guesses = []
        self.wordlist = WordList()
        self.five_words = ['fjord', 'gucks', 'nymph', 'vibex', 'waltz']
        self.index = -1

    def make_guess(self):
        self.num_guesses += 1
        self.index += 1
        if self.index >= 5 or len(self.wordlist) == 1:
            return self.wordlist.get_random_word()
        return self.five_words[self.index]
            
    def update_knowledge(self, info):
        self.guesses.append(info.guess)
        self.wordlist.refine(info)
        print(info)

class EntropySolver(Player):
    def __init__(self):
        self.num_guesses = 0
        self.wordlist = WordList("possible_words.txt")
        self.all_patterns = patterns()

    def make_guess(self):
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
        return guess

    def update_knowledge(self, info):
        self.wordlist.refine(info)
        print(info)

class OriginalSolver(Player):
    def __init__(self):
        self.num_guesses = 0
        self.wordlist = WordList("possible_words.txt")
        self.all_patterns = patterns()
        self.frequencies = [{}] * 5 # # of letters per position in the word
        self.fixed_letters = set()

    def make_guess(self):
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
        self.wordlist.refine(info)
        for i in range(len(info.pat.pattern)):
            letter = info.pat.pattern[i]
            if letter == Code.hit:
                self.fixed_letters.add(info.guess[i])
        self.frequencies = [{}] * 5
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
        solver4 = EntropySolver()
        manager = GameManager(solver, word)
        n_guess = manager.play_game()
        random_guesses.append(n_guess)
        manager = GameManager(solver2, word)
        n_guess = manager.play_game()
        parker_guesses.append(n_guess)
        manager = GameManager(solver3, word)
        n_guess = manager.play_game()
        original_guesses.append(n_guess)
        manager = GameManager(solver4, word)
        n_guess = manager.play_game()
        entropy_guesses.append(n_guess)
    print("RANDOM AVERAGE:",sum(random_guesses)/100,"guesses")
    print("PARKER AVERAGE:",sum(parker_guesses)/100,"guesses")
    print("Original AVERAGE:",sum(original_guesses)/100,'guesses')
    print("Entropy AVERAGE:",sum(entropy_guesses)/100,'guesses')
    print("you found the word in", n_guess, "guesses")
    start_time = time.time()
    solver = OriginalSolver()
    manager = GameManager(solver)
    n_guess = manager.play_game()
    print("you found the word in", n_guess, "guesses")
    end_time = time.time()
    execution_time = end_time - start_time
    print("execution time:",execution_time)

if __name__ == "__main__": main()
