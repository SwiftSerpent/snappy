import tracemalloc
import unittest
import os
import asyncio
from tools import AsyncScreenshotter

tracemalloc.start()

class TestAsyncScreenshotter(unittest.IsolatedAsyncioTestCase):
    async def test_take_screenshot(self):
        img_format = 'png'
        screenshotter = AsyncScreenshotter(format=img_format, output_dir='test_images')
        url = 'https://www.google.com'
        filename = 'google'
        await screenshotter.take_screenshot(url, filename)
        self.assertTrue(os.path.exists(os.path.join('test_images', filename + '.' + img_format)))

    async def test_take_screenshot_with_invalid_url(self):
        screenshotter = AsyncScreenshotter(output_dir='test_images')
        url = 'invalid_url'
        filename = 'invalid'
        with self.assertRaises(Exception):
            await screenshotter.take_screenshot(url, filename)

    async def test_take_screenshot_with_invalid_filename(self):
        screenshotter = AsyncScreenshotter(output_dir='test_images')
        url = 'https://www.google.com'
        filename = ''
        with self.assertRaises(Exception):
            await screenshotter.take_screenshot(url, filename)

    async def test_take_screenshot_with_fullscreen(self):
        img_format = 'png'
        screenshotter = AsyncScreenshotter(fullscreen=True, format=img_format, output_dir='test_images')
        url = 'https://www.google.com'
        filename = 'google_fullscreen'
        await screenshotter.take_screenshot(url, filename)
        self.assertTrue(os.path.exists(os.path.join('test_images', filename + '.' + img_format)))

    async def test_take_screenshot_with_close_popups(self):
        img_format = 'png'
        screenshotter = AsyncScreenshotter(close_popups=True, format=img_format, output_dir='test_images')
        url = 'https://www.google.com'
        filename = 'google_close_popups'
        await screenshotter.take_screenshot(url, filename)
        self.assertTrue(os.path.exists(os.path.join('test_images', filename + '.' + img_format)))

    async def test_take_screenshot_with_scroll_delay(self):
        img_format = 'png'
        screenshotter = AsyncScreenshotter(scroll_delay=1, format=img_format, output_dir='test_images')
        url = 'https://www.google.com'
        filename = 'google_scroll_page'
        await screenshotter.take_screenshot(url, filename)
        self.assertTrue(os.path.exists(os.path.join('test_images', filename + '.' + img_format)))
    
    async def test_take_screenshot_with_device_emulation(self):
        img_format = 'png'
        screenshotter = AsyncScreenshotter(format=img_format, output_dir='test_images')
        url = 'https://www.google.com'
        filename = 'google_iphone_13'
        device = 'iPhone 13'  # Specify the device for emulation
        await screenshotter.take_screenshot(url, filename, device=device)
        self.assertTrue(os.path.exists(os.path.join('test_images', filename + '.' + img_format)))

if __name__ == '__main__':
    asyncio.run(unittest.main())
