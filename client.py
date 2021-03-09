from flask import Flask, request
from termcolor import colored
import requests
from os import get_terminal_size
from socket import gethostbyname, gethostname, timeout
from ipaddress import ip_address
from time import sleep
import json
import threading
import logging




def checkWindowSize() -> bool:
    """
    Checks for the size of terminal window of the player
    """
    width, height = get_terminal_size(0)
    if width < 50 or height < 26:
        return False
    return True


def askName() -> str:
    """
    Asks for the nickname of the player
    """

    # Asking for the player's name
    name = input(colored('Please enter your nickname: ', 'green', attrs=['bold']))

    # Creating the player's name from "Player" word and the last number of IP Address of
    # the player's device (was tested only with IPv4) if the name was not provided
    if not name:
        digit = gethostbyname(gethostname()).split('.')[-1]
        name = f'Player{digit}'
    
    # Shorten the player's name to 15 characters
    if len(name) > 15:
        name = name[:14] + '~'

    return name


def askForGameMode() -> int:
    """
    Asks the player for the game mode he wants to play
    """
    print(colored('Please choose a game mode:', 'green', attrs=['bold']))
    print(colored('1. Against the computer\n2. Over the network', 'green', attrs=['bold']))
    while True:
        answer = input()
        if answer == '1' or answer == '2':
            return int(answer)
        else:
            print(colored('Enter "1" or "2" please:', 'white', 'on_red') + ' ', end='')


def connectToIPAddress():
    """
    Asks for the IP Address of the server with the game and checks it for correctness
    Then tries to establish a connection
    """
    print(colored('Please enter IP Address of the server ' + \
        'with the "Durak" game\nand port number if needed (5000 is default) ',
        'green', attrs=['bold']) + '("q" for exit): ', end ='')
    while True:

        # Waiting for player's input
        addressPort = input()

        # Exit the game if "q" was entered
        if addressPort == 'q':
            return False

        # Handle player's input
        if ':' in addressPort: # If the player entered "ipaddress:port" 
            address = addressPort.split(':')[0]
            port = addressPort.split(':')[-1]
        else: # If the player entered "ipaddress" only
            address = addressPort
            port = '5000'
        if not port.isnumeric(): # Check for validness of port number
            print(colored(f'{address}:{port} doesn\'t look like a valid IP address. Try again:',
                'white', 'on_red') + ' ', end='')
        elif int(port) < 0 or int(port) > 65536: # Check for validness of port number
            print(colored(f'{address}:{port} doesn\'t look like a valid IP address. Try again:',
                'white', 'on_red') + ' ', end='')
        else:
            try: # Check for validness of "ipaddress"
                ip_address(address)
                url = f'http://{address}:{port}/'
                try: # Try to create connection to valid IP Address
                    requests.get(url, timeout=2)
                    return url
                except requests.exceptions.ConnectTimeout: # If wrong IP Address
                    print(colored(f'No connection to {address}:{port}. Check if you entered ' +
                        'the correct IP address or server is running:', 'white', 'on_red') + ' ', end='')
                except requests.exceptions.ConnectionError: # If wrong port number
                    print(colored(f'Connection to {address}:{port} refused. Check if you entered ' +
                        'the correct port number or server is running:', 'white', 'on_red') + ' ', end='')
            except ValueError: # If "ipaddress" invalid
                print(colored(f'{address}:{port} doesn\'t look like a valid IP address. Try again:',
                    'white', 'on_red') + ' ', end='')


def main():

    # Checking if the current terminal window size is comfortable for gameplay
    if not checkWindowSize():
        print(colored('The size of your terminal window is not large enough ' + \
            'for a comfortable gameplay.', 'white', 'on_red'))
        print(colored('Please increase the terminal window size or decrease ' + \
            'the font size and restart the application.', 'white', 'on_red'))
        return None

    print('\n') # Formatting output

    # Printing a greeting
    print(colored('Welcome to the "Durak" game', 'green', attrs=['bold']) + '\n')

    # Asking for the game mode
    mode = askForGameMode()
    if mode == 1: # Start the game against computer
        startGameAgainstComputer()
    else: # Ask for IP Address of the server with the game
        print('\n') # Formatting output

        serverURL = connectToIPAddress()

        # Exit the game if the player entered "q" instead of IP Address
        if not serverURL:
            print('\n' + colored(f'Good Bye {name}!', 'green', attrs=['bold']) + '\n')
            return None
        
        print('\n') # Formatting output

        # Printing a greeting and asking for the player's name
        name = askName()

        print('\n') # Formatting output
        
        # Start the game over network
        startNetworkGame(serverURL, name)


def startGameAgainstComputer():
    """
    This function starts the game against the computer
    """
    pass


def startNetworkGame(url, name):
    """
    This function starts the network game.
    """

    app = Flask(__name__)

    # Disable flask log messages
    # log = logging.getLogger('werkzeug')
    # log.disabled = True


    @app.route('/', methods=['GET', 'POST'])
    def hello():
        """
        Accepts and processes messages from the server
        """
        receivedMessage = request.get_json(force=True)
        if receivedMessage['status'] == 'info':
            print(colored(receivedMessage['content'], 'green'))
        elif receivedMessage['status'] == 'host':
            print(colored(receivedMessage['content'], 'green'))
        return 'Hello!'


    # This was used to emulate devices with different IP addresses  
    port = '4999'
    myURL = f'http://127.0.0.1:{port}/'

    # myIP = gethostbyname(gethostname()
    # myURL = f'http://{myIP}:{port}/'

    # Send a request to the server for checking possibility of registration
    # (there are available seats and our address is not used)
    attempt = requests.post(f'{url}attempt', params={'name': name, 'url': myURL})

    # If our address in use by someone
    if attempt.text == 'repeatedURL':
        print(colored('It looks like Durak client is already running on this device.\n' +
            'Or you are testing my app!', 'red'))
        return None
    
    # If our nickname in use by someone
    elif attempt.text == 'repeatedName':
        while attempt.text == 'repeatedName':
            name = input(colored(f'The nickname {name} is already in use, think of another one:' + ' ',
                'red', attrs=['bold']))
            if len(name) > 15:
                name = name[:14] + '~'
            attempt = requests.post(f'{url}attempt', params={'name': name, 'url': myURL})
    
    # If there are no available seats
    elif attempt.text == 'noSeats':
        print(colored(f'Sorry, {name}, but all six seats are occupied.\n', 'red') +
            colored('Try to find another server or create your own durak server!', 'green'))
        return None
    
    # If the server can register us
    # Start client's flask application for listening messages from server
    clientListener = threading.Thread(target=app.run, kwargs={'port':port})
    clientListener.start()

    # Send our name and url for registering
    register = requests.post(f'{url}player', params={'name': name, 'url': myURL})

# Start the programm
main()