import lib.functions as helpers
from lib.shape_client import ShapeClient

async def get_method_choice(methods, client: ShapeClient):
    """
    Prompt the user for which gRPC method they would like to run

    :param methods: Available methods to call
    :param client: gRPC client object used for method execution
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
        await client.create_shape()
    elif fxn == 'G':
        print()
        print()
        print("Welcome to GetShape!")
        await client.get_shape()
    elif fxn == 'P':
        print()
        print()
        print("Welcome to GetPerimetersGreaterThan!")
        await client.get_perimeters_greater_than()
    elif fxn == 'T':
        print()
        print()
        print("Welcome to GetTotalArea!")
        await client.get_total_area()
    elif fxn == 'A':
        print()
        print()
        print("Welcome to GetAreas!")
        await client.get_areas()
    elif fxn == 'E':
        exit()
    else:
        print('Please choose a valid function:')

        # Reset to beginning choice
        print()
        print()
        await get_method_choice(methods, client)

    # Loop back to beginning of choice once successfully completing a method
    print()
    print()
    await get_method_choice(methods, client)