import os
import asyncio
from playwright.async_api import async_playwright

class AsyncScreenshotter:
    """
    A class for taking screenshots of web pages asynchronously.

    Args:
        output_dir (str): The directory where the screenshot will be saved. Default is the current directory.
        fullscreen (bool): Whether to take a screenshot of the full screen or just the visible area. Default is False.
        close_popups (bool): Whether to close any popups that appear on the page before taking the screenshot. Default is False.
        scroll_delay (int): Whether to scroll the page to capture the entire page. Default is 0.
        format (str): The format of the screenshot. Default is 'png'.
        device (str): The device type for which the screenshot should be taken. Default is None.

    Attributes:
        output_dir (str): The directory where the screenshot will be saved.
        fullscreen (bool): Whether to take a screenshot of the full screen or just the visible area.
        close_popups (bool): Whether to close any popups that appear on the page before taking the screenshot.
        scroll_delay (int): Whether to scroll the page to capture the entire page and how long to wait for resources to load.
        format (str): The format of the screenshot.
        device (str): The device type for which the screenshot should be taken.

    Methods:
        _find_and_close_popups(page): Private method to find and close any popups that appear on the page.
        _scroll_page(page): Private method to scroll the page to capture the entire page.
        async take_screenshot(url, filename, device): Takes a screenshot of the specified URL and saves it with the specified filename.

    """

    def __init__(self, output_dir='.', fullscreen=False, headless=True, close_popups=False, format='png', device=None, scroll_delay=1):
        self.output_dir = output_dir
        self.fullscreen = fullscreen
        self.headless = headless
        self.close_popups = close_popups
        self.scroll_delay = scroll_delay
        self.format = format
        self.device = device

    async def _find_and_close_popups(self, page):
        """
        Private method to find and close any popups that appear on the page.

        Args:
            page: The Playwright page object.

        Returns:
            None
        """
        link_text_to_click = ['reject', 'decline',
                              'accept', 'acknowledge', 'necessary', 'allow']
        for link_text in link_text_to_click:
            query_strings = [
                f'button:has-text("{link_text}")',
                f'a:has-text("{link_text}")',
            ]
            while len(query_strings) > 0:
                query_string = query_strings.pop(0)
                try:
                    buttons = await page.query_selector_all(query_string)
                    if len(buttons) > 0:
                        for button in buttons:
                            await button.click()
                        break
                except:
                    continue

    async def _scroll_page(self, page):
        """
        Private method to scroll the page to capture the entire page.

        Args:
            page: The Playwright page object.

        Returns:
            None
        """
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(self.scroll_delay)
        await page.evaluate('window.scrollTo(0, 0)')

    async def take_screenshot(self, url, filename, device=None):
        """
        Takes a screenshot of the specified URL and saves it with the specified filename.

        Args:
            url (str): The URL of the web page to take a screenshot of.
            filename (str): The name of the file to save the screenshot as.
            device (str): The device type for which the screenshot should be taken. Default is None.

        Returns:
            The screenshot as a binary string.
        """
        if not filename:
            raise ValueError('Filename cannot be empty.')

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()

            if device:
                print("attempting device emulation")
                emulated_device = p.devices[device]
                context = await browser.new_context(**emulated_device)

            page = await context.new_page()
            response = await page.goto(url)

            # Close popups
            if self.close_popups:
                await self._find_and_close_popups(page)

            # Scroll page
            if self.scroll_delay > 0:
                await self._scroll_page(page)

            if self.fullscreen:
                photo = await page.screenshot(
                    path=os.path.join(self.output_dir, f'{filename}.{self.format}'), type=self.format, full_page=True)
            else:
                photo = await page.screenshot(
                    path=os.path.join(self.output_dir, f'{filename}.{self.format}'), type=self.format)

            await browser.close()
            return photo
