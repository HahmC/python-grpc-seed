def get_methods(methods) -> str:
    """
    Takes a list of methods and returns them in the format below:

    [F] - FirstMethod
    [S] - SecondMethod
    .
    .
    .

    :param methods: list of method
    :return: formatted method string
    """
    method_string: str = ''

    for m in methods:
        method_string += f"\n[{m.upper()}] - {methods[m]} "

    method_string = method_string.rstrip()

    return method_string