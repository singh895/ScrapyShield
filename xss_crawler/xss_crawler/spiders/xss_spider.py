import scrapy
from scrapy.linkextractors import LinkExtractor
import urllib.parse

class XSSSpider(scrapy.Spider):
    name = "xss_spider"
    allowed_domains = ["localhost"]
    start_urls = ["http://localhost:5001/xss"]

    def parse(self, response):
        with open("/workspaces/ScrapyShield/xss_crawler/xss_crawler/payloads.txt", "r") as f:
            xss_payloads = [line.strip() for line in f]
            for payload in xss_payloads:
                url = response.url + f"?name={urllib.parse.quote(payload)}"
                yield scrapy.Request(url, callback=self.check_xss, meta={'payload': payload})
                if payload in response.text:
                    print(f"[!] Payload reflected: {payload}")
        # self.log(f"Visiting: {response.url}")

        # # Extract links to attack pages
        # attack_links = response.xpath("//a/@href").extract()

        # for link in attack_links:
        #     if "xss_" in link:  # Filter only XSS attack pages
        #         yield response.follow(link, callback=self.parse_attack)

    
    def check_xss(self, response):
        payload = response.meta['payload']
        if payload in response.text:
            self.logger.info(f"[!] Potential XSS at {response.url} with payload: {payload}")
            yield {
                'url': response.url,
                'payload': payload,
                'content': response.text
            }
            self.logger.info(f"[🧪 XSS FOUND] Payload reflected: {payload}")
        else:
            self.logger.info(f"[✅ SAFE] Payload NOT reflected: {payload}")

    def parse_attack(self, response):
        self.log(f"Testing XSS on: {response.url}")
        yield {"url": response.url, "content": response.text}

    # def parse(self, response):

    #     # Extract links from XSS page
    #     link_extractor = LinkExtractor()
    #     links = link_extractor.extract_links(response)

    #     for link in links:
    #         yield scrapy.Request(url=link.url, callback=self.parse_page)

    # def parse_page(self, response):
    #     # Log any suspicious script tags
    #     scripts = response.xpath("//script/text()").getall()
    #     images = response.xpath("//img/@onerror").getall()
    #     iframes = response.xpath("//iframe/@src").getall()

    #     if scripts:
    #         self.logger.warning(f"[XSS Found] Script tags in {response.url}: {scripts}")
    #     if images:
    #         self.logger.warning(f"[XSS Found] Image XSS in {response.url}: {images}")
    #     if iframes:
    #         self.logger.warning(f"[XSS Found] Iframe XSS in {response.url}: {iframes}")

    #     # Store results in a file
    #     with open("xss_log.txt", "a") as f:
    #         f.write(f"URL: {response.url}\n")
    #         f.write(f"Scripts: {scripts}\n")
    #         f.write(f"Images: {images}\n")
    #         f.write(f"Iframes: {iframes}\n")
    #         f.write("="*50 + "\n")

