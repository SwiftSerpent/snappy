import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class BaseCrawler:
    def __init__(self, base_url, crawl_external=False, external_crawl_depth=2, headers=None):
        self.base_url = base_url
        self.url_list = set()
        self.adjacency_list = {}
        self.crawl_external = crawl_external
        self.external_crawl_depth = external_crawl_depth
        self.headers = headers
    
    @property
    def internal_urls(self):
        return [url for url in self.url_list if self._is_internal_url(url)]

    @property
    def external_urls(self):
        return [url for url in self.url_list if not self._is_internal_url(url)]

    def _is_internal_url(self, url):
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    def _is_image(self, url):
        return url.endswith(('.jpg', '.jpeg', '.png', '.gif'))
    
    def run(self):
        raise NotImplementedError
    
    def __repr__(self):
        return f'<{self.__class__.__name__} base_url={self.base_url}>'
    
    def __str__(self):
        return self.__repr__()
    
    def __len__(self):
        return len(self.url_list)
    
    def __iter__(self):
        return iter(self.url_list)
    
    def __getitem__(self, index):
        return list(self.url_list)[index]
    
    def __contains__(self, url):
        return url in self.url_list


class UrlCrawler(BaseCrawler):
    def _get_urls(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        hrefs = []
        for link in soup.find_all('a'):
            hrefs.append(link.get('href'))
        hrefs = [href for href in hrefs if href]
        hrefs = [urljoin(url, href) for href in hrefs]
        hrefs = [href for href in hrefs if not self._is_image(href)]
        hrefs = [href.strip('/') for href in hrefs]
        return hrefs

    def run(self):
        crawled_urls = set()
        current_external_crawl_depth = 0
        queue = [self.base_url]

        while queue:
            url = queue.pop()
            if url in crawled_urls:
                continue

            try:
                page_urls = self._get_urls(url)
                self.adjacency_list[url] = page_urls
            except:
                continue
            finally:
                crawled_urls.add(url)
                self.url_list.add(url)

            for page_url in page_urls:
                if self._is_internal_url(page_url):
                    queue.append(page_url)
                elif self.crawl_external and current_external_crawl_depth < self.external_crawl_depth:
                    queue.append(page_url)
                    current_external_crawl_depth += 1
                else:
                    self.url_list.add(page_url)
                    self.adjacency_list[page_url] = []