# snappy

## Installation

```
pip install swift-snappy
```

## Usage

Examples:

1. Capture screenshots for specific URLs:
```
snapper --urls "https://www.example.com" "https://www.example.com/blog"
```
2. Capture screenshots for URLs specified in a CSV file:
```
snapper --csv urls.csv
```
3. Customize settings:
```
snapper --urls "https://www.example.com" "https://www.example.com/blog" \
--output_dir "test_async_screenshotter" --fullscreen --close_popups --scroll_delay 2 --device "iPhone 11"
```
