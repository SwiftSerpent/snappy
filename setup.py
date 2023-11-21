from setuptools import setup, find_packages

setup(
    name='swift-snappy',
    version='0.0.1',
    description='Crawl any website, extracting URLs, images, or clean screenshots.',
    author='SwiftSerpent',
    author_email='brownpt98@gmail.com',
    packages=find_packages(),
    install_requires=[
        'playwright',
        'requests',
        'bs4',
        'urllib3',
        'asyncio',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'snapper = snappy.snapper:main',
        ],
    },
)
