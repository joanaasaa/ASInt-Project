from termcolor import colored, cprint


def log2term(type: str, msg: str):
    """Prints log messages to the terminal according to their importance.

    Args:
        type (str): Letter that indicates the type of log message 
            according to its importance. 
            There are 5 types of log messages:
                * F (FATAL) 
                * E (ERROR)
                * W (WARNING) 
                * I (INFO)
                * D (DEBUG)
        msg (str): Log mesage that is to be printed out to the terminal
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
