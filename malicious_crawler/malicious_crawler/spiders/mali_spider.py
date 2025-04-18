import scrapy


class MaliSpiderSpider(scrapy.Spider):
    name = "mali_spider"
    allowed_domains = ["127.0.0.1:5001"]
    start_urls = ["http://127.0.0.1:5001/malware"]

    def parse(self, response):
        pass
