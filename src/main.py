import os

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()
    print(os.environ['API_KEY'])
    response = requests.get("http://localhost")
    print(response.text)


if __name__ == '__main__':
    main()
