from snappy.crawlers import ImageCrawler
from pprint import pprint

if __name__ == '__main__':
  crawler = ImageCrawler('https://www.pbrown.dev', parser='playwright', crawl_external=True, external_crawl_depth=5)
  crawler.run()
  print('Images found:', len(crawler.image_list))
  pprint(crawler.image_list)