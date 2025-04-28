import scrapy
from urllib.parse import urljoin
from datetime import datetime

class MaliSpiderSpider(scrapy.Spider):
    name = "mali_spider"
    allowed_domains = ["localhost"]
    start_urls = ["http://localhost:5000/malware"]

    def parse(self, response):
        # Find all download links
        download_links = response.css('a.btn-download::attr(href)').getall()
        for link in download_links:
            file_url = urljoin(response.url, link)
            filename = link.split('/')[-1]
            yield scrapy.Request(file_url, callback=self.save_file, cb_kwargs={'filename': filename})

    def save_file(self, response, filename):
        with open(filename, 'wb') as f:
            f.write(response.body)
        yield {
            'timestamp': datetime.now().isoformat(),  # Add ISO-formatted timestamp
            'url': response.url,
            'filename': filename,
            'status': 'downloaded',
            'size_bytes': len(response.body)
        }
