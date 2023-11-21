import asyncio
from snappy.tools import AsyncScreenshotter

async def main():
  screenshotter = AsyncScreenshotter(output_dir='test_images', close_popups=True, scroll_delay=1)
  await screenshotter.take_screenshot('https://frntpg-next.vercel.app', 'frntpg1')

if __name__ == '__main__':
  asyncio.run(main())