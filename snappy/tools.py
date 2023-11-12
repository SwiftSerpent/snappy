import time
import os

from playwright.sync_api import sync_playwright


import os
import time
from playwright.sync_api import sync_playwright

class Screenshotter:
    """
    A class for taking screenshots of web pages.

    Args:
        output_dir (str): The directory where the screenshot will be saved. Default is the current directory.
        fullscreen (bool): Whether to take a screenshot of the full screen or just the visible area. Default is False.
        close_popups (bool): Whether to close any popups that appear on the page before taking the screenshot. Default is False.
        scroll_page (bool): Whether to scroll the page to capture the entire page. Default is False.
        format (str): The format of the screenshot. Default is 'png'.

    Attributes:
        output_dir (str): The directory where the screenshot will be saved.
        fullscreen (bool): Whether to take a screenshot of the full screen or just the visible area.
        close_popups (bool): Whether to close any popups that appear on the page before taking the screenshot.
        scroll_page (bool): Whether to scroll the page to capture the entire page.
        format (str): The format of the screenshot.

    Methods:
        _find_and_close_popups(page): Private method to find and close any popups that appear on the page.
        _scroll_page(page): Private method to scroll the page to capture the entire page.
        take_screenshot(url, filename): Takes a screenshot of the specified URL and saves it with the specified filename.

    """

    def __init__(self, output_dir='.', fullscreen=False, close_popups=False, scroll_page=False, format='png'):
        self.output_dir = output_dir
        self.fullscreen = fullscreen
        self.close_popups = close_popups
        self.scroll_page = scroll_page
        self.format = format

    def _find_and_close_popups(self, page):
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
                    buttons = page.query_selector_all(query_string)
                    if len(buttons) > 0:
                        for button in buttons:
                            button.click()
                        break
                except:
                    continue

    def _scroll_page(self, page):
        """
        Private method to scroll the page to capture the entire page.

        Args:
            page: The Playwright page object.

        Returns:
            None
        """
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(1)
        page.evaluate('window.scrollTo(0, 0)')

    def take_screenshot(self, url, filename):
        """
        Takes a screenshot of the specified URL and saves it with the specified filename.

        Args:
            url (str): The URL of the web page to take a screenshot of.
            filename (str): The name of the file to save the screenshot as.

        Returns:
            The screenshot as a binary string.
        """
        if not filename:
            raise ValueError('Filename cannot be empty.')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            response = page.goto(url)

            # Close popups
            if self.close_popups:
                self._find_and_close_popups(page)

            # Scroll page
            if self.scroll_page:
                self._scroll_page(page)

            if self.fullscreen:
                photo = page.screenshot(
                    path=os.path.join(self.output_dir, f'{filename}.{self.format}'), type=self.format)
            else:
                photo = page.screenshot(
                    path=os.path.join(self.output_dir, f'{filename}.{self.format}'), full_page=True, type=self.format)

            browser.close()
            return photo
