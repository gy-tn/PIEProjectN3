from deck import deck
from random import shuffle, randint, choice

class Player:
    def __init__(self, name:str, who, status:str='waiting'):
        self.name = name
        self.who = who
    
    def setHand(self):
        self.hand = []
    
    def __str__(self):
        output = f'{self.name}: '
        for card in self.hand:
            output += str(card) + ' '
        return output


def drawField(deck, trump, data):
    """
    Prints playground on the screen
    """
    if deck:
        print('|' * len(deck) + f' - {len(deck)} cards')
        print(f'{str(deck[0])} - trump suit card\n')
    else:
        print('No cards in the pile')
        print(f'{trump} - trump suit\n')
    print(data['message'])
    print('\n  Attack / Defense')

    for i in range(1, 7):
        print(str(i) + '.    ' + str(data['attacks'][i]) + ' / ' + str(data['defences'][i]))



def whoseFirstMove(players:list, trump:str):
    """
    This function for determining the player who makes the first move
    The player with the lowest trump card makes the first move
    """
    minPower = 100
    firstPlayer = None
    for player in players:
        for card in player.hand:
            if card.suit == trump and card.power < minPower:
                minPower = card.power
                firstPlayer = player

    # If there is no trump cards on players hands
    if not firstPlayer:
        firstPlayer = players[0]
    return firstPlayer


def whoIsClockwise(players, player):
    try:
        nextPlayer = players[players.index(player) + 1]
    except IndexError:
        nextPlayer = players[0]
    return nextPlayer


def makeMove(player):
    if player.who == 'human':
        move = input('Your move: ')
    else:
        move = randint(0, len(player.hand) - 1)
    return player.hand.pop(int(move))


def playRound(deck, trump, players, attacker):

    def makeAttack(attacker, data):
        allowedCards = set()
        for card in data['attacks'].values():
            try:
                allowedCards.add(card.rank)
            except AttributeError:
                pass
        for card in data['defences'].values():
            try:
                allowedCards.add(card.rank)
            except AttributeError:
                pass
        
        if len(allowedCards) == 0:
            move = sorted(attacker.hand, key=lambda card: card.power)[0]
            attacker.hand.remove(move)
            return move
        else:
            attackingHand = []
            for card in attacker.hand:
                if card.rank in allowedCards:
                    attackingHand.append(card)
            if attackingHand:
                move = sorted(attackingHand, key=lambda card: card.power)[0]
                attacker.hand.remove(move)
                return move
            else:
                return False
    
    def makeDefence(defender, data, moveNumber, trump):
        allowedCards = []
        attackingCard = data['attacks'][moveNumber]
        for card in defender.hand:
            if (card.suit == attackingCard.suit and card.power > attackingCard.power) or (card.suit == trump and card.power > attackingCard.power):
                allowedCards.append(card)
        if allowedCards:
            move = sorted(allowedCards, key=lambda card: card.power)[0]
            defender.hand.remove(move)
            return move
        else:
            playedCards = []
            for card in data['attacks'].values():
                if card:
                    defender.hand.append(card)
            for card in data['defences'].values():
                if card:
                    defender.hand.append(card)

    # Dictionary with data of the current state of the game
    roundData = {
        'message': 'Some message',
        'attacks': {
            1: '',
            2: '',
            3: '',
            4: '',
            5: '',
            6: ''
        },
        'defences': {
            1: '',
            2: '',
            3: '',
            4: '',
            5: '',
            6: ''
        }
    }
    defender = whoIsClockwise(players, attacker)
    attacker2 = whoIsClockwise(players, defender)
    
    print(attacker)
    print(defender)

    roundData['message'] = f'{attacker.name} attacks {defender.name}'
    drawField(deck, trump, roundData)
    
    for i in range(1, 7):
        attack = makeAttack(attacker, roundData)
        if attack:
            roundData['attacks'][i] = attack
            drawField(deck, trump, roundData)
        else:
            attacker = defender
            break
        defence = makeDefence(defender, roundData, i, trump)
        if defence:
            roundData['defences'][i] = defence
            drawField(deck, trump, roundData)
        else:
            attacker = attacker2
            break

        print(attacker)
        print(defender)
    
    if deck:
        while len(attacker.hand) < 6 and deck:
            attacker.hand.append(deck.pop())
        while len(attacker2.hand) < 6 and deck:
            attacker2.hand.append(deck.pop())
        while len(defender.hand) < 6 and deck:
            defender.hand.append(deck.pop())
    
    return attacker


def startGame(players:list):
    """
    The game logic
    Accepts list of players (instances of the Player class)
    """

    # Out of the game cards
    discardPile = []

    # Shuffle the deck
    shuffle(deck)
    while deck[0].rank == 'A':
        shuffle(deck)

    # Determine the trump suit
    trumpSuit = deck[0].suit

    # Update power of the cards
    for card in deck:
        if card.suit == trumpSuit:
            card.is_trump = True
        card.updatePower()

    # Deal cards to the players
    for player in players:
        player.setHand()
        for i in range(6):
            player.hand.append(deck.pop())

    # Determine the player who makes the first move
    attacker = whoseFirstMove(players, trumpSuit)
    # attacker.status = 'attacker'
    
    # Special rules for the first round
    roundNumber = 1

    while True:
        playersWithCards = []
        for player in players:
            if player.hand:
                playersWithCards.append(player)
        if len(playersWithCards) > 1:
            attacker = playRound(deck, trumpSuit, players, attacker)
        else:
            print(playersWithCards[0].name + ' is Durak')
            break

    # drawField(deck, trumpSuit, data)
    # print(attacker)
    # print(defender)
    # print(attacker2)
    
    
p1 = Player('First', 'ai')
p2 = Player('Second', 'human')

players = []
players.append(p1)
players.append(p2)

startGame(players)
