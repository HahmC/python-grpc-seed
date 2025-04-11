import logging
import socket

class Logger(logging.LoggerAdapter):
    """
    Custom LoggerAdapter to inject extra context into log messages
    """
    def __init__(self, config):
        extra = {
            'server_name': socket.gethostname()
        }
        super().__init__(self.__get_logger(config), extra)

    @staticmethod
    def __get_logger(config):
        """
        Returns a logger configured to the specifications of the config.ini file

        Date Format: %Y-%m-%d %H:%M:%S
        """
        logger = logging.getLogger(config['logging']['logger_name'])
        logger.setLevel(config['logging']['level'].upper())
        formatter = logging.Formatter(
            config['logging']['format'],
            datefmt="%Y-%m-%d %H:%M:%S",
            style='{'
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(config['logging']['level'].upper())
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        return logger