from deck import deck
from random import shuffle, randint, choice
from colorText import greenBoldMessage, redMessage
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


def drawField(deck, trump, data, players, dummy):
    """
    Prints playground on the screen
    """

    # Clear the window
    print(chr(27) + "[2J")

    # Print section with players and their cards
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
                # Cheat! You can see opponent's cards (used for tests)
                # print(f'{card + 1}.{str(player.hand[card])} | ', end='')
        print('\n')
    print('#' * 40 + '\n')

    # Print section with table (playground itself)
    print('#' * 15 + ' Table ' + '#' * 15)
    if deck: # Print info about the deck
        if len(deck) == 1:
            print('|' * len(deck) + f' - {len(deck)} card in the pile')
        else:
            print('|' * len(deck) + f' - {len(deck)} cards in the pile')
        print(f'{str(deck[0])} - trump suit card\n')
    else:
        print('No cards in the pile')
        print(f'{trump} - trump suit\n')
    print(data['message']) # Info message (dinamically changing)
    print('\n  Attack / Defense')
    for i in range(1, 7): # Print played cards
        print(str(i) + '.    ' + str(data['attacks'][i]) + ' / ' + str(data['defences'][i]))
    print('\n', end='')
    print('#' * 40 + '\n')

    # This is for to fix printing playground
    # If human is waiting for his turn
    if dummy:
        print('#' * 15 + ' Your moves ' + '#' * 15 + '\n')
        print('Waiting...\n\n\n')

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


def playRound(deck, trump, players, attacker, round):
    """
    This function describes the logic of single round
    """

    def makeAttack(attacker, data):
        """
        Attacking logic
        """

        # Which cards can be used for attack (already played in current round)
        allowedCards = set()
        for card in data['attacks'].values(): # Collect attacking cards
            try:
                allowedCards.add(card.rank)
            except AttributeError: # If not card (empty string may be)
                pass
        for card in data['defences'].values(): # Collect defending cards
            try:
                allowedCards.add(card.rank)
            except AttributeError: # If not card (empty string may be)
                pass
        
        # Logic for computer to attack
        if attacker.who == 'ai':
            sleep(2)
            # Card for the first attacking move (the card with the lowest power)
            if len(allowedCards) == 0:
                move = sorted(attacker.hand, key=lambda card: card.power)[0]
                attacker.hand.remove(move)
                return move
            
            # Cards wich attacker can use for the next attacks
            else:
                attackingHand = [] # Collect possible cards to this list
                for card in attacker.hand:
                    if card.rank in allowedCards: # Look only on rank (suit does not matter)
                        attackingHand.append(card)
                if attackingHand: # Attack if there are cards (simple logic for computer)
                    move = sorted(attackingHand, key=lambda card: card.power)[0]
                    attacker.hand.remove(move)
                    return move # Return card
                else:
                    return False # If computer can not attack
        
        # Logic for human to attack
        else:
            allowedMoves = possibleMoves(attacker, allowedCards) # Highlight possible moves
            if attacker.hand: # Ask for the move if there are cards on the hand
                move = input('Your turn? ')
                while True:
                    if move in allowedMoves:
                        break
                    move = input(redMessage('Choose another possible variant: ')) # Handle user input
                try:
                    move = attacker.hand[int(move) - 1]
                    attacker.hand.remove(move)
                except ValueError:
                    return move # If move not a card but just a command (take cards or pass move)
                return move # Return card
            else:
                return False # If player have no cards on hand
    
    def addCards(attacker, data):
        """
        Attackers adding card to failed defence
        """

        # Which cards can be added (already played in current round)
        allowedCards = set()
        for card in data['attacks'].values(): # Collect attacking cards
            try:
                allowedCards.add(card.rank)
            except AttributeError: # If not card (empty string may be)
                pass
        for card in data['defences'].values(): # Collect defending cards
            try:
                allowedCards.add(card.rank)
            except AttributeError: # If not card (empty string may be)
                pass
        
        # The first attacker add cards first, the second attacker is next
        if len(allowedCards):
            if attacker.who == 'ai': # Logic for computer
                sleep(2)
                for card in sorted(attacker.hand, key=lambda card: card.power):
                    if card.rank in allowedCards:
                        attacker.hand.remove(card)
                        return card
                    else:
                        continue
            else: # Logic for human (same as for attack)
                allowedMoves = possibleMoves(attacker, allowedCards)
                if attacker.hand:
                    move = input('Your turn? ')
                    while True:
                        if move in allowedMoves:
                            break
                        move = input(redMessage('Choose another possible variant: '))
                    try:
                        move = attacker.hand[int(move) - 1]
                        attacker.hand.remove(move)
                    except ValueError:
                        return move
                    return move

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
                or (card.suit == trump and card.power > attackingCard.power): # Suit and rank matters
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
            allowedMoves = possibleMoves(defender, allowedCards) # Highlight possible moves
            move = input('Your turn? ')
            while defender.hand:
                if move in allowedMoves:
                    break
                move = input(redMessage('Choose another possible variant: ')) # Handle user input
            try:
                move = defender.hand[int(move) - 1]
                defender.hand.remove(move)
            except ValueError:
                return move
            return move

    def possibleMoves(player, allowed):
        """
        This function prints possible moves for attack and defence to human
        """
        allowedMoves = []
        player.hand = sorted(player.hand, key=lambda card: card.power)
        print('#' * 15 + ' Your moves ' + '#' * 15 + '\n')
        if player.status == 'attacking' or player.status == 'attacker2':
            allowedMoves.append('p') # p - pass the move
            if allowed: # Print possible moves with green color
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
            allowedMoves.append('t') # t - take cards
            if allowed: # Print possible moves with green color
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
        'message': 'Some message', # Message to player
        # Attacking cards
        'attacks': {
            1: '',
            2: '',
            3: '',
            4: '',
            5: '',
            6: ''
        },
        # Defending cards
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
        attacker2.status = 'attacker2'
        attackers = [attacker, attacker2]
    else:
        # List with attackers
        attackers = [attacker]

    # Count of attacks can not be more than count of cards in defender's hand and more than 6
    # (5 for the first round)
    if round == 1:
        allowedAttacks = min(5, len(defender.hand))
        if attacker.who == 'human':
            roundData['message'] = greenBoldMessage('You have the lowest trump suit card and start first')
        else:
            roundData['message'] = greenBoldMessage(f'{attacker.name} has the lowest trump suit card and start first')
        drawField(deck, trump, roundData, players, True)
        sleep(2)
    else:
        allowedAttacks = min(6, len(defender.hand))

    whoAttack = attacker
    asked = 0 # Using for breaking attacing loop
    
    for i in range(1, allowedAttacks + 1): # Start attacks and defences
        while asked < len(attackers):
            # Change the message
            if whoAttack.who == 'human':
                if whoAttack.status == 'attacking':
                    roundData['message'] = greenBoldMessage(f'You attack {defender.name}')
                else:
                    roundData['message'] = greenBoldMessage(f'You can continue to attack {defender.name}')
                dummy = False
            else:
                if defender.who == 'human':
                    if whoAttack.status == 'attacking':
                        roundData['message'] = greenBoldMessage(f'{whoAttack.name} attack You')
                    else:
                        roundData['message'] = greenBoldMessage(f'{whoAttack.name} can continue to attack You')
                    dummy = True
                else:
                    if whoAttack.status == 'attacking':
                        roundData['message'] = greenBoldMessage(f'{whoAttack.name} attack {defender.name}')
                    else:
                        roundData['message'] = greenBoldMessage(f'{whoAttack.name} can continue to attack {defender.name}')
                    dummy = True
            drawField(deck, trump, roundData, players, dummy) # Refresh the playground
            attack = makeAttack(whoAttack, roundData) # Make attack
            if attack and type(attack) != str:
                if defender.who == 'human':
                    dummy = False
                else:
                    dummy = True
                asked = 0
                roundData['attacks'][i] = attack # Put attacking card to data of the round
                drawField(deck, trump, roundData, players, dummy) # Refresh the playground
                if len(players) > 2: 
                    nextAttacker = attacker2 # Attacker for the next round (works when defender takes cards)
                break
            else:
                if len(players) > 2:
                    if whoAttack == attacker:
                        whoAttack = attacker2 # Second attacker can continue attack after first attacker
                    else:
                        whoAttack = attacker # First attacker can continue attack after second attacker
                asked += 1
        
        if not roundData['attacks'][i]:
            nextAttacker = defender # Attacker for the next round (works when attackers have no more cards to attack)
            break
        
        # Make defense
        defence = makeDefence(defender, roundData, i, trump)

        # If there is card for defense
        if defence and type(defence) != str:
            dummy = True
            roundData['defences'][i] = defence # Put defending card to data of the round
            drawField(deck, trump, roundData, players, dummy) # Refresh the playground
            nextAttacker = defender # Attacker for the next round (works when defender beated all attacking cards)
            defended = True # When defense is successfull

        # If there is no card for defense
        else:
            defended = False # When defense was failed
            # Attacker add cards to failed defense
            whoAdd = attacker # First attacker add cards first
            countOfAddedCards = i # Serial number of adding card (equals to attacking move number)
            if countOfAddedCards < allowedAttacks:
                while True:
                    # Form message
                    if whoAdd.who == 'ai':
                        if defender.who == 'ai':
                            if (allowedAttacks - countOfAddedCards) == 1:
                                roundData['message'] = \
                                    greenBoldMessage(f'{defender.name} take cards. {whoAdd.name} can add up to {allowedAttacks - countOfAddedCards} card')
                            else:
                                roundData['message'] = \
                                    greenBoldMessage(f'{defender.name} take cards. {whoAdd.name} can add up to {allowedAttacks - countOfAddedCards} cards')
                            dummy = True
                        else:
                            if (allowedAttacks - countOfAddedCards) == 1:
                                roundData['message'] = \
                                    greenBoldMessage(f'You take cards. {whoAdd.name} can add up to {allowedAttacks - countOfAddedCards} card')
                            else:
                                roundData['message'] = \
                                    greenBoldMessage(f'You take cards. {whoAdd.name} can add up to {allowedAttacks - countOfAddedCards} cards')
                            dummy = True
                    else:
                        if (allowedAttacks - countOfAddedCards) == 1:
                            roundData['message'] = \
                                greenBoldMessage(f'{defender.name} take cards. You can add up to {allowedAttacks - countOfAddedCards} card')
                        else:
                            roundData['message'] = \
                                greenBoldMessage(f'{defender.name} take cards. You can add up to {allowedAttacks - countOfAddedCards} cards')
                        dummy = False
                    drawField(deck, trump, roundData, players, dummy) # Refresh the playground
                    added = addCards(whoAdd, roundData) # Attacker adding card
                    if added and type(added) != str:
                        roundData['attacks'][countOfAddedCards + 1] = added
                        drawField(deck, trump, roundData, players, dummy) # Refresh the playground
                        countOfAddedCards += 1
                    else:
                        if len(players) > 2:
                            if whoAdd == attacker2:
                                break
                            whoAdd = attacker2 # Second attacker can add cards too
                        else:
                            break
                    if countOfAddedCards == allowedAttacks: # 
                        break
            sleep(2)

            # New message
            if defender.who == 'human':
                roundData['message'] = greenBoldMessage(f'Defence failed, You take played cards')
            else:
                roundData['message'] = greenBoldMessage(f'Defence failed, {defender.name} take played cards')
            dummy = True
            drawField(deck, trump, roundData, players, dummy) # Refresh the playground
            sleep(2)
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
    
    if defended: # Defence was successfull
        roundData['message'] = greenBoldMessage('Defence was successfull')
        dummy = True
        drawField(deck, trump, roundData, players, dummy)
        sleep(2)

    # Every player takes card from the pile if there are cards in the pile and players have less than
    # six cards on hands
    if deck:
        while len(attacker.hand) < 6 and deck:
            attacker.hand.append(deck.pop())
        if len(players) > 2:
            while len(attacker2.hand) < 6 and deck:
                attacker2.hand.append(deck.pop())
        while len(defender.hand) < 6 and deck:
            defender.hand.append(deck.pop())
    
    if not defender.hand: # If defender has no cards after dealing (attacker takes cards first)
        if len(players) > 2:
            nextAttacker = attacker2
    
    if len(players) > 2: # If the second attacker has no cards after dealing (first attacker takes cards first)
        if not attacker2.hand:
            nextAttacker = whoIsClockwise(players, attacker2)
    
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

    roundNumber = 1

    while True:

        # Players who still in the game (have cards in hands)
        playersWithCards = []
        for player in players:
            if player.hand:
                playersWithCards.append(player)
        
        # Start new round if there are two or more players with cards
        if len(playersWithCards) > 1:
            attacker = playRound(deck, trumpSuit, playersWithCards, attacker, roundNumber)
            sleep(2)
            roundNumber += 1
        
        # If at the end of the game the players have no cards left
        elif len(playersWithCards) == 0:
            print('Nobody is Durak!')
            break

        # The last player with cards lost
        else:
            if playersWithCards[0].who == 'human':
                print(greenBoldMessage('\n\nYou are Durak!\n\n'))
            else:
                print(greenBoldMessage(f'{playersWithCards[0].name} is Durak!\n\n'))
            break
    
    
p1 = Player('Giga', 'human')
p2 = Player('AI1', 'ai')
p3 = Player('AI2', 'ai')
p4 = Player('AI3', 'ai')
p5 = Player('AI4', 'ai')

players = []
players.append(p1)
players.append(p2)
# players.append(p3)
# players.append(p4)
# players.append(p5)

startGame(players)
