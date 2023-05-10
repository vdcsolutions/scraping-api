import requests
import configparser
import logging
import random
from typing import List


logging.basicConfig(filename='get_proxy_list.log', level=logging.DEBUG)


def get_from_api(api_url: str) -> dict:
    """
    Fetches data from the specified API URL.

    Args:
        api_url (str): The URL of the API to fetch data from.

    Returns:
        dict: JSON response from the API.
    """
    # Send a GET request to the API
    response = requests.get(api_url)

    # Check if the response was successful
    if response.status_code != 200:
        raise Exception('API response not successful')
        logging.debug('API response not successful')

    # Get the data from the response
    data = response.json()

    return data


def get_timestamp(data: List[dict]) -> str:
    """
    Retrieves the timestamp from the provided data.

    Args:
        data (List[dict]): List of dictionaries containing data.

    Returns:
        str: The timestamp value.
    """
    try:
        timestamp = data[0]['timestamp']
    except IndexError:
        logging.debug('There is no timestamp in the downloaded JSON')
        timestamp = ''

    return timestamp


def get_proxies_from_json(data: List[dict]) -> List[str]:
    """
    Extracts proxy URLs from the provided data.

    Args:
        data (List[dict]): List of dictionaries containing proxy data.

    Returns:
        List[str]: List of proxy URLs.
    """
    urls = []
    for d in data:
        url = f"http://{d['ip']}:{d['port']}"
        urls.append(url)

    return urls


def get_proxies() -> tuple:
    """
    Retrieves the timestamp and proxy URLs from the API.

    Returns:
        tuple: A tuple containing the timestamp and a list of proxy URLs.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')

    data = get_from_api(config.get('PRODUCTION', 'proxy_api_url'))
    timestamp = get_timestamp(data)
    urls = get_proxies_from_json(data)
    return timestamp, urls


def get_random_proxy(proxy_list: List[str]) -> str:
    """
    Returns a random proxy URL from the provided list.

    Args:
        proxy_list (List[str]): List of proxy URLs.

    Returns:
        str: A randomly selected proxy URL.
    """
    proxy = random.choice(proxy_list)
    return proxy


if __name__ == '__main__':
    timestamp, urls = get_proxies()
    print(timestamp)
    print(urls)
