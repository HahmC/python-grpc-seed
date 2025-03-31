import json

def get_grpc_config(filepath: str):
    """
    Attempts to retrieve the gRPC config for the server client if it exists

    :param filepath: Location of the gRPC client config JSON file
    :return: client config | None
    """
    try:
        with open(filepath, 'r') as config:
            return json.load(config)
    except IOError:
        return None