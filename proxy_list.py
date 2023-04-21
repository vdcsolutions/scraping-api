import requests
import configparser
import logging
import random

logging.basicConfig(filename='get_proxy_list.log', level=logging.DEBUG)

# Log a message
logging.debug('This is a debug message')

config = configparser.ConfigParser()

config.read('config.ini')


def get_from_api(api_url):
    # Send a GET request to the API
    response = requests.get(api_url)

    # Check if the response was successful
    if response.status_code != 200:
        raise Exception('API response not successful')
        logging.debug('API response not successful')

    # Get the data from the response
    data = response.json()

    return data

def get_timestamp(data):
    try:
        timestamp = data[0]['timestamp']
    except:
        logging.debug('There is no timestamp in downloaded json')
    return timestamp

def get_proxies_from_json(data):
    urls = []
    for d in data:
        url = f"http://{d['ip']}:{d['port']}"
        urls.append(url)

    return urls


def get_proxies():
    data = get_from_api(config.get('PRODUCTION','proxy_api_url'))
    timestamp = get_timestamp(data)
    urls = get_proxies_from_json(data)
    return timestamp, urls

def get_random_proxy(proxy_list):
    proxy = random.choice(proxy_list)
    return proxy

if __name__ == '__main__':
    timestamp, urls = get_data()
    print(timestamp)
    print(urls)