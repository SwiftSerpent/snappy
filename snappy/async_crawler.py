import asyncio
from acrawlers import ImageCrawler, UrlCrawler
import csv

def write_csv_from_dict(dictionary, filename):
    """
    Writes a CSV file from a dictionary where the key is a URL and the value is a list of links from that URL.

    :param dictionary: The dictionary with URLs and links.
    :param filename: The name of the CSV file to write.
    """
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Source URL', 'Target URL'])  # Write CSV header

        for source, targets in dictionary.items():
            for target in targets:
                writer.writerow([source, target])

async def main():
    base_url = "https://sallysbakingaddiction.com/"  # Replace with the URL you want to crawl
    crawl_external = False
    external_crawl_depth = 1
    headers = None
    parser = 'playwright'
    limit = 1000  # Limit the number of pages to crawl (set to None for unlimited)

    url_crawler = UrlCrawler(base_url, crawl_external, external_crawl_depth, headers, parser, limit)
    await url_crawler.run()

    print(f"Number of URLs crawled: {len(url_crawler)}")
    print("-"*20)
    print(f"List of crawled URLs:")
    for url in url_crawler:
        print(url)
    print("-"*20)

    print(f"Number of images found: {len(url_crawler.url_list)}")
    print("-"*20)

    print(f"List of crawled images:")
    for url_info in url_crawler.url_list:
        print(url_info)
    print("-"*20)

    csv_filename = 'links.csv'
    write_csv_from_dict(url_crawler.adjacency_list, csv_filename)

if __name__ == "__main__":
    asyncio.run(main())