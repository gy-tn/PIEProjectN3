"""
This file contains the function for coloring output messages
Just for aesthetic beauty
"""
from termcolor import colored


def greenBoldMessage(text:str) -> str:
    """
    Returns green and bold text
    """
    return colored(text, 'green', attrs=['bold'])


def greenMessage(text: str) -> str:
    """
    Returns green text
    """
    return colored(text, 'green')


def redMessage(text: str) -> str:
    """
    Returns red text
    """
    return colored(text, 'red')


def redBoldMessage(text: str) -> str:
    """
    Returns white text on red background
    """
    return colored(text, 'red', attrs=['bold'])
