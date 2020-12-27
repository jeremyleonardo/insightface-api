import logging
import app.settings as settings

filename = "main"

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="{asctime} {levelname:<8}: {message}",
    style='{',
    filename='%s.log' % filename,
    filemode='w'
)


def debug(message):
    print(f"{bcolors.OKCYAN}DEBUG:   {bcolors.ENDC}", message)
    logging.debug(message)


def info(message):
    print(f"{bcolors.OKGREEN}INFO:    {bcolors.ENDC}", message)
    logging.info(message)


def error(message):
    print(f"{bcolors.FAIL}ERROR:   {bcolors.FAIL}", message)
    logging.error(message)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'