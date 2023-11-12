import requests

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urljoin


class BaseCrawler:
    def __init__(self, base_url, crawl_external=False, external_crawl_depth=2, headers=None, parser='bs4'):
        self.base_url = base_url
        self.url_list = set()
        self.adjacency_list = {}
        self.crawl_external = crawl_external
        self.external_crawl_depth = external_crawl_depth
        self.headers = headers
        self.parser = parser

        if parser not in ['bs4', 'playwright']:
            raise ValueError('parser must be bs4 or playwright')

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
    def __init__(self, base_url, crawl_external=False, external_crawl_depth=2, headers=None, parser='bs4', limit=None):
        super().__init__(base_url, crawl_external, external_crawl_depth, headers, parser)
        self.limit = limit

    def _get_urls_playwright(self, page, url):
        page.goto(url)
        # Select all <a> tags with href attribute
        hrefs = page.query_selector_all("//a[@href]")
        urls = [href.get_attribute('href') for href in hrefs]
        urls = [urljoin(url, href) for href in urls]
        urls = [href for href in urls if not self._is_image(href)]
        urls = [href.strip('/') for href in urls]
        return urls

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

    def _run_playwright(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            crawled_urls = set()
            current_external_crawl_depth = 0
            queue = [self.base_url]
            count = 0

            while queue:
                if self.limit and count >= self.limit:
                    break

                url = queue.pop()
                if url in crawled_urls:
                    continue

                crawled_urls.add(url)
                self.url_list.add(url)

                try:
                    page_urls = self._get_urls_playwright(page, url)
                    self.adjacency_list[url] = page_urls
                except:
                    continue

                for page_url in page_urls:
                    if self._is_internal_url(page_url):
                        queue.append(page_url)
                    elif self.crawl_external and current_external_crawl_depth < self.external_crawl_depth:
                        queue.append(page_url)
                        current_external_crawl_depth += 1
                    else:
                        self.url_list.add(page_url)
                        self.adjacency_list[page_url] = []

                count += 1

            browser.close()

    def run(self):
        if self.parser == 'playwright':
            self._run_playwright()
            return

        crawled_urls = set()
        current_external_crawl_depth = 0
        queue = [self.base_url]
        count = 0

        while queue:
            if self.limit and count >= self.limit:
                break

            url = queue.pop()
            if url in crawled_urls:
                continue

            crawled_urls.add(url)
            self.url_list.add(url)

            try:
                page_urls = self._get_urls(url)
                self.adjacency_list[url] = page_urls
            except:
                continue

            for page_url in page_urls:
                if self._is_internal_url(page_url):
                    queue.append(page_url)
                elif self.crawl_external and current_external_crawl_depth < self.external_crawl_depth:
                    queue.append(page_url)
                    current_external_crawl_depth += 1
                else:
                    self.url_list.add(page_url)
                    self.adjacency_list[page_url] = []

            count += 1


class ImageCrawler(UrlCrawler):
    def __init__(self, base_url, crawl_external=False, external_crawl_depth=2, headers=None, parser='bs4', limit=None):
        super().__init__(base_url, crawl_external,
                         external_crawl_depth, headers, parser, limit)
        self.image_list = []

    def _get_image_info_playwright(self, page, url):
        image_list = []
        page.goto(url)

        # Select all image elements
        images = page.query_selector_all('img')

        for image in images:
            src = image.get_attribute('src')
            alt = image.get_attribute('alt')
            width = image.get_attribute('width')
            height = image.get_attribute('height')
            image_format = src.split('.')[-1]
            self.image_list.append({'src': src, 'alt': alt, 'width': width,
                                    'height': height, 'format': image_format, 'from': url})

        return image_list

    def _get_image_info(self, url):
        image_list = []
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for img in soup.find_all('img'):
            src = urljoin(self.base_url, img.get('src'))
            matching_src = any([src == image['src']
                               for image in self.image_list])
            if matching_src:
                continue

            alt = img.get('alt')
            width = img.get('width')
            height = img.get('height')
            image_format = src.split('.')[-1]
            image_list.append({'src': src, 'alt': alt, 'width': width,
                              'height': height, 'format': image_format, 'from': url})
        return image_list

    def _run_playwright(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            crawled_urls = set()
            current_external_crawl_depth = 0
            queue = [self.base_url]
            count = 0

            while queue:
                if self.limit and count >= self.limit:
                    break

                url = queue.pop()
                if url in crawled_urls:
                    continue

                crawled_urls.add(url)
                self.url_list.add(url)

                try:
                    page_images = self._get_image_info_playwright(page, url)
                    self.image_list.extend(page_images)
                except:
                    continue

                try:
                    page_urls = self._get_urls_playwright(page, url)
                    self.adjacency_list[url] = page_urls
                except:
                    continue

                for page_url in page_urls:
                    if self._is_internal_url(page_url):
                        queue.append(page_url)
                    elif self.crawl_external and current_external_crawl_depth < self.external_crawl_depth:
                        queue.append(page_url)
                        current_external_crawl_depth += 1
                    else:
                        self.url_list.add(page_url)
                        self.adjacency_list[page_url] = []

                count += 1

            browser.close()

    def run(self):
        if self.parser == 'playwright':
            self._run_playwright()
            return

        crawled_urls = set()
        current_external_crawl_depth = 0
        queue = [self.base_url]
        count = 0

        while queue:
            if self.limit and count >= self.limit:
                break

            url = queue.pop()
            if url in crawled_urls:
                continue

            crawled_urls.add(url)
            self.url_list.add(url)

            try:
                page_images = self._get_image_info(url)
                self.image_list.extend(page_images)
            except:
                continue

            try:
                page_urls = self._get_urls(url)
                self.adjacency_list[url] = page_urls
            except:
                continue

            for page_url in page_urls:
                if self._is_internal_url(page_url):
                    queue.append(page_url)
                elif self.crawl_external and current_external_crawl_depth < self.external_crawl_depth:
                    queue.append(page_url)
                    current_external_crawl_depth += 1
                else:
                    self.url_list.add(page_url)
                    self.adjacency_list[page_url] = []

            count += 1
