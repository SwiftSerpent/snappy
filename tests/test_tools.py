import unittest
import os

from snappy.tools import Screenshotter


class TestScreenshotter(unittest.TestCase):
  def test_take_screenshot(self):
    img_format = 'png'
    screenshotter = Screenshotter(format=img_format)
    url = 'https://www.google.com'
    filename = 'google'
    screenshotter.take_screenshot(url, filename)
    self.assertTrue(os.path.exists(filename + '.' + img_format))

  def test_take_screenshot_with_invalid_url(self):
    screenshotter = Screenshotter()
    url = 'invalid_url'
    filename = 'invalid'
    with self.assertRaises(Exception):
      screenshotter.take_screenshot(url, filename)

  def test_take_screenshot_with_invalid_filename(self):
    screenshotter = Screenshotter()
    url = 'https://www.google.com'
    filename = ''
    with self.assertRaises(Exception):
      screenshotter.take_screenshot(url, filename)

  def test_take_screenshot_with_fullscreen(self):
    img_format = 'png'
    screenshotter = Screenshotter(fullscreen=True, format=img_format)
    url = 'https://www.google.com'
    filename = 'google_fullscreen'
    screenshotter.take_screenshot(url, filename)
    self.assertTrue(os.path.exists(filename + '.' + img_format))

  def test_take_screenshot_with_close_popups(self):
    img_format = 'png'
    screenshotter = Screenshotter(close_popups=True, format=img_format)
    url = 'https://www.google.com'
    filename = 'google_close_popups'
    screenshotter.take_screenshot(url, filename)
    self.assertTrue(os.path.exists(filename + '.' + img_format))

  def test_take_screenshot_with_scroll_page(self):
    img_format = 'png'
    screenshotter = Screenshotter(scroll_page=True, format=img_format)
    url = 'https://www.google.com'
    filename = 'google_scroll_page'
    screenshotter.take_screenshot(url, filename)
    self.assertTrue(os.path.exists(filename + '.' + img_format))
