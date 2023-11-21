import asyncio
from snappy.acrawlers import ImageCrawler

async def main():
    base_url = "https://pbrown.dev"  # Replace with the URL you want to crawl
    crawl_external = False
    external_crawl_depth = 1
    headers = None
    parser = 'playwright'
    limit = 10  # Limit the number of pages to crawl (set to None for unlimited)

    image_crawler = ImageCrawler(base_url, crawl_external, external_crawl_depth, headers, parser, limit)
    await image_crawler.run()

    print(f"Number of URLs crawled: {len(image_crawler)}")
    print(f"List of crawled URLs:")
    for url in image_crawler:
        print(url)

    print(f"Number of images found: {len(image_crawler.image_list)}")
    print(f"List of crawled images:")
    for image_info in image_crawler.image_list:
        print(image_info)

if __name__ == "__main__":
    asyncio.run(main())