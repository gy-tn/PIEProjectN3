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

    print('\n', end='')


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
    """
    Returns the next clockwise player in players list
    """
    try:
        nextPlayer = players[players.index(player) + 1]
    except (IndexError, ValueError):
        nextPlayer = players[0]
    return nextPlayer


def makeMove(player):
    if player.who == 'human':
        move = input('Your move: ')
    else:
        move = randint(0, len(player.hand) - 1)
    return player.hand.pop(int(move))


def playRound(deck, trump, players, attacker):
    """
    This function describes the logic of single round
    """

    def makeAttack(attacker, data):
        """
        Attacking logic
        """

        # Which cards can be used for attack (already played in current round)
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
        
        # Card for the first attacking move (the card with the lowest power)
        if len(allowedCards) == 0:
            move = sorted(attacker.hand, key=lambda card: card.power)[0]
            attacker.hand.remove(move)
            return move
        
        # Cards wich attacker can use for the next attacks
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
    
    def addCards(attackers, data):
        """
        Attackers adding card to failed defence
        """

        # Which cards can be added (already played in current round)
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
        
        # The first attacker add cards first, the second attacker is next
        if len(allowedCards):
            for attacker in attackers:
                for card in attacker.hand:
                    if card.rank in allowedCards:
                        data['message'] = f'{attacker.name} added card'
                        attacker.hand.remove(card)
                        return card

        # If nothing to add
        else:
            return False
    
    def makeDefence(defender, data, moveNumber, trump):
        """
        Defending logic
        """

        # Which cards can be used for defense
        allowedCards = []
        attackingCard = data['attacks'][moveNumber]
        for card in defender.hand:
            if (card.suit == attackingCard.suit and card.power > attackingCard.power) \
                or (card.suit == trump and card.power > attackingCard.power):
                allowedCards.append(card)
        
        # First of all use the weakest card
        if allowedCards:
            move = sorted(allowedCards, key=lambda card: card.power)[0]
            defender.hand.remove(move)
            return move
        
        # If there are no any cards for defense
        else:
            return False
            

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

    # Who is defender
    defender = whoIsClockwise(players, attacker)

    # Who is the second attacker
    attacker2 = whoIsClockwise(players, defender)
    
    # List with attackers
    attackers = [attacker, attacker2]

    # For testing
    print(attacker)
    print(defender)

    # Message with attacker and defender
    roundData['message'] = f'{attacker.name} attacks {defender.name}'
    drawField(deck, trump, roundData)

    # Count of attacks can not be more than count of cards in defender's hand
    allowedAttacks = len(defender.hand)
    
    # Count of attacks can not be more than 6
    for i in range(1, min(7, allowedAttacks + 1)):

        # Change the message
        roundData['message'] = f'{attacker.name} attacks {defender.name}'

        # Make an attack
        attack = makeAttack(attacker, roundData)

        # If the first attacker have card for attack
        if attack:
            roundData['attacks'][i] = attack
            drawField(deck, trump, roundData)
            nextAttacker = attacker2

        # If the second attacker have card of attack
        else:
            roundData['message'] = f'{attacker2.name} attacks {defender.name}'
            attack = makeAttack(attacker2, roundData)
            if attack:
                roundData['attacks'][i] = attack
                drawField(deck, trump, roundData)
                nextAttacker = attacker2
            
            # If attackers have no cards for attack
            else:
                
                # Defence is successfull, defender now is a new attacker
                nextAttacker = defender
                break
        
        # Make defense
        defence = makeDefence(defender, roundData, i, trump)

        # If there is card for defense
        if defence:
            roundData['defences'][i] = defence
            drawField(deck, trump, roundData)

            # If defender have cards after defense
            if defender.hand:
                nextAttacker = defender
            
            # If defender have no cards after defense
            else:
                nextAttacker = attacker2
        
        # If there is no card for defense
        else:

            # Attacker add cards to failed defense
            for j in range(i + 1, allowedAttacks + 1):
                roundData['attacks'][j] = addCards(attackers, roundData)
                if roundData['attacks'][j]:
                    drawField(deck, trump, roundData)

            # Defender takes all cards played in current round
            for card in roundData['attacks'].values():
                if card:
                    defender.hand.append(card)
            for card in roundData['defences'].values():
                if card:
                    defender.hand.append(card)
            
            nextAttacker = attacker2
            break

        # Used for tests
        print(attacker)
        print(defender)
    
    # Every player takes card from the pile if there are cards in the pile and players have less than
    # six cards on hands
    if deck:
        while len(attacker.hand) < 6 and deck:
            attacker.hand.append(deck.pop())
        while len(attacker2.hand) < 6 and deck:
            attacker2.hand.append(deck.pop())
        while len(defender.hand) < 6 and deck:
            defender.hand.append(deck.pop())

    return nextAttacker


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

    while True:

        # Players who still in the game (have cards in hands)
        playersWithCards = []
        for player in players:
            if player.hand:
                playersWithCards.append(player)
        
        # Start new round if there are two or more players with cards
        if len(playersWithCards) > 1:
            for player in playersWithCards:
                print(player)
            attacker = playRound(deck, trumpSuit, playersWithCards, attacker)
        
        # If at the end of the game the players have no cards left
        elif len(playersWithCards) == 0:
            print('Nobody is Durak!')
            break

        # The last player with cards lost
        else:
            print(playersWithCards[0].name + ' is Durak!')
            break
    
    
p1 = Player('First', 'ai')
p2 = Player('Second', 'ai')
p3 = Player('Third', 'ai')
p4 = Player('Fourth', 'ai')
p5 = Player('Fifth', 'ai')

players = []
players.append(p1)
players.append(p2)
players.append(p3)
# players.append(p4)
# players.append(p5)

startGame(players)
