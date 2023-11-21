import asyncio
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urljoin


class BaseCrawler:
    """
    A base class for web crawlers.

    Attributes:
        base_url (str): The base URL to start crawling from.
        url_list (set): A set of URLs that have been crawled.
        adjacency_list (dict): A dictionary representing the adjacency list of the crawled URLs.
        crawl_external (bool): A flag indicating whether to crawl external URLs.
        external_crawl_depth (int): The maximum depth to crawl external URLs.
        headers (dict): A dictionary of headers to use for HTTP requests.
        parser (str): The parser to use for parsing HTML. Must be either 'bs4' or 'playwright'.
    """

    def __init__(self, base_url, crawl_external=False, external_crawl_depth=2, headers=None, parser='bs4'):
        """
        Initializes a new instance of the BaseCrawler class.

        Args:
            base_url (str): The base URL to start crawling from.
            crawl_external (bool): A flag indicating whether to crawl external URLs.
            external_crawl_depth (int): The maximum depth to crawl external URLs.
            headers (dict): A dictionary of headers to use for HTTP requests.
            parser (str): The parser to use for parsing HTML. Must be either 'bs4' or 'playwright'.

        Raises:
            ValueError: If the parser is not 'bs4' or 'playwright'.
        """
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
        """
        Returns a list of internal URLs that have been crawled.
        """
        return [url for url in self.url_list if self._is_internal_url(url)]

    @property
    def external_urls(self):
        """
        Returns a list of external URLs that have been crawled.
        """
        return [url for url in self.url_list if not self._is_internal_url(url)]

    def _is_internal_url(self, url):
        """
        Returns True if the given URL is internal to the base URL, False otherwise.
        """
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    def _is_pdf(self, url):
        """
        Returns True if the given URL is a PDF, False otherwise.
        """
        return url.endswith(('.pdf'))

    def _is_image(self, url):
        """
        Returns True if the given URL is an image, False otherwise.
        """
        return url.endswith(('.jpg', '.jpeg', '.png', '.gif'))

    async def run(self):
        """
        Runs the crawler.
        """
        raise NotImplementedError

    def __repr__(self):
        """
        Returns a string representation of the BaseCrawler instance.
        """
        return f'<{self.__class__.__name__} base_url={self.base_url}>'

    def __str__(self):
        """
        Returns a string representation of the BaseCrawler instance.
        """
        return self.__repr__()

    def __len__(self):
        """
        Returns the number of URLs that have been crawled.
        """
        return len(self.url_list)

    def __iter__(self):
        """
        Returns an iterator over the URLs that have been crawled.
        """
        return iter(self.url_list)

    def __getitem__(self, index):
        """
        Returns the URL at the given index in the list of crawled URLs.
        """
        return list(self.url_list)[index]

    def __contains__(self, url):
        """
        Returns True if the given URL has been crawled, False otherwise.
        """
        return url in self.url_list


class UrlCrawler(BaseCrawler):
    """
    A class for crawling URLs and building an adjacency list of internal and external links.

    Args:
        base_url (str): The starting URL to crawl.
        crawl_external (bool): Whether to crawl external links.
        external_crawl_depth (int): The maximum depth to crawl external links.
        headers (dict): Optional headers to include in requests.
        parser (str): The parser to use for parsing HTML. Either 'bs4' or 'playwright'.
        limit (int): The maximum number of URLs to crawl.

    Attributes:
        url_list (set): A set of all crawled URLs.
        adjacency_list (dict): An adjacency list of internal and external links.
    """

    def __init__(self, base_url, crawl_external=False, external_crawl_depth=2, headers=None, parser='bs4', limit=None):
        super().__init__(base_url, crawl_external, external_crawl_depth, headers, parser)
        self.limit = limit
    async def _get_urls_playwright(self, page, url):
        await page.goto(url)
        print(url)
        hrefs = await page.query_selector_all("//a[@href]")
        urls = [await href.get_attribute('href') for href in hrefs]
        urls = [urljoin(url, href) for href in urls]
        urls = [href for href in urls if not self._is_image(href)]
        urls = [href for href in urls if not self._is_pdf(href)]
        urls = [href.strip('/') for href in urls]
        return urls

    async def _get_urls(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                content = await response.text()

        soup = BeautifulSoup(content, 'html.parser')
        hrefs = [link.get('href') for link in soup.find_all('a')]
        hrefs = [urljoin(url, href) for href in hrefs]
        hrefs = [href for href in hrefs if not self._is_image(href)]
        hrefs = [href.strip('/') for href in hrefs]
        return hrefs

    async def _run_playwright(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
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
                    page_urls = await self._get_urls_playwright(page, url)
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

            await browser.close()

    async def run(self):
        if self.parser == 'playwright':
            await self._run_playwright()
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
                page_urls = await self._get_urls(url)
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
    """
    A class for crawling images from a given URL.

    Args:
    base_url (str): The URL to start crawling from.
    crawl_external (bool): Whether to crawl external URLs.
    external_crawl_depth (int): The maximum depth to crawl external URLs.
    headers (dict): A dictionary of headers to include in requests.
    parser (str): The parser to use for parsing HTML. Either 'bs4' or 'playwright'.
    limit (int): The maximum number of pages to crawl.

    Attributes:
    image_list (list): A list of dictionaries containing information about crawled images.
    """

    def __init__(self, base_url, crawl_external=False, external_crawl_depth=2, headers=None, parser='bs4', limit=None):
        super().__init__(base_url, crawl_external, external_crawl_depth, headers, parser, limit)
        self.image_list = []

    async def _get_image_info_playwright(self, page, url):
        image_list = []
        await page.goto(url)
        images = await page.query_selector_all('img')

        for image in images:
            src = await image.get_attribute('src')
            alt = await image.get_attribute('alt')
            width = await image.get_attribute('width')
            height = await image.get_attribute('height')
            image_format = src.split('.')[-1]
            self.image_list.append({'src': src, 'alt': alt, 'width': width, 'height': height, 'format': image_format, 'from': url})

        return image_list

    async def _get_image_info(self, url):
        image_list = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()

        soup = BeautifulSoup(content, 'html.parser')
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

    async def _run_playwright(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
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
                    page_images = await self._get_image_info_playwright(page, url)
                    self.image_list.extend(page_images)
                except:
                    continue

                try:
                    page_urls = await self._get_urls_playwright(page, url)
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

            await browser.close()

    async def run(self):
        if self.parser == 'playwright':
            await self._run_playwright()
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
                page_images = await self._get_image_info(url)
                self.image_list.extend(page_images)
            except:
                continue

            try:
                page_urls = await self._get_urls(url)
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
