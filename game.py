from deck import deck
from random import shuffle, randint, choice
from colorText import greenBoldMessage
from time import sleep

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


def drawField(deck, trump, data, players):
    """
    Prints playground on the screen
    """
    print(chr(27) + "[2J")
    print('#' * 15 + ' Players ' + '#' * 15)
    for player in players:
        if player.who == 'human':
            print('Your cards')
            for card in range(len(player.hand)):
                print(f'{card + 1}.{str(player.hand[card])} | ', end='')
        else:
            print(player.name)
            for card in range(len(player.hand)):
                print(f'{card + 1}.## | ', end='')
        print('\n')
    print('#' * 40 + '\n')
    print('#' * 15 + ' Table ' + '#' * 15)
    if deck:
        if len(deck) == 1:
            print('|' * len(deck) + f' - {len(deck)} card in the pile')
        else:
            print('|' * len(deck) + f' - {len(deck)} cards in the pile')
        print(f'{str(deck[0])} - trump suit card\n')
    else:
        print('No cards in the pile')
        print(f'{trump} - trump suit')
    print(data['message']) 
    print('\n  Attack / Defense')
    for i in range(1, 7):
        print(str(i) + '.    ' + str(data['attacks'][i]) + ' / ' + str(data['defences'][i]))
    print('\n', end='')
    print('#' * 40 + '\n')
    

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
            
        if attacker.who == 'ai':
            sleep(2)
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
        
        else:
            allowedMoves = possibleMoves(attacker, allowedCards)
            if attacker.hand:
                move = input('Your turn? ')
                while True:
                    if move in allowedMoves:
                        break
                    move = input('Your turn? ')
                try:
                    move = attacker.hand[int(move) - 1]
                    attacker.hand.remove(move)
                except ValueError:
                    return move
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
                if attacker.who == 'ai':
                    data['message'] = greenBoldMessage(f'{attacker.name} can add cards')
                    for card in attacker.hand:
                        if card.rank in allowedCards:
                            attacker.hand.remove(card)
                            return card
                        else:
                            continue
                else:
                    data['message'] = greenBoldMessage('You can add cards')
                    allowedMoves = possibleMoves(attacker, allowedCards)
                    if attacker.hand:
                        move = input('Your turn? ')
                        while True:
                            if move in allowedMoves:
                                break
                            move = input('Your turn? ')
                        try:
                            move = attacker.hand[int(move) - 1]
                            attacker.hand.remove(move)
                        except ValueError:
                            return move
                        return move
                    else:
                        continue
            return False

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
        
        if defender.who == 'ai':
            sleep(2)
            # First of all use the weakest card
            if allowedCards:
                move = sorted(allowedCards, key=lambda card: card.power)[0]
                defender.hand.remove(move)
                return move
            
            # If there are no any cards for defense
            else:
                return False
        
        else:
            allowedMoves = possibleMoves(defender, allowedCards)
            while defender.hand:
                move = input('Your turn? ')
                if move in allowedMoves:
                    break
            try:
                move = defender.hand[int(move) - 1]
                defender.hand.remove(move)
            except ValueError:
                return move
            return move

    def possibleMoves(player, allowed):
        allowedMoves = []
        player.hand = sorted(player.hand, key=lambda card: card.power)
        print('#' * 15 + ' Your moves ' + '#' * 15 + '\n')
        if player.status == 'attacking':
            allowedMoves.append('p')
            if allowed:
                for card in player.hand:
                    if card.rank in allowed:
                        allowedMoves.append(str(player.hand.index(card) + 1))
                        print(greenBoldMessage(f'{player.hand.index(card) + 1}.') + str(card) + ' | ', end='')
                    else:
                        print(f'{str(player.hand.index(card) + 1)}.{str(card)} | ', end='')
                print(greenBoldMessage('\np') + ' - Pass')
            else:
                for card in range(len(player.hand)):
                    allowedMoves.append(str(card + 1))
                    print(greenBoldMessage(f'{card + 1}.') + str(player.hand[card]) + ' | ', end='')
                print('\np - Pass')
            print('\n')
        elif player.status == 'defending':
            allowedMoves.append('t')
            if allowed:
                for card in player.hand:
                    if card in allowed:
                        allowedMoves.append(str(player.hand.index(card) + 1))
                        print(greenBoldMessage(f'{player.hand.index(card) + 1}.') + str(card) + ' | ', end='')
                    else:
                        print(f'{str(player.hand.index(card) + 1)}.{str(card)} | ', end='')
            else:
                for card in player.hand:
                    print(f'{str(player.hand.index(card) + 1)}.{str(card)} | ', end='')
            print(greenBoldMessage('\nt') + ' - Take')
            print('\n')

        return allowedMoves


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

    for player in players:
        player.status = 'waiting'

    attacker.status = 'attacking'

    # Who is defender
    defender = whoIsClockwise(players, attacker)
    defender.status = 'defending'

    # Who is the second attacker
    if len(players) > 2:
        attacker2 = whoIsClockwise(players, defender)
        attacker2.status = 'attacking'
        attackers = [attacker, attacker2]
    else:
        # List with attackers
        attackers = [attacker]

    # Message with attacker and defender
    if attacker.who == 'human':
        roundData['message'] = greenBoldMessage(f'You attack {defender.name}')
    else:
        if defender.who == 'human':
            roundData['message'] = greenBoldMessage(f'{attacker.name} attack You')
        else:
            roundData['message'] = greenBoldMessage(f'{attacker.name} attack {defender.name}')
    drawField(deck, trump, roundData, players)

    # Count of attacks can not be more than count of cards in defender's hand
    allowedAttacks = len(defender.hand)

    whoAttack = attacker
    asked = 0
    
    # Count of attacks can not be more than 6
    for i in range(1, min(7, allowedAttacks + 1)):
        while asked < 2:
            # Change the message
            if whoAttack.who == 'human':
                roundData['message'] = greenBoldMessage(f'You attack {defender.name}')
            else:
                if defender.who == 'human':
                    roundData['message'] = greenBoldMessage(f'{whoAttack.name} attack You')
                else:
                    roundData['message'] = greenBoldMessage(f'{whoAttack.name} attack {defender.name}')
            
            attack = makeAttack(whoAttack, roundData)
            if attack and type(attack) != str:
                asked = 0
                roundData['attacks'][i] = attack
                drawField(deck, trump, roundData, players)
                if len(players) > 2: 
                    nextAttacker = attacker2
                break
            else:
                if len(players) > 2:
                    if whoAttack == attacker:
                        whoAttack = attacker2
                    else:
                        whoAttack = attacker
                asked += 1
        
        if not roundData['attacks'][i]:
            nextAttacker = defender
            break
                
            
        """
        # Make an attack
        attack = makeAttack(attacker, roundData)
        # If the first attacker have card for attack
        if attack and type(attack) != str:
            roundData['attacks'][i] = attack
            drawField(deck, trump, roundData, players)
            nextAttacker = attacker2
        # If the second attacker have card of attack
        else:
            if len(players) > 2:
                if attacker2.who == 'human':
                    roundData['message'] = greenBoldMessage(f'You attack {defender.name}')
                else:
                    if defender.who == 'human':
                        roundData['message'] = greenBoldMessage(f'{attacker2.name} attacks You')
                    else:
                        roundData['message'] = greenBoldMessage(f'{attacker2.name} attacks {defender.name}')
                drawField(deck, trump, roundData, players)
                attack = makeAttack(attacker2, roundData)
                if attack and type(attack) != str:
                    roundData['attacks'][i] = attack
                    drawField(deck, trump, roundData, players)
                    nextAttacker = attacker2
                # If attackers have no cards for attack
                else:              
                    # Defence is successfull, defender now is a new attacker
                    nextAttacker = defender
                    break
            else:
                nextAttacker = defender
                break
        """
        
        # Make defense
        defence = makeDefence(defender, roundData, i, trump)
        # If there is card for defense
        if defence and type(defence) != str:
            roundData['defences'][i] = defence
            drawField(deck, trump, roundData, players)
            nextAttacker = defender
        # If there is no card for defense
        else:
            # Attacker add cards to failed defense
            for j in range(i + 1, allowedAttacks + 1):
                if whoAttack.who == 'human':
                    roundData['message'] = \
                        greenBoldMessage(f'You can add up to {allowedAttacks - j + 1} cards if you want to')
                roundData['attacks'][j] = addCards(attackers, roundData)
                drawField(deck, trump, roundData, players)
                if roundData['attacks'][j] and type(roundData['attacks'][j]) != str:
                    drawField(deck, trump, roundData, players)
                else:
                    break
            # Defender takes all cards played in current round
            for card in roundData['attacks'].values():
                if card:
                    defender.hand.append(card)
            for card in roundData['defences'].values():
                if card:
                    defender.hand.append(card)
            if len(players) > 2:
                nextAttacker = attacker2
            else:
                nextAttacker = attacker
            break
    
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
            attacker = playRound(deck, trumpSuit, playersWithCards, attacker)
        
        # If at the end of the game the players have no cards left
        elif len(playersWithCards) == 0:
            print('Nobody is Durak!')
            break

        # The last player with cards lost
        else:
            if playersWithCards[0].who == 'human':
                print('You are Durak!')
            else:
                print(playersWithCards[0].name + ' is Durak!')
            break
    
    
p1 = Player('First', 'ai')
p2 = Player('Second', 'human')
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
