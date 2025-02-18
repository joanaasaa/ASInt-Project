#!/usr/bin/env python3
"""
Aux
===

This file provides useful functions and classes which are 
used by the app's backend.
"""

from enum import Enum
from termcolor import colored
from termcolor import cprint


class ServerConfig:
    """Class to save and interact with teh flask servers'
    information.
    """
    def __init__(self, addr: str, port: int):
        self.addr = addr
        self.port = port

    def set(self, addr: str, port: int):
        """Method to set the server's port and IP address.

        Parameters
        ----------
        addr : str
            The server's IP address.
        port : int
            The port where the server is working.
        """
        self.addr = addr
        self.port = port


class EventType(Enum):
    """Class used to categorize the types of communications 
    between the system's members, which can be logged. 
    
    A communication between the system's users and servers 
    is, therefore, considered to be an event.
    """
    GET_USER = 1
    GET_ADMIN = 2
    GET_USERS_ADMINS = 3
    GET_USERSTATS = 4
    GET_VIDEO = 5
    GET_QAS = 6
    GET_ALL_LOGS = 7
    PUT_VIEW = 8
    PUT_VIDEO_VIEW = 9
    PUT_USERSTATS_VIDEO = 10
    PUT_USERSTATS_VIEW = 11
    PUT_USERSTATS_QUESTION = 12
    PUT_USERSTATS_ANSWER = 13
    POST_NEW_USER = 14
    POST_NEW_ADMIN = 15
    POST_NEW_VIDEO = 16
    POST_NEW_QUESTION = 17
    POST_NEW_ANSWER = 18


def log2term(type: str, msg: str):
    """log2term Prints log messages to the terminal according to their importance.

    Parameters
    ----------
    type : str
        Letter that indicates the type of log message according to its importance. 
        There are 5 types of log messages:
            * F (FATAL) 
            * E (ERROR)
            * W (WARNING) 
            * I (INFO)
            * D (DEBUG)
    msg : str
        Log mesage that is to be printed out to the terminal
    """

    if (type == 'F'):
        string = f'F    {msg}'
        pretty_string = colored(string, 'grey', 'on_red')
        print(pretty_string)

    elif (type == 'E'):
        string = f'E    {msg}'
        pretty_string = colored(string, 'red')
        print(pretty_string)

    elif (type == 'W'):
        string = f'W    {msg}'
        pretty_string = colored(string, 'yellow')
        print(pretty_string)

    elif (type == 'I'):
        string = f'I    {msg}'
        pretty_string = colored(string, 'green')
        print(pretty_string)

    elif (type == 'D'):
        string = f'D    {msg}'
        pretty_string = colored(string, 'cyan')
        print(pretty_string)

    else:
        print(msg)
