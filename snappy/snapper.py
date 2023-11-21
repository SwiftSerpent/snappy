import asyncio
import argparse
import csv
from snappy.tools import AsyncScreenshotter

"""
If installed using pip, replace "python snapper.py" with "snapper" in the following examples.  
Like this:
    snapper --urls "https://www.example.com" "https://www.example.com/blog" --output_dir "my_screenshots"


Examples:
    1. Capture screenshots for specific URLs:
        python snapper.py --urls "https://www.example.com" "https://www.example.com/blog"

    2. Capture screenshots for URLs specified in a CSV file:
        python snapper.py --csv urls.csv

    3. Customize settings:
        python snapper.py --urls "https://www.example.com" "https://www.example.com/blog" \
            --output_dir "test_async_screenshotter" --fullscreen --close_popups --scroll_delay 2 --device "iPhone 11"

Expected CSV Format:
    https://www.example.com
    https://www.example.com/blog
    # Add more URLs...

Available Devices:
    Explore available devices for emulation:
    https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/deviceDescriptorsSource.json

Device Examples:
    - "Pixel 7"
    - "iPhone 13"
    - "Desktop Safari"
"""

async def test_website(urls, output_dir='screenshots', fullscreen=True, close_popups=True, scroll_delay=0, device=None):
    """
    Test websites and capture screenshots.

    Args:
        urls (list): List of URLs to test.
        output_dir (str): Output directory for screenshots. Default is 'screenshots'.
        fullscreen (bool): Capture fullscreen screenshots. Default is True.
        close_popups (bool): Close popups before taking screenshots. Default is True.
        scroll_delay (int): If greater than 0, scroll the page to capture the entire content. Default is 0.
        device (str): Device to emulate for mobile screenshots. Default is 'iPhone 11'.

    Returns:
        None
    """
    screenshotter = AsyncScreenshotter(output_dir=output_dir, fullscreen=fullscreen, close_popups=close_popups, scroll_delay=scroll_delay)

    tasks = []
    for url in urls:
        tasks.append(screenshotter.take_screenshot(url, url.split("/")[-1]))
        if device:
            tasks.append(screenshotter.take_screenshot(url, url.split("/")[-1] + "_mobile", device=device))

    await asyncio.gather(*tasks)

def read_urls_from_csv(csv_filename):
    """
    Read URLs from a CSV file.

    Args:
        csv_filename (str): Path to the CSV file.

    Returns:
        list: List of URLs.
    """
    with open(csv_filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        return [row[0] for row in reader]

def main():
    """
    Main function to parse command-line arguments and run the website testing.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Test website and capture screenshots.')
    parser.add_argument('--urls', nargs='+', help='List of URLs to test')
    parser.add_argument('--csv', help='CSV file containing URLs')
    parser.add_argument('--output_dir', default='screenshots', help='Output directory for screenshots')
    parser.add_argument('--fullscreen', action='store_true', help='Capture fullscreen screenshots')
    parser.add_argument('--close_popups', action='store_true', help='Close popups before taking screenshots')
    parser.add_argument('--scroll_delay', default=0, help='If greater than 0, scroll the page to capture the entire content', type=int)
    parser.add_argument('--device', default='iPhone 11', help='Device to emulate for mobile screenshots')

    args = parser.parse_args()

    if args.urls:
        urls = args.urls
    elif args.csv:
        urls = read_urls_from_csv(args.csv)
    else:
        print("Please provide either --urls or --csv option.")
        return

    asyncio.run(test_website(urls, output_dir=args.output_dir, fullscreen=args.fullscreen, close_popups=args.close_popups, scroll_delay=args.scroll_delay, device=args.device))

if __name__ == "__main__":
    main()