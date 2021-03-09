from termcolor import colored


hearts = colored('\u2665', 'red')
diamonds = colored('\u2666', 'red')
spades = '\u2660'
clubs = '\u2663'

suits = [hearts, diamonds, spades, clubs]
ranks = {
    '6': 1,
    '7': 2,
    '8': 3,
    '9': 4,
    '10': 5,
    'J': 6,
    'Q': 7,
    'K': 8,
    'A': 9
}


class Card:
    """
    Class for creating cards
    """
    def __init__(self, rank:str, suit:str, power:int, is_trump:bool=False):
        self.rank = rank
        self.suit = suit
        self.power = power
        self.is_trump = is_trump

    def updatePower(self):
        if self.is_trump:
            self.power += 10

    def __str__(self):
        return f'{self.rank}{self.suit}'


def create_deck(suits:list, ranks:dict) -> list:
    """
    Creates and returns card deck
    """
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append(Card(rank, suit, ranks[rank]))
    
    return deck


deck = create_deck(suits, ranks)

# for card in deck:
#     print(card, end=' ')