# BEGIN: 6b2f8d5d7f6c
import unittest
from snappy.crawlers import UrlCrawler, ImageCrawler


class TestUrlCrawler(unittest.TestCase):
  def setUp(self):
    self.base_url = 'https://example.com'
    self.crawler = UrlCrawler(self.base_url)

  def test_internal_urls(self):
    self.assertEqual(len(self.crawler.internal_urls), 0)

  def test_external_urls(self):
    self.assertEqual(len(self.crawler.external_urls), 0)

  def test_is_internal_url(self):
    self.assertTrue(self.crawler._is_internal_url(self.base_url))
    self.assertTrue(self.crawler._is_internal_url(self.base_url + '/about'))
    self.assertFalse(self.crawler._is_internal_url('https://google.com'))

  def test_is_image(self):
    self.assertFalse(self.crawler._is_image(self.base_url))
    self.assertFalse(self.crawler._is_image(self.base_url + '/about'))
    self.assertTrue(self.crawler._is_image(self.base_url + '/image.jpg'))

  def test_run(self):
    self.crawler.run()
    self.assertGreater(len(self.crawler.internal_urls), 0)


class TestImageCrawler(unittest.TestCase):
  def setUp(self):
    self.base_url = 'https://example.com'
    self.crawler = ImageCrawler(self.base_url)

  def test_internal_urls(self):
    self.assertEqual(len(self.crawler.internal_urls), 0)

  def test_external_urls(self):
    self.assertEqual(len(self.crawler.external_urls), 0)

  def test_is_internal_url(self):
    self.assertTrue(self.crawler._is_internal_url(self.base_url))
    self.assertTrue(self.crawler._is_internal_url(self.base_url + '/about'))
    self.assertFalse(self.crawler._is_internal_url('https://google.com'))

  def test_is_image(self):
    self.assertFalse(self.crawler._is_image(self.base_url))
    self.assertFalse(self.crawler._is_image(self.base_url + '/about'))
    self.assertTrue(self.crawler._is_image(self.base_url + '/image.jpg'))

  def test_run(self):
    self.crawler.run()
    self.assertGreater(len(self.crawler.internal_urls), 0)
    self.assertGreaterEqual(len(self.crawler.image_list), 0)