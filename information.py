

from termcolor import colored
from enum import Enum
class Color():
    """Produces ANSI colorized strings"""

    @staticmethod
    def green(s):
        """converts the string `s` to an ANSI green string"""
        return colored(s, "green")

    @staticmethod
    def yellow(s):
        """converts the string `s` to an ANSI yellow string"""
        return colored(s, "yellow")

class Code(Enum):
    """ A `Code` represents the outcome of one letter in a wordle game.

    For each letter:
    - Code.hit conveys that the letter is correctly placed
      and at the correct position (i.e. green)
    - Code.mem conveys that the letter is in the word,
      but incorrectly placed (i.e. yellow)
    - Code.miss conveys that the letter is not in the word (i.e. grey)

    NOTE: It is considered DANGEROUS AND UNSAFE to use the literal codes `-1`,
    `0` and `1`. Please instead use the enum values `Code.miss`,
    `Code.hit`, and `Code.mem`.
    """
    hit = 1
    miss = -1
    mem = 0

class Pattern():
    """The pattern of outcomes expressed as `Code`s for a wordle guess"""

    def __init__(self, pattern = None, guess = None, goal = None):
        """Initialize Pattern.

        One of `pattern` or `guess` and `goal` must be provided. Will trigger an
        assertion error if insufficient arguments are procided.

        given a an option list of `Code`s (which is by default
        empty)

        """
        assert guess is not None and goal is not None or pattern is not None
        if pattern is None:
            self.pattern = self.__generate_code_list(guess, goal)
        else:
            self.pattern = pattern

    def __generate_code_list(self, guess, word):
        """ Private helper function to generate the pattern code list given a guess and a word.

        Takes in a `guess` and a `word` and returns a list of `Code`s that represent the
        pattern of the guess in the word.

        Both `guess` and `word` must be provided. The function will return a list of `Code`s.
        
        """

        word_pattern_list = [None] * len(guess)
        word_letters = list(word)
        
        for (idx, letter) in enumerate(guess):
            if word_letters[idx] == letter:
                word_pattern_list[idx] = Code.hit
                word_letters[idx] = '_'
        for (idx, letter) in enumerate(guess):
            if word_pattern_list[idx] is None:
                if letter in word_letters:
                    goal_idx = word_letters.index(letter)
                    word_pattern_list[idx] = Code.mem
                    word_letters[goal_idx] = '_'
        for i in range(len(word_pattern_list)):
            if word_pattern_list[i] is None:
                word_pattern_list[i] = Code.miss

        return word_pattern_list

    def __getitem__(self, i):
        """Gets the `i`th element of the pattern"""
        return self.pattern[i]

    def matches(self, guess, word):
        """Checks that `word` and `guess` are consistent w.r.t the pattern.

        Returns True if `word` could be a solution to the wordle problem and
        have produced the pattern held in `self` in response to the player
        guessing `guess`.

        """
        return tuple(self.__generate_code_list(guess, word)) == tuple(self.pattern)

    
class Information():
    """Information maintains a `guess` word and the `Pattern` associated with that guess."""

    def __init__(self, goal, guess):
        """Create Information

        The `goal` is the secret word that drives the wordle game, and
        `guess` is the player's guess.

        PRECONDITIONS:
        - `guess` is not None
        - `goal` is not None
        - length of `guess` and `goal_word` must be the same
        """
        assert guess is not None
        assert goal is not None
        assert len(goal) == len(guess)
        self.guess = guess
        self.pat = Pattern(guess = guess, goal = goal)


    def __str__(self):
        string = ""
        for (i,code) in enumerate(self.pat):
            if code == Code.hit:
                string += Color.green(self.guess[i])
            elif code == Code.mem:
                string += Color.yellow(self.guess[i])
            else:
                string += self.guess[i]
        return string

    def matches(self, word):
        """Returns True if `word` could have yielded `self.pat` for guess `self.guess`"""
        return self.pat.matches(self.guess, word)

def patterns():
    """constructs a list of all 3^5 possible patterns in no particular order"""
    outcomes = [()]
    for i in range(5):
        outcomes = [
            pattern + (code,)
            for pattern in outcomes
            for code in [Code.hit, Code.miss, Code.mem]
        ]
    return [Pattern(outcome) for outcome in outcomes]
