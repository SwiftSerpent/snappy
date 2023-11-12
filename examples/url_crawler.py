from snappy.crawlers import UrlCrawler
from pprint import pprint

if __name__ == '__main__':
  crawler = UrlCrawler('https://www.pbrown.dev', parser='playwright')
  crawler.run()
  pprint(crawler.url_list)
  pprint(crawler.adjacency_list)
  print('URLs found:', len(crawler.url_list))
  print('Internal URL count:', len(crawler.internal_urls))
  print('External URL count:', len(crawler.external_urls))