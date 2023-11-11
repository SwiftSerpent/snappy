import requests

from bs4 import BeautifulSoup


def get_hrefs_from_url(url, class_name=None, http_only=False):
    """
    Returns a list of all hrefs from a url.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    hrefs = []
    for link in soup.find_all('a'):
        if class_name:
            if class_name in link.get('class', []):
                hrefs.append(link.get('href'))
        else:
            hrefs.append(link.get('href'))
    if http_only:
        hrefs = [href for href in hrefs if href.startswith('http')]
    return hrefs


def split_internal_and_external_urls(base_path, link_list):
    """
    Returns a list of internal and external urls.
    """
    internal_urls = set()
    external_urls = set()
    for link in link_list:
        if link.startswith(base_path):
            internal_urls.add(link)
        else:
            external_urls.add(link)
    return internal_urls, external_urls


def is_image(url):
    """
    Returns True if url ends with .jpg, .jpeg, .png, or .gif.
    """
    return url.endswith(('.jpg', '.jpeg', '.png', '.gif'))
