import sys
import logging

# exception logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

"""

Make sw diagram before proceeding!!

"""


def print_h():
    print('Hello')
    raise TypeError


def exception_hook(exc_type, exc_value, exc_traceback):
    # ignore keyboard interruptions "ctrl + c"
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # log uncaught errors to file
    logging.basicConfig(filename="CrashLog.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == '__main__':
    sys.excepthook = exception_hook  # uncomment if no hook is needed. Running Pycharm on debugger mode disables hook.

    print_h()

