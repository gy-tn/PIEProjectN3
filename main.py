"""
This is the main file of the Durak game program.
It interacts with user and executes the necessary files.
"""
from colorText import *
from os import get_terminal_size


def selectMode() -> str:
    """
    Prints message about available game modes.
    Asks the user to select a mode.
    Returns selected mode.
    """
    # Tell the user about game modes
    print(greenMessage(
        'Please choose a game mode:\n' + 
        '1. Against the computer\n' +
        '2. Create the Durak server for networking game\n' +
        '3. Connect to the Durak server for networking game\n' +
        '("q" to exit the program)\n'))

    # User inputs his choice
    choice = input(greenMessage('\nYour choice: '))

    # Handling user input
    while True:
        if choice.lower() not in ['1', '2', '3', 'q']:
            choice = input(redMessage('Type "1", "2", "3" or "q" only: '))
        else:
            return choice.lower()


def checkWindowSize() -> bool:
    """
    Checks for the size of terminal window of the player
    """
    width, height = get_terminal_size(0)
    if width < 50 or height < 26:
        return False
    return True


def main():
    # Check that the size of the user's terminal window is large enough for comfortable game
    if not checkWindowSize():
        print(redBoldMessage(
            'The size of your terminal window is not large enough for a comfortable gameplay.\n' +
            'Please increase the terminal window size or decrease the font size and restart the application.'))
        return None

    # Say hi to the user
    print(greenBoldMessage('Welcome to the Durak game!'))
    print('\n') #Formatting output

    # User choose a game mode
    gameMode = selectMode()

    # Handle user input
    if gameMode == 'q':
        print(greenBoldMessage('\nGoodbye!'))
    elif gameMode == '1':
        pass
    elif gameMode == '2':
        pass
    else:
        pass


main()