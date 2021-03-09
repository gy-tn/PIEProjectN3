from flask import Flask, request, make_response
import requests
from deck import deck
from random import shuffle
import json
from time import sleep


class Player:
    def __init__(self, name:str, url:str, hand:list=[], status:str='client'):
        self.name = name
        self.hand = hand
        self.status = status
        self.url = url
    
    def __str__(self):
        return f'My name is {self.name} and url is {self.url}'
    

# Players list is used for storing players
registeredPlayers = []



def registerPlayer(name:str, url:str, players:list) -> dict:
    """
    This function creates players
    """
    players.append(Player(name, url))
    # Give status "host" to the first registered player
    if len(players) == 1:
        players[0].status = 'host'
    message = {
        'status': 'info',
        'content': f'You are registered under the nickname {name}!\n'
    }

    return message


def formMessageAboutRegisteredPlayers(players:list) -> dict:
    """
    Forms information message to send after every player registration
    """
    msgContent = 'Registered players:\n'
    for number in range(len(players)):
        msgContent += f'{number + 1}. {players[number].name} - {players[number].status}\n'
    message = {
        'status': 'info',
        'content': f'{msgContent}\n'
    }
    return message


app = Flask(__name__)


@app.route('/')
def hello():
    """
    This route is used by the client to check whether the Durak server is running
    """
    return 'Hello!'


@app.route('/attempt', methods=['POST'])
def attempt():
    """
    Performs to checks:
    1. Are there any available seats
    2. Is the nickname of the new player unique
    3. Does the client connect from an address already used by another client
    The response is processed on the client side
    """
    if len(registeredPlayers) < 6:
        # URLs list is used for storing players URLs
        registeredURLs = []
        # List with registered players names
        registeredNames = []
        url = request.args.get('url') # This url is ipaddress of registering player device
        name = request.args.get('name') # This name sent by the registering player
        for player in registeredPlayers:
            registeredURLs.append(player.url)
            registeredNames.append(player.name)
        if url in registeredURLs:
            return 'repeatedURL'
        elif name in registeredNames:
            return 'repeatedName'
        else:
            return 'Welcome!'
    else:
        return 'noSeats'


@app.route('/player', methods=['GET', 'POST'])
def createPlayer():
    """
    Creates a new player
    """
    name = request.args.get('name') # This name sent by the registering player
    url = request.args.get('url') # This url is ipaddress of registering player device
    # Try to register the new player
    registrationMessage = registerPlayer(name, url, registeredPlayers)
    # Send answer to registration request
    requests.post(url, json.dumps(registrationMessage))
    # Send information about registered players to already registered players
    messageAboutRegisteredPlayers = formMessageAboutRegisteredPlayers(registeredPlayers)
    for player in registeredPlayers:
        try:
            requests.post(player.url, json.dumps(messageAboutRegisteredPlayers))
            if player.status == 'host':
                messageToHost = {
                    'status': 'host',
                    'content': 'You are the host of this game.\n' +
                        'You can start the game typing "start" command.\n'       
                }
                requests.post(player.url, json.dumps(messageToHost))
        except requests.exceptions.ConnectionError:
            pass
    return 'Hello!'


@app.route('/start')
def startGame():
    print('Start Game')
    return 'Hello!'


if __name__ == '__main__':
    app.run()
