import logging as log
from pprint import pformat

GOT_LOGGER = False

def get_logger():
    "Helper function to get the logger"
    global GOT_LOGGER
    if GOT_LOGGER:
        return log
    GOT_LOGGER = True
    logger = log.getLogger()
    logger.setLevel(log.DEBUG)
    ch = log.StreamHandler()
    ch.setFormatter(log.Formatter('%(levelname)s: %(message)s'))
    logger.removeHandler(0)
    logger.addHandler(ch)
    return log