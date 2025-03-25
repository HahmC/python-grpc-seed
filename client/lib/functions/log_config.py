import logging

def log_config(logger, config):
    logger.info("App Configuration...")

    for section in config.sections():
        logger.info("['{}']".format(section))

        for key, value in config.items(section):
            if key == "format" and section == "logging":
                continue
            else:
                logger.info("'{}': '{}'".format(key, value))