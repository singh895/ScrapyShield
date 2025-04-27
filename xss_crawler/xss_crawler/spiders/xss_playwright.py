import scrapy
import urllib.parse

class XSSPlaywrightSpider(scrapy.Spider):
    name = "xss_playwright"
    start_urls = ["http://localhost:5001/xss_script"]

    def start_requests(self):
        with open("/workspaces/ScrapyShield/xss_crawler/payloads.txt") as f:
            for line in f:
                payload = line.strip()
                url = f"{self.start_urls[0]}?name={urllib.parse.quote(payload)}"
                yield scrapy.Request(
                    url,
                    callback=self.parse_result,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "payload": payload,
                    },
                    dont_filter=True,
                )

    async def parse_result(self, response):
        page = response.meta["playwright_page"]
        payload = response.meta["payload"]
        await page.evaluate("""
            () => {
                window._lastAlert = "";
                window.alert = msg => { window._lastAlert = msg; };
            }
        """)


        await page.wait_for_timeout(1000)
        if "<details" in payload:
            await page.click("details")
            await page.wait_for_timeout(500)
        if "<input" in payload:
            await page.focus("input")
            await page.wait_for_timeout(500)

        alert_text = await page.evaluate("() => window._lastAlert")
        await page.close()

        yield {
            "url": response.url,
            "payload": payload,
            "alert_text": alert_text,
            "xss_triggered": bool(alert_text),
        }
