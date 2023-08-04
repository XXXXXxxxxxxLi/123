from pywebio import start_server
from login import login
from upload import upload_images


def main():
    login()
    upload_images()


if __name__ == "__main__":
    start_server(main, port=5004)
