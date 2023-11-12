from snappy.tools import Screenshotter

if __name__ == '__main__':
  screenshotter = Screenshotter(output_dir='test_images', close_popups=True, scroll_page=True)
  screenshotter.take_screenshot('https://frntpg-next.vercel.app', 'frntpg1')