import configparser

def get_config():
    config = configparser.ConfigParser(interpolation=None)
    config.read('config.ini')

    return config