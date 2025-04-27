import scrapy
import urllib.parse

class XSSPlaywrightSpider(scrapy.Spider):
    name = "xss_playwright"
    start_urls = ["http://localhost:5001/xss_img"]

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
        #  (optional) bypass any CSP headers so inline JS can run
        # await page.set_bypass_csp(True)


        # monkey-patch alert() so it stores its argument instead of popping a dialog
        await page.evaluate("""
            () => {
                window._lastAlert = "";
                window.alert = msg => { window._lastAlert = msg; };
            }
        """)


         # give the page more time to run onload/onerror handlers
        await page.wait_for_timeout(1000)

        # if your payload injects a <details> or <input> you need to trigger them:
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
