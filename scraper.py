import asyncio
from bs4 import BeautifulSoup
import aiohttp
from typing import Optional, Dict, Any, Union, List
from proxy_list import  get_random_proxy, get_proxies
from fake_useragent import UserAgent


async def scrape_url(session: aiohttp.ClientSession, url: str, proxy: Optional[str], to_scrape: Dict[str, Any]) -> \
        Union[int, Dict[str, Any]]:
    """
    Scrape the given URL using the specified selector (CSS or XPath) and return the scraped data.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        url (str): The URL to scrape.
        proxy (Optional[str]): The proxy to be used for the request.
        to_scrape (Dict[str, Any]): The scraping configuration containing the selector and data extraction details.

    Returns:
        Union[int, Dict[str, Any]]: The scraped data if successful, or the HTTP status code if the request fails.
    """
    timestamp, proxy_list = get_proxies()
    for i in range(3):
        try:
            proxy = get_random_proxy(proxy_list)
            async with session.get(url, proxy=proxy, headers={'User-Agent': UserAgent().random}) as response:
                print(response.status)
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    data = {}

                    if 'payload' in to_scrape:
                        payload = to_scrape['payload']
                        if isinstance(payload, list):
                            data = scrape_data(soup, payload)
                        else:
                            raise ValueError("Invalid payload format. Must be a list of payload objects.")
                    else:
                        raise ValueError("Payload not provided in 'to_scrape'.")

                    to_scrape['result'] = data
                    return to_scrape
                else:
                    return response.status
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            if i == 2:
                return e
            else:
                await asyncio.sleep(5)
                proxy = get_random_proxy(proxy_list)


def scrape_data(soup: BeautifulSoup, payload: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scrape the data from the BeautifulSoup object using CSS or XPath selectors.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
        payload (List[Dict[str, Any]]): The list of payload objects containing the selector type (css or xpath),
            the selector value, and the name.

    Returns:
        Dict[str, Any]: The scraped data.
    """
    data = {}
    for item in payload:
        selector_type = item.get('type')
        selector_value = item.get('selector')
        name = item.get('name')

        if selector_type == 'css':
            data[name] = [element.text for element in soup.select(selector_value)]
        elif selector_type == 'xpath':
            elements = soup.select(selector_value)
            data[name] = [element.text.strip() for element in elements]
        else:
            raise ValueError("Invalid selector type. Must be either 'css' or 'xpath'.")
    return data

def scrape_css(soup: BeautifulSoup, selectors: List[str], names: List[str]) -> Dict[str, Any]:
    """
    Scrape the data from the BeautifulSoup object using CSS selectors.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
        selectors (List[str]): The list of CSS selectors to extract data from.
        names (List[str]): The list of names to assign to the extracted data.

    Returns:
        Dict[str, Any]: The scraped data.
    """
    data = {}
    for css_selector, name in zip(selectors, names):
        data[name] = [element.text for element in soup.select(css_selector)]
    return data


def scrape_xpath(html_text: str, xpaths: List[str], names: List[str]) -> Dict[str, Any]:
    """
    Scrape the data from the HTML using XPath expressions.

    Args:
        html_text (str): The HTML content as a string.
        xpaths (List[str]): The list of XPath expressions to extract data from.
        names (List[str]): The list of names to assign to the extracted data.

    Returns:
        Dict[str, Any]: The scraped data.
    """
    tree = html.fromstring(html_text)
    data = {}
    for xpath_expression, name in zip(xpaths, names):
        elements = tree.xpath(xpath_expression)
        data[name] = [element.text_content().strip() for element in elements]
    return data