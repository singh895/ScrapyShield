BOT_NAME = 'malware_crawler'
USER_AGENT = 'SecurityScanner/1.0 (+http://yourdomain.com)'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

AUTOTHROTTLE_ENABLED = True
DOWNLOAD_DELAY = 1  # Be gentle with local server