
import os


def root_dir():
    root_dir = os.path.dirname(__file__)
    if __name__ == "__main__":
        root_dir = os.getcwd()
    root_dir += "/static/"
    return os.path.abspath(root_dir)

from .flask_server import run_flask_socket_app
