import scrapy
from urllib.parse import urljoin

class MaliSpiderSpider(scrapy.Spider):
    name = "mali_spider"
    allowed_domains = ["localhost"]
    start_urls = ["http://localhost:5000/malware"]  # Change port if needed

    def parse(self, response):
        # Find the download link
        download_link = response.css('a.btn-download::attr(href)').get()
        if download_link:
            # Make the link absolute
            file_url = urljoin(response.url, download_link)
            self.log(f"Found download link: {file_url}")
            # Yield a request to download the file, with a callback to save it
            yield scrapy.Request(file_url, callback=self.save_file)

    def save_file(self, response):
        # Save the file to disk
        filename = "MalwareSimulation.exe"
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f"Downloaded file saved as {filename}")
