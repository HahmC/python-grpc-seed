import lib.functions as helpers
from .create_shape import create_shape
from .get_shape import get_shape

def get_method_choice(methods, stub):
    """
    Prompt the user for which gRPC method they would like to run

    :param methods: Available methods to call
    :param stub: gRPC stub for method execution
    :return: None
    """

    method_string: str = f"Choose a method to run: {helpers.get_methods(methods)}"

    print(method_string)

    # Get user choice
    fxn: str = input('Enter the method you would like to use: ')
    fxn = fxn.upper()

    if fxn == 'C':
        print()
        print()
        print("Welcome to CreateShape!")
        create_shape(methods, stub)
    elif fxn == 'G':
        print()
        print()
        print("Welcome to GetShape!")
        get_shape(stub)
    elif fxn == 'E':
        exit()
    else:
        print('Please choose a valid function:')

        # Reset to beginning choice
        print()
        print()
        get_method_choice(methods, stub)

    # Loop back to beginning of choice once successfully completing a method
    print()
    print()
    get_method_choice(methods, stub)