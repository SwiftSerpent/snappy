import time
import os

from playwright.sync_api import sync_playwright


class Screenshotter:
    def __init__(self, output_dir='.', fullscreen=False, close_popups=False, scroll_page=False, format='png'):
        self.output_dir = output_dir
        self.fullscreen = fullscreen
        self.close_popups = close_popups
        self.scroll_page = scroll_page
        self.format = format

    def _find_and_close_popups(self, page):
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
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(1)
        page.evaluate('window.scrollTo(0, 0)')

    def take_screenshot(self, url, filename):
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
